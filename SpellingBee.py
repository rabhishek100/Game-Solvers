import itertools
from nltk.corpus import words

# Letters provided for the game
letters = ['m', 'o', 't', 'b', 'a', 'r']
center_letter = 'h'
all_letters = letters + [center_letter]

# Load English words from the nltk corpus (o another word list)
word_list = set(words.words())


# Function to check if a word is valid
def is_valid_word(word):
    # Word must contain the center letter
    if center_letter not in word:
        return False
    # Word must consist only of the provided letters
    return all(char in all_letters for char in word)


# Function to score words based on criteria
def score_word(word):
    score = len(word)  # Base score: longer words are better
    if sorted(word) == sorted(all_letters):
        score += 2  # Spangrams get an extra score
    elif sorted(word) == sorted(set(word)):
        score += 1  # Anagrams score higher
    return score


# Find all valid words
valid_words = []
for word in word_list:
    word = word.lower()
    if is_valid_word(word):
        valid_words.append((word, score_word(word)))

# Sort valid words by score, then by length as a tie-breaker
valid_words.sort(key=lambda x: (-x[1], -len(x[0])))

# Output the valid words
print("Valid words found:")
for word, score in valid_words:
    print(f"{word}: {score}")

# Optional: Find the best spangram
spangrams = [word for word, score in valid_words if sorted(word) == sorted(all_letters)]
if spangrams:
    print("\nBest spangram(s):")
    for spangram in spangrams:
        print(spangram)
