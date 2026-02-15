from kivy.storage.jsonstore import JsonStore
from kivy.uix.textinput import TextInput
from core.utils import book_id


class ReaderStateManager:
    def __init__(self, store_path="reader_state.json"):
        self.store = JsonStore(store_path)
        self.pages = []
        self.current_page = 0
        self.current_book_id = None
        self.current_path = None
        if self.store.exists('_system_meta'):
            self.current_book_id = self.store.get('_system_meta')['last_id']
        else:
            self.current_book_id = None

    def load_cached_state(self):
        if not self.current_book_id:
            return False

        if self.store.exists(self.current_book_id):
            data = self.store.get(self.current_book_id)
            self.pages = data.get("pages", [])
            self.current_page = data.get("page", 0)
            return bool(self.pages)

        return False

    def set_current_file(self, filepath, bid=None):
        # Jeśli nie podano ID, próbujemy wygenerować (ale lepiej podawać)
        if bid is None:
            bid = book_id(filepath)
        
        # Sprawdzamy czy to nowa książka ZANIM nadpiszemy atrybuty
        is_new_book = (self.current_book_id != bid)
        
        self.current_book_id = bid
        self.current_path = filepath
        
        # Zapisujemy w JsonStore informację o ostatniej książce
        self.store.put('_system_meta', last_id=bid)

        # Jeśli otwieramy inną książkę niż poprzednio, czyścimy cache w pamięci RAM
        if is_new_book:
            self.pages = []
            self.current_page = 0
            print(f"New book detected. ID: {bid}")
        else:
            # Jeśli ta sama, ale np. wymuszamy przeładowanie
            # Możesz zdecydować czy chcesz czyścić pages czy nie
            pass

    def save_position(self):
        if not self.current_book_id:
            return

        self.store.put(
            self.current_book_id,
            page=self.current_page,
            pages=self.pages   # 🔥 ZAPIS STRON
        )

    def restore_position(self):
        if not self.current_book_id:
            return 0

        if not self.store.exists(self.current_book_id):
            return 0

        page = self.store.get(self.current_book_id).get("page", 0)
        return min(page, len(self.pages) - 1)

    def remove_file_state_by_id(self, book_id):
        if self.store.exists(book_id):
            self.store.delete(book_id)

    def get_book_progress_data(self, bid):
        """Pobiera dane postępu dla konkretnego ID książki bezpośrednio z pliku JSON."""
        if self.store.exists(bid):
            return self.store.get(bid)
        return {}
    
    def get_all_progress(self):
        """Pobiera postępy wszystkich książek ze store'a i zwraca je jako słownik."""
        all_data = {}
        # Przechodzimy przez wszystkie klucze w pliku JSON
        for key in self.store.keys():
            # Pomijamy metadane systemowe, jeśli nie są danymi książki
            if key == '_system_meta':
                continue
            
            data = self.store.get(key)
            all_data[key] = {
                "page": data.get("page", 0),
                "pages": data.get("pages", [])
            }
        return all_data
