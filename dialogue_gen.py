
from process_data import friends_dataset
from process_data import BBT_dataset
from process_data import trump_dataset

def friends_gen(character):
	outfile = character + ".txt"
	friends_dataset.fetch_character(character, outfile)


def BBT_gen(character):
	outfile = character + ".txt"
	BBT_dataset.fetch_character(character, outfile)
    

def trump_gen():
    outfile = "Trump.txt"
    trump_dataset.fetch(outfile)


def main():
	character = "Raj"
	BBT_gen(character)
	#friends_gen(character)
    #trump_gen()


if __name__ == '__main__':
    main()



