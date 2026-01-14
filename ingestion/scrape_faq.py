import requests
import json
import hashlib
import re
from bs4 import BeautifulSoup
from pathlib import Path



FAQ_URLS = {
    "orders": "https://www.jashanmal.com/pages/orders",
    "gift_card": "https://www.jashanmal.com/pages/gift-card-wallet",
    "payment": "https://www.jashanmal.com/pages/payment",
    "shipping": "https://www.jashanmal.com/pages/shipping-delivery",
    "returns": "https://www.jashanmal.com/pages/returns-exchanges",
    "about": "https://www.jashanmal.com/pages/about",
}

FAQ_PAGES = {"orders", "gift_card", "payment", "shipping", "returns"}
ABOUT_PAGES = {"about"}

OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "faqs.json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (CustomerSupportBot/1.0)"
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def hash_content(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def remove_noise(soup: BeautifulSoup):
    for tag in soup([
        "header", "footer", "nav", "script",
        "style", "noscript", "form"
    ]):
        tag.decompose()

    for cls in [
        "call-us", "call-wrap", "support",
        "contact", "contact-us"
    ]:
        for div in soup.find_all(class_=cls):
            div.decompose()

def is_cta_text(text: str) -> bool:
    cta_phrases = [
        "whatsapp us",
        "email us",
        "call us",
        "contact us",
        "need assistance",
        "customer support team",
    ]
    t = text.lower()
    return any(p in t for p in cta_phrases)

              

def extract_faq_sections(html: str, page_name: str, url: str):
    soup = BeautifulSoup(html, "html.parser")
    remove_noise(soup)

    main = soup.find("main") or soup

    faqs = []
    current_question = None

    for el in main.find_all(["h2", "h3", "p", "li"]):
        text = clean_text(el.get_text())

        if text.lower().startswith("need assistance"):
            break

        if el.name in ["h2", "h3"]:
            current_question = text

        else:
            if (
                current_question
                and len(text) > 20
                and not is_cta_text(text)
            ):
                faqs.append({
                    "category": page_name,
                    "question": current_question,
                    "answer": text,
                    "source": url
                })

    return faqs

def extract_about_content(html: str, url: str):
    soup = BeautifulSoup(html, "html.parser")
    remove_noise(soup)

    main = soup.find("main") or soup.find("article") or soup

    sections = []
    for p in main.find_all("p"):
        text = clean_text(p.get_text())
        if len(text) > 50:
            sections.append({
                "category": "about",
                "title": "About Jashanmal",
                "text": text,
                "source": url
            })

    return sections


def main():
    all_docs = []

    for page_name, url in FAQ_URLS.items():
        print(f"Scraping {page_name} → {url}")

        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            res.raise_for_status()
            html = res.text

            if page_name in FAQ_PAGES:
                docs = extract_faq_sections(html, page_name, url)
            elif page_name in ABOUT_PAGES:
                docs = extract_about_content(html, url)
            else:
                docs = []

            for d in docs:
                d["content_hash"] = hash_content(
                    json.dumps(d, ensure_ascii=False)
                )
                all_docs.append(d)

            print(f"  Extracted {len(docs)} clean entries")

        except Exception as e:
            print(f"  Failed: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2, ensure_ascii=False)

    print("\nScraping complete")
    print(f"Total documents: {len(all_docs)}")
    print(f"Saved to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
