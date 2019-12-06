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
                is_retweet = line['is_retweet']
                tweet = line['text']
                tweet = tweet.replace('\n', ' ')
                
                if is_retweet or tweet[0:2] == "\"@": # Skip retweet or user quote
                    continue
                
                tweets.append(tweet)


    with open(os.path.join(CORPUS_DIR, outfile), 'w') as f:
        for tweet in tweets:
            f.write(tweet + "\n")
