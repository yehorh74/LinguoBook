from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.slider import Slider
from kivymd.uix.screen import MDScreen
from kivy.animation import Animation

from ui.reader_widgets import ReaderTextInput

class ReaderScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.l = self.app.lang
        self.target_lang = self.app.reader_state.target_lang 
        self.setup_ui()

    def on_pre_enter(self, *args):
        """Metoda Kivy wywoływana automatycznie przed wejściem na ekran."""
        self.refresh_localization()
        self.on_enter_screen()
        # Aktualizacja tytułu książki na toolbarze przy każdym wejściu
        self.tool_bar.title = self.app.get_current_book_title()

    def setup_ui(self):
        # Główny kontener ekranu
        main_layout = MDBoxLayout(orientation='vertical')

        l = self.app.lang

        self.drop_lang_menu = MDDropdownMenu(
            width_mult=4,
        )

        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))

        title = self.app.get_current_book_title()
        theme_icon = "weather-sunny" if self.app.theme_cls.theme_style == "Dark" else "weather-night"
        self.app.theme_cls.bind(theme_style=self.update_theme_ui)

        self.tool_bar = MDTopAppBar(
            title=title,
            anchor_title="left", 
            left_action_items=[["menu", lambda *_: self.open_drawer()]], 
            right_action_items = [["translate", self.open_lang_menu],
                                  [theme_icon, self.switch_theme_logic]]
        )
        top_layout.add_widget(self.tool_bar)
        main_layout.add_widget(top_layout)

        self.reader_container = MDBoxLayout(orientation='vertical')

        pages = self.app.reader_state.pages
        page = self.app.reader_state.current_page

        side_margin = dp(20)

        self.reader = ReaderTextInput(
            self.app,
            text=pages[page] if pages else "",
            font_size=dp(18),
            readonly=True,
            multiline=True,
            size_hint_y=1,  
            padding=[side_margin, dp(10), side_margin, dp(10)],
            background_color=self.theme_mode_background_color(),
            foreground_color=self.theme_mode_text_color()
        )

        self.reader.reader_screen = self
        
        self.page_label = MDLabel(
            text=f"{l['page_number']} {page + 1} / {len(pages)}" if pages else f"{l['page_number']} 0 / 0",
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

        main_layout.add_widget(self.reader_container)
        self.add_widget(main_layout)

    def switch_theme_logic(self, *args):
        # Ta metoda teraz TYLKO zmienia stan globalny
        self.app.theme_cls.theme_style = (
            "Dark" if self.app.theme_cls.theme_style == "Light" else "Light"
        )
        self.app.settings.set_theme(self.app.theme_cls.theme_style)

    def update_theme_ui(self, interval, value):
        """Wywoływane automatycznie przy każdej zmianie motywu."""
        new_icon = "weather-sunny" if value == "Dark" else "weather-night"
        
        # Kluczowe: Nadpisujemy całą listę, aby KivyMD przerysowało ikonki
        self.tool_bar.right_action_items = [
            ["translate", self.open_lang_menu],
            [new_icon, self.switch_theme_logic]
        ]
        
        # Aktualizacja kolorów czytnika (TextInput)
        if hasattr(self, 'reader'):
            self.reader.background_color = self.theme_mode_background_color()
            self.reader.foreground_color = self.theme_mode_text_color()

    def next_page(self):
        if self.app.reader_state.current_page < len(self.app.reader_state.pages) - 1:
            # 1. Animujemy wyjazd starej strony w lewo
            anim = Animation(x=-Window.width, opacity=0, duration=0.15, t='in_quad')
            
            def change_text(*args):
                self.app.reader_state.current_page += 1
                self.update_page()
                # Ustawiamy tekst poza ekranem z prawej strony
                self.reader.x = Window.width
                # 2. Animujemy wjazd nowej strony do centrum
                final_anim = Animation(x=0, opacity=1, duration=0.15, t='out_quad')
                final_anim.start(self.reader)

            anim.bind(on_complete=change_text)
            anim.start(self.reader)

    def prev_page(self):
        if self.app.reader_state.current_page > 0:
            # Animujemy wyjazd w prawo
            anim = Animation(x=Window.width, opacity=0, duration=0.15, t='in_quad')
            
            def change_text(*args):
                self.app.reader_state.current_page -= 1
                self.update_page()
                self.reader.x = -Window.width
                final_anim = Animation(x=0, opacity=1, duration=0.15, t='out_quad')
                final_anim.start(self.reader)

            anim.bind(on_complete=change_text)
            anim.start(self.reader)

    def update_page(self):
        l = self.app.lang
        current_page = self.app.reader_state.current_page
        self.reader.text = self.app.reader_state.pages[current_page]
        self.page_label.text = f"{l['page_number']} {current_page + 1} / {len(self.app.reader_state.pages)}"
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

    def on_enter_screen(self):
        l = self.app.lang
        pages = self.app.reader_state.pages
        page = self.app.reader_state.current_page

        if pages and page < len(pages):
            self.reader.text = pages[page]
            self.reader._trigger_refresh_text()
            self.page_label.text = f"{l['page_number']} {page + 1} / {len(pages)}"
            self.slider.max = len(pages)
            self.slider.value = page + 1
            self.reader.background_color = self.theme_mode_background_color()
            self.reader.foreground_color = self.theme_mode_text_color()

    def set_language(self, lang_code):
        self.app.selected_language = lang_code
        self.app.settings.set_language(lang_code)
        self.app.lang = self.app.localization.get_text()
        self.refresh_localization()

    def open_lang_menu(self, button_instance):
        # Najpierw aktualizujemy kolory elementów
        self.update_lang_menu_items()
        
        # Potem otwieramy
        self.drop_lang_menu.caller = button_instance
        self.drop_lang_menu.hor_growth = "left"
        self.drop_lang_menu.open()

    def menu_lang_callback(self, lang_code):
        """Zmienia język docelowy tłumaczenia i fizycznie zapisuje go w JSON."""
        self.drop_lang_menu.dismiss()
        
        # 1. Zapisujemy do stanu aplikacji (żeby translator wiedział co robić)
        self.app.reader_state.target_lang = lang_code 
        
        # 2. ZAPISUJEMY do pliku JSON przez Twój manager
        if hasattr(self.app, 'settings'):
            self.app.settings.set_target_lang(lang_code) 
        
        # 3. Odświeżamy menu, żeby "kropka" (podświetlenie) się przesunęła
        self.update_lang_menu_items()
    
    def on_slider_value_change(self, instance, value):
        page_num = int(value) - 1
        if 0 <= page_num < len(self.app.reader_state.pages):
            self.app.reader_state.current_page = page_num
            self.update_page()
    
    def theme_mode_background_color(self):
        if self.app.theme_cls.theme_style == "Dark":
            return [0.1, 0.1, 0.1, 1]
        else:
            return [1, 1, 1, 1]
        
    def theme_mode_text_color(self):
        if self.app.theme_cls.theme_style == "Dark":
            return [1, 1, 1, 1]
        else:
            return [0, 0, 0, 1]
    
    def update_lang_menu_items(self):
        """Generuje listę języków tłumaczenia z poprawnymi kodami ISO."""
        l = self.app.lang
        primary_color = self.app.theme_cls.primary_color
        # Kolor tła dla zaznaczonego elementu
        selected_bg = [primary_color[0], primary_color[1], primary_color[2], 0.3]
        
        # Mapowanie: (Nazwa z lokalizacji, Kod ISO do translatora i JSONa)
        languages = [
            (l["lang_menu_english"], "en"),
            (l["lang_menu_polish"], "pl"),
            (l["lang_menu_ukrainian"], "uk"),
            (l["lang_menu_czech"], "cs"),
        ]
        
        menu_items = []
        # Pobieramy aktualny kod z zapisu (jeśli nie ma, to 'en')
        current_target = self.app.settings.get_target_lang()

        for text, code in languages:
            is_selected = (current_target == code)
            menu_items.append({
                "text": text,
                "viewclass": "OneLineListItem",
                "bg_color": selected_bg if is_selected else [0, 0, 0, 0],
                # Tutaj lambda x=code zapewnia, że do callbacka trafi "pl", "en" itd.
                "on_release": lambda x=code: self.menu_lang_callback(x),
            })
        
        self.drop_lang_menu.items = menu_items

    def refresh_localization(self):
        """Aktualizuje wszystkie teksty na ekranie czytnika."""
        l = self.app.lang # Pobierz już zaktualizowany słownik
        
        # 1. Aktualizacja paska narzędzi (tytuł książki może mieć prefiks w przyszłości)
        self.tool_bar.title = self.app.get_current_book_title()
        
        # 2. Aktualizacja numeracji stron
        pages = self.app.reader_state.pages
        page = self.app.reader_state.current_page
        if pages:
            self.page_label.text = f"{l['page_number']} {page + 1} / {len(pages)}"
        else:
            self.page_label.text = f"{l['page_number']} 0 / 0"
            
        # 3. Aktualizacja widgetu ReaderTextInput (dla popupów tłumaczeń)
        if hasattr(self, 'reader'):
            self.reader.refresh_localization()
            
        # 4. Przeładowanie menu wyboru języka (żeby nazwy języków się zmieniły)
        self.update_lang_menu_items()