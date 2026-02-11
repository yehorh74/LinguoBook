from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import IconRightWidget, IconLeftWidgetWithoutTouch
from kivymd.uix.list import ThreeLineAvatarIconListItem 
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
#from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

# To jest kluczowe: definiujemy jak OneLineIconListItem ma obsługiwać ikony
Builder.load_string('''
<MyMenuItem@OneLineIconListItem>:
    icon: ""
    IconLeftWidget:
        icon: root.icon
''')

class ShelfScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', spacing=10, **kwargs)
        self.app = app
        self.books_to_load = [] # Inicjalizacja listy

        self.drop_sort_menu = MDDropdownMenu(width_mult=4)
        self.setup_sort_menu()

        # 1. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        tool_bar = MDTopAppBar(
            title="BOOK SHELF", 
            anchor_title="left",
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]], 
            right_action_items=[["sort", self.open_sort_menu], ["plus", self.app.open_file]]
        )
        top_layout.add_widget(tool_bar)
        self.add_widget(top_layout)

        # 2. Layout książek
        self.layout_books = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.layout_books.bind(minimum_height=self.layout_books.setter('height'))

        scroll_view = MDScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.layout_books)
        self.add_widget(scroll_view)

    def on_enter(self, *args):
        """Wywoływane przy każdym wejściu na ekran."""
        self.refresh_shelf()

    def refresh_shelf(self, sort_type=None):
        # 1. Zatrzymaj poprzednie ładowanie
        Clock.unschedule(self.load_next_book)
        
        # 2. Wyczyść widok
        self.layout_books.clear_widgets()
        
        # 3. Pobierz i posortuj dane
        books = self.app.shelf.get_books()
        
        if sort_type == "abc":
            # Sortujemy po tytule (zamiana na małe litery dla poprawności)
            books.sort(key=lambda x: x.get("title", "").lower())
        elif sort_type == "new":
            books.reverse()
        # "old" to domyślna kolejność z bazy
            
        self.books_to_load = books
        
        # 4. Uruchom ładowanie widgetów
        Clock.schedule_interval(self.load_next_book, 0.01)

    def load_next_book(self, dt):
        if not self.books_to_load:
            return False # Kończy schedule_interval

        book = self.books_to_load.pop(0)
        book_id = book["id"]

        progress_data = self.app.reader_state.get_book_progress_data(book_id)
        current_p = progress_data.get("page", 0)
        pages_list = progress_data.get("pages", [])
        total_p = len(pages_list)
        
        calc_value = 0
        if total_p > 0:
            calc_value = min(100, (current_p / total_p) * 100)

        # Tworzenie elementu listy
        list_book = ThreeLineAvatarIconListItem(
            text=book.get("title", "No Title"),
            secondary_text=book.get("author", "Unknown Author"),
            tertiary_text=f"Progress: {int(calc_value)}%",
            size_hint_x=0.95,
            pos_hint={"center_x": .5}
        )
        list_book.bind(on_release=lambda *_, b=book: self.app.on_shelf_book_clicked(b))

        # Dodajemy ikony
        list_book.add_widget(IconLeftWidgetWithoutTouch(icon="book-open"))
        
        # Pamiętaj o usunięciu nawiasów przy wywołaniu open_dialog w on_release!
        trash_icon = IconRightWidget(
            icon="trash-can",
            on_release=lambda x, b=book: self.open_dialog_instance(b)
        )
        list_book.add_widget(trash_icon)

        self.layout_books.add_widget(list_book)
        return True

    def open_sort_menu(self, button):
        self.drop_sort_menu.caller = button
        self.drop_sort_menu.open()

    def setup_sort_menu(self):
        menu_data = [
            ("Sort (A-Z)", "sort-alphabetical-ascending", "abc"),
            ("Sort (Newest)", "sort-calendar-ascending", "new"),
            ("Sort (Oldest)", "sort-calendar-descending", "old"),
        ]
        items = []
        for text, icon_name, sort_code in menu_data:
            items.append({
                "viewclass": "MyMenuItem",
                "text": text,
                "icon": icon_name,
                "on_release": lambda x=sort_code: self.sort_action(x),
            })
        self.drop_sort_menu.items = items

    def sort_action(self, sort_type):
        self.drop_sort_menu.dismiss()
        self.refresh_shelf(sort_type)

    def open_dialog_instance(self, book):
        """Uproszczona wersja dialogu usuwania."""
        dialog = MDDialog(
            title="Delete Book",
            text=f"Are you sure you want to delete '{book['title']}'?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="DELETE", on_release=lambda x: self.perform_delete(book, dialog)),
            ],
        )
        dialog.open()

    def perform_delete(self, book_to_delete, dialog):
        dialog.dismiss()
        self.app.shelf.remove_book(book_to_delete["id"])
        self.app.reader_state.remove_file_state_by_id(book_to_delete["id"])

        if self.app.reader_state.current_book_id == book_to_delete["id"]:
            self.app.clear_reader_state()
            self.app.show_home()
        else:
            self.refresh_shelf()
        


