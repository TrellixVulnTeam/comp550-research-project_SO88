from bs4 import BeautifulSoup
from requests import get
import urllib.request
import re




dataset_url = "https://fangj.github.io/friends/"

'''
fetch all utterance of one character in a page
ex.
Joey: Yeah, right!.......Y'serious?
'''
def episode_page(link, character, outfile):
	outfile = open(outfile,"a")  #only append

	contents = urllib.request.urlopen(link).read()
	soup = BeautifulSoup(contents, 'html.parser')
	soup.prettify()

	lines = soup.get_text().split(':')   #split by \n don't work that well
	talking = False
	for line in lines:
		if (talking):
			if (not line.endswith(character)):
				talking = False
			parsed = line.split('\n')
			sentence = ""

			#check if parsed[-1] is a character
			if (" " not in parsed[-1]):
				for k in range(len(parsed)-1):
					sentence = sentence + " " + parsed[k]
			else:
				for k in range(len(parsed)):
					sentence = sentence + " " + parsed[k]

			outfile.write(sentence + "\n")
		if line.endswith(character):
			talking = True

	outfile.close()


'''
grab all the utterances of one particular character in friends dataset

1. grab all episode links in the homepage 
2. parse each episode page by character
'''
def fetch_character(character, outfile):
	response = get(dataset_url)
	soup = BeautifulSoup(response.text, 'html.parser')
	soup.prettify()
	links = []		#store all episode html

	f= open(outfile,"w")	#initialize the output file
	f.close()


	for link in soup.findAll('a'):
		if "season" in link.get('href'):
			links.append(dataset_url + link.get('href'))

	for link in links:
		episode_page(link, character, outfile)

















def main():
	print ("hi")
	

if __name__ == '__main__':
    main()



