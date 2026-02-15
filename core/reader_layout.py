from kivymd.uix.navigationdrawer import (
    MDNavigationLayout,
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerHeader,
    MDNavigationDrawerItem,
)
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from screens.reader import ReaderScreen

class ReaderLayout(MDScreen): 
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        # Pobieramy inicjalny język
        l = self.app.lang

        self.app.theme_cls.bind(theme_style=self.update_drawer_colors)
        
        # 1. Layout nawigacji
        self.nav_layout = MDNavigationLayout()
        
        # 2. Wewnętrzny ScreenManager
        self.internal_sm = MDScreenManager()
        
        # 3. Ekran czytnika (ReaderScreen)
        self.reader_screen = ReaderScreen(app=self.app, name="reader_content")
        self.reader_screen.open_drawer = self.open_drawer 
        self.internal_sm.add_widget(self.reader_screen)

        self.nav_layout.add_widget(self.internal_sm)

        # ===== DEFINICJA ELEMENTÓW DRAWERA JAKO ATRYBUTY =====
        # Dzięki temu refresh_localization() zawsze zadziała
        self.drawer_header = MDNavigationDrawerHeader(text=l["menu"])
        
        self.item_home = MDNavigationDrawerItem(
            icon="home", text=l["home_menu"], 
            on_release=lambda *_: self.go_home()
        )
        self.item_shelf = MDNavigationDrawerItem(
            icon="book", text=l["book_shelf_menu"], 
            on_release=lambda *_: self.go_shelf()
        )
        self.item_dict = MDNavigationDrawerItem(
            icon="translate", text=l["dictionary_menu"], 
            on_release=lambda *_: self.go_dictionary()
        )
        self.item_settings = MDNavigationDrawerItem(
            icon="cog", text=l["settings_menu"], 
            on_release=lambda *_: self.go_settings()
        )
        self.item_exit = MDNavigationDrawerItem(
            icon="exit-to-app", text=l["exit_menu"], 
            on_release=lambda *_: self.app.stop()
        )

        # ===== BUDOWA DRAWERA =====
        self.nav_drawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                self.drawer_header,
                self.item_home,
                self.item_shelf,
                self.item_dict,
                self.item_settings,
                self.item_exit,
            ),
            radius=(0, 16, 16, 0)   
        )

        self.nav_layout.add_widget(self.nav_drawer)
        self.add_widget(self.nav_layout)

    def on_pre_enter(self, *args):
        # 1. Odświeżamy teksty w drawerze
        self.refresh_localization()
        # 2. Wywołujemy on_pre_enter w samym czytniku (toolbar, slider itp.)
        if hasattr(self.reader_screen, "on_pre_enter"):
            self.reader_screen.on_pre_enter()

    def refresh_localization(self):
        """Aktualizuje teksty bezpośrednio przez zapisane atrybuty."""
        # Pobieramy najświeższy słownik z app
        l = self.app.lang 
        
        self.drawer_header.text = l["menu"]
        self.item_home.text = l["home_menu"]
        self.item_shelf.text = l["book_shelf_menu"]
        self.item_dict.text = l["dictionary_menu"]
        self.item_settings.text = l["settings_menu"]
        self.item_exit.text = l["exit_menu"]

    def open_drawer(self, *args):
        self.nav_drawer.set_state("open")
    
    def go_home(self):
        self.nav_drawer.set_state("close")
        self.app.show_home()

    def go_shelf(self):
        self.nav_drawer.set_state("close")
        self.app.open_shelf(source="reader")

    def go_dictionary(self):
        self.nav_drawer.set_state("close")
        self.app.open_dictionary(source="reader")

    def go_settings(self):
        self.nav_drawer.set_state("close")
        self.app.open_settings(source="reader")
    
    def update_drawer_colors(self, *args):
        """Aktualizacja kolorów przy zmianie motywu Dark/Light."""
        self.nav_drawer.md_bg_color = self.app.theme_cls.bg_normal
        
        # Lista elementów do aktualizacji kolorów
        items = [self.item_home, self.item_shelf, self.item_dict, self.item_settings, self.item_exit]
        
        for item in items:
            item.theme_text_color = "Primary"
            if hasattr(item, "icon_color"):
                item.icon_color = self.app.theme_cls.text_color