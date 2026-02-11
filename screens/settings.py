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
from kivymd.color_definitions import colors # Import dla kolorowych ikon

class RightCheckbox(MDCheckbox, IRightBodyTouch):
    '''Checkbox ustawiony po prawej stronie elementu listy.'''

class SettingsScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app

        self.app.theme_cls.bind(theme_style=self.update_theme_ui)

        # 1. Toolbar
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        theme_icon = "weather-sunny" if self.app.theme_cls.theme_style == "Dark" else "weather-night"
        
        self.tool_bar = MDTopAppBar(  # Dodano self.
            title="SETTINGS", 
            anchor_title="left",
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]],
            right_action_items=[[theme_icon, self.switch_theme_logic]]
        )
        top_layout.add_widget(self.tool_bar)
        self.add_widget(top_layout)

        # 2. Kontener na ustawienia
        self.layout_sett = GridLayout(cols=1, size_hint_y=None, spacing=dp(5), padding=[0, 0, 0, dp(20)])
        self.layout_sett.bind(minimum_height=self.layout_sett.setter('height'))

        scroll = MDScrollView(size_hint=(1, 1))
        scroll.add_widget(self.layout_sett)
        self.add_widget(scroll)

        # 3. Kolejka ładowania - podzielona na sekcje logiczne
        self.settings_queue = ["interface_header", "theme_settings", "translation_header", "model_settings", "advanced_header", "extra_settings", "extra_info", "version_info"]

        Clock.schedule_once(self.load_settings_step, 0.1)

    # --- DODANA SYNCHRONIZACJA ---
    def on_enter(self, *args):
        """Aktualizuje widok na podstawie aktualnego stanu managera przy wejściu na ekran."""
        if hasattr(self, 'btn_theme'):
            self.btn_theme.text = f"Theme: {self.app.theme_cls.theme_style}"
        if hasattr(self, 'btn_palette'):
            self.btn_palette.text = f"Primary Color: {self.app.theme_cls.primary_palette}"
        if hasattr(self, 'btn_model'):
            self.btn_model.text = f"Model: {self.app.selected_model}"
        if hasattr(self, 'last_book_check'):
            self.last_book_check.active = self.app.settings.get_open_last_book()
        if hasattr(self, 'highlight_check'):
            self.highlight_check.active = self.app.settings.get_highlight_enabled()

    def _create_header(self, text):
        """Pomocnicza metoda do tworzenia stylowych nagłówków sekcji."""
        return MDLabel(
            text=text,
            font_style="Subtitle2",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40),
            padding=(dp(20), dp(10))
        )

    def load_settings_step(self, dt):
        if not self.settings_queue:
            return False

        step = self.settings_queue.pop(0)

        # --- SEKCIJA: INTERFEJS ---
        if step == "interface_header":
            self.layout_sett.add_widget(self._create_header("INTERFACE"))
        
        elif step == "theme_settings":
            self.btn_theme = OneLineAvatarIconListItem(
                text=f"Theme: {self.app.theme_cls.theme_style}",
                size_hint_x=0.9, pos_hint={"center_x": .5}
            )
            self.btn_theme.bind(on_release=self.open_theme_popup)
            self.btn_theme.add_widget(IconLeftWidget(icon="palette-outline"))

            self.btn_palette = OneLineAvatarIconListItem(
                text=f"Primary Color: {self.app.theme_cls.primary_palette}",
                size_hint_x=0.9, pos_hint={"center_x": .5}
            )
            self.btn_palette.bind(on_release=self.open_palette_popup)
            self.btn_palette.add_widget(IconLeftWidget(icon="format-color-fill"))

            self.layout_sett.add_widget(self.btn_theme)
            self.layout_sett.add_widget(self.btn_palette)

        # --- SEKCJA: TŁUMACZENIE ---
        elif step == "translation_header":
            self.layout_sett.add_widget(self._create_header("TRANSLATION"))

        elif step == "model_settings":
            self.btn_model = OneLineAvatarIconListItem(
                text=f"Model: {self.app.selected_model}",
                size_hint_x=0.9, pos_hint={"center_x": .5}
            )
            self.btn_model.bind(on_release=self.open_model_popup)
            self.btn_model.add_widget(IconLeftWidget(icon="translate"))
            self.layout_sett.add_widget(self.btn_model)

        # --- SEKCJA: ZAAWANSOWANE ---
        elif step == "advanced_header":
            self.layout_sett.add_widget(self._create_header("ADVANCED"))

        elif step == "extra_settings":
            # 1. Ostatnia książka
            item_last = OneLineAvatarIconListItem(
                text="Open last book on start",
                _no_ripple_effect=True, 
                size_hint_x=0.9, pos_hint={"center_x": .5}
            )
            self.last_book_check = RightCheckbox(
                active=self.app.settings.get_open_last_book()
            )
            self.last_book_check.bind(active=lambda cb, val: self.app.settings.set_open_last_book(val))
            item_last.add_widget(IconLeftWidget(icon="book-clock-outline"))
            item_last.add_widget(self.last_book_check)
            self.layout_sett.add_widget(item_last)

            # 2. Podświetlanie słowa
            item_highlight = OneLineAvatarIconListItem(
                text="Highlight selected word",
                _no_ripple_effect=True,
                size_hint_x=0.9, pos_hint={"center_x": .5}
            )
            self.highlight_check = RightCheckbox(
                active=self.app.settings.get_highlight_enabled()
            )
            self.highlight_check.bind(active=self.on_highlight_change)
            item_highlight.add_widget(IconLeftWidget(icon="marker"))
            item_highlight.add_widget(self.highlight_check)
            self.layout_sett.add_widget(item_highlight)
        
        # --- SEKCJA: INFO ---
        elif step == "extra_info":
            self.layout_sett.add_widget(self._create_header("APP INFO"))

        elif step == "version_info":
            version_label = MDLabel(
                text="App Version 1.3.0",
                halign="center",          # Wyśrodkowanie w poziomie
                theme_text_color="Hint",   # Subtelny, szary kolor
                font_style="Caption",      # Mniejsza czcionka
                size_hint_y=None,
                height=dp(80),             # Wysokość pola (daje margines od dołu)
                valign="center"
            )
            self.layout_sett.add_widget(version_label)

        # Planujemy kolejny krok
        Clock.schedule_once(self.load_settings_step, 0.05)
        return True

    def on_highlight_change(self, checkbox, value):
        self.app.settings.set_highlight_enabled(value)

    # --- POPUPY ---
    def open_palette_popup(self, *_):
        def change_pallete(palette_name):
            # Usuwamy spacje dla nazw takich jak "Deep Purple" -> "DeepPurple"
            clean_name = palette_name.replace(" ", "")
            self.app.theme_cls.primary_palette = clean_name  
            self.app.settings.set_palette(clean_name)
            if hasattr(self, 'btn_palette'):
                self.btn_palette.text = f"Primary Color: {palette_name}" 
            dialog.dismiss()

        palettes = [
            ("Gray", "Gray"), ("Red", "Red"), ("Pink", "Pink"), ("Purple", "Purple"),
            ("Deep Purple", "DeepPurple"), ("Indigo", "Indigo"), ("Blue", "Blue"),
            ("Light Blue", "LightBlue"), ("Cyan", "Cyan"), ("Teal", "Teal"),
            ("Green", "Green"), ("Light Green", "LightGreen"), ("Lime", "Lime"),
            ("Yellow", "Yellow"), ("Amber", "Amber"), ("Orange", "Orange"),
            ("Deep Orange", "DeepOrange")
        ]

        palette_list = MDList()
        for display_name, internal_name in palettes:
            # Używamy n=display_name, aby zapisać wartość w domknięciu (closure)
            item = OneLineIconListItem(
                text=display_name, 
                on_release=lambda x, n=display_name: change_pallete(n)
            )
            
            icon_color = colors[internal_name]["500"]
            item.add_widget(IconLeftWidget(
                icon="circle", 
                theme_text_color="Custom", 
                text_color=icon_color
            ))
            palette_list.add_widget(item)

        scroll_dialog = MDScrollView(size_hint_y=None, height=dp(300))
        scroll_dialog.add_widget(palette_list)
        dialog = MDDialog(
            title="Choose Primary Color",
            type="custom",
            content_cls=scroll_dialog,
            auto_dismiss=True
        )
        dialog.open()

    def open_theme_popup(self, *_):
        def change_theme(theme_name, *args):
            self.app.theme_cls.theme_style = theme_name  
            self.app.settings.set_theme(theme_name)
            self.btn_theme.text = f"Theme: {theme_name}" 
            dialog.dismiss()

        theme_list = MDList()
        for name, icon in [("Light", "weather-sunny"), ("Dark", "weather-night")]:
            item = OneLineIconListItem(text=name, on_release=lambda _, n=name: change_theme(n))
            item.add_widget(IconLeftWidget(icon=icon))
            theme_list.add_widget(item)
            
        scroll_dialog = MDScrollView(size_hint_y=None, height=dp(120))
        scroll_dialog.add_widget(theme_list)
        dialog = MDDialog(title="Choose Theme", type="custom", content_cls=scroll_dialog)
        dialog.open()

    def open_model_popup(self, *_):
        def choose_model(model_name, *args):
            self.app.selected_model = model_name
            self.app.settings.set_model(model_name)
            self.btn_model.text = f"Model: {model_name}"
            dialog.dismiss()

        model_list = MDList()
        for name, icon in [("GoogleTranslator", "google"), ("LingueeTranslator", "translate"), ("PonsTranslator", "book")]:
            item = OneLineIconListItem(text=name, on_release=lambda _, n=name: choose_model(n))
            item.add_widget(IconLeftWidget(icon=icon))
            model_list.add_widget(item)

        scroll_dialog = MDScrollView(size_hint_y=None, height=dp(180))
        scroll_dialog.add_widget(model_list)
        dialog = MDDialog(title="Translation Model", type="custom", content_cls=scroll_dialog)
        dialog.open()
    
    def switch_theme_logic(self, *args):
        # Tylko zmiana globalna
        self.app.theme_cls.theme_style = (
            "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"
        )
        self.app.settings.set_theme(self.app.theme_cls.theme_style)

    def update_theme_ui(self, interval, value):
        """Aktualizuje ikonkę toolbaru i tekst na liście."""
        new_icon = "weather-sunny" if value == "Dark" else "weather-night"
        
        # Odświeżenie ikony toolbaru
        self.tool_bar.right_action_items = [[new_icon, self.switch_theme_logic]]
        
        # Odświeżenie tekstu w OneLineAvatarIconListItem
        if hasattr(self, 'btn_theme'):
            self.btn_theme.text = f"Theme: {value}"
    
    def on_highlight_change(self, checkbox, value):
        # Dodane zabezpieczenie, by nie wywoływać zapisu przed załadowaniem aplikacji
        if hasattr(self.app, 'settings'):
            self.app.settings.set_highlight_enabled(value)
