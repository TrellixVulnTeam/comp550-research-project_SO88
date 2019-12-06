import os
import spacy

from collections import Counter

nlp = spacy.load("en_core_web_sm")

INTERJECTIONS_DIRECTORY = "interjections"

CORPORA = {
    'BBT_corpus': ['Howard', 'Leonard', 'Penny', 'Raj', 'Sheldon'],
    'friends_corpus': ['Chandler', 'Joey', 'Monica', 'Phoebe', 'Rachel', 'Ross'],
    'trump_corpus': ['Trump']
}


def load_lines(corpus, person):
    with open(os.path.join(os.pardir, corpus, f"{person}.txt"), 'r') as f:
        return f.read().splitlines()

    
def collect_interjections(token, interjection_counter, interjection_span):
    token_text = token.text.lower().strip()
    
    if token.pos_ == 'INTJ': # Start of span or in a span
        interjection_span.append(token_text)
    
    elif token.pos_ == 'PUNCT': # End of span
        if interjection_span:
            span_string = ' '.join(interjection_span)
        
            interjection_counter[span_string] += 1
                
            interjection_span.clear()
        
    elif interjection_span: # In a span
        interjection_span.append(token_text)
        
        
def get_frequent_counter_elements(counter, threshold=10):
    frequent_elements = []
    
    for key in counter:
        if counter[key] >= threshold:
            frequent_elements.append(key)
            
    return frequent_elements


def write_list_to_file(elements, corpus, person):
    with open(os.path.join(INTERJECTIONS_DIRECTORY, corpus, f"{person}.txt"), 'w') as f:
        for element in elements:
            f.write(f"{element}\n")
    

for corpus, persons in CORPORA.items():
    for person in persons:
        interjection_counter = Counter()
        
        for line in load_lines(corpus, person):
        
            doc = nlp(line)
            
            interjection_span = []
            
            for token in doc:
                collect_interjections(token, interjection_counter, interjection_span)

            
        frequent_interjections = get_frequent_counter_elements(interjection_counter)
        write_list_to_file(frequent_interjections, corpus, person)