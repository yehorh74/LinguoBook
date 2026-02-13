import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from core.fb2_loader import load_fb2_simple as load_fb2
from core.reader_state import ReaderStateManager
from core.shelf_manager import ShelfManager
from ui.reader_widgets import ReaderTextInput
from core.book_importer import BookImportManager

DEV_BOOK = "dev/test_books/The Little Prince - Antoine de Saint-Exupéry - FB2.fb2"
STATE_FILE = "dev_reader_state.json"


class DevBookReaderApp(App):

    def build(self):
        self.root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.reader = None
        self.reader_state = ReaderStateManager(STATE_FILE)
        self.shelf = ShelfManager()
        self.previous_screen = None
        return self.root

    def on_start(self):
        if os.path.exists(DEV_BOOK):
            self.load_book(DEV_BOOK)
        else:
            print("DEV_BOOK not found:", DEV_BOOK)
            self.show_home()

    # ================= HOME =================

    def show_home(self):
        self.root.clear_widgets()

        label = Label(text="DEV MODE\nLinguoBook", font_size="20sp")
        label.bind(size=label.setter("text_size"))

        btn_open = Button(text="OPEN DEV BOOK", height=dp(40), size_hint_y=None)
        btn_open.bind(on_release=lambda *_: self.load_book(DEV_BOOK))

        btn_shelf = Button(text="BOOK SHELF", height=dp(40), size_hint_y=None)
        btn_shelf.bind(on_release=self.open_shelf)

        btn_exit = Button(text="EXIT", height=dp(40), size_hint_y=None)
        btn_exit.bind(on_release=lambda *_: self.stop())

        self.root.add_widget(btn_open)
        self.root.add_widget(btn_shelf)
        self.root.add_widget(btn_exit)
        self.root.add_widget(label)

    # ================= SHELF =================

    def open_shelf(self, *_):
        self.previous_screen = "home"
        self.root.clear_widgets()

        layout = BoxLayout(orientation="vertical", spacing=10)

        top = BoxLayout(size_hint_y=None, height=dp(40))
        btn_back = Button(text="BACK")
        btn_back.bind(on_release=self.on_back)
        top.add_widget(btn_back)

        layout.add_widget(top)

        books_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        books_layout.bind(minimum_height=books_layout.setter("height"))

        for book in self.shelf.get_books():
            btn = Button(text=book["title"], height=dp(40), size_hint_y=None)
            # Ważne: lambda musi złapać book w default argumencie
            btn.bind(on_release=lambda _, b=book: self.load_book(b["path"]))
            books_layout.add_widget(btn)

        scroll = ScrollView()
        scroll.add_widget(books_layout)

        layout.add_widget(scroll)
        self.root.add_widget(layout)

    # ================= LOADING =================

    def load_book(self, path):
        if not os.path.exists(path):
            print("File does not exist:", path)
            self.show_home()
            return

        book = BookImportManager.import_book(path)
        self.shelf.add_book(book)
        self.reader_state.set_current_file(book["path"])

        self.reader_state.pages = []
        self.reader_state.current_page = 0

        self.show_loading("Loading book…")
        Clock.schedule_once(lambda dt: self._load_and_paginate(book["path"]), 0)

    def show_loading(self, text):
        self.root.clear_widgets()
        self.root.add_widget(Label(text=text, font_size="20sp"))

    def _load_and_paginate(self, path):
        if self.reader_state.load_cached_state():
            self.show_reader()
            return

        try:
            text = load_fb2(path)
            self.start_background_pagination(text)
        except Exception as e:
            print("Error:", e)
            self.show_home()

    # ================= PAGINATION =================

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
        MAX_STEPS = 150
        CHUNK = 6

        for _ in range(MAX_STEPS):
            if self._word_index >= len(self._words):
                if self._current_words:
                    self._pages.append(" ".join(self._current_words))
                    self._current_words = []

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
                # Nie przesuwamy indeksu, słowa zostaną spróbowane na następnej stronie
            else:
                self._current_words.extend(words)
                self._word_index += CHUNK

        Clock.schedule_once(self._paginate_step, 0)

    # ================= READER =================

    def show_reader(self):
        self.previous_screen = "reader"
        self.root.clear_widgets()

        top = GridLayout(cols=3, size_hint_y=None, height=dp(40))
        btn_home = Button(text="HOME")
        btn_shelf = Button(text="SHELF")
        btn_exit = Button(text="EXIT")

        btn_home.bind(on_release=self.show_home)
        btn_shelf.bind(on_release=self.open_shelf)
        btn_exit.bind(on_release=lambda *_: self.stop())

        top.add_widget(btn_home)
        top.add_widget(btn_shelf)
        top.add_widget(btn_exit)

        self.pages = self.reader_state.pages
        self.current_page = self.reader_state.current_page

        self.reader = ReaderTextInput(
            text=self.pages[self.current_page],
            font_size=dp(18),
            readonly=True,
            multiline=True,
            size_hint_y=None,
            height=self.get_reader_height(),
            padding=[dp(5), dp(10), dp(5), dp(10)]
        )

        self.page_label = Label(
            text=f"Page {self.current_page + 1} / {len(self.pages)}",
            size_hint_y=None,
            height=dp(30)
        )

        nav = BoxLayout(size_hint_y=None, height=dp(40))
        self.page_input = TextInput(
            text=str(self.current_page + 1),
            input_filter="int",
            size_hint_x=0.3
        )

        btn_go = Button(text="Go")
        btn_go.bind(on_release=self.on_go_to_page)

        nav.add_widget(self.page_input)
        nav.add_widget(btn_go)

        container = BoxLayout(orientation="vertical")
        container.add_widget(self.reader)
        container.add_widget(self.page_label)
        container.add_widget(nav)

        self.root.add_widget(top)
        self.root.add_widget(container)

    # ================= HELPERS =================

    def get_reader_height(self):
        return Window.height - dp(40) - dp(30) - dp(40) - dp(20)

    def update_page(self):
        self.reader.text = self.pages[self.reader_state.current_page]
        self.page_label.text = f"Page {self.reader_state.current_page + 1} / {len(self.pages)}"
        self.page_input.text = str(self.reader_state.current_page + 1)
        self.reader_state.save_position()

    def on_go_to_page(self, *_):
        try:
            p = int(self.page_input.text) - 1
            if 0 <= p < len(self.pages):
                self.reader_state.current_page = p
                self.update_page()
            else:
                print("Invalid page number")
        except ValueError:
            print("Invalid input: not a number")

    def on_back(self, *_):
        self.show_home()

    def on_stop(self):
        self.reader_state.save_position()


if __name__ == "__main__":
    DevBookReaderApp().run()
