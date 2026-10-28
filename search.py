# Read every line of notes.txt into a list
with open("notes.txt") as f:
    lines = f.readlines()

# Ask the user for a word
word = input("Search for a word: ")

# Check each line and print the ones that match
for line in lines:
    if word.lower() in line.lower():
        print(line.strip())