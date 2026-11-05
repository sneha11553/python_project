"""Rule-Based Interactive Terminal Assistant / Chatbot

Run:  python3 chatbot.py [path/to/faq.json]
Defaults to sample_faq.json in the same folder.

JSON format:
{
  "greetings": ["hello", "hi", ...],
  "faqs": [{"question": "...", "answer": "..."}, ...]
}

How it works (conversation states: GREETING -> ASSISTING -> EXIT):
  1. Input is normalized (lowercase, punctuation stripped, whitespace collapsed).
  2. Regex rules detect exit commands, greetings, thanks and help requests.
  3. Otherwise each FAQ is scored by keyword overlap (with synonym expansion).
     Every FAQ above the confidence threshold is answered, so a message
     containing several questions gets several answers (multi-intent).
  4. Low confidence -> graceful fallback; repeated misses list the topics.
"""

import json
import os
import re
import sys

DEFAULT_FAQ_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_faq.json")

BUILTIN_DATA = {
    "greetings": ["hello", "hi", "hey", "good morning", "good afternoon"],
    "faqs": [
        {"question": "What are your hours of operation?",
         "answer": "We operate Monday through Friday from 9:00 AM to 6:00 PM IST."},
    ],
}

CONFIDENCE_THRESHOLD = 0.5   # share of an FAQ's keywords that must appear in the input
MAX_ANSWERS = 3

EXIT_PATTERN = re.compile(r"^(bye|goodbye|exit|quit|see you|good night|q)\b[\s!.]*$|\b(bye|goodbye)\b")
THANKS_PATTERN = re.compile(r"\b(thanks|thank you|thx|cheers)\b")
HELP_PATTERN = re.compile(r"\b(help|what can you do|topics|menu|options)\b")

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "do", "does", "did", "i", "my", "me", "you", "your",
    "we", "our", "to", "of", "in", "on", "at", "for", "and", "or", "can", "will", "would",
    "what", "when", "how", "where", "which", "who", "it", "be", "this", "that", "please",
    "tell", "about", "there", "get", "have", "has",
}

# Maps common user wording onto the keywords used in FAQ questions.
SYNONYMS = {
    "open": "hours", "opening": "hours", "close": "hours", "closing": "hours",
    "timing": "hours", "timings": "hours", "schedule": "hours", "time": "hours",
    "working": "hours", "available": "hours", "operate": "operation", "operating": "operation",
    "upload": "submit", "send": "submit", "turn": "submit", "deliver": "submit",
    "submission": "submit", "submitting": "submit", "project": "project",
    "certificates": "certificate", "certification": "certificate", "cert": "certificate",
    "receive": "receive", "issued": "receive", "issue": "receive", "get": "receive",
    "delivered": "receive", "days": "receive",
}


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def stem(word):
    word = word.replace("'", "")
    for suffix in ("ing", "ies", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def keywords(text):
    """Normalized keyword set: stopwords removed, synonyms mapped, stemmed."""
    result = set()
    for word in normalize(text).split():
        word = SYNONYMS.get(word, word)
        if word in STOPWORDS:
            continue
        result.add(stem(word))
    return result


def load_data(path):
    """Load the FAQ JSON; fall back to a built-in dataset on any problem."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        faqs = [item for item in data.get("faqs", []) if "question" in item and "answer" in item]
        if not faqs:
            raise ValueError("no valid FAQ entries")
        return {"greetings": data.get("greetings", BUILTIN_DATA["greetings"]), "faqs": faqs}
    except FileNotFoundError:
        print(f"[Note] '{path}' not found - using built-in FAQs.")
    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        print(f"[Note] Could not read FAQ file ({exc}) - using built-in FAQs.")
    return BUILTIN_DATA


class Chatbot:
    GREETING, ASSISTING, EXIT = "GREETING", "ASSISTING", "EXIT"

    def __init__(self, data):
        self.faqs = [{**f, "keys": keywords(f["question"])} for f in data["faqs"]]
        self.greetings = [normalize(g) for g in data["greetings"]]
        self.state = self.GREETING
        self.misses = 0

    def is_greeting(self, text):
        return any(re.search(rf"\b{re.escape(g)}\b", text) for g in self.greetings)

    def match_faqs(self, text):
        """Return [(confidence, faq)] for every FAQ above the threshold, best first."""
        user_keys = keywords(text)
        scored = []
        for faq in self.faqs:
            if not faq["keys"]:
                continue
            confidence = len(user_keys & faq["keys"]) / len(faq["keys"])
            if confidence >= CONFIDENCE_THRESHOLD:
                scored.append((confidence, faq))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:MAX_ANSWERS]

    def topics(self):
        return "\n".join(f"  - {f['question']}" for f in self.faqs)

    def respond(self, raw):
        text = normalize(raw)

        if not text:
            return "Please type a question, or 'help' to see what I can answer."

        if EXIT_PATTERN.search(text):
            self.state = self.EXIT
            return "Goodbye! Have a great day."

        if THANKS_PATTERN.search(text) and not self.match_faqs(text):
            return "You're welcome! Is there anything else I can help with?"

        if HELP_PATTERN.search(text) and not self.match_faqs(text):
            return "I can help with these questions:\n" + self.topics()

        matches = self.match_faqs(text)
        greeted = self.is_greeting(text)

        if matches:
            first_turn = self.state == self.GREETING
            self.state = self.ASSISTING
            self.misses = 0
            answers = [m[1]["answer"] for m in matches]
            reply = "\n".join(answers) if len(answers) == 1 else \
                "\n".join(f"{i}. {a}" for i, a in enumerate(answers, 1))
            return ("Hello! " if greeted and first_turn else "") + reply

        if greeted:
            self.state = self.ASSISTING
            return "Hello! How can I help you today? (type 'help' to see topics)"

        self.misses += 1
        if self.misses >= 2:
            return ("I'm still not sure what you mean. Here is what I can answer:\n"
                    + self.topics())
        return "Sorry, I didn't understand that. Could you rephrase your question?"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FAQ_PATH
    bot = Chatbot(load_data(path))

    print("=" * 52)
    print("  Support Assistant  (type 'bye', 'exit' or 'quit' to leave)")
    print("=" * 52)
    print("Bot: Hi there! Ask me a question, or type 'help' to see topics.")

    while bot.state != Chatbot.EXIT:
        try:
            user_input = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye! Have a great day.")
            break
        print(f"Bot: {bot.respond(user_input)}")


if __name__ == "__main__":
    main()
