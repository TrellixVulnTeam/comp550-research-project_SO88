import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random
import spacy
import json

nlp = spacy.load("en_core_web_sm")

'''
swap NER after adding interjections
'''
def swap_NER(sentence, NER_dict):
    doc = nlp(sentence)
    NP = ""
    output = sentence
    NER_mod = False
    has_verb = False
    verb = ""
    for token in doc:
        if (token.pos_ == "VERB"):
            if (token.lemma_ in NER_dict):
                verb = token.lemma_
                NP = random.choice(NER_dict[verb])
                has_verb = True

    if (has_verb):
        for chunk in doc.noun_chunks:
            if (chunk.root.dep_ in ["nsubj", "dobj"]):
                if (chunk.root.head.text == verb):
                    output = output.replace(chunk.text, NP, 1)
                    NER_mod = True
    return (output, NER_mod)
                        




'''
heuristics for adding interjections
'''
def add_interjection(sentence, interject_dict):
    is_Pos = check_sentiment(sentence)
    interjection = ""
    if (is_Pos):
        interjection = random.choice(interject_dict["pos"])
    else:
        interjection = random.choice(interject_dict["neg"])

    output = interjection + ", " + sentence
    return output



'''
check sentiment for a sentence
False = negative 
True = positive
'''
def check_sentiment(sentence):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(sentence)
    if (ss['neg'] > 0):
        return False
    else:
        return True






'''
split interjections into two types of sentiments 
'''
def interject_sentiment(interjections):
    pos_interject = []
    neg_interject = []
    sid = SentimentIntensityAnalyzer()
    for word in interjections:
        ss = sid.polarity_scores(word)
        if (ss['neg'] > 0):
            neg_interject.append(word)
        else:
            pos_interject.append(word)
    
    return pos_interject, neg_interject


'''
read interjections from a file
'''
def read_interjections(fname):
    interjections = []
    f = open(fname, 'r')
    lines = list(f.readlines())
    f.close()

    for line in lines:
        inter = line.strip()
        interjections.append(inter)
    return interjections

def read_NER(fname):
    with open(fname, 'r') as json_file:
        NER_dict = json.load(json_file)
    return NER_dict

def setup_NERs():
    corpus = "BBT_corpus"
    person = "Sheldon"
    fname = os.path.join(os.pardir, "style_transfer","NER", corpus, f"{person}.txt")
    NER_dict = read_NER(fname)

    return NER_dict




def setup_interjections():
    corpus = "BBT_corpus"
    person = "Sheldon"


    # corpus = "friends_corpus"
    # person = "Monica"
    fname = os.path.join(os.pardir, "style_transfer","interjections", corpus, f"{person}.txt")
    interjections = read_interjections(fname)
    pos_interject, neg_interject = interject_sentiment(interjections)
    interject_dict = {}
    interject_dict["pos"] = pos_interject
    interject_dict["neg"] = neg_interject

    return interject_dict


if __name__ == "__main__":
    main()


