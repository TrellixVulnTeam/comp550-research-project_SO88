import re
import os


'''
Raw corpus obtained from https://github.com/skashyap7/TBBTCorpus.git
'''



dataset_url = "https://fangj.github.io/friends/"

'''
fetch all utterance of one character in a page
ex.
Joey: Yeah, right!.......Y'serious?
'''
def episode_page(link, character, outfile):
	outfile = open(outfile,"a")  #only append
	infile = open(link, "r")

	lines = list(infile.readlines())
	infile.close()

	for line in lines:
		if (line.startswith(character)):
			parsed = line.split(":")
			#parsed[0] is the character
			sentence = ""
			for k in range(1,len(parsed)):
				sentence = sentence + parsed[k]
			outfile.write(sentence)
	outfile.close()


'''
grab all the utterances of one particular character in BBT dataset
1. grab all raw episode files
2. parse each one by character to output file
'''
def fetch_character(character, outfile):
	BBT_dir = "/mnt/c/Users/sheny/Desktop/comp550-research-project/BBT_corpus/raw"
	links = []

	#create the outfile
	f = open(outfile, "w")
	f.close()

	for file in os.listdir(BBT_dir):
	    if file.endswith(".txt"):
	        links.append(os.path.join(BBT_dir, file))

	for link in links:
		episode_page(link, character, outfile)


def main():
	print ("hi")
	

if __name__ == '__main__':
    main()



