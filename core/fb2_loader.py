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

    text = re.sub(r'xmlns="[^"]+"', '', text, count=1)
    soup = BeautifulSoup(text, "html.parser")

    # Szukamy tytułów i akapitów
    # FB2 używa <title> dla nagłówków rozdziałów i <p> dla treści
    elements = soup.find_all(['title', 'p'])

    structured_data = []
    for el in elements:
        content = el.get_text(strip=True)
        if not content:
            continue
        
        # Jeśli element jest wewnątrz tagu <title>, oznaczamy go jako tytuł
        # (BeautifulSoup znajdzie <p> wewnątrz <title>, więc sprawdzamy rodzica)
        if el.name == 'title' or el.parent.name == 'title':
            structured_data.append({'type': 'title', 'content': content})
        else:
            structured_data.append({'type': 'paragraph', 'content': content})

    if not structured_data:
        raise ValueError("FB2 loaded but no content found")

    return structured_data
