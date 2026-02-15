from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineAvatarIconListItem, MDList, OneLineIconListItem, IconLeftWidget, IRightBodyTouch
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.color_definitions import colors

class RightCheckbox(MDCheckbox, IRightBodyTouch):
    '''Checkbox ustawiony po prawej stronie elementu listy.'''

class SettingsScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        self.l = self.app.lang
        self.app.theme_cls.bind(theme_style=self.update_theme_ui)

        # 1. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        theme_icon = "weather-sunny" if self.app.theme_cls.theme_style == "Dark" else "weather-night"
        
        self.tool_bar = MDTopAppBar(
            title=self.l["settings"], 
            anchor_title="left",
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]],
            right_action_items=[[theme_icon, self.switch_theme_logic]]
        )
        top_layout.add_widget(self.tool_bar)
        self.add_widget(top_layout)

        # 2. Kontener
        self.layout_sett = GridLayout(cols=1, size_hint_y=None, spacing=dp(5), padding=[0, 0, 0, dp(20)])
        self.layout_sett.bind(minimum_height=self.layout_sett.setter('height'))
        scroll = MDScrollView(size_hint=(1, 1))
        scroll.add_widget(self.layout_sett)
        self.add_widget(scroll)

        self.settings_queue = ["interface_header", "language_settings", "theme_settings", "translation_header", "model_settings", "advanced_header", "extra_settings", "extra_info", "version_info"]
        Clock.schedule_once(self.load_settings_step, 0.1)

    def on_enter(self, *args):
        self.refresh_localization() # Synchronizacja przy każdym wejściu

    def _create_header(self, text):
        return MDLabel(text=text, font_style="Subtitle2", theme_text_color="Primary", size_hint_y=None, height=dp(40), padding=(dp(20), dp(10)))

    def load_settings_step(self, dt):
        if not self.settings_queue: return False
        step = self.settings_queue.pop(0)
        l = self.app.lang

        if step == "interface_header":
            self.header_interface = self._create_header(l["interface_lable"])
            self.layout_sett.add_widget(self.header_interface)

        elif step == "language_settings":
            self.btn_language = OneLineAvatarIconListItem()
            self.btn_language.bind(on_release=self.open_language_popup)
            self.btn_language.add_widget(IconLeftWidget(icon="earth"))
            self.layout_sett.add_widget(self.btn_language)
        
        elif step == "theme_settings":
            self.btn_theme = OneLineAvatarIconListItem()
            self.btn_theme.bind(on_release=self.open_theme_popup)
            self.btn_theme.add_widget(IconLeftWidget(icon="palette-outline"))
            
            self.btn_palette = OneLineAvatarIconListItem()
            self.btn_palette.bind(on_release=self.open_palette_popup)
            self.btn_palette.add_widget(IconLeftWidget(icon="format-color-fill"))
            
            self.layout_sett.add_widget(self.btn_theme)
            self.layout_sett.add_widget(self.btn_palette)

        elif step == "translation_header":
            self.header_trans = self._create_header(l["translation_lable"])
            self.layout_sett.add_widget(self.header_trans)

        elif step == "model_settings":
            self.btn_model = OneLineAvatarIconListItem()
            self.btn_model.bind(on_release=self.open_model_popup)
            self.btn_model.add_widget(IconLeftWidget(icon="translate"))
            self.layout_sett.add_widget(self.btn_model)

        elif step == "advanced_header":
            self.header_adv = self._create_header(l["advanced_lable"])
            self.layout_sett.add_widget(self.header_adv)

        elif step == "extra_settings":
            self.last_book_item = OneLineAvatarIconListItem(_no_ripple_effect=True)
            self.last_book_check = RightCheckbox(active=self.app.settings.get_open_last_book())
            self.last_book_check.bind(active=lambda cb, v: self.app.settings.set_open_last_book(v))
            self.last_book_item.add_widget(IconLeftWidget(icon="book-clock-outline"))
            self.last_book_item.add_widget(self.last_book_check)
            
            self.highlight_item = OneLineAvatarIconListItem(_no_ripple_effect=True)
            self.highlight_check = RightCheckbox(active=self.app.settings.get_highlight_enabled())
            self.highlight_check.bind(active=self.on_highlight_change)
            self.highlight_item.add_widget(IconLeftWidget(icon="marker"))
            self.highlight_item.add_widget(self.highlight_check)
            
            self.layout_sett.add_widget(self.last_book_item)
            self.layout_sett.add_widget(self.highlight_item)

        elif step == "extra_info":
            self.header_info = self._create_header(l["app_info_lable"])
            self.layout_sett.add_widget(self.header_info)

        elif step == "version_info":
            self.version_label = MDLabel(halign="center", theme_text_color="Hint", font_style="Caption", size_hint_y=None, height=dp(40))
            self.layout_sett.add_widget(self.version_label)

        self.refresh_localization() # Odśwież teksty dla nowo dodanego elementu
        Clock.schedule_once(self.load_settings_step, 0.02)
        return True

    def refresh_localization(self):
        """Pełne odświeżenie tekstów po zmianie języka."""
        l = self.app.lang # Słownik zwrócony przez Localization().get_text()
        
        self.tool_bar.title = l["settings"]
        
        # Nagłówki (Używamy kluczy dokładnie jak w klasie Localization)
        if hasattr(self, 'header_interface'): self.header_interface.text = l["interface_lable"]
        if hasattr(self, 'header_trans'): self.header_trans.text = l["translation_lable"]
        if hasattr(self, 'header_adv'): self.header_adv.text = l["advanced_lable"]
        if hasattr(self, 'header_info'): self.header_info.text = l["app_info_lable"]
        
        # Elementy listy (W klasie Localization f-stringi już zawierają wartości)
        if hasattr(self, 'btn_language'): self.btn_language.text = l["language"]
        if hasattr(self, 'btn_theme'): self.btn_theme.text = l["theme"]
        if hasattr(self, 'btn_palette'): self.btn_palette.text = l["color"]
        if hasattr(self, 'btn_model'): self.btn_model.text = l["model"]
        
        # Opcje zaawansowane
        if hasattr(self, 'last_book_item'): self.last_book_item.text = l["open_last_book"]
        if hasattr(self, 'highlight_item'): self.highlight_item.text = l["highlight_new_words"]
        
        # Info o wersji
        if hasattr(self, 'version_label'): self.version_label.text = l["app_version"]

    def switch_theme_logic(self, *args):
        self.app.theme_cls.theme_style = "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"
        self.app.settings.set_theme(self.app.theme_cls.theme_style)

    def update_theme_ui(self, interval, value):
        new_icon = "weather-sunny" if value == "Dark" else "weather-night"
        self.tool_bar.right_action_items = [[new_icon, self.switch_theme_logic]]
        self.refresh_localization()

    def on_highlight_change(self, checkbox, value):
        if hasattr(self.app, 'settings'):
            self.app.settings.set_highlight_enabled(value)

    # POPUPY z użyciem lokalizacji
    def open_language_popup(self, *_):
        l = self.app.lang
        
        def change_lang(lang_code):
            # To wywołuje Twoją metodę w App, która zmienia self.selected_language
            # i przeładowuje self.lang = self.localization.get_text()
            self.app.update_language(lang_code) 
            dialog.dismiss()
            # Po zmianie języka UI, SettingsScreen sam się odświeży przez on_enter lub bezpośrednie wywołanie
            self.refresh_localization()

        lang_list = MDList()
        # Nazwy języków w popupie wyboru UI powinny być w ich własnych językach
        # żeby np. Ukrainiec zawsze widział napis "Українська"
        langs = [("English", "English"), ("Українська", "Українська"), ("Polski", "Polski"), ("Česky", "Česky")]
        
        for name, code in langs:
            item = OneLineIconListItem(
                text=name, 
                on_release=lambda x, c=code: change_lang(c)
            )
            lang_list.add_widget(item)

        dialog = MDDialog(
            title=l["choose_lang"],
            type="custom",
            content_cls=MDScrollView(lang_list, size_hint_y=None, height=dp(120))
        )
        dialog.open()

    def open_theme_popup(self, *_):
        l = self.app.lang
        def change_theme(theme_name, *args):
            self.app.theme_cls.theme_style = theme_name  
            self.app.settings.set_theme(theme_name)
            self.refresh_localization() # Odświeżamy f-stringi w btn_theme
            dialog.dismiss()

        theme_list = MDList()
        for name, icon in [("Light", "weather-sunny"), ("Dark", "weather-night")]:
            item = OneLineIconListItem(text=name, on_release=lambda _, n=name: change_theme(n))
            item.add_widget(IconLeftWidget(icon=icon))
            theme_list.add_widget(item)
            
        dialog = MDDialog(title=l["choose_theme"], type="custom", content_cls=MDScrollView(theme_list, size_hint_y=None, height=dp(120)))
        dialog.open()

    def open_palette_popup(self, *_):
        l = self.app.lang
        def change_pallete(palette_name):
            clean_name = palette_name.replace(" ", "")
            self.app.theme_cls.primary_palette = clean_name  
            self.app.settings.set_palette(clean_name)
            self.refresh_localization()
            dialog.dismiss()

        palette_list = MDList()
        palettes = ["Gray", "Red", "Pink", "Purple", "Deep Purple", "Indigo", "Blue", "Light Blue", "Cyan", "Teal", "Green", "Light Green", "Lime", "Yellow", "Amber", "Orange", "Deep Orange"]

        for p_name in palettes:
            item = OneLineIconListItem(text=p_name, on_release=lambda x, n=p_name: change_pallete(n))
            item.add_widget(IconLeftWidget(icon="circle", theme_text_color="Custom", text_color=colors[p_name.replace(" ", "")]["500"]))
            palette_list.add_widget(item)

        dialog = MDDialog(title=l["choose_color"], type="custom", content_cls=MDScrollView(palette_list, size_hint_y=None, height=dp(300)))
        dialog.open()

    def open_model_popup(self, *_):
        l = self.app.lang
        def choose_model(model_name, *args):
            self.app.selected_model = model_name
            self.app.settings.set_model(model_name)
            self.refresh_localization()
            dialog.dismiss()

        model_list = MDList()
        for name, icon in [("GoogleTranslator", "google"), ("LingueeTranslator", "translate"), ("PonsTranslator", "book")]:
            item = OneLineIconListItem(text=name, on_release=lambda _, n=name: choose_model(n))
            item.add_widget(IconLeftWidget(icon=icon))
            model_list.add_widget(item)

        # Używamy l["model"] jako tytułu, bo l["model"] w Localization zawiera f-stringa, 
        # ale MDDialog i tak go wyświetli poprawnie.
        dialog = MDDialog(title=l["choose_model"], type="custom", content_cls=MDScrollView(model_list, size_hint_y=None, height=dp(180)))
        dialog.open()

    