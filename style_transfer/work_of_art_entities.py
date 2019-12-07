import os
import re
import spacy

from collections import Counter

nlp = spacy.load("en_core_web_sm")

WORK_OF_ART_ENTITIES_DIRECTORY = "work_of_art_entities"

CORPORA = {
    'BBT_corpus': ['Howard', 'Leonard', 'Penny', 'Raj', 'Sheldon'],
    'friends_corpus': ['Chandler', 'Joey', 'Monica', 'Phoebe', 'Rachel', 'Ross'],
    'trump_corpus': ['Trump']
}

ENTITY_REGEX = re.compile('^.*[a-zA-Z].*$') # Must contain at least one letter (used to filter out invalid entities)


def load_lines(corpus, person):
    with open(os.path.join(os.pardir, corpus, f"{person}.txt"), 'r') as f:
        return f.read().splitlines()


def collect_named_entities(doc, named_entity_counter):
    for entity in doc.ents:
        entity_text = entity.text.lower().strip()
        
        if entity.label_ == 'WORK_OF_ART' and re.match(ENTITY_REGEX, entity_text):
            named_entity_counter[entity_text] += 1


def get_frequent_counter_elements(counter, threshold=10):
    frequent_elements = []
    
    for key in counter:
        if counter[key] >= threshold:
            frequent_elements.append(key)
            
    return frequent_elements


def write_list_to_file(elements, corpus, person):
    with open(os.path.join(WORK_OF_ART_ENTITIES_DIRECTORY, corpus, f"{person}.txt"), 'w') as f:
        for element in elements:
            f.write(f"{element}\n")


for corpus, persons in CORPORA.items():
    for person in persons:
        work_of_art_entity_counter = Counter()
        
        for line in load_lines(corpus, person):
        
            doc = nlp(line)
            
            collect_named_entities(doc, work_of_art_entity_counter)

        frequent_work_of_art_entities = get_frequent_counter_elements(work_of_art_entity_counter)
        write_list_to_file(frequent_work_of_art_entities, corpus, person)