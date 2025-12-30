import requests
from bs4 import BeautifulSoup
import os
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://iost.tu.edu.np/notices"

KEYWORDS = [
    "B.Sc.CSIT 2078",
    "B.Sc.CSIT VIII Semester",
    "B.Sc.CSIT VIII Semester Exam"
]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

SENT_FILE = "sent.json"


def send(msg):
    requests.post(
        f"{TG_API}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        verify=False,
        timeout=10
    )


def load_sent_ids():
    if not os.path.exists(SENT_FILE):
        return set()
    with open(SENT_FILE, "r") as f:
        return set(json.load(f))


def save_sent_ids(sent_ids):
    with open(SENT_FILE, "w") as f:
        json.dump(sorted(sent_ids), f, indent=2)


def main():
    sent_ids = load_sent_ids()
    updated = False

    r = requests.get(URL, timeout=15, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        href = a.get("href")

        if not text or not href:
            continue

        if not any(k.lower() in text.lower() for k in KEYWORDS):
            continue

        if href.startswith("http"):
            notice_id = href
            full_link = href
        else:
            notice_id = href
            full_link = "https://iost.tu.edu.np" + href

        if notice_id in sent_ids:
            continue

        # send alert
        send(f"📢 New IOST Notice\n\n{text}\n{full_link}")

        sent_ids.add(notice_id)
        updated = True

    if updated:
        save_sent_ids(sent_ids)


if __name__ == "__main__":
    main()
