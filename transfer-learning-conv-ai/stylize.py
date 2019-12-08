import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random
import spacy

nlp = spacy.load("en_core_web_sm")

'''
swap NER after adding interjections
'''
def swap_NER(sentence, NER_dict):
    doc = nlp(sentence)
    NP = ""
    output = sentence
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
    return output
                        




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


def setup_NERs():
    corpus = "BBT_corpus"
    person = "Sheldon"
    fname = os.path.join(os.pardir, "style_transfer","NER", corpus, f"{person}.txt")


    NER_dict = {"win": ["my nobel prize", "a nobel prize", "the nobel peace prize", "the nobel prize"], 
    "share": ["a nobel prize"], "bring": ["these star wars sheets"], 
    "return": ["my star wars sheets"], "have": ["the nobel prize"], 
    "destroy": ["the batman movie franchise"], 
    "meet": ["her bible study group"], 
    "see": ["the new star wars movie", "star trek the motion picture"], 
    "hear": ["the original star trek theme"], 
    "adapt": ["a star trek fan fiction novella"], 
    "wear": ["a star trek uniform", "a star trek balok mask"], 
    "know": ["batman"], "include": ["a nobel prize"], 
    "clutch": ["that nobel prize"], 
    "embarrass": ["a nobel laureate"], "get": ["nobel prizes"], 
    "quote": ["the bible"], "celebrate": ["star wars day"], 
    "enjoy": ["star wars day"], "play": ["the star trek theme"], 
    "keep": ["the bible"], "compose": ["my nobel acceptance speech"], 
    "eat": ["enough star wars cereal"], "call": ["star wars toast"]}

    return NER_dict




def setup_interjections():
    #corpus = "BBT_corpus"
    #person = "Sheldon"


    corpus = "friends_corpus"
    person = "Monica"
    fname = os.path.join(os.pardir, "style_transfer","interjections", corpus, f"{person}.txt")
    interjections = read_interjections(fname)
    pos_interject, neg_interject = interject_sentiment(interjections)
    interject_dict = {}
    interject_dict["pos"] = pos_interject
    interject_dict["neg"] = neg_interject

    return interject_dict


if __name__ == "__main__":
    main()


