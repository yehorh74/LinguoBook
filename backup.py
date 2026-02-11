import os
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

from core.fb2_loader import load_fb2_simple as load_fb2
from core.reader_state import ReaderStateManager
from core.shelf_manager import ShelfManager
from core.dictionary_manager import DictionaryManager
from core.settings_manager import SettingsManager
from core.book_importer import BookImportManager
from screens.home import HomeScreen
from screens.shelf import ShelfScreen
from screens.settings import SettingsScreen
from screens.dictionary import DictionaryScreen
from core.reader_layout import ReaderLayout
from screens.loading_screen import LoadingScreen
from core.pagination_engine import PaginationEngine

if platform == "android":
    from native.android_picker import open_android_file_picker as open_file_picker, resolve_content_uri as resolve_uri

state_file = "reader_state.json" if platform == 'android' else "dev_reader_state.json"

class LinguoBookApp(MDApp):
    def build(self):
        # Używamy ScreenManagera dla płynnych przejść
        self.sm = MDScreenManager()
        
        self.settings = SettingsManager()
        self.selected_language = self.settings.get_language()
        self.reader_state = ReaderStateManager(state_file)
        self.shelf = ShelfManager()
        self.dictionary = DictionaryManager()
        self.selected_model = self.settings.get_model()
        self.theme_cls.primary_palette = self.settings.get_palette()
        self.theme_cls.theme_style = self.settings.get_theme()
        
        self.delete_mode = False
        self.previous_screen = "home"

        # Inicjalne ekrany (dodajemy je raz, potem tylko przełączamy)
        self.setup_screens()
        
        return self.sm

    def setup_screens(self):
        self.screens = {}

        # 1. NAJPIERW dodaj ekran Home - on stanie się domyślnym ekranem startowym
        self.screens["home"] = MDScreen(name="home")
        self.screens["home"].add_widget(HomeScreen(app=self))
        self.sm.add_widget(self.screens["home"])

        # 2. POTEM dodaj resztę ekranów
        self.reader_screen_instance = ReaderLayout(app=self, name="reader")
        self.sm.add_widget(self.reader_screen_instance)

        self.loading_screen = LoadingScreen() 
        self.sm.add_widget(self.loading_screen)

        self.screens["shelf"] = MDScreen(name="shelf")
        self.screens["shelf"].add_widget(ShelfScreen(app=self))

        self.screens["settings"] = MDScreen(name="settings")
        self.screens["settings"].add_widget(SettingsScreen(app=self))

        self.screens["dictionary"] = MDScreen(name="dictionary")
        self.screens["dictionary"].add_widget(DictionaryScreen(app=self))

        # Rejestrujemy resztę w pętli (pomijając home, który już dodaliśmy)
        for name, screen in self.screens.items():
            if name != "home":
                self.sm.add_widget(screen)

    # --- Nawigacja zoptymalizowana ---
    def switch_screen(self, screen_name, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = screen_name
        
        # SYNCHRONIZACJA: Pobierz widget i wymuś odświeżenie danych
        target_screen = self.sm.get_screen(screen_name)
        if target_screen.children:
            content = target_screen.children[0]
            if hasattr(content, "on_enter"):
                content.on_enter()

    def show_home(self):
        self.switch_screen("home", direction="right")
        self.previous_screen = "home"

    def open_shelf(self, source="home", *_):
        self.previous_screen = source
        self.switch_screen("shelf", direction="left")

    def open_dictionary(self, source="home", *_):
        self.previous_screen = source
        self.switch_screen("dictionary", direction="left")

    def open_settings(self, source="home", *_):
        self.previous_screen = source
        self.switch_screen("settings", direction="left")

    def show_reader(self):
        self.switch_screen("reader", direction="left")
        # reader_screen_instance to ReaderLayout
        # Wywołujemy on_pre_enter, który przekaże polecenie do wewnętrznego czytnika
        if hasattr(self.reader_screen_instance, "on_pre_enter"):
            self.reader_screen_instance.on_pre_enter()
        self.previous_screen = "reader"

    # --- Logika ładowania i plików ---
    def on_shelf_book_clicked(self, book):
        if self.delete_mode:
            self.shelf.remove_book(book["id"])
            self.reader_state.remove_file_state_by_id(book["id"])
            self.open_shelf()
            return

        # Używamy ID z książki, aby uniknąć błędów cache
        self.reader_state.set_current_file(book["path"], book["id"])
        self.show_loading("Loading book…")

        Clock.schedule_once(
            lambda dt: self._load_and_start_pagination(book["path"]),
            0.1 # Dajemy ułamek sekundy na odświeżenie UI przed ciężką pracą
        )

    def on_start(self):
        should_open_last = self.settings.get_open_last_book()
        
        if should_open_last:
            # Pobieramy ostatni ID, który był zapisany jako 'current'
            last_id = self.reader_state.current_book_id
            if last_id:
                all_books = self.shelf.get_books()
                current_book = next((b for b in all_books if b["id"] == last_id), None)
                
                if current_book:
                    # Ustawiamy parametry ZANIM Clock wywoła ładowanie
                    self.reader_state.set_current_file(current_book["path"], current_book["id"])
                    Clock.schedule_once(lambda dt: self.last_book(current_book), 0.2)
                    return

        self.show_home()
        
    def get_current_book_title(self):
        current_id = self.reader_state.current_book_id
        if not current_id:
            return "No book open"
        
        books = self.shelf.get_books()
        for book in books:
            if book["id"] == current_id:
                return book.get("title", "Unknown")
        return "Unknown"
    
    def last_book(self, book):
        path = book.get("path")
        if not path or not os.path.exists(path):
            self.clear_reader_state()
            self.show_home()
            return

        self.reader_state.set_current_file(book["path"], book["id"])
        self.show_loading("Loading last book…")
        Clock.schedule_once(lambda dt: self._load_and_start_pagination(path), 0.1)

    def open_file(self, *_):
        if platform == 'android':
            open_file_picker(self.on_file_selected)

    def on_file_selected(self, uri):
        if uri:
            Clock.schedule_once(lambda dt: self.load(uri), 0)

    def load(self, uri):
        if platform == "android" and uri.startswith("content://"):
            uri = resolve_uri(uri)

        book = BookImportManager.import_book(uri)
        self.shelf.add_book(book)
        
        # FIX: przekazujemy ID z importu, żeby manager stanu wiedział dokładnie co czytamy
        self.reader_state.set_current_file(book["path"], bid=book["id"])
        
        self.reader_state.pages = []
        self.reader_state.current_page = 0
        
        self.show_loading("Importing & Loading…")
        Clock.schedule_once(lambda dt: self._load_and_start_pagination(book["path"]), 0.1)

    def _load_and_start_pagination(self, uri):
        # Najpierw sprawdź, czy mamy to w JSONie
        if self.reader_state.load_cached_state():
            # Skoro mamy strony i stronę, idziemy prosto do czytnika
            self.show_reader() 
            return

        # JEŚLI NIE MA CACHE:
        try:
            # Dopiero tutaj resetujemy parametry dla nowej paginacji
            self.reader_state.pages = []
            self.reader_state.current_page = 0
            
            text = load_fb2(uri)
            self.start_background_pagination(text)
        except Exception as e:
            print(f"Error: {e}")
            self.show_home()

    def show_loading(self, text="Loading…"):
        self.loading_screen.update_status(text, 0)
        self.switch_screen("loading")

    def start_background_pagination(self, text):
        # Resetujemy UI paska przed startem
        self.loading_screen.progress_bar.value = 0
        self.show_loading("Paginating book…")
        
        # Inicjalizacja silnika
        self.pagination_engine = PaginationEngine(
            app=self,
            text=text,
            on_progress=self._update_pagination_ui,
            on_complete=self._finalize_pagination
        )
        self.pagination_engine.start()

    def _update_pagination_ui(self, percentage):
        # To wywołuje silnik co klatkę
        self.loading_screen.progress_bar.value = percentage
        self.loading_screen.status_label.text = f"Paginating: {int(percentage)}%"

    def _finalize_pagination(self, pages):
        self.reader_state.pages = pages
        # Przywróć stronę lub zacznij od 0
        self.reader_state.current_page = self.reader_state.restore_position()
        self.show_reader()

    def get_reader_height(self):
        return Window.height - dp(130) # Uproszczony margines dla stabilności

    def go_back(self):
        if self.sm.current == "reader":
            self.show_home()
        elif self.previous_screen == "reader":
            self.show_reader()
        else:
            self.show_home()

    def clear_reader_state(self):
        self.reader_state.current_book_id = None
        self.reader_state.pages = []
        self.reader_state.current_page = 0

    def on_pause(self):
        self.reader_state.save_position()
        return True

    def on_stop(self):
        self.reader_state.save_position()

if __name__ == "__main__":
    LinguoBookApp().run()