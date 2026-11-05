# Datheon Python Programming Internship

Submission by **Sneha Garde**. All four tasks are complete, written in Python 3 using mostly the standard library.

## Folder Structure

```
Datheon_Python_Programming_Internship/
├── Task1_Hangman/              hangman.py, words.txt
├── Task2_Portfolio_Tracker/    portfolio.py, constituents.csv, holdings.csv, portfolio_summary.csv
├── Task3_File_Organizer/       organizer.py
├── Task4_Chatbot/              chatbot.py, sample_faq.json
└── requirements.txt
```

## Tasks

### 1. Hangman Word Guessing Game
Console game with 6 attempts and ASCII gallows art that updates on each wrong guess. It tracks guessed letters, does not penalize repeated guesses, and shows victory/defeat screens. Words come from `words.txt` (Google 10,000 English list), or a built-in list if the file is missing.
```
cd Task1_Hangman && python3 hangman.py
```

### 2. Stock Portfolio Performance Tracker
Enter ticker, buy price and shares (or load them from `holdings.csv`). Tickers are validated against the S&P 500 list in `constituents.csv`. Calculates total value and gain/loss per holding and overall, prints a formatted report, and appends the results to `portfolio_summary.csv`. Current prices are fetched live with yfinance, falling back to manual entry.
```
cd Task2_Portfolio_Tracker && python3 -m pip install yfinance && python3 portfolio.py
```

### 3. Automated File Organizer & Cleanup Utility
Sorts files in a folder into Documents, Images, Videos, Audio, Archives, Code and Others using `os`, `shutil` and `pathlib`. Name collisions are renamed, never overwritten. Permission errors are handled, actions are logged to `organizer.log`, and a summary is printed. Use `--dry-run` to preview.
```
cd Task3_File_Organizer && python3 organizer.py /path/to/folder --dry-run
```

### 4. Rule-Based Terminal Chatbot
Keyword and regex based assistant that loads FAQs from `sample_faq.json`. It handles greetings, multiple questions in one message, fallbacks for unknown queries, and the exit commands `bye`, `exit` and `quit`.
```
cd Task4_Chatbot && python3 chatbot.py
```

## Requirements
Python 3.9+. Only Task 2 needs an extra package (`yfinance`, optional for live prices).
