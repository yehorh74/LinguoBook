from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import (
    MDNavigationLayout,
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerHeader,
    MDNavigationDrawerItem,
)
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatIconButton
from kivy.metrics import dp


class BaseNavigationDrawerItem(MDNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 24


class DrawerClickableItem(BaseNavigationDrawerItem):
    pass


class HomeScreen(MDNavigationLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        # ===== SCREEN MANAGER (WYMAGANE) =====
        self.screen_manager = ScreenManager()

        home_screen = MDScreen(name="home")

        # ===== CONTENT =====
        content = MDBoxLayout(orientation="vertical")

        tool_bar = MDTopAppBar(
            title="LINGUOBOOK",
            left_action_items=[
                ["menu", lambda *_: self.nav_drawer.set_state("open")]
            ],
            right_action_items=[
                ["help-circle", lambda *_: print("HELP")]
            ]
        )

        content.add_widget(tool_bar)

        middle_section = AnchorLayout(anchor_x="center", anchor_y="center")

        menu_container = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(280),
            spacing=dp(15),
        )
        menu_container.bind(minimum_height=menu_container.setter("height"))

        welcome_label = MDLabel(
            text="Welcome to LinguoBook!",
            halign="center",
            font_style="H4",
            size_hint=(1, None),
            height=dp(100),
        )

        info_lable = MDLabel(
            text = "Your recent book will appear here. " \
            "Use the menu to open a book or use the shelf to add more books to your collection.",
            halign="center",
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(120),
        )

        btn_book = MDRectangleFlatIconButton(
            text="Open Book",
            icon="book-open",
            on_release=lambda *_: self.app.open_file(),
            size_hint_y=None, # Wyłączamy automatyczną wysokość
            height=dp(56),     # Ustawiamy wysokość na standard material design
            size_hint_x=1,
            pos_hint={"center_x": .5}
        )

        recent = self.recent_books()
        
        if recent:
            progress_data = self.app.reader_state.get_book_progress_data(recent["id"])
        
            current_p = progress_data.get("page", 0) # Klucz w Twoim JsonStore to "page" (liczba pojedyncza)
            pages_list = progress_data.get("pages", [])
            total_p = len(pages_list)
            
            calc_value = 0
            if total_p > 0:
                calc_value = min(100, (current_p / total_p) * 100)
                
            # PRZYCISK KONTYNUACJI (tylko jeśli jest co czytać)
            recent_btn = MDRectangleFlatIconButton(
                text=f"Continue: {recent['title']} ({int(calc_value)}%)",
                icon="book-play", # Zmieniłem na play dla odróżnienia
                on_release=lambda *_: self.app.on_shelf_book_clicked(recent),
                size_hint_x=1,
                pos_hint={"center_x": .5},
                height=dp(64) # Nieco większy, żeby był ważniejszy
            )
            menu_container.add_widget(welcome_label)
            menu_container.add_widget(recent_btn)
            
            # Dodajmy napis "LUB" albo po prostu odstęp
            #menu_container.add_widget(MDLabel(text="or", halign="center", theme_text_color="Hint"))
            
        else:
            # Tylko jeśli shelf jest całkiem pusty
            menu_container.add_widget(welcome_label)
            menu_container.add_widget(info_lable)

        # TEN PRZYCISK JEST ZAWSZE (żeby dało się dodać nową książkę bez wchodzenia w menu)
        menu_container.add_widget(btn_book)

        middle_section.add_widget(menu_container)

        content.add_widget(middle_section)
        home_screen.add_widget(content)

        self.screen_manager.add_widget(home_screen)
        self.add_widget(self.screen_manager)

        # ===== NAV DRAWER =====
        self.nav_drawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                MDNavigationDrawerHeader(text="Menu"),

                DrawerClickableItem(
                    icon="book-open",
                    text="Open Book",
                    on_release=lambda *_: self.app.open_file(),
                    text_color=self.theme_cls.text_color,
                ),
                DrawerClickableItem(
                    icon="book",
                    text="Book Shelf",
                    on_release=lambda *_: self.app.open_shelf(),
                    text_color=self.theme_cls.text_color,
                ),
                DrawerClickableItem(
                    icon="translate",
                    text="Dictionary",
                    on_release=lambda *_: self.app.open_dictionary(),
                    text_color=self.theme_cls.text_color,
                ),
                DrawerClickableItem(
                    icon="cog",
                    text="Settings",
                    on_release=lambda *_: self.app.open_settings(),
                    text_color=self.theme_cls.text_color,
                ),
                DrawerClickableItem(
                    icon="exit-to-app",
                    text="Exit",
                    on_release=lambda *_: self.app.stop(),
                    text_color=self.theme_cls.text_color,
                ),
            ),
            radius=(0, 16, 16, 0),
        )

        self.add_widget(self.nav_drawer)

    def recent_books(self):
        # 1. Sprawdźmy ID ostatnio otwartej książki z Managera Stanu
        last_read_id = self.app.reader_state.current_book_id
        all_books = self.app.shelf.get_books()
        
        if not all_books:
            return None

        # 2. Jeśli mamy ID, znajdźmy tę konkretną książkę
        if last_read_id:
            for book in all_books:
                if book["id"] == last_read_id:
                    return book
        
        # 3. Jeśli nie ma ID (np. pierwsze uruchomienie), zwróć ostatnią dodaną
        return all_books[-1]
    
