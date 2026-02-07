from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, IconLeftWidgetWithoutTouch
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.clock import Clock

class DictionaryScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', spacing=10, **kwargs)
        self.app = app

        # 1. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        tool_bar = MDTopAppBar(
            title="DICTIONARY", 
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]],
            anchor_title="center"
        )
        top_layout.add_widget(tool_bar)
        self.add_widget(top_layout)

        # 2. Tworzymy layout słownika
        self.layout_dict = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        self.layout_dict.bind(minimum_height=self.layout_dict.setter('height'))

        scroll_view = MDScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.layout_dict)
        self.add_widget(scroll_view)

        # 3. KLUCZ: Ładujemy dane etapami, żeby nie zamulić animacji
        Clock.schedule_once(self.start_loading_words, 0.2)

    def start_loading_words(self, *args):
        self.words_to_load = list(self.app.dictionary.get_all().items())
        # Odpalamy generator - dodaje 1 słowo co klatkę
        Clock.schedule_interval(self.load_next_word, 0)

    def load_next_word(self, dt):
        if not self.words_to_load:
            return False # Kończymy cykl Clock

        key, value = self.words_to_load.pop(0)
        
        # Tworzymy Twój sprawdzony element listy
        list_word = OneLineAvatarIconListItem(
            text=f"{key} : {value['translation']}",
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
        return True # Kontynuuj ładowanie kolejnego słowa

    def delete_word(self, key, list_word):
        self.app.dictionary.delete(key)
        if list_word.parent:
            list_word.parent.remove_widget(list_word)