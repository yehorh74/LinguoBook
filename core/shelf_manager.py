import os
from kivy.storage.jsonstore import JsonStore

class ShelfManager:
    def __init__(self, filename="shelf.json"):
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, "..", "data")
        os.makedirs(data_dir, exist_ok=True)

        self.store = JsonStore(os.path.join(data_dir, filename))

    def get_books(self):
        books = []
        for key in self.store.keys():
            data = self.store.get(key)
            books.append({
                "id": key,
                "path": data.get("path", ""),
                "title": data.get("title", "Unknown")
            })
        return books

    def add_book(self, book: dict):
        bid = book["id"]

        if self.store.exists(bid):
            return

        self.store.put(
            bid,
            path=book["path"],
            title=book["title"]
        )

    def remove_book(self, book_id: str):
        if self.store.exists(book_id):
            data = self.store.get(book_id)
            path = data.get("path", None)
            
            # Usuwamy wpis z półki
            self.store.delete(book_id)
            
            # Usuwamy plik książki jeśli istnieje
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Error deleting file {path}: {e}")

    def get_last_book(self):
        keys = list(self.store.keys())
        if not keys:
            return None

        last_key = keys[-1]
        data = self.store.get(last_key)

        return {
            "id": last_key,
            "path": data.get("path", ""),
            "title": data.get("title", "Unknown")
        }
