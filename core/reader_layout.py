from kivymd.uix.navigationdrawer import (
    MDNavigationLayout,
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerHeader,
    MDNavigationDrawerItem,
)
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen

from screens.reader import ReaderScreen


class ReaderLayout(MDNavigationLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        # ===== SCREEN MANAGER =====
        self.sm = ScreenManager()
        screen = MDScreen(name="reader")

        self.reader_screen = ReaderScreen(app=self.app)
        self.reader_screen.open_drawer = self.open_drawer  #hook

        screen.add_widget(self.reader_screen)
        self.sm.add_widget(screen)
        self.add_widget(self.sm)

        # ===== RIGHT DRAWER =====
        self.nav_drawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                MDNavigationDrawerHeader(text="Menu"),

                MDNavigationDrawerItem(
                    icon="home",
                    text="Home",
                    on_release=lambda *_: self.go_home(),
                    text_color=self.theme_cls.text_color,
                ),
                MDNavigationDrawerItem(
                    icon="book",
                    text="Book Shelf",
                    on_release=lambda *_: self.go_shelf(),
                    text_color=self.theme_cls.text_color,
                ),
                MDNavigationDrawerItem(
                    icon="translate",
                    text="Dictionary",
                    on_release=lambda *_: self.go_dictionary(),
                    text_color=self.theme_cls.text_color,
                ),
                MDNavigationDrawerItem(
                    icon="cog",
                    text="Settings",
                    on_release=lambda *_: self.go_settings(),
                    text_color=self.theme_cls.text_color,
                ),
                MDNavigationDrawerItem(
                    icon="exit-to-app",
                    text="Exit",
                    on_release=lambda *_: self.app.stop(),
                    text_color=self.theme_cls.text_color,
                ),
            ),
            radius=(0, 16, 16, 0)   
        )

        self.add_widget(self.nav_drawer)

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
