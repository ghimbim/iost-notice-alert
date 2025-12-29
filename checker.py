import requests
from bs4 import BeautifulSoup
import os
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# IOST notices page
URL = "https://iost.tu.edu.np/notices"

# Keywords to match relevant notices
KEYWORDS = ["CSIT", "B.Sc CSIT", "B.Sc. CSIT", "8th Semester", "VIII Semester", "Eighth Semester"]

# Telegram credentials from Step 3
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# File to store already seen notice links
seen_file = "seen.txt"

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, verify=False)

# Load already seen links
seen = set()
if os.path.exists(seen_file):
    with open(seen_file) as f:
        seen = set(f.read().splitlines())

try:
    r = requests.get(URL, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a")

    new_seen = set(seen)

    for a in links:
        text = a.get_text(strip=True)
        href = a.get("href")
        if not href:
            continue

        # Check for keywords
        if any(k.lower() in text.lower() for k in KEYWORDS):
            if True:
                send(f"New IOST Notice:\n{text}")
                new_seen.add(href)

    # Update seen file
    with open(seen_file, "w") as f:
        f.write("\n".join(new_seen))

except Exception as e:
    print("Error:", e)

