import nltk
from nltk.corpus import words
from collections import defaultdict, deque
import sys

# Adjust the recursion limit if necessary
sys.setrecursionlimit(10000)


# Download NLTK data if not already present
def download_nltk_data():
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        print("Downloading NLTK word corpus...")
        nltk.download('words')


# Trie Node class for the trie data structure
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False


# Trie class for efficient prefix and word lookup
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for letter in word:
            if letter not in current.children:
                current.children[letter] = TrieNode()
            current = current.children[letter]
        current.is_word = True

    def search(self, word):
        current = self.root
        for letter in word:
            if letter not in current.children:
                return False
            current = current.children[letter]
        return current.is_word

    def starts_with(self, prefix):
        current = self.root
        for letter in prefix:
            if letter not in current.children:
                return False
            current = current.children[letter]
        return True


# Load the dictionary into a trie for efficient lookup
def load_dictionary(max_word_length):
    download_nltk_data()
    word_list = words.words()
    trie = Trie()
    for word in word_list:
        word = word.strip().upper()
        if len(word) >= 3 and len(word) <= max_word_length and word.isalpha():
            trie.insert(word)
    return trie


# Generate all valid words under the constraints
def generate_valid_words(letters, trie, max_word_length):
    valid_words = set()
    letter_positions = {}
    for idx, row in enumerate(letters):
        for letter in row:
            letter_positions.setdefault(letter.upper(), set()).add(idx)
    available_letters = list(letter_positions.keys())
    letter_rows = {letter: rows for letter, rows in letter_positions.items()}

    # Build all sequences of letters under constraints
    def generate_sequences(current_sequence, last_rows):
        word_so_far = ''.join(current_sequence)
        if not trie.starts_with(word_so_far):
            return
        if len(current_sequence) >= 3 and trie.search(word_so_far):
            valid_words.add((word_so_far, frozenset(word_so_far)))
        if len(current_sequence) >= max_word_length:
            return
        for letter in available_letters:
            rows = letter_rows[letter]
            if last_rows is None or not (rows & last_rows):
                generate_sequences(current_sequence + [letter], rows)

    # Start sequences from each letter
    for letter in available_letters:
        generate_sequences([letter], letter_rows[letter])

    return list(valid_words)


# Build the word graph
def build_word_graph(valid_words):
    graph = defaultdict(list)
    word_letter_sets = {}
    for word, letters in valid_words:
        word_letter_sets[word] = letters
    for word1, letters1 in valid_words:
        for word2, letters2 in valid_words:
            # Ensure we're chaining words together
            if word1 != word2 and word1[-1] == word2[0]:
                graph[word1].append(word2)
    return graph, word_letter_sets


# Find sequences that solve the full puzzle using BFS
def find_full_solutions(graph, word_letter_sets, total_letters, max_solutions=20):
    queue = deque()
    visited = {}
    min_word_count = None
    solutions = []

    # Convert graph.keys() to a list to prevent modification issues
    graph_keys = list(graph.keys())

    # Start BFS from each word
    for start_word in graph_keys:
        initial_used_letters = word_letter_sets[start_word]
        queue.append((start_word, [start_word], initial_used_letters))

    while queue and len(solutions) < max_solutions:
        current_word, path, used_letters = queue.popleft()

        # If used_letters is equal to total_letters, we have a full solution
        if used_letters == total_letters:
            if min_word_count is None or len(path) <= min_word_count:
                min_word_count = len(path)
                solutions.append(list(path))
            continue

        # Safely get the list of next words
        for next_word in graph.get(current_word, []):
            next_used_letters = used_letters | word_letter_sets[next_word]
            state = (next_word, next_used_letters)
            if state not in visited or len(path) + 1 <= visited[state]:
                visited[state] = len(path) + 1
                queue.append((next_word, path + [next_word], next_used_letters))

    # Sort solutions by the number of words in ascending order
    solutions.sort(key=len)

    return solutions


# Main function to solve the puzzle
def solve_puzzle(letters, max_word_length=8, max_solutions=20):
    trie = load_dictionary(max_word_length)
    valid_words = generate_valid_words(letters, trie, max_word_length)
    if not valid_words:
        print("No valid words found with the given letters and dictionary.")
        return
    graph, word_letter_sets = build_word_graph(valid_words)
    total_letters = frozenset(''.join(letter.upper() for row in letters for letter in row))
    full_solutions = find_full_solutions(graph, word_letter_sets, total_letters, max_solutions)

    if full_solutions:
        print(f"Found {len(full_solutions)} full solution(s) using all letters:\n")
        for idx, sequence in enumerate(full_solutions, 1):
            print(f"Solution {idx} ({len(sequence)} words): {' -> '.join(sequence)}")
        print()
    else:
        print("No full solution found.")


# Example usage
letters = [
    ["N", "K", "J"],  # Row 0
    ["O", "T", "D"],  # Row 1
    ["I", "L", "G"],  # Row 2
    ["U", "R", "W"],  # Row 3
]
max_word_length = 12  # You can adjust this value
solve_puzzle(letters, max_word_length, max_solutions=20)
