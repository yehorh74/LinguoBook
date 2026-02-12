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
        self.l = self.app.lang
        self.words_to_load = []

        l = self.app.lang

        # 1. Menu Sortowania (Budowane ręcznie)
        self.drop_sort_menu = MDDropdownMenu(width_mult=4)
        self.setup_sort_menu()

        # 2. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        self.tool_bar = MDTopAppBar(
            title=l["dictionary"], 
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]],
            right_action_items=[["sort", self.open_sort_menu]],
            anchor_title="left"
        )
        top_layout.add_widget(self.tool_bar)
        self.add_widget(top_layout)

        # 2. Layout słownika
        self.layout_dict = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.layout_dict.bind(minimum_height=self.layout_dict.setter('height'))

        scroll_view = MDScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.layout_dict)
        self.add_widget(scroll_view)

    def on_enter(self, *args):
        """Wywoływane przez ScreenManager przy każdym wejściu na ekran."""
        # 1. Odśwież tłumaczenia UI
        self.refresh_localization()
        
        # 2. Reszta logiki ładowania słów
        Clock.unschedule(self.load_next_word)
        self.layout_dict.clear_widgets()
        self.start_loading_words()

    def setup_sort_menu(self):
        l = self.app.lang
        # Definiujemy dane menu
        menu_data = [
            (l["sort_menu_AZ"], "sort-alphabetical-ascending", "abc"),
            (l["sort_menu_newest"], "sort-calendar-ascending", "new"),
            (l["sort_menu_oldest"], "sort-calendar-descending", "old"),
        ]
        
        # Tworzymy listę widgetów zamiast czystych słowników
        items = []
        for text, icon_name, sort_code in menu_data:
            items.append({
                "viewclass": "MyMenuItem",
                "text": text,
                "icon": icon_name,
                "on_release": lambda x=sort_code: self.sort_words(x),
            })
        self.drop_sort_menu.items = items

    def open_sort_menu(self, button):
        self.drop_sort_menu.caller = button
        self.drop_sort_menu.open()

    def on_enter(self, *args):
        """Metoda wywoływana przez ScreenManager przy każdym wejściu na ekran."""
        # Zatrzymaj poprzednie ładowanie, jeśli jeszcze trwało
        Clock.unschedule(self.load_next_word)
        
        # Wyczyść aktualne widgety
        self.layout_dict.clear_widgets()
        
        # Pobierz świeże dane i zacznij ładowanie
        self.start_loading_words()

    def start_loading_words(self, *args):
        # Pobieramy najnowsze słowa z managera słownika
        self.words_to_load = list(self.app.dictionary.get_all().items())
        # Sortujemy od najnowszych (dodać w drop menu)
        #self.words_to_load.reverse() 
        
        Clock.schedule_interval(self.load_next_word, 0)

    def load_next_word(self, dt):
        if not self.words_to_load:
            return False

        key, value = self.words_to_load.pop(0)
        
        list_word = OneLineAvatarIconListItem(
            text=f"{key} : {value['translation']}",
            _no_ripple_effect=True,
            size_hint_x=0.9,
            pos_hint={"center_x": .5}
        )

        trash = IconRightWidget(
            icon="trash-can",
            on_release=lambda btn, k=key, lw=list_word: self.delete_word(k, lw)
        )

        word_icon = IconLeftWidgetWithoutTouch(icon="translate")
        list_word.add_widget(word_icon)
        list_word.add_widget(trash)
        
        self.layout_dict.add_widget(list_word)
        return True

    def delete_word(self, key, list_word):
        self.app.dictionary.delete(key)
        if list_word.parent:
            list_word.parent.remove_widget(list_word)
 
    def sort_words(self, sort_type):
        self.drop_sort_menu.dismiss()
        Clock.unschedule(self.load_next_word)
        self.layout_dict.clear_widgets()
        
        # Najpierw pobierz listę
        self.words_to_load = list(self.app.dictionary.get_all().items())
        
        # Potem posortuj
        if sort_type == "abc":
            self.words_to_load.sort(key=lambda x: x[0].lower())
        elif sort_type == "new":
            self.words_to_load.reverse()
        # "old" zostaje tak jak jest w bazie
        
        # Na końcu zacznij wyświetlać
        Clock.schedule_interval(self.load_next_word, 0)
        
    def refresh_localization(self):
        """Aktualizuje teksty interfejsu po zmianie języka."""
        l = self.app.lang
        
        # 1. Aktualizacja tytułu Toolbaru
        if hasattr(self, 'tool_bar'):
            self.tool_bar.title = l["dictionary"]
            
        # 2. Przebudowanie menu sortowania (aby zmienić napisy A-Z, Najnowsze itp.)
        self.setup_sort_menu()
        
    
        

    
    
    
