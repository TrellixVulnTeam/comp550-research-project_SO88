# Dataset source: https://github.com/bpb27/trump_tweet_data_archive

import json
import os

CORPUS_DIR = "trump_corpus"

def fetch(outfile):
    tweets = []
    
    for year in range(2009, 2019):
        with open(os.path.join(CORPUS_DIR, "raw", f"condensed_{year}.json"), 'r') as f:
            lines = json.load(f)
            for line in lines:
                tweet = line['text']
                tweet = tweet.replace('\n', ' ')
                tweets.append(tweet)


    with open(os.path.join(CORPUS_DIR, outfile), 'w') as f:
        for tweet in tweets:
            f.write(tweet + "\n")
