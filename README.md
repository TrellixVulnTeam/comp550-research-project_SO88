### comp550-research-project

# How to interact with chatbot
$ cd transfer-learning-conv-ai
$ python ./interact.py --dataset_path Sheldon.txt --log conv1.txt --inter yes --NER yes
remember to remove dataset_cache_OpenAIGPTTokenizer when you change character

# How to generate friends and BBT corpus

1. edit the character name in dialogue_gen.py to the character that you want

2. use friends_gen for friends corpus or BBT_gen for BBT corpus

2. $python dialogue_gen.py


# How to generate Trump corpus

1. in dialogue_gen.py, use trump_gen

2. $python dialogue_gen.py
