import nltk
from nltk.corpus import words

# Download the words corpus if you haven't already
nltk.download('words')

# Get a list of all 5-letter words from the NLTK corpus
word_list = [word.lower() for word in words.words() if len(word) == 5]

# Inputs
current_pattern = '_o__y'
wrong_letters = set(['e', 'r', 't', 'u', 'i', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'k', 'l', 'c', 'n'])
current_letters_wrong_position = []

# Function to check if the word matches the current pattern
def matches_pattern(word, pattern):
    for i, char in enumerate(pattern):
        if char != '_' and word[i] != char:
            return False
    return True

# Function to check if any of the wrong letters are present in the word
def contains_wrong_letters(word, wrong_letters):
    return any(letter in word for letter in wrong_letters)

# Function to check if any of the current letters in the wrong position are at the wrong index
def letters_in_wrong_position(word, wrong_positions):
    for letter, index in wrong_positions:
        if word[index] == letter:
            return True
    return False

# Filter words based on the pattern, wrong letters, and wrong positions
def guess_words(word_list, pattern, wrong_letters, wrong_positions):
    possible_words = []
    for word in word_list:
        if matches_pattern(word, pattern) and not contains_wrong_letters(word, wrong_letters) and not letters_in_wrong_position(word, wrong_positions):
            possible_words.append(word)
    return possible_words

# Guess the possible words based on the current state
possible_words = guess_words(word_list, current_pattern, wrong_letters, current_letters_wrong_position)

# Print the possible words
print("Possible words:", possible_words)
