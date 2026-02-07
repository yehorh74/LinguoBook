from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import IconRightWidget, IconLeftWidgetWithoutTouch
from kivymd.uix.list import ThreeLineAvatarIconListItem 
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock

class ShelfScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', spacing=10, **kwargs)
        self.app = app

        # 1. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        tool_bar = MDTopAppBar(
            title="BOOK SHELF", 
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]], 
            right_action_items=[["plus", self.app.open_file]]
        )
        top_layout.add_widget(tool_bar)
        self.add_widget(top_layout)

        # 2. Layout książek (pusty na starcie)
        self.layout_books = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.layout_books.bind(minimum_height=self.layout_books.setter('height'))

        scroll_view = MDScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.layout_books)
        self.add_widget(scroll_view)

        # 3. Uruchamiamy ładowanie książek po krótkiej przerwie (płynna animacja ekranu)
        Clock.schedule_once(self.start_loading_shelf, 0.15)

    def start_loading_shelf(self, *args):
        # Pobieramy listę książek
        self.books_to_load = self.app.shelf.get_books()
        # Odpalamy dodawanie książek co klatkę (0 sekundy = następna klatka)
        Clock.schedule_interval(self.load_next_book, 0)

    def load_next_book(self, dt):
        if not self.books_to_load:
            return False

        book = self.books_to_load.pop(0)
        book_id = book["id"]

        # Wywołujemy nową, bezpieczną metodę
        progress_data = self.app.reader_state.get_book_progress_data(book_id)
        
        current_p = progress_data.get("page", 0) # Klucz w Twoim JsonStore to "page" (liczba pojedyncza)
        pages_list = progress_data.get("pages", [])
        total_p = len(pages_list)
        
        calc_value = 0
        if total_p > 0:
            calc_value = min(100, (current_p / total_p) * 100)

        # Tworzenie elementu listy (ThreeLineAvatarIconListItem)
        list_book = ThreeLineAvatarIconListItem(
            text=book["title"],
            secondary_text=book.get("author", "Unknown Author"),
            tertiary_text=f"Progress: {int(calc_value)}%",
            size_hint_x=0.95,
            pos_hint={"center_x": .5}
        )
        list_book.bind(on_release=lambda *_, b=book: self.app.on_shelf_book_clicked(b))

        # 2. Tworzymy kontener, który ograniczy szerokość paska
        # To jest klucz! Tu ustawiasz jak szeroki ma być pasek względem całej listy
        progress_container = MDBoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(160), # Tu ustawiasz konkretną szerokość paska (np. 160dp)
            adaptive_height=True,
            pos_hint={"center_x": .45, "center_y": .2} # Przesunięcie lekko w lewo, by nie biło w ikonę kosza
        )

        progress = MDProgressBar(
            value=calc_value,
            max=100,
            size_hint_x=1, # Wypełnia całe 160dp kontenera
            height=dp(4)
        )

        progress_container.add_widget(progress)

        # 3. Dodajemy ikony i kontener z paskiem do listy
        list_book.add_widget(IconLeftWidgetWithoutTouch(icon="book-open"))
        list_book.add_widget(IconRightWidget(
            icon="trash-can",
            on_release=lambda widget, b=book: self.open_dialog()(widget, b)
        ))
        
        # Dodajemy kontener jako widget - on "wskoczy" w okolice trzeciej linii
        list_book.add_widget(progress_container)

        self.layout_books.add_widget(list_book)
        return True

    def open_dialog(self):
        def close_dialog(*args):
            dialog.dismiss()

        def delete_book_action(*args):
            self.perform_delete(book_to_delete)
            dialog.dismiss()

        book_to_delete = None

        def set_book_to_delete(b):
            nonlocal book_to_delete
            book_to_delete = b

        dialog = MDDialog(
            title="Delete Book",
            text="Are you sure you want to delete this book from the shelf?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=close_dialog),
                MDFlatButton(text="DELETE", on_release=delete_book_action),
            ],
        )

        def wrapper(btn, b):
            set_book_to_delete(b)
            dialog.open()

        return wrapper
    
    def perform_delete(self, book_to_delete):
        self.app.shelf.remove_book(book_to_delete["id"])
        self.app.reader_state.remove_file_state_by_id(book_to_delete["id"])

        if self.app.reader_state.current_book_id == book_to_delete["id"]:
            self.app.clear_reader_state()
            self.app.show_home()
        else:
            # Zamiast przeładowywać cały ekran, usuwamy fizycznie widget
            # To jest szybsze niż open_shelf()
            self.app.open_shelf()
        


