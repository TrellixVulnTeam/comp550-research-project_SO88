
from process_data import friends_dataset
from process_data import BBT_dataset

def friends_gen(character):
	outfile = character + ".txt"
	friends_dataset.fetch_character(character, outfile)


def BBT_gen(character):
	outfile = character + ".txt"
	BBT_dataset.fetch_character(character, outfile)


def main():
	character = "Raj"
	BBT_gen(character)
	#friends_gen(character)


if __name__ == '__main__':
    main()



