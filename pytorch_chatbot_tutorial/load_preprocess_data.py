# Source: https://github.com/pytorch/tutorials/blob/master/beginner_source/chatbot_tutorial.py

from constants import EOS_token, PAD_token, SOS_token
from string_utils import normalizeString

######################################################################
# Load and trim data
# ~~~~~~~~~~~~~~~~~~
#
# Our next order of business is to create a vocabulary and load
# query/response sentence pairs into memory.
#
# Note that we are dealing with sequences of **words**, which do not have
# an implicit mapping to a discrete numerical space. Thus, we must create
# one by mapping each unique word that we encounter in our dataset to an
# index value.
#
# For this we define a ``Voc`` class, which keeps a mapping from words to
# indexes, a reverse mapping of indexes to words, a count of each word and
# a total word count. The class provides methods for adding a word to the
# vocabulary (``addWord``), adding all words in a sentence
# (``addSentence``) and trimming infrequently seen words (``trim``). More
# on trimming later.
#

class Voc:
    def __init__(self, name):
        self.name = name
        self.trimmed = False
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token: "PAD", SOS_token: "SOS", EOS_token: "EOS"}
        self.num_words = 3  # Count SOS, EOS, PAD

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.num_words
            self.word2count[word] = 1
            self.index2word[self.num_words] = word
            self.num_words += 1
        else:
            self.word2count[word] += 1

    # Remove words below a certain count threshold
    def trim(self, min_count):
        if self.trimmed:
            return
        self.trimmed = True

        keep_words = []

        for k, v in self.word2count.items():
            if v >= min_count:
                keep_words.append(k)

        print('keep_words {} / {} = {:.4f}'.format(
            len(keep_words), len(self.word2index), len(keep_words) / len(self.word2index)
        ))

        # Reinitialize dictionaries
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token: "PAD", SOS_token: "SOS", EOS_token: "EOS"}
        self.num_words = 3 # Count default tokens

        for word in keep_words:
            self.addWord(word)


######################################################################
# Now we can assemble our vocabulary and query/response sentence pairs.
# Before we are ready to use this data, we must perform some
# preprocessing.
#
# First, we must convert the Unicode strings to ASCII using
# ``unicodeToAscii``. Next, we should convert all letters to lowercase and
# trim all non-letter characters except for basic punctuation
# (``normalizeString``). Finally, to aid in training convergence, we will
# filter out sentences with length greater than the ``MAX_LENGTH``
# threshold (``filterPairs``).
#

# Read query/response pairs and return a voc object
def readVocs(datafile, corpus_name):
    print("Reading lines...")
    # Read the file and split into lines
    lines = open(datafile, encoding='utf-8').\
        read().strip().split('\n')
    # Split every line into pairs and normalize
    pairs = [[normalizeString(s) for s in l.split('\t')] for l in lines]
    voc = Voc(corpus_name)
    return voc, pairs

# Returns True iff both sentences in a pair 'p' are under the MAX_LENGTH threshold
def filterPair(p, max_length):
    # Input sequences need to preserve the last word for EOS token
    return len(p[0].split(' ')) < max_length and len(p[1].split(' ')) < max_length

# Filter pairs using filterPair condition
def filterPairs(pairs, max_length):
    return [pair for pair in pairs if filterPair(pair, max_length)]

# Using the functions defined above, return a populated voc object and pairs list
def loadPrepareData(corpus, corpus_name, datafile, save_dir, max_length):
    print("Start preparing training data ...")
    voc, pairs = readVocs(datafile, corpus_name)
    print("Read {!s} sentence pairs".format(len(pairs)))
    pairs = filterPairs(pairs, max_length)
    print("Trimmed to {!s} sentence pairs".format(len(pairs)))
    print("Counting words...")
    for pair in pairs:
        voc.addSentence(pair[0])
        voc.addSentence(pair[1])
    print("Counted words:", voc.num_words)
    return voc, pairs

# Load/Assemble voc and pairs
def loadAssembleVocAndPairs(corpus, corpus_name, datafile, save_dir, max_length):
    voc, pairs = loadPrepareData(corpus, corpus_name, datafile, save_dir, max_length)
    # Print some pairs to validate
    print("\npairs:")
    for pair in pairs[:10]:
        print(pair)
        
    return voc, pairs, corpus_name


######################################################################
# Another tactic that is beneficial to achieving faster convergence during
# training is trimming rarely used words out of our vocabulary. Decreasing
# the feature space will also soften the difficulty of the function that
# the model must learn to approximate. We will do this as a two-step
# process:
#
# 1) Trim words used under ``MIN_COUNT`` threshold using the ``voc.trim``
#    function.
#
# 2) Filter out pairs with trimmed words.
#

MIN_COUNT = 3    # Minimum word count threshold for trimming

def trimRareWords(voc, pairs, MIN_COUNT):
    # Trim words used under the MIN_COUNT from the voc
    voc.trim(MIN_COUNT)
    # Filter out pairs with trimmed words
    keep_pairs = []
    for pair in pairs:
        input_sentence = pair[0]
        output_sentence = pair[1]
        keep_input = True
        keep_output = True
        # Check input sentence
        for word in input_sentence.split(' '):
            if word not in voc.word2index:
                keep_input = False
                break
        # Check output sentence
        for word in output_sentence.split(' '):
            if word not in voc.word2index:
                keep_output = False
                break

        # Only keep pairs that do not contain trimmed word(s) in their input or output sentence
        if keep_input and keep_output:
            keep_pairs.append(pair)

    print("Trimmed from {} pairs to {}, {:.4f} of total".format(len(pairs), len(keep_pairs), len(keep_pairs) / len(pairs)))
    return keep_pairs


def loadPreprocessData(corpus, corpus_name, datafile, save_dir, max_length):
    voc, pairs, corpus_name = loadAssembleVocAndPairs(corpus, corpus_name, datafile, save_dir, max_length)
    
    # Trim voc and pairs
    pairs = trimRareWords(voc, pairs, MIN_COUNT)
    
    return voc, pairs, corpus_name