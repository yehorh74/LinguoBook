import os
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
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

if platform == "android":
    from native.android_picker import open_android_file_picker as open_file_picker, resolve_content_uri as resolve_uri

state_file = "reader_state.json" if platform == 'android' else "dev_reader_state.json"

class LinguoBookApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.sm = MDScreenManager()
        
        self.settings = SettingsManager()
        self.selected_language = self.settings.get_language()
        self.reader_state = ReaderStateManager(state_file)
        self.shelf = ShelfManager()
        self.dictionary = DictionaryManager()
        self.selected_model = self.settings.get_model()
        
        self.delete_mode = False
        self.previous_screen = "home"

        self.setup_screens()
        return self.sm

    def setup_screens(self):
        self.screens = {
            "home": MDScreen(name="home"),
            "shelf": MDScreen(name="shelf"),
            "settings": MDScreen(name="settings"),
            "dictionary": MDScreen(name="dictionary"),
            "reader": MDScreen(name="reader")
        }
        for screen in self.screens.values():
            self.sm.add_widget(screen)

    def switch_screen(self, screen_name, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = screen_name

    # --- Zoptymalizowana Nawigacja (Lazy Loading) ---

    def show_home(self):
        self.switch_screen("home", direction="right")
        # Budujemy zawartość po rozpoczęciu animacji
        Clock.schedule_once(lambda dt: self._lazy_load("home", HomeScreen), 0.15)
        self.previous_screen = "home"

    def open_shelf(self, source="home", *_):
        self.previous_screen = source
        self.switch_screen("shelf", direction="left")
        Clock.schedule_once(lambda dt: self._lazy_load("shelf", ShelfScreen), 0.15)

    def open_dictionary(self, source="home", *_):
        self.previous_screen = source
        self.switch_screen("dictionary", direction="left")
        Clock.schedule_once(lambda dt: self._lazy_load("dictionary", DictionaryScreen), 0.15)

    def open_settings(self, source="home", *_):
        self.previous_screen = source
        self.switch_screen("settings", direction="left")
        Clock.schedule_once(lambda dt: self._lazy_load("settings", SettingsScreen), 0.15)

    def show_reader(self):
        self.switch_screen("reader", direction="left")
        Clock.schedule_once(lambda dt: self._lazy_load("reader", ReaderLayout), 0.15)
        self.previous_screen = "reader"

    def _lazy_load(self, screen_name, screen_class):
        """Pomocnicza funkcja do budowania ekranu w tle."""
        self.screens[screen_name].clear_widgets()
        self.screens[screen_name].add_widget(screen_class(app=self))

    # --- Logika ładowania ---

    def on_shelf_book_clicked(self, book):
        if self.delete_mode:
            self.shelf.remove_book(book["id"])
            self.reader_state.remove_file_state_by_id(book["id"])
            self.open_shelf()
            return

        self.reader_state.set_current_file(book["path"], book["id"])
        self.show_loading("Loading book…")
        # Większy timeout dla stabilności przejścia do ekranu ładowania
        Clock.schedule_once(lambda dt: self._load_and_start_pagination(book["path"]), 0.2)

    def on_start(self):
        last_id = self.reader_state.current_book_id
        if last_id:
            all_books = self.shelf.get_books()
            current_book = next((b for b in all_books if b["id"] == last_id), None)
            if current_book:
                self.last_book(current_book)
                return
        
        last_added = self.shelf.get_last_book()
        if last_added:
            self.last_book(last_added)
        else:
            self.show_home()

    def get_current_book_title(self):
        current_id = self.reader_state.current_book_id
        if not current_id: return "No book open"
        books = self.shelf.get_books()
        for book in books:
            if book["id"] == current_id: return book.get("title", "Unknown")
        return "Unknown"

    def last_book(self, book):
        path = book.get("path")
        if not path or not os.path.exists(path):
            self.clear_reader_state()
            self.show_home()
            return
        self.reader_state.set_current_file(book["path"], book["id"])
        self.show_loading("Loading last book…")
        Clock.schedule_once(lambda dt: self._load_and_start_pagination(path), 0.2)

    def load(self, uri):
        if platform == "android" and uri.startswith("content://"):
            uri = resolve_uri(uri)
        book = BookImportManager.import_book(uri)
        self.shelf.add_book(book)
        self.reader_state.set_current_file(book["path"], bid=book["id"])
        self.reader_state.pages = []
        self.reader_state.current_page = 0
        self.show_loading("Importing…")
        Clock.schedule_once(lambda dt: self._load_and_start_pagination(book["path"]), 0.2)

    def _load_and_start_pagination(self, uri):
        if self.reader_state.load_cached_state():
            self.show_reader()
            return
        try:
            text = load_fb2(uri)
            self.start_background_pagination(text)
        except Exception as e:
            self.show_home()

    def show_loading(self, text="Loading…"):
        self.sm.current_screen.clear_widgets()
        self.sm.current_screen.add_widget(
            MDBoxLayout(
                MDLabel(text=text, halign="center", font_style="H6"),
                orientation="vertical", padding=dp(20)
            )
        )

    def start_background_pagination(self, text):
        self._words = text.split(" ")
        self._word_index = 0
        self._current_words = []
        self._pages = []
        self._ti = TextInput(
            font_size=dp(18), size_hint=(None, None),
            width=Window.width - dp(20), height=self.get_reader_height(),
            readonly=True, multiline=True
        )
        Clock.schedule_once(self._paginate_step, 0)

    def _paginate_step(self, dt):
        MAX_STEPS = 80 # Jeszcze mniejszy chunk dla płynności animacji "Paginating"
        CHUNK = 6
        for _ in range(MAX_STEPS):
            if self._word_index >= len(self._words):
                if self._current_words: self._pages.append(" ".join(self._current_words))
                self.reader_state.pages = self._pages
                self.reader_state.current_page = self.reader_state.restore_position()
                self.reader_state.save_position()
                self.show_reader()
                return
            words = self._words[self._word_index:self._word_index + CHUNK]
            candidate = self._current_words + words
            self._ti.text = " ".join(candidate)
            self._ti._trigger_refresh_text()
            if self._ti.minimum_height + self._ti.line_height > self._ti.height:
                if self._current_words: self._pages.append(" ".join(self._current_words))
                self._current_words = []
            else:
                self._current_words.extend(words)
                self._word_index += CHUNK
        Clock.schedule_once(self._paginate_step, 0)

    def get_reader_height(self):
        return Window.height - dp(130)

    def go_back(self):
        dir = "right"
        if self.sm.current == "reader": self.show_home()
        elif self.previous_screen == "reader": self.show_reader()
        else: self.show_home()

    def open_file(self, *_):
        if platform == 'android': open_file_picker(self.on_file_selected)

    def on_file_selected(self, uri):
        if uri: Clock.schedule_once(lambda dt: self.load(uri), 0)

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