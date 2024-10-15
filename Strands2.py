import nltk
import random
from nltk.corpus import words, wordnet
from collections import defaultdict

# Ensure you have the necessary corpora downloaded
nltk.download('words')
nltk.download('wordnet')

# Trie data structure for fast word lookup
class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            node = node.children[char]
        node.is_end_of_word = True

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word


# Load dictionary and create the Trie
word_list = set(words.words())
min_word_length = 4  # Filter shorter words
trie = Trie()

# Precompute word frequencies using WordNet
def word_frequency(word):
    synsets = wordnet.synsets(word.lower())
    if not synsets:
        return 0  # If the word doesn't have a frequency, return 0
    return max(lemma.count() for synset in synsets for lemma in synset.lemmas())

# Add words to the trie and store their frequencies
word_frequencies = {}
for word in word_list:
    if len(word) >= min_word_length:
        trie.insert(word.upper())
        word_frequencies[word.upper()] = word_frequency(word)

# This is where you can manually input the board after solving part of the puzzle by adding `_` manually
letters = [
    ['_', '_', '_', 'C', '_', '_'],
    ['_', '_', 'O', '_', '_', '_'],
    ['_', 'S', 'B', '_', '_', '_'],
    ['_', 'N', 'B', '_', '_', '_'],
    ['_', '_', 'E', 'S', '_', '_'],
    ['_', 'E', 'A', '_', '_', '_'],
    ['N', 'C', 'R', 'L', 'A', '_'],
    ['O', 'A', 'B', 'G', 'D', '_'],
]

rows = len(letters)
cols = len(letters[0])

# Precompute valid moves for each cell to optimize movement checks
directions = [
    (-1, 0), (1, 0), (0, -1), (0, 1),  # vertical and horizontal
    (-1, -1), (-1, 1), (1, -1), (1, 1)  # diagonals
]

valid_moves = {}
for i in range(rows):
    for j in range(cols):
        valid_moves[(i, j)] = [(i + di, j + dj) for di, dj in directions if 0 <= i + di < rows and 0 <= j + dj < cols]


def find_words(i, j, visited, current_word, current_path):
    if visited[i][j] or letters[i][j] == '_':  # Skip cells marked with '_'
        return []

    current_word += letters[i][j]
    current_path.append((i, j))

    # Prune the search if it's not a valid prefix
    if not trie.starts_with(current_word):
        current_path.pop()
        return []

    found_words = []
    if trie.search(current_word) and len(current_word) >= min_word_length:
        found_words.append((current_word, list(current_path)))

    visited[i][j] = True
    for ni, nj in valid_moves[(i, j)]:
        found_words += find_words(ni, nj, visited, current_word, current_path)

    visited[i][j] = False
    current_path.pop()
    return found_words


def generate_all_words():
    visited = [[False] * cols for _ in range(rows)]
    all_words = []
    for i in range(rows):
        for j in range(cols):
            all_words += find_words(i, j, visited, "", [])
    return all_words


# Greedy heuristic to find partial solutions, prioritizing common words
def greedy_cover_matrix(word_list):
    covered = set()
    selected_words = []

    # Shuffle words to introduce randomness
    random.shuffle(word_list)

    # Sort words by frequency, length, and coverage
    word_list.sort(key=lambda x: (word_frequencies.get(x[0], 0), len(x[0]), len(set(x[1]))), reverse=True)

    while len(covered) < rows * cols and word_list:
        best_word = None
        max_new_coverage = 0

        # Find the word that covers the most uncovered cells
        for word, path in word_list:
            new_covered = set(path) - covered
            if len(new_covered) > max_new_coverage:
                max_new_coverage = len(new_covered)
                best_word = (word, path)

        if not best_word:
            break  # No more words can contribute new coverage

        word, path = best_word
        covered.update(path)
        selected_words.append(word)
        word_list.remove(best_word)

    return selected_words, len(covered)


def find_multiple_solutions(word_list, num_solutions=3):
    solutions = []
    all_words = word_list[:]

    for _ in range(num_solutions):
        solution, covered_cells = greedy_cover_matrix(all_words)
        if solution:
            solutions.append((solution, covered_cells))
            print(f"Solution {len(solutions)}: {solution} (Covered {covered_cells}/{rows * cols} cells, Used {len(solution)} words)")

            # Remove the selected words from the word list for the next solution
            all_words = [w for w in all_words if w[0] not in [sw for sw in solution]]
        else:
            break

    return solutions


# Main solver function
def solve_word_game():
    all_words = generate_all_words()

    # Find multiple solutions (including partial ones)
    solutions = find_multiple_solutions(all_words, num_solutions=10)

    if not solutions:
        print("No solution found.")


# Run the solver
solve_word_game()

# Print the board after solving some parts of the puzzle
for row in letters:
    print(' '.join(row))
