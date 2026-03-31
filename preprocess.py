import csv
import re
import os

POS_NEG_FILE = "data/films_pos_neg.csv"
NEUTRAL_FILE = "data/neutral.csv"
OUTPUT_FILE = "data/reviews_final.csv"


def clean_text(text):
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^a-záčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_and_clean(filepath, expected_sentiment=None):
    rows = list(csv.DictReader(open(filepath, encoding="utf-8")))
    print(f"Nacteno z {filepath}: {len(rows)}")

    cleaned = []
    skipped = 0

    for row in rows:
        text = clean_text(row["text"])
        if len(text.split()) < 10:
            skipped += 1
            continue

        sentiment = expected_sentiment if expected_sentiment else row["sentiment"]

        cleaned.append({
            "text": text,
            "sentiment": sentiment,
            "film_id": row.get("film_id", ""),
        })

    print(f"  Po cisteni: {len(cleaned)} (preskoceno: {skipped})")
    return cleaned


def main():
    os.makedirs("data", exist_ok=True)

    pos_neg = load_and_clean(POS_NEG_FILE)
    neutral = load_and_clean(NEUTRAL_FILE, expected_sentiment="neutral")

    all_rows = pos_neg + neutral

    pos = sum(1 for r in all_rows if r["sentiment"] == "positive")
    neg = sum(1 for r in all_rows if r["sentiment"] == "negative")
    neu = sum(1 for r in all_rows if r["sentiment"] == "neutral")
    print(f"\nCelkem: {len(all_rows)}")
    print(f"Positive: {pos}, Negative: {neg}, Neutral: {neu}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "sentiment", "film_id"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nUlozeno do {OUTPUT_FILE}")


if __name__ == "__main__":
    main()