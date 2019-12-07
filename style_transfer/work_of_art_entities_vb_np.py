import json
import os
import re
import spacy

from collections import Counter

nlp = spacy.load("en_core_web_sm")

WORK_OF_ART_ENTITIES_VB_NP_DIRECTORY = "work_of_art_entities_vb_np"

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


def write_dict_to_file(verb_to_np_dict, corpus, person):
    serializable_dict = {}
    
    for vb in verb_to_np_dict:
        serializable_dict[vb] = list(verb_to_np_dict[vb]) # Convert set (non serializable) to list (serializable)
    
    with open(os.path.join(WORK_OF_ART_ENTITIES_VB_NP_DIRECTORY, corpus, f"{person}.txt"), 'w') as f:
        json.dump(serializable_dict, f)


for corpus, persons in CORPORA.items():
    for person in persons:
        print(person)
        
        work_of_art_entity_counter = Counter()
        
        lines = load_lines(corpus, person)
        
        # Collect frequent work of art entities
        for line in lines:
        
            doc = nlp(line)
         
            collect_named_entities(doc, work_of_art_entity_counter)
        
        frequent_work_of_art_entities = get_frequent_counter_elements(work_of_art_entity_counter, threshold=5)
        
        print(frequent_work_of_art_entities)
        
        verb_to_work_of_art_np = {}
        
        # Collect verb and their associated NPs (containing work of art entity)
        for line in lines:
        
            doc = nlp(line)
        
            for chunk in doc.noun_chunks:
                np_text = chunk.text.lower().strip()
                
                for frequent_work_of_art_entity in frequent_work_of_art_entities:
                    if frequent_work_of_art_entity in np_text and chunk.root.dep_ in ['dobj']:
                        verb_text = chunk.root.head.text.lower().strip()
                        
                        if verb_text in verb_to_work_of_art_np:
                            verb_to_work_of_art_np[verb_text].add(np_text)
                        else:
                            verb_to_work_of_art_np[verb_text] = set([np_text])
                            
        print(verb_to_work_of_art_np)

        write_dict_to_file(verb_to_work_of_art_np, corpus, person)