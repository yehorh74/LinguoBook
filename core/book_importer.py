import os
import shutil
import hashlib
import re
from bs4 import BeautifulSoup
from kivy.app import App

class BookImportManager:

    @staticmethod
    def get_books_dir():
        app = App.get_running_app()
        base = app.user_data_dir
        books_dir = os.path.join(base, "books")
        os.makedirs(books_dir, exist_ok=True)
        return books_dir

    @staticmethod
    def generate_book_id(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:12]

    @staticmethod
    def extract_title_fb2(path):
        try:
            with open(path, "rb") as f:
                raw = f.read()

            for enc in ("utf-8", "utf-16", "windows-1250", "latin-1"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return None

            text = re.sub(r'xmlns="[^"]+"', '', text, count=1)
            soup = BeautifulSoup(text, "html.parser")

            title = soup.find("book-title")
            if title and title.get_text(strip=True):
                return title.get_text(strip=True)
        except Exception as e:
            print("Title extract error:", e)

        return None
    
    @staticmethod
    def extract_author_fb2(path):
        try:
            # Czytamy binarnie, aby uniknąć problemów z kodowaniem (utf-8 vs windows-1250)
            with open(path, "rb") as f:
                # Czytamy większy fragment na wypadek długich opisów
                raw_data = f.read(20000)
            
            # Zamieniamy na tekst, ignorując znaki spoza standardu
            content = raw_data.decode('utf-8', errors='ignore')

            # 1. Znajdź sekcję title-info (tam zawsze jest autor)
            title_info = re.search(r'<title-info>(.*?)</title-info>', content, re.DOTALL | re.IGNORECASE)
            if not title_info:
                return "Unknown Author"
            
            section = title_info.group(1)

            # 2. Znajdź blok autora wewnątrz title-info
            author_match = re.search(r'<author>(.*?)</author>', section, re.DOTALL | re.IGNORECASE)
            if author_match:
                author_content = author_match.group(1)
                
                # Funkcja pomocnicza do wyciągania tekstu z tagów bez względu na wielkość liter
                def get_tag(tag_name, text):
                    m = re.search(f'<{tag_name}>(.*?)</{tag_name}>', text, re.DOTALL | re.IGNORECASE)
                    return m.group(1).strip() if m else ""

                first = get_tag('first-name', author_content)
                middle = get_tag('middle-name', author_content)
                last = get_tag('last-name', author_content)
                nick = get_tag('nickname', author_content)

                parts = [p for p in [first, middle, last] if p]
                if parts:
                    return " ".join(parts)
                if nick:
                    return nick

        except Exception as e:
            print(f"Błąd krytyczny extract_author: {e}")

        return "Unknown Author"

    @classmethod
    def import_book(cls, source_path):
        books_dir = cls.get_books_dir()
        book_id = cls.generate_book_id(source_path)

        ext = os.path.splitext(source_path)[1].lower() or ".fb2"
        dest_path = os.path.join(books_dir, f"{book_id}{ext}")

        if not os.path.exists(dest_path):
            shutil.copyfile(source_path, dest_path)

        title = cls.extract_title_fb2(dest_path)
        if not title:
            title = os.path.basename(source_path)

        # WYWOŁANIE NOWEJ METODY
        author = cls.extract_author_fb2(dest_path)
        print(f"DEBUG: Znalazłem autora: '{author}' dla pliku {source_path}")

        return {
            "id": book_id,
            "path": dest_path,
            "title": title,
            "author": author  
        }

    
