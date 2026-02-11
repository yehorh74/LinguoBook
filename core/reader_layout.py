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

        self.app.theme_cls.bind(theme_style=self.update_drawer_colors)
        
        # 1. Tworzymy layout nawigacji
        self.nav_layout = MDNavigationLayout()
        
        # 2. Tworzymy wewnętrzny ScreenManager (wymagany przez MDNavigationLayout)
        self.internal_sm = MDScreenManager()
        
        # 3. Tworzymy ekran czytnika i dodajemy go do wewnętrznego managera
        self.reader_screen = ReaderScreen(app=self.app, name="reader_content")
        self.reader_screen.open_drawer = self.open_drawer 
        self.internal_sm.add_widget(self.reader_screen)

        # 4. Dodajemy wewnętrzny manager do layoutu nawigacji
        self.nav_layout.add_widget(self.internal_sm)

        # ===== RIGHT DRAWER =====
        self.nav_drawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                MDNavigationDrawerHeader(text="Menu"),
                MDNavigationDrawerItem(
                    icon="home",
                    text="Home",
                    theme_text_color="Primary", 
                    on_release=lambda *_: self.go_home(),
                ),
                MDNavigationDrawerItem(
                    icon="book",
                    text="Book Shelf",
                    theme_text_color="Primary",  
                    on_release=lambda *_: self.go_shelf(),
                ),
                MDNavigationDrawerItem(
                    icon="translate",
                    text="Dictionary",
                    theme_text_color="Primary", 
                    on_release=lambda *_: self.go_dictionary(),
                ),
                MDNavigationDrawerItem(
                    icon="cog",
                    text="Settings",
                    theme_text_color="Primary", 
                    on_release=lambda *_: self.go_settings(),
                ),
                MDNavigationDrawerItem(
                    icon="exit-to-app",
                    text="Exit",
                    theme_text_color="Primary", 
                    on_release=lambda *_: self.app.stop(),
                ),
            ),
            radius=(0, 16, 16, 0)   
        )

        # 5. Dodajemy drawer do layoutu nawigacji
        self.nav_layout.add_widget(self.nav_drawer)
        
        # 6. Dodajemy cały layout nawigacji do tego ekranu (ReaderLayout)
        self.add_widget(self.nav_layout)

    def on_pre_enter(self, *args):
        if hasattr(self.reader_screen, "on_pre_enter"):
            self.reader_screen.on_pre_enter()

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
        """Wywoływane automatycznie przy zmianie motywu."""
        self.nav_drawer.md_bg_color = self.app.theme_cls.bg_normal

        try:
            menu = self.nav_drawer.children[0] 
            for item in menu.children:
                if isinstance(item, (MDNavigationDrawerItem, MDNavigationDrawerHeader)):
                    # Ustawienie theme_text_color na Primary zazwyczaj 
                    # automatycznie naprawia też kolor ikony w KivyMD
                    item.theme_text_color = "Primary"
                    
                    # Jeśli chcesz mieć pewność co do koloru ikony, 
                    # użyj icon_color zamiast theme_icon_color
                    if hasattr(item, "icon_color"):
                        # Pobieramy kolor tekstu odpowiedni dla obecnego motywu
                        item.icon_color = self.app.theme_cls.text_color
        except Exception as e:
            print(f"Błąd aktualizacji kolorów drawera: {e}")
