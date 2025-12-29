import requests
from bs4 import BeautifulSoup
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://iost.tu.edu.np/notices"

KEYWORDS = [
    "B.Sc.CSIT 2078",
    "B.Sc.CSIT VIII Semester",
    "B.Sc.CSIT VIII Semester Exam"
]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")              # real alerts
STORAGE_CHAT_ID = os.getenv("STORAGE_CHAT_ID")  # private channel

TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send(chat_id, msg):
    requests.post(
        f"{TG_API}/sendMessage",
        data={"chat_id": chat_id, "text": msg},
        verify=False
    )

def get_sent_ids():
    """Read SENT markers from private channel"""
    sent_ids = set()
    r = requests.get(f"{TG_API}/getUpdates", verify=False).json()

    if not r.get("ok"):
        return sent_ids

    for upd in r["result"]:
        msg = upd.get("message", {})
        if str(msg.get("chat", {}).get("id")) != str(STORAGE_CHAT_ID):
            continue

        text = msg.get("text", "")
        if text.startswith("SENT:"):
            sent_ids.add(text.replace("SENT:", "").strip())

    return sent_ids

try:
    sent_ids = get_sent_ids()
    seen_this_run = set()  # prevents duplicates in same run

    r = requests.get(URL, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a")

    for a in links:
        text = a.get_text(strip=True)
        href = a.get("href")

        if not href or not text:
            continue

        if not any(k.lower() in text.lower() for k in KEYWORDS):
            continue

        # normalize notice ID
        if href.startswith("http"):
            notice_id = href.split("iost.tu.edu.np")[-1]
            full_link = href
        else:
            notice_id = href
            full_link = "https://iost.tu.edu.np" + href

        # block duplicates
        if notice_id in sent_ids or notice_id in seen_this_run:
            continue

        # send real alert
        send(
            CHAT_ID,
            f"📢 New IOST Notice\n\n{text}\n{full_link}"
        )

        # store marker silently
        send(STORAGE_CHAT_ID, f"SENT:{notice_id}")

        seen_this_run.add(notice_id)

except Exception as e:
    print("Error:", e)
