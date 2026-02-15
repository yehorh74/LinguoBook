from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import IconRightWidget, IconLeftWidgetWithoutTouch
from kivymd.uix.list import ThreeLineAvatarIconListItem 
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget

# Definicja elementu menu
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
        self.l = self.app.lang
        self._book_widgets = {}  # Cache dla widżetów książek
        self.books_to_load = []

        self.drop_sort_menu = MDDropdownMenu(width_mult=4)
        self.setup_sort_menu()

        l = self.app.lang

        # 1. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        self.tool_bar = MDTopAppBar(
            title=l["book_shelf"], 
            anchor_title="left",
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]], 
            right_action_items=[["sort", self.open_sort_menu], ["plus", self.app.open_file]]
        )
        top_layout.add_widget(self.tool_bar)
        self.add_widget(top_layout)

        # 2. Layout książek
        self.layout_books = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.layout_books.bind(minimum_height=self.layout_books.setter('height'))

        scroll_view = MDScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.layout_books)
        self.add_widget(scroll_view)

    def _create_and_add_widget(self, book, p_text):
        """Pomocnicza metoda do tworzenia widżetu i dodawania go do cache i layoutu."""
        list_book = ThreeLineAvatarIconListItem(
            text=book.get("title", "No Title"),
            secondary_text=book.get("author", "Unknown Author"),
            tertiary_text=p_text,
            size_hint_x=0.95,
            pos_hint={"center_x": .5}
        )
        list_book.bind(on_release=lambda *_, b=book: self.app.on_shelf_book_clicked(b))
        list_book.add_widget(IconLeftWidgetWithoutTouch(icon="book-open"))
        
        trash_icon = IconRightWidget(
            icon="trash-can",
            on_release=lambda x, b=book: self.open_dialog_instance(b)
        )
        list_book.add_widget(trash_icon)
        
        # Zapisujemy w cache i dodajemy do widoku
        self._book_widgets[book["id"]] = list_book
        self.layout_books.add_widget(list_book)

    def update_shelf_silently(self):
        """Metoda aktualizująca widżety w tle bez czyszczenia całego layoutu."""
        books = self.app.shelf.get_books()
        l = self.app.lang
        
        # Pobieramy postępy (używamy batch loading jeśli app to wspiera)
        all_progress = self.app.reader_state.get_all_progress() if hasattr(self.app.reader_state, 'get_all_progress') else None

        for book in books:
            b_id = book["id"]
            
            # Pobieranie danych progressu
            if all_progress:
                progress_data = all_progress.get(b_id, {"page": 0, "pages": []})
            else:
                progress_data = self.app.reader_state.get_book_progress_data(b_id)
            
            current_p = progress_data.get("page", 0)
            total_p = len(progress_data.get("pages", []))
            calc_value = int((current_p / total_p) * 100) if total_p > 0 else 0
            p_text = f"{l['progress']}: {calc_value}%"

            if b_id in self._book_widgets:
                # Jeśli widżet istnieje, aktualizujemy tylko tekst (błyskawiczne)
                self._book_widgets[b_id].tertiary_text = p_text
            else:
                # Jeśli to nowa książka, tworzymy widżet
                self._create_and_add_widget(book, p_text)

    def on_enter(self, *args):
        """Wywoływane przy wejściu na ekran - szybka aktualizacja."""
        self.update_shelf_silently()
        self.refresh_localization()

    def refresh_shelf(self, sort_type=None):
        """Twarde odświeżenie (np. po zmianie sortowania)."""
        Clock.unschedule(self.load_next_book)
        self.layout_books.clear_widgets()
        self._book_widgets.clear() # Czyścimy cache przy pełnym odświeżeniu
        
        books = self.app.shelf.get_books()
        if sort_type == "abc":
            books.sort(key=lambda x: x.get("title", "").lower())
        elif sort_type == "new":
            books.reverse()
            
        self.books_to_load = books
        Clock.schedule_interval(self.load_next_book, 0.01)

    def load_next_book(self, dt):
        if not self.books_to_load:
            return False

        l = self.app.lang
        book = self.books_to_load.pop(0)
        
        progress_data = self.app.reader_state.get_book_progress_data(book["id"])
        current_p = progress_data.get("page", 0)
        total_p = len(progress_data.get("pages", []))
        calc_value = int((current_p / total_p) * 100) if total_p > 0 else 0
        
        self._create_and_add_widget(book, f"{l['progress']}: {calc_value}%")
        return True

    def open_sort_menu(self, button):
        self.drop_sort_menu.caller = button
        self.drop_sort_menu.hor_growth = "left"
        self.drop_sort_menu.open()

    def setup_sort_menu(self):
        l = self.app.lang
        menu_data = [
            (l["sort_menu_AZ"], "sort-alphabetical-ascending", "abc"),
            (l["sort_menu_newest"], "sort-calendar-ascending", "new"),
            (l["sort_menu_oldest"], "sort-calendar-descending", "old"),
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
        l = self.app.lang
        dialog = MDDialog(
            title=l["delete_book_menu"],
            text=l["delete_confirm"].format(book_title=book['title']),
            buttons=[
                MDFlatButton(text=l["delete_book_menu_cancel"], on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text=l["delete_book_menu_confirm_button"], on_release=lambda x: self.perform_delete(book, dialog)),
            ],
        )
        dialog.open()

    def perform_delete(self, book_to_delete, dialog):
        dialog.dismiss()
        b_id = book_to_delete["id"]
        self.app.shelf.remove_book(b_id)
        self.app.reader_state.remove_file_state_by_id(b_id)

        # Usuwamy widżet z cache i layoutu, żeby nie przeładowywać wszystkiego
        if b_id in self._book_widgets:
            widget = self._book_widgets.pop(b_id)
            self.layout_books.remove_widget(widget)

        if self.app.reader_state.current_book_id == b_id:
            self.app.clear_reader_state()
            self.app.show_home()
        # Nie musimy wywoływać refresh_shelf, bo usunęliśmy konkretny widżet powyżej

    def refresh_localization(self):
        l = self.app.lang
        if hasattr(self, 'tool_bar'):
            self.tool_bar.title = l["book_shelf"]
        self.setup_sort_menu()
        if not self.books_to_load:
            self.update_shelf_silently()