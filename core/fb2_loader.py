from bs4 import BeautifulSoup
import re

def load_fb2_simple(path):
    with open(path, "rb") as f:
        raw = f.read()

    for enc in ("utf-8", "utf-16", "windows-1250", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="ignore")

    # usuń namespace FB2
    text = re.sub(r'xmlns="[^"]+"', '', text, count=1)

    # 🔥 BEZ lxml
    soup = BeautifulSoup(text, "html.parser")

    paragraphs = soup.find_all("p")

    clean = [
        p.get_text(strip=True)
        for p in paragraphs
        if p.get_text(strip=True)
    ]

    if not clean:
        raise ValueError("FB2 loaded but no paragraphs found")

    return "\n\n".join(clean)
