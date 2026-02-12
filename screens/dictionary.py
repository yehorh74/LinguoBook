from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, IconLeftWidgetWithoutTouch
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu

class DictionaryScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', spacing=10, **kwargs)
        self.app = app
        self._word_widgets = {}  # Słownik cache: {word_key: widget_object}
        self.words_to_load = []

        # 1. Menu Sortowania
        self.drop_sort_menu = MDDropdownMenu(width_mult=4)
        self.setup_sort_menu()

        # 2. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        self.tool_bar = MDTopAppBar(
            title=self.app.lang["dictionary"], 
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]],
            right_action_items=[["sort", self.open_sort_menu]],
            anchor_title="left"
        )
        top_layout.add_widget(self.tool_bar)
        self.add_widget(top_layout)

        # 3. Layout słownika
        self.layout_dict = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.layout_dict.bind(minimum_height=self.layout_dict.setter('height'))

        scroll_view = MDScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.layout_dict)
        self.add_widget(scroll_view)

    def on_enter(self, *args):
        """Wywoływane przy wejściu. Aktualizujemy tylko to, co nowe."""
        self.refresh_localization()
        self.update_dictionary_silently()

    def update_dictionary_silently(self):
        """Dodaje nowe słowa do listy bez przeładowywania całości."""
        words_dict = self.app.dictionary.get_all()
        
        # Sprawdzamy, czy w bazie są słowa, których nie mamy w cache
        for key, value in words_dict.items():
            if key not in self._word_widgets:
                self._create_word_widget(key, value)
        
        # Opcjonalnie: usuwamy z widoku te, które zostały usunięte z bazy w międzyczasie
        current_keys = set(words_dict.keys())
        cached_keys = list(self._word_widgets.keys())
        for cached_key in cached_keys:
            if cached_key not in current_keys:
                self._remove_widget_from_ui(cached_key)

    def _create_word_widget(self, key, value):
        """Tworzy widżet i dodaje go do cache."""
        list_word = OneLineAvatarIconListItem(
            text=f"{key} : {value['translation']}",
            _no_ripple_effect=True,
            size_hint_x=0.9,
            pos_hint={"center_x": .5}
        )
        
        trash = IconRightWidget(
            icon="trash-can",
            on_release=lambda btn, k=key: self.delete_word(k)
        )
        
        list_word.add_widget(IconLeftWidgetWithoutTouch(icon="translate"))
        list_word.add_widget(trash)
        
        self._word_widgets[key] = list_word
        self.layout_dict.add_widget(list_word)

    def _remove_widget_from_ui(self, key):
        """Usuwa widżet z ekranu i z pamięci cache."""
        if key in self._word_widgets:
            widget = self._word_widgets.pop(key)
            if widget.parent:
                widget.parent.remove_widget(widget)

    def delete_word(self, key):
        """Usuwa słowo z bazy i natychmiastowo z UI."""
        self.app.dictionary.delete(key)
        self._remove_widget_from_ui(key)

    def sort_words(self, sort_type):
        """Sortowanie wymaga przebudowania layoutu (zmiana kolejności)."""
        self.drop_sort_menu.dismiss()
        Clock.unschedule(self.load_next_word)
        
        self.layout_dict.clear_widgets()
        self._word_widgets.clear()
        
        # Pobierz i posortuj dane
        all_words = list(self.app.dictionary.get_all().items())
        if sort_type == "abc":
            all_words.sort(key=lambda x: x[0].lower())
        elif sort_type == "new":
            all_words.reverse()
        
        self.words_to_load = all_words
        Clock.schedule_interval(self.load_next_word, 0)

    def load_next_word(self, dt):
        """Krokowe ładowanie używane tylko przy pełnym re-sortowaniu."""
        if not self.words_to_load:
            return False
        key, value = self.words_to_load.pop(0)
        self._create_word_widget(key, value)
        return True

    def setup_sort_menu(self):
        l = self.app.lang
        menu_data = [
            (l["sort_menu_AZ"], "sort-alphabetical-ascending", "abc"),
            (l["sort_menu_newest"], "sort-calendar-ascending", "new"),
            (l["sort_menu_oldest"], "sort-calendar-descending", "old"),
        ]
        self.drop_sort_menu.items = [
            {
                "viewclass": "MyMenuItem",
                "text": text,
                "icon": icon_name,
                "on_release": lambda x=sort_code: self.sort_words(x),
            } for text, icon_name, sort_code in menu_data
        ]

    def open_sort_menu(self, button):
        self.drop_sort_menu.caller = button
        self.drop_sort_menu.open()

    def refresh_localization(self):
        if hasattr(self, 'tool_bar'):
            self.tool_bar.title = self.app.lang["dictionary"]
        self.setup_sort_menu()