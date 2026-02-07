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
from kivymd.uix.progressbar import MDProgressBar

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
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.theme_style = "Light"
        
        # Używamy ScreenManagera dla płynnych przejść
        self.sm = MDScreenManager()
        
        self.settings = SettingsManager()
        self.selected_language = self.settings.get_language()
        self.reader_state = ReaderStateManager(state_file)
        self.shelf = ShelfManager()
        self.dictionary = DictionaryManager()
        self.selected_model = self.settings.get_model()
        
        self.delete_mode = False
        self.previous_screen = "home"

        # Inicjalne ekrany (dodajemy je raz, potem tylko przełączamy)
        self.setup_screens()
        
        return self.sm

    def setup_screens(self):
        """Tworzy instancje ekranów i dodaje je do managera."""
        self.screens = {
            "home": MDScreen(name="home"),
            "shelf": MDScreen(name="shelf"),
            "settings": MDScreen(name="settings"),
            "dictionary": MDScreen(name="dictionary"),
            "reader": MDScreen(name="reader")
        }
        for screen in self.screens.values():
            self.sm.add_widget(screen)

    # --- Nawigacja zoptymalizowana ---
    def switch_screen(self, screen_name, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = screen_name

    def show_home(self):
        self.screens["home"].clear_widgets()
        self.screens["home"].add_widget(HomeScreen(app=self))
        self.switch_screen("home", direction="right")
        self.previous_screen = "home"

    def open_shelf(self, source="home", *_):
        self.previous_screen = source
        self.screens["shelf"].clear_widgets()
        self.screens["shelf"].add_widget(ShelfScreen(app=self))
        self.switch_screen("shelf", direction="left")

    def open_dictionary(self, source="home", *_):
        self.previous_screen = source
        self.screens["dictionary"].clear_widgets()
        self.screens["dictionary"].add_widget(DictionaryScreen(app=self))
        self.switch_screen("dictionary", direction="left")

    def open_settings(self, source="home", *_):
        self.previous_screen = source
        self.screens["settings"].clear_widgets()
        self.screens["settings"].add_widget(SettingsScreen(app=self))
        self.switch_screen("settings", direction="left")

    def show_reader(self):
        self.screens["reader"].clear_widgets()
        self.screens["reader"].add_widget(ReaderLayout(app=self))
        self.switch_screen("reader", direction="left")
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
        if self.reader_state.load_cached_state():
            self.show_reader()
            return

        try:
            text = load_fb2(uri)
            self.start_background_pagination(text)
        except Exception as e:
            print(f"Error loading book: {e}")
            self.show_home()

    def show_loading(self, text="Loading…"):
        self.sm.current_screen.clear_widgets()
        
        layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(40),
            spacing=dp(20),
            adaptive_height=True,
            pos_hint={"center_x": .5, "center_y": .5}
        )
        
        self.loading_label = MDLabel(
            text=text, 
            halign="center", 
            font_style="H6"
        )
        
        # Tworzymy pasek postępu jako atrybut klasy
        self.pagination_progress = MDProgressBar(
            type="determinate", 
            value=0, 
            max=100,
            size_hint_x=0.8,
            pos_hint={"center_x": .5}
        )
        
        layout.add_widget(self.loading_label)
        layout.add_widget(self.pagination_progress)
        self.sm.current_screen.add_widget(layout)

    def start_background_pagination(self, text):
        self.show_loading("Paginating book…")
        self._words = text.split(" ")
        self._word_index = 0
        self._current_words = []
        self._pages = []

        self._ti = TextInput(
            font_size=dp(18),
            size_hint=(None, None),
            width=Window.width - dp(20),
            height=self.get_reader_height(),
            readonly=True,
            multiline=True
        )
        Clock.schedule_once(self._paginate_step, 0)

    def _paginate_step(self, dt):
        MAX_STEPS = 100 
        CHUNK = 6
        
        # Obliczanie całkowitej liczby słów dla procentów
        total_words = len(self._words)

        for _ in range(MAX_STEPS):
            if self._word_index >= total_words:
                # Koniec paginacji
                if self._current_words:
                    self._pages.append(" ".join(self._current_words))
                
                self.pagination_progress.value = 100 
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
                if self._current_words:
                    self._pages.append(" ".join(self._current_words))
                self._current_words = []
            else:
                self._current_words.extend(words)
                self._word_index += CHUNK
        
        # AKTUALIZACJA PASKA PO KAŻDYM MAX_STEPS
        if total_words > 0:
            percentage = (self._word_index / total_words) * 100
            self.pagination_progress.value = percentage
            self.loading_label.text = f"Paginating: {int(percentage)}%"

        Clock.schedule_once(self._paginate_step, 0)

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