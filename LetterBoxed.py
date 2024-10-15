import requests
from collections import defaultdict, deque
import sys

# Adjust the recursion limit if necessary
sys.setrecursionlimit(10000)


# Download SOWPODS dictionary
def download_sowpods():
    url = "https://raw.githubusercontent.com/redbo/scrabble/master/dictionary.txt"
    response = requests.get(url)
    if response.status_code == 200:
        return set(word.strip().upper() for word in response.text.splitlines())
    else:
        raise Exception("Failed to download SOWPODS dictionary")


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
    word_list = download_sowpods()
    trie = Trie()
    for word in word_list:
        if 3 <= len(word) <= max_word_length and word.isalpha():
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
            if word1 != word2 and word1[-1] == word2[0]:
                graph[word1].append(word2)
    return graph, word_letter_sets


# Find up to max_solutions best solutions using BFS
def find_sequences(graph, word_letter_sets, total_letters, max_solutions=10):
    queue = deque()
    visited = {}
    min_word_count = None
    solutions = []

    graph_keys = list(graph.keys())

    for start_word in graph_keys:
        initial_used_letters = word_letter_sets[start_word]
        queue.append((start_word, [start_word], initial_used_letters))
    while queue:
        current_word, path, used_letters = queue.popleft()

        if min_word_count is not None and len(path) > min_word_count:
            continue

        if used_letters == total_letters:
            if min_word_count is None or len(path) <= min_word_count:
                min_word_count = len(path)
                solutions.append(list(path))
                if len(solutions) >= max_solutions:
                    return solutions
            continue

        for next_word in graph.get(current_word, []):
            next_used_letters = used_letters | word_letter_sets[next_word]
            state = (next_word, next_used_letters)
            if state not in visited or len(path) + 1 <= visited[state]:
                visited[state] = len(path) + 1
                queue.append((next_word, path + [next_word], next_used_letters))
    return solutions


# Main function to solve the puzzle
def solve_puzzle(letters, max_word_length=8, max_solutions=10):
    trie = load_dictionary(max_word_length)
    valid_words = generate_valid_words(letters, trie, max_word_length)
    if not valid_words:
        print("No valid words found with the given letters and dictionary.")
        return
    graph, word_letter_sets = build_word_graph(valid_words)
    total_letters = frozenset(''.join(letter.upper() for row in letters for letter in row))
    sequences = find_sequences(graph, word_letter_sets, total_letters, max_solutions)
    if sequences:
        print(f"Found {len(sequences)} optimal solution(s):\n")
        for idx, sequence in enumerate(sequences, 1):
            print(f"Solution {idx}:")
            for word in sequence:
                print(word)
            print()
    else:
        print("No solution found.")


# Example usage
letters = [
    ["I", "R", "Y"],  # Row 0
    ["O", "W", "S"],  # Row 1
    ["K", "A", "M"],  # Row 2
    ["J", "D", "E"],  # Row 3
]
max_word_length = 12  # You can adjust this value
max_solutions = 10  # Number of optimal solutions to find
solve_puzzle(letters, max_word_length, max_solutions)
