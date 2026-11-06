# Python Projects

A collection of four Python projects covering string handling, file I/O, data processing, regular expressions, and error handling. Built by **Sneha Garde**.

## Projects

| # | Project | Highlights |
|---|---------|------------|
| 1 | [Hangman Game](Task1_Hangman) | ASCII gallows art, 6 attempts, 10,000-word dictionary |
| 2 | [Stock Portfolio Tracker](Task2_Portfolio_Tracker) | Live prices, gain/loss per holding, CSV reports |
| 3 | [File Organizer](Task3_File_Organizer) | Sorts folders by file type, collision-safe, logged |
| 4 | [FAQ Chatbot](Task4_Chatbot) | Regex and keyword matching, multi-question replies |

## Folder Structure

```
├── Task1_Hangman/              hangman.py, words.txt
├── Task2_Portfolio_Tracker/    portfolio.py, constituents.csv, holdings.csv, portfolio_summary.csv
├── Task3_File_Organizer/       organizer.py
├── Task4_Chatbot/              chatbot.py, sample_faq.json
└── requirements.txt
```

## 1. Hangman Game

A terminal Hangman game. The ASCII gallows updates with each wrong guess, guessed letters are tracked, and repeating a letter does not cost an attempt. Words come from `words.txt` (Google 10,000 English list), with a built-in list as a fallback.

```
cd Task1_Hangman
python3 hangman.py
```

## 2. Stock Portfolio Tracker

Enter ticker symbols, buy prices, and share counts (or load them from `holdings.csv`). Tickers are validated against the S&P 500 list in `constituents.csv`. The program fetches current prices, calculates total value and gain/loss per holding and overall, prints a formatted report, and appends each run to `portfolio_summary.csv`.

Prices come from live data via `yfinance`, falling back to `prices.csv` or manual entry.

```
cd Task2_Portfolio_Tracker
python3 -m pip install yfinance
python3 portfolio.py
```

`holdings.csv` format:

```
Symbol,BuyPrice,Shares
AAPL,150,10
MSFT,300,5
```

## 3. File Organizer

Sorts files in a folder into Documents, Images, Videos, Audio, Archives, Code, and Others. Name collisions are renamed (`photo (1).png`) and never overwritten. Permission errors are handled per file, and every action is logged to `organizer.log`. Hidden files and subfolders are skipped.

```
cd Task3_File_Organizer
python3 organizer.py /path/to/folder --dry-run   # preview only
python3 organizer.py /path/to/folder             # organize
```

If no folder is given, it uses `~/Downloads`.

## 4. FAQ Chatbot

A rule-based terminal assistant that loads questions and answers from `sample_faq.json`. It handles greetings, answers several questions in one message, understands synonyms (for example, "what time do you open?" matches the business-hours FAQ), and falls back gracefully on unknown questions. Type `bye`, `exit`, or `quit` to leave.

```
cd Task4_Chatbot
python3 chatbot.py
```

To add your own FAQs, edit `sample_faq.json`:

```json
{
  "greetings": ["hello", "hi"],
  "faqs": [{"question": "...", "answer": "..."}]
}
```

## Requirements

Python 3.9 or newer. Only the portfolio tracker needs an extra package (`yfinance`, for live prices). Everything else uses the standard library.

## Skills Demonstrated

String manipulation, control flow, file and directory operations, CSV and JSON handling, regular expressions, input validation, error handling, and logging.
