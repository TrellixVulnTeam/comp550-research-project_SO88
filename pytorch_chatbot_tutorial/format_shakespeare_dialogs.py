# Source: https://github.com/pytorch/tutorials/blob/master/beginner_source/chatbot_tutorial.py

import csv
import os

corpus_name = "shakespeare"
corpus = os.path.join("data", corpus_name)
datafile = os.path.join(corpus, 'shakespeare.csv')
formatted_datafile = os.path.join(corpus, 'formatted_shakespeare.txt')

lines = []

with open(datafile) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        playerLine = row[5]
        lines.append(playerLine)
        
# Write new csv file
print("\nWriting newly formatted file...")
with open(formatted_datafile, 'w', encoding='utf-8') as outputfile:
    writer = csv.writer(outputfile, delimiter='\t', lineterminator='\n')
    for line_index in range(1, len(lines) - 1):
        current_line = lines[line_index]
        next_line = lines[line_index + 1]
        writer.writerow([current_line, next_line])
