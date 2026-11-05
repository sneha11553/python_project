"""Hangman Word Guessing Game (Console)

Run:  python3 hangman.py
Optional: place a words.txt (one word per line) next to this file to use
the downloaded English word list. Otherwise a built-in list is used.
"""

import os
import random

MAX_MISTAKES = 6

STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========""",
]

DEFAULT_WORDS = [
    "python", "variable", "function", "algorithm", "database", "compiler",
    "keyboard", "software", "network", "program", "developer", "interface",
    "hangman", "iteration", "boolean", "integer", "library", "terminal",
    "debugging", "recursion", "elephant", "mountain", "chocolate", "adventure",
]


def load_words():
    """Load words from words.txt if present, else use the built-in list."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip().isalpha() and len(w.strip()) >= 4]
        if words:
            return words
    return DEFAULT_WORDS


def choose_word(words):
    return random.choice(words)


def masked_word(word, guessed):
    return " ".join(ch.upper() if ch in guessed else "_" for ch in word)


def display(word, guessed, mistakes):
    print(STAGES[mistakes])
    print(f"\n  Word:    {masked_word(word, guessed)}")
    wrong = sorted(g for g in guessed if g not in word)
    print(f"  Guessed: {' '.join(sorted(l.upper() for l in guessed)) or '-'}")
    print(f"  Wrong:   {' '.join(l.upper() for l in wrong) or '-'}")
    print(f"  Attempts left: {MAX_MISTAKES - mistakes}\n")


def get_guess(guessed):
    """Prompt until a valid, new single letter is entered."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter (A-Z).")
        elif guess in guessed:
            print(f"You already guessed '{guess.upper()}'. No penalty - try another.")
        else:
            return guess


def play_round(words):
    word = choose_word(words)
    guessed = set()
    mistakes = 0

    print("\n=== HANGMAN ===")
    while mistakes < MAX_MISTAKES and not set(word) <= guessed:
        display(word, guessed, mistakes)
        guess = get_guess(guessed)
        guessed.add(guess)
        if guess in word:
            print(f"Good guess! '{guess.upper()}' is in the word.")
        else:
            mistakes += 1
            print(f"Sorry, '{guess.upper()}' is not in the word.")

    display(word, guessed, mistakes)
    if set(word) <= guessed:
        print("*" * 34)
        print("   VICTORY! You guessed the word!")
        print("*" * 34)
    else:
        print("#" * 34)
        print("   GAME OVER! You were hanged.")
        print(f"   The word was: {word.upper()}")
        print("#" * 34)


def main():
    words = load_words()
    while True:
        play_round(words)
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
