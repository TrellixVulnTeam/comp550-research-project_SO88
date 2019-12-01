
from process_data import friends_dataset

def main():
	character = "Rachel"
	outfile = character + ".txt"
	friends_dataset.fetch_character(character, outfile)

if __name__ == '__main__':
    main()



