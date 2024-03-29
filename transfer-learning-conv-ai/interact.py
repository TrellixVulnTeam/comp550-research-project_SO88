# # Copyright (c) 2019-present, HuggingFace Inc.
# All rights reserved.
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import logging
import random
from argparse import ArgumentParser
from itertools import chain
from pprint import pformat
import warnings
from stylize import *
import os
import torch
import torch.nn.functional as F

from pytorch_transformers import OpenAIGPTLMHeadModel, OpenAIGPTTokenizer, GPT2LMHeadModel, GPT2Tokenizer
from train import SPECIAL_TOKENS, build_input_from_segments, add_special_tokens_
from utils import get_dataset, download_pretrained_model

def top_filtering(logits, top_k=0., top_p=0.9, threshold=-float('Inf'), filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k, top-p (nucleus) and/or threshold filtering
        Args:
            logits: logits distribution shape (vocabulary size)
            top_k: <=0: no filtering, >0: keep only top k tokens with highest probability.
            top_p: <=0.0: no filtering, >0.0: keep only a subset S of candidates, where S is the smallest subset
                whose total probability mass is greater than or equal to the threshold top_p.
                In practice, we select the highest probability tokens whose cumulative probability mass exceeds
                the threshold top_p.
            threshold: a minimal threshold to keep logits
    """
    assert logits.dim() == 1  # Only work for batch size 1 for now - could update but it would obfuscate a bit the code
    top_k = min(top_k, logits.size(-1))
    if top_k > 0:
        # Remove all tokens with a probability less than the last token in the top-k tokens
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        # Compute cumulative probabilities of sorted tokens
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probabilities = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probabilities > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        # Back to unsorted indices and set them to -infinity
        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value

    indices_to_remove = logits < threshold
    logits[indices_to_remove] = filter_value

    return logits


def sample_sequence(personality, history, tokenizer, model, args, current_output=None):
    special_tokens_ids = tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS)
    if current_output is None:
        current_output = []

    for i in range(args.max_length):
        instance = build_input_from_segments(personality, history, current_output, tokenizer, with_eos=False)

        input_ids = torch.tensor(instance["input_ids"], device=args.device).unsqueeze(0)
        token_type_ids = torch.tensor(instance["token_type_ids"], device=args.device).unsqueeze(0)

        logits = model(input_ids, token_type_ids=token_type_ids)
        if isinstance(logits, tuple):  # for gpt2 and maybe others
            logits = logits[0]
        logits = logits[0, -1, :] / args.temperature
        logits = top_filtering(logits, top_k=args.top_k, top_p=args.top_p)
        probs = F.softmax(logits, dim=-1)

        prev = torch.topk(probs, 1)[1] if args.no_sample else torch.multinomial(probs, 1)
        if i < args.min_length and prev.item() in special_tokens_ids:
            while prev.item() in special_tokens_ids:
                if probs.max().item() == 1:
                    warnings.warn("Warning: model generating special token with probability 1.")
                    break  # avoid infinitely looping over special token
                prev = torch.multinomial(probs, num_samples=1)

        if prev.item() in special_tokens_ids:
            break
        current_output.append(prev.item())

    return current_output

def run():


    '''
    Use case
    REMEBER TO CLEAN CACHE FILE
    python ./interact.py --dataset_path english.txt --log conv --shake yes
    python ./interact.py --dataset_path sheldon.txt --log conv --inter yes --NER yes
    '''
    parser = ArgumentParser()
    parser.add_argument("--dataset_path", type=str, default="", help="Path or url of the dataset. If empty download from S3.")
    parser.add_argument("--log", type=str, default="", help="file name of the log file for conversation")
    parser.add_argument("--shake", type=str, default="", help="Shakespearize the response")
    parser.add_argument("--inter", type=str, default="", help="add interjection into bot response")
    parser.add_argument("--NER", type=str, default="", help="swap NER in bot response")



    parser.add_argument("--dataset_cache", type=str, default='./dataset_cache', help="Path or url of the dataset cache")
    parser.add_argument("--model", type=str, default="openai-gpt", help="Model type (openai-gpt or gpt2)", choices=['openai-gpt', 'gpt2'])  # anything besides gpt2 will load openai-gpt
    parser.add_argument("--model_checkpoint", type=str, default="", help="Path, url or short name of the model")
    parser.add_argument("--max_history", type=int, default=2, help="Number of previous utterances to keep in history")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu", help="Device (cuda or cpu)")



    parser.add_argument("--no_sample", action='store_true', help="Set to use greedy decoding instead of sampling")
    parser.add_argument("--max_length", type=int, default=20, help="Maximum length of the output utterances")
    parser.add_argument("--min_length", type=int, default=1, help="Minimum length of the output utterances")
    parser.add_argument("--seed", type=int, default=0, help="Seed")
    parser.add_argument("--temperature", type=int, default=0.7, help="Sampling softmax temperature")
    parser.add_argument("--top_k", type=int, default=0, help="Filter top-k tokens before sampling (<=0: no filtering)")
    parser.add_argument("--top_p", type=float, default=0.9, help="Nucleus filtering (top-p) before sampling (<=0.0: no filtering)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__file__)
    #logger.info(pformat(args))

    if args.model_checkpoint == "":
        if args.model == 'gpt2':
            raise ValueError("Interacting with GPT2 requires passing a finetuned model_checkpoint")
        else:
            args.model_checkpoint = download_pretrained_model()
    
    
    if args.seed != 0:
        random.seed(args.seed)
        torch.random.manual_seed(args.seed)
        torch.cuda.manual_seed(args.seed)


    #logger.info("Get pretrained model and tokenizer")
    tokenizer_class, model_class = (GPT2Tokenizer, GPT2LMHeadModel) if args.model == 'gpt2' else (OpenAIGPTTokenizer, OpenAIGPTLMHeadModel)
    tokenizer = tokenizer_class.from_pretrained(args.model_checkpoint)
    model = model_class.from_pretrained(args.model_checkpoint)
    model.to(args.device)
    add_special_tokens_(model, tokenizer)

    #logger.info("Sample a personality")
    dataset = get_dataset(tokenizer, args.dataset_path, args.dataset_cache)
    personalities = [dialog["personality"] for dataset in dataset.values() for dialog in dataset]
    personality = random.choice(personalities)
    logger.info("Selected personality: %s", tokenizer.decode(chain(*personality)))

    history = []
    isJoey = False
    isSheldon = False
    if ("joey" in args.log):
        isJoey = True

    if ("sheldon" in args.log):
        isSheldon = True



    interject_dict = setup_interjections(isJoey, isSheldon)
    NER_dict = setup_NERs(isJoey, isSheldon)
    shake_dict = setup_Shakespeare()

    isInterject = False
    isNER = False
    isShake = False


    if (args.shake != ""):
        isShake = True 

    if (args.inter != ""):
        isInterject = True

    if (args.NER != ""):
        isNER = True




    if (args.log != ""):
        if os.path.isfile(args.log + ".txt"):
            outfile = args.log + str(random.randint(1,100)) + ".txt"
        else:
            outfile = args.log + ".txt"
        outfile = open(outfile, "w")
        outfile.write("Selected personality: " + tokenizer.decode(chain(*personality)))
        if (isShake):
            outfile.write("Shakespearize the response \n")
        if (isInterject):
            outfile.write("Adding Interjection \n")
        if (isNER):
            outfile.write("Swapping NER \n")

    has_swap = False
    NERmod = False


    while True:
        raw_text = input(">>> ")
        while not raw_text:
            print('Prompt should not be empty!')
            raw_text = input(">>> ")

        #add exit command
        if (raw_text in ["exit", "quit"]):
            print ("exiting system, thanks for the conversation, human")
            break

        #write to log file
        if (args.log != ""):
            outfile.write("human: " + raw_text + "\n")



        history.append(tokenizer.encode(raw_text))
        with torch.no_grad():
            out_ids = sample_sequence(personality, history, tokenizer, model, args)
        history.append(out_ids)
        history = history[-(2*args.max_history+1):]
        out_text = tokenizer.decode(out_ids, skip_special_tokens=True)


        '''
        make changes to out_text here :)
        '''
        if (isShake):
            out_text, has_swap = shakespearize(out_text, shake_dict)
        elif (isInterject):
            out_text = add_interjection(out_text, interject_dict)
        elif (isNER):
            out_text, NERmod = swap_NER(out_text, NER_dict)

        print(out_text)

        #write to log file
        if (args.log != ""):
            if (NERmod):
                outfile.write("bot: " + out_text + " [NER] " "\n")
            elif (has_swap):
                outfile.write("bot: " + out_text + " [Shakespeare] " + "\n")
            else:
                outfile.write("bot: " + out_text + "\n")


        NERmod = False
        has_swap = False

    if (args.log != ""):
        print ("log file complete")
        outfile.close()




if __name__ == "__main__":
    run()
