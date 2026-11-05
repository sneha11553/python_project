"""Stock Portfolio Performance Tracker

Run:  python3 portfolio.py

Enter ticker, buy price and share quantity for each holding. The program
validates tickers against constituents.csv (S&P 500 dataset, same folder),
fetches current prices, computes value and gain/loss, prints a formatted
report and appends it to portfolio_summary.csv.

Optional: put your holdings in holdings.csv (columns: Symbol,BuyPrice,Shares)
and the program offers to load them so you don't have to type anything.

Price lookup order:
  1. Live via yfinance (if installed: pip install yfinance)
  2. prices.csv in the same folder (columns: Symbol,Price)
  3. Manual entry at the prompt
"""

import csv
import os
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")  # hide harmless urllib3/LibreSSL notice on macOS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTITUENTS_FILE = os.path.join(BASE_DIR, "constituents.csv")
PRICES_FILE = os.path.join(BASE_DIR, "prices.csv")
HOLDINGS_FILE = os.path.join(BASE_DIR, "holdings.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "portfolio_summary.csv")

SUMMARY_HEADER = [
    "Timestamp", "Symbol", "Company", "Shares", "Buy Price",
    "Current Price", "Invested", "Market Value", "Gain/Loss", "Gain/Loss %",
]


# ---------- Data loading ----------

def load_constituents():
    """Return {symbol: (company, sector)} from constituents.csv."""
    data = {}
    if not os.path.exists(CONSTITUENTS_FILE):
        print(f"Note: {os.path.basename(CONSTITUENTS_FILE)} not found - ticker validation skipped.")
        return data
    with open(CONSTITUENTS_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            data[row["Symbol"].strip().upper()] = (row["Security"], row.get("GICS Sector", ""))
    return data


def load_local_prices():
    """Return {symbol: price} from optional prices.csv."""
    prices = {}
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    prices[row["Symbol"].strip().upper()] = float(row["Price"])
                except (KeyError, ValueError):
                    continue
    return prices


def load_holdings(constituents):
    """Load {symbol: {'shares', 'buy_price'}} from holdings.csv (merging repeats)."""
    portfolio = {}
    with open(HOLDINGS_FILE, newline="", encoding="utf-8") as f:
        for line_no, row in enumerate(csv.DictReader(f), start=2):
            try:
                symbol = row["Symbol"].strip().upper()
                buy_price = float(row["BuyPrice"])
                shares = float(row["Shares"])
                if buy_price <= 0 or shares <= 0:
                    raise ValueError
            except (KeyError, ValueError, AttributeError):
                print(f"  Skipping invalid row {line_no} in holdings.csv")
                continue
            if constituents and symbol not in constituents:
                print(f"  Skipping {symbol} (row {line_no}): not in the S&P 500 dataset")
                continue
            add_position(portfolio, symbol, buy_price, shares)
    return portfolio


def add_position(portfolio, symbol, buy_price, shares):
    """Add a holding; repeats merge using the weighted-average buy price."""
    if symbol in portfolio:
        old = portfolio[symbol]
        total_shares = old["shares"] + shares
        avg = (old["shares"] * old["buy_price"] + shares * buy_price) / total_shares
        portfolio[symbol] = {"shares": total_shares, "buy_price": avg}
    else:
        portfolio[symbol] = {"shares": shares, "buy_price": buy_price}


# ---------- Price lookup ----------

def fetch_live_price(symbol):
    """Try yfinance; return float or None."""
    try:
        import yfinance as yf
        hist = yf.Ticker(symbol.replace(".", "-")).history(period="5d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None


def get_current_price(symbol, local_prices):
    price = fetch_live_price(symbol)
    if price is not None:
        return price, "live"
    if symbol in local_prices:
        return local_prices[symbol], "prices.csv"
    return prompt_float(f"  Could not fetch a price for {symbol}. Enter current price: "), "manual"


# ---------- Input helpers ----------

def prompt_float(message, allow_zero=False):
    while True:
        raw = input(message).strip().replace(",", "")
        try:
            value = float(raw)
            if value > 0 or (allow_zero and value == 0):
                return value
        except ValueError:
            pass
        print("  Please enter a positive number.")


def prompt_symbol(constituents):
    while True:
        symbol = input("Ticker symbol (or press Enter to finish): ").strip().upper()
        if not symbol:
            return None
        if constituents and symbol not in constituents:
            print(f"  '{symbol}' is not in the S&P 500 dataset. Try again.")
            continue
        return symbol


def collect_positions(constituents):
    """Build the portfolio dictionary: {symbol: {'shares', 'buy_price'}}.

    Buying the same ticker again merges into one position using the
    weighted-average buy price.
    """
    portfolio = {}
    print("\n=== Add your holdings ===")
    while True:
        symbol = prompt_symbol(constituents)
        if symbol is None:
            if portfolio:
                return portfolio
            print("  Add at least one holding first.")
            continue
        buy_price = prompt_float("  Buy price per share: ")
        shares = prompt_float("  Number of shares: ")
        if symbol in portfolio:
            print(f"  Merged with existing {symbol} position.")
        add_position(portfolio, symbol, buy_price, shares)


# ---------- Calculations ----------

def evaluate(portfolio, constituents):
    local_prices = load_local_prices()
    results = []
    print("\nFetching current prices...")
    for symbol, pos in portfolio.items():
        current, source = get_current_price(symbol, local_prices)
        invested = pos["shares"] * pos["buy_price"]
        value = pos["shares"] * current
        gain = value - invested
        pct = (gain / invested) * 100 if invested else 0.0
        results.append({
            "symbol": symbol,
            "company": constituents.get(symbol, (symbol, ""))[0],
            "shares": pos["shares"],
            "buy_price": pos["buy_price"],
            "current": current,
            "source": source,
            "invested": invested,
            "value": value,
            "gain": gain,
            "pct": pct,
        })
    return results


# ---------- Output ----------

def print_report(results):
    line = "=" * 100
    print("\n" + line)
    print(f"{'PORTFOLIO PERFORMANCE REPORT':^100}")
    print(f"{datetime.now().strftime('%d %b %Y, %H:%M'):^100}")
    print(line)
    print(f"{'Symbol':<8}{'Company':<24}{'Shares':>9}{'Buy':>10}{'Current':>10}"
          f"{'Invested':>13}{'Value':>13}{'Gain/Loss':>12}{'%':>10}")
    print("-" * 100)
    for r in results:
        print(f"{r['symbol']:<8}{r['company'][:22]:<24}{r['shares']:>9,.2f}{r['buy_price']:>10,.2f}"
              f"{r['current']:>10,.2f}{r['invested']:>13,.2f}{r['value']:>13,.2f}"
              f"{r['gain']:>+12,.2f}{r['pct']:>+9.2f}%")
    print("-" * 100)

    total_invested = sum(r["invested"] for r in results)
    total_value = sum(r["value"] for r in results)
    total_gain = total_value - total_invested
    total_pct = (total_gain / total_invested) * 100 if total_invested else 0.0
    print(f"{'TOTAL':<8}{'':<24}{'':>9}{'':>10}{'':>10}"
          f"{total_invested:>13,.2f}{total_value:>13,.2f}{total_gain:>+12,.2f}{total_pct:>+9.2f}%")
    print(line)

    best = max(results, key=lambda r: r["pct"])
    worst = min(results, key=lambda r: r["pct"])
    print(f"Best performer:  {best['symbol']} ({best['pct']:+.2f}%)")
    print(f"Worst performer: {worst['symbol']} ({worst['pct']:+.2f}%)")
    print(f"Overall result:  {'PROFIT' if total_gain >= 0 else 'LOSS'} of {abs(total_gain):,.2f} "
          f"({total_pct:+.2f}%)")
    sources = sorted({r["source"] for r in results})
    print(f"Price source:    {', '.join(sources)}\n")


def save_summary(results):
    """Append this run's results to portfolio_summary.csv (header added once)."""
    is_new = not os.path.exists(SUMMARY_FILE) or os.path.getsize(SUMMARY_FILE) == 0
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SUMMARY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(SUMMARY_HEADER)
        for r in results:
            writer.writerow([
                stamp, r["symbol"], r["company"], f"{r['shares']:.2f}",
                f"{r['buy_price']:.2f}", f"{r['current']:.2f}", f"{r['invested']:.2f}",
                f"{r['value']:.2f}", f"{r['gain']:.2f}", f"{r['pct']:.2f}",
            ])
        total_invested = sum(r["invested"] for r in results)
        total_value = sum(r["value"] for r in results)
        total_gain = total_value - total_invested
        total_pct = (total_gain / total_invested) * 100 if total_invested else 0.0
        writer.writerow([stamp, "TOTAL", "", "", "", "", f"{total_invested:.2f}",
                         f"{total_value:.2f}", f"{total_gain:.2f}", f"{total_pct:.2f}"])
    print(f"Summary saved to {SUMMARY_FILE}")


def main():
    print("=== Stock Portfolio Performance Tracker ===")
    constituents = load_constituents()
    while True:
        portfolio = {}
        if os.path.exists(HOLDINGS_FILE):
            if input("holdings.csv found. Load it? (y/n): ").strip().lower() == "y":
                portfolio = load_holdings(constituents)
                print(f"  Loaded {len(portfolio)} holding(s).")
        if not portfolio:
            portfolio = collect_positions(constituents)
        results = evaluate(portfolio, constituents)
        print_report(results)
        save_summary(results)
        if input("\nTrack another portfolio? (y/n): ").strip().lower() != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
