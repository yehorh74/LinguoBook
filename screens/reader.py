from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.slider import Slider

from ui.reader_widgets import ReaderTextInput

class ReaderScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app

        lang_menu = [
            {"text": "English",   "on_release": lambda x="English": self.menu_lang_callback(x)},
            {"text": "Polish",    "on_release": lambda x="Polish": self.menu_lang_callback(x)},
            {"text": "Ukrainian", "on_release": lambda x="Ukrainian": self.menu_lang_callback(x)},
            {"text": "Czech",     "on_release": lambda x="Czech": self.menu_lang_callback(x)},
        ]

        self.drop_lang_menu = MDDropdownMenu(
            caller=None,  # ustawimy później dynamicznie
            items=lang_menu,
            width_mult=4,
        )

        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))

        title = self.app.get_current_book_title()
        tool_bar = MDTopAppBar(title=title, 
                               left_action_items=[["menu", lambda *_: self.open_drawer()]], 
                               right_action_items = [["translate", self.open_lang_menu]]
                                                     )
        top_layout.add_widget(tool_bar)

        self.add_widget(top_layout)

        self.reader_container = MDBoxLayout(orientation='vertical')
        available_height = (
            Window.height
            - dp(40)  # top bar
            - dp(30)  # page label
            - dp(40)  # nav
            - dp(20)  # padding
        )

        pages = self.app.reader_state.pages
        page = self.app.reader_state.current_page

        self.reader = ReaderTextInput(
            text=pages[page] if pages else "",
            font_size=dp(18),
            readonly=True,
            multiline=True,
            size_hint_y=None,
            height=available_height,
            padding=[dp(1), dp(10), dp(10), dp(1)],
        )

        self.reader.reader_screen = self
        
        self.page_label = MDLabel(
            text=f"Page {self.app.reader_state.current_page + 1} / {len(self.app.reader_state.pages)}",
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle"
        )
        self.page_label.bind(size=self.page_label.setter('text_size'))

        nav_layout = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))

        self.slider = Slider(min=1, max=max(len(pages), 1), value=page + 1, size_hint_x=0.7)
        self.slider.bind(value=self.on_slider_value_change)

        nav_layout.add_widget(self.slider)

        self.reader_container.add_widget(self.reader)
        self.reader_container.add_widget(self.page_label)
        self.reader_container.add_widget(nav_layout)

        self.add_widget(self.reader_container)

    def next_page(self):
        if self.app.reader_state.current_page < len(self.app.reader_state.pages) - 1:
            self.app.reader_state.current_page += 1
            self.update_page()

    def prev_page(self):
        if self.app.reader_state.current_page > 0:
            self.app.reader_state.current_page -= 1
            self.update_page()

    def update_page(self):
        current_page = self.app.reader_state.current_page
        self.reader.text = self.app.reader_state.pages[current_page]
        self.page_label.text = f"Page {current_page + 1} / {len(self.app.reader_state.pages)}"
        self.slider.value = current_page + 1
        self.app.reader_state.save_position()

    def on_go_to_page(self, instance):
        try:
            page_num = int(self.page_input.text) - 1
            if 0 <= page_num < len(self.app.reader_state.pages):
                self.app.reader_state.current_page = page_num
                self.update_page()
            else:
                print("Invalid page number")
        except ValueError:
            print("Invalid input: not a number")
    
    def set_language(self, lang_code):
        print(f"Language set to {lang_code}")
        self.app.selected_language = lang_code
        self.app.settings.set_language(lang_code)

    def open_lang_menu(self, button_instance):
        self.drop_lang_menu.caller = button_instance
        self.drop_lang_menu.hor_growth = "left"
        self.drop_lang_menu.open()
    
    def menu_lang_callback(self, text_item):
        self.drop_lang_menu.dismiss()
        if text_item == "English":
            self.set_language("en")
        elif text_item == "Polish":
            self.set_language("pl")
        elif text_item == "Ukrainian":
            self.set_language("uk")
        else:
            self.set_language("cs")
    
    def on_slider_value_change(self, instance, value):
        page_num = int(value) - 1
        if 0 <= page_num < len(self.app.reader_state.pages):
            self.app.reader_state.current_page = page_num
            self.update_page()
    


    



