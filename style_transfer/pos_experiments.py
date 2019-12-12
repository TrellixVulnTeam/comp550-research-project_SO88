import os
import spacy

from collections import Counter

nlp = spacy.load("en_core_web_sm")
    
lines = []

with open(os.path.join(os.pardir, 'BBT_corpus', 'Sheldon.txt'), 'r') as f:
    lines = f.read().splitlines()

    
def collect_interjections(token, interjection_counter, interjection_span):
    token_text = token.text.lower().strip()
    
    if token.pos_ == 'PUNCT':
        if interjection_span:
            span = ' '.join(interjection_span)
        
            if span in interjection_counter:
                interjection_counter[span] += 1
            else:
                interjection_counter[span] = 1
                
            interjection_span.clear()
    
    elif token.pos_ == 'INTJ':
        interjection_span.append(token_text)
        
    elif interjection_span:
        interjection_span.append(token_text)


def collect_adverbs(token, adverb_counter, adverb_span):
    token_text = token.text.lower().strip()

    if token.pos_ == 'ADV':
        adverb_span.append(token_text)
        
    elif adverb_span:
        span = ' '.join(adverb_span)
    
        if span in adverb_counter:
            adverb_counter[span] += 1
        else:
            adverb_counter[span] = 1
            
        adverb_span.clear()


def collect_adjectives(token, adjective_counter):
    token_text = token.text.lower().strip()
    
    if token.pos_ == 'ADJ' and token.tag_ == 'JJ':
        if token_text in adjective_counter:
            adjective_counter[token_text] += 1
        else:
            adjective_counter[token_text] = 1
            
            
def collect_clauses(token, clause_counter):
    token_text = token.text.lower().strip()
    
    if token.pos_ == 'PUNCT' and clauses_span:
        span = ' '.join(clauses_span)
        
        if span in clause_counter:
            clause_counter[span] += 1
        else:
            clause_counter[span] = 1
            
        clauses_span.clear()
        
    elif token_text:
        clauses_span.append(token_text)


def collect_noun_chunks(doc, noun_chunk_counter):
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        
        if ' ' in chunk_text:
            if chunk_text in noun_chunk_counter:
                noun_chunk_counter[chunk_text] += 1
            else:
                noun_chunk_counter[chunk_text] = 1


def collect_named_entities(entity_label, doc, named_entity_counter):
    for entity in doc.ents:
        entity_text = entity.text.lower().strip()
        
        if entity.label_ == entity_label:
            if entity_text in named_entity_counter:
                named_entity_counter[entity_text] += 1
            else:
                named_entity_counter[entity_text] = 1
    

interjection_counter = {}
adverb_counter = {}
adjective_counter = {}
clause_counter = {}
noun_chunk_counter = {}
person_entity_counter = {}
work_of_art_entity_counter = {}

for line in lines:

    doc = nlp(line)
    
    interjection_span = []
    adverb_span = []
    clauses_span = []
    
    for index, token in enumerate(doc):
        collect_interjections(token, interjection_counter, interjection_span)
        collect_adverbs(token, adverb_counter, adverb_span)
        collect_adjectives(token, adjective_counter)
        collect_clauses(token, clause_counter)
        
    collect_noun_chunks(doc, noun_chunk_counter)
    
    collect_named_entities('PERSON', doc, person_entity_counter)
    collect_named_entities('WORK_OF_ART', doc, work_of_art_entity_counter)

            
print("Interjections")
print(dict(Counter(interjection_counter).most_common(50)))
print("Adverbs")
print(dict(Counter(adverb_counter).most_common(50)))
print("Adjectives")
print(dict(Counter(adjective_counter).most_common(50)))
print("Clauses")
print(dict(Counter(clause_counter).most_common(50)))
print("Noun chunks")
print(dict(Counter(noun_chunk_counter).most_common(50)))
print("Person entities")
print(dict(Counter(person_entity_counter).most_common(50)))
print("Work of art entities")
print(dict(Counter(work_of_art_entity_counter).most_common(50)))