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
from kivy.clock import Clock


class BaseNavigationDrawerItem(MDNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 24


class DrawerClickableItem(MDNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 24
        self.update_theme_colors()

    def update_theme_colors(self):
        # Ustawiamy kolory tak, by reagowały na Light/Dark
        # 'Primary' w KivyMD automatycznie zmienia się między białym a czarnym
        self.theme_text_color = "Primary"
        self.theme_icon_color = "Primary"


class HomeScreen(MDNavigationLayout):
    def __init__(self, app, **kwargs):
        super().__init__(kwargs)
        self.app = app
        self.l = self.app.lang

        self.app.theme_cls.bind(theme_style=self.update_theme_ui)

        # 1. GŁÓWNA STRUKTURA
        self.screen_manager = ScreenManager()
        home_screen = MDScreen(name="home")
        
        content = MDBoxLayout(orientation="vertical")

        # Toolbar
        tool_bar = MDTopAppBar(
            title="LINGUOBOOK",
            left_action_items=[["menu", lambda *_: self.nav_drawer.set_state("open")]],
            right_action_items=[["help-circle", lambda *_: print("HELP")]]
        )
        content.add_widget(tool_bar)

        self.middle_section = AnchorLayout(anchor_x="center", anchor_y="center")
        content.add_widget(self.middle_section)
        
        home_screen.add_widget(content)
        self.screen_manager.add_widget(home_screen)
        self.add_widget(self.screen_manager)

        # 2. NAV DRAWER
        self.setup_nav_drawer()

        Clock.schedule_once(lambda dt: self.refresh_menu(), 0.1)

    def on_enter(self, *args):
        self.refresh_localization() # To teraz załatwia i drawer, i środkowe menu

    def update_theme_ui(self, interval, value):
        """
        Wywoływane automatycznie przy zmianie motywu. 
        Wymusza odświeżenie kolorów w drawerze.
        """
        # Odświeżamy kolory tekstu i ikon w menu
        # KivyMD DrawerItem automatycznie korzysta z theme_cls, 
        # ale czasem trzeba wymusić przerysowanie płótna (canvas)
        if hasattr(self, 'nav_drawer'):
            # Wymuszenie aktualizacji tła drawera (jeśli nie reaguje)
            self.nav_drawer.md_bg_color = self.app.theme_cls.bg_normal
            
            # Jeśli używasz niestandardowych kolorów w DrawerClickableItem,
            # tutaj możesz je zaktualizować w pętli:
            for item in self.nav_drawer.children[0].children: # Dostęp do MDNavigationDrawerMenu
                if hasattr(item, 'update_theme_colors'):
                    item.update_theme_colors()

        # Odświeżamy też środkową sekcję (przyciski)
        self.refresh_menu()

    def setup_nav_drawer(self):
        l = self.app.lang
        def nav_to(method):
            self.nav_drawer.set_state("close")
            method()

        # Tworzymy nagłówek i elementy jako atrybuty, by móc je odświeżyć
        self.drawer_header = MDNavigationDrawerHeader(text=l["menu"])
        self.drawer_item_open = DrawerClickableItem(icon="book-open", text=l["open_book"], on_release=lambda *_: nav_to(self.app.open_file))
        self.drawer_item_shelf = DrawerClickableItem(icon="book", text=l["book_shelf_menu"], on_release=lambda *_: nav_to(self.app.open_shelf))
        self.drawer_item_dict = DrawerClickableItem(icon="translate", text=l["dictionary_menu"], on_release=lambda *_: nav_to(self.app.open_dictionary))
        self.drawer_item_settings = DrawerClickableItem(icon="cog", text=l["settings_menu"], on_release=lambda *_: nav_to(self.app.open_settings))
        self.drawer_item_exit = DrawerClickableItem(icon="exit-to-app", text=l["exit_menu"], on_release=lambda *_: self.app.stop())

        self.nav_drawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                self.drawer_header,
                self.drawer_item_open,
                self.drawer_item_shelf,
                self.drawer_item_dict,
                self.drawer_item_settings,
                self.drawer_item_exit,
            ),
            radius=(0, 16, 16, 0),
        )
        self.add_widget(self.nav_drawer)

    def on_enter(self, *args):
        self.refresh_menu()

    def refresh_menu(self):
        l = self.app.lang
        """Buduje menu dynamicznie"""
        self.middle_section.clear_widgets()

        menu_container = MDBoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(300), # Nieco szerszy dla lepszego wyglądu
            spacing=dp(15),
            adaptive_height=True,
            pos_hint={"center_x": .5} # Centrowanie kontenera
        )

        recent = self.recent_books()

        # Nagłówek
        welcome_label = MDLabel(
            text=l["welcome_message"],
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=dp(100),
        )
        menu_container.add_widget(welcome_label)

        if recent:
            progress_data = self.app.reader_state.get_book_progress_data(recent["id"])
            current_p = progress_data.get("page", 0)
            total_p = len(progress_data.get("pages", []))
            calc_value = (current_p / total_p * 100) if total_p > 0 else 0
                
            recent_btn = MDRectangleFlatIconButton(
                text=f"{l['continue_book']}: {recent['title']} ({int(calc_value)}%)",
                icon="book-play",
                on_release=lambda *_: self.app.on_shelf_book_clicked(recent),
                size_hint_x=None,
                width=dp(280),
                pos_hint={"center_x": .5}, # WYCENTROWANIE
                height=dp(64)
            )
            menu_container.add_widget(recent_btn)
        else:
            info_label = MDLabel(
                text=l["recent_book"],
                halign="center",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(80),
            )
            menu_container.add_widget(info_label)

        # Przycisk "Open Book" - WYCENTROWANY
        btn_book = MDRectangleFlatIconButton(
            text=l["open_book"],
            icon="book-open",
            on_release=lambda *_: self.app.open_file(),
            size_hint_x=None,
            width=dp(200),             # Stała szerokość dla ładnego wyglądu
            pos_hint={"center_x": .5}, # KLUCZ DO CENTROWANIA
            height=dp(56)
        )
        menu_container.add_widget(btn_book)

        self.middle_section.add_widget(menu_container)

    def recent_books(self):
        # ... (Twoja niezmieniona logika)
        try:
            last_read_id = self.app.reader_state.current_book_id
            all_books = self.app.shelf.get_books()
            if not all_books: return None
            if last_read_id:
                for book in all_books:
                    if book["id"] == last_read_id: return book
            return all_books[-1]
        except Exception:
            return None
        
    def refresh_localization(self):
        l = self.app.lang  # Pobierz świeże tłumaczenia
        
        # 1. Odśwież Nav Drawer (jeśli atrybuty istnieją)
        if hasattr(self, 'drawer_header'):
            self.drawer_header.text = l["menu"]
            self.drawer_item_open.text = l["open_book"]
            self.drawer_item_shelf.text = l["book_shelf_menu"]
            self.drawer_item_dict.text = l["dictionary_menu"]
            self.drawer_item_settings.text = l["settings_menu"]
            self.drawer_item_exit.text = l["exit_menu"]

        # 2. Odśwież dynamiczne menu na środku (Welcome, Continue itp.)
        self.refresh_menu()