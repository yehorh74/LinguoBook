from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineAvatarIconListItem, MDList, OneLineIconListItem, IconLeftWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.clock import Clock

class SettingsScreen(MDBoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app

        # 1. Toolbar - standardowo
        top_layout = MDBoxLayout(size_hint_y=None, height=dp(40) + dp(24), padding=(0, dp(24), 0, 0))
        tool_bar = MDTopAppBar(
            title="SETTINGS", 
            left_action_items=[["arrow-left", lambda x: self.app.go_back()]]
        )
        top_layout.add_widget(tool_bar)
        self.add_widget(top_layout)

        # 2. Kontener na ustawienia
        self.layout_sett = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.layout_sett.bind(minimum_height=self.layout_sett.setter('height'))

        scroll = MDScrollView(size_hint=(1, 1))
        scroll.add_widget(self.layout_sett)
        self.add_widget(scroll)

        # 3. Kolejka ustawień do załadowania
        # Możesz tu dopisać kolejne pozycje w przyszłości
        self.settings_queue = [
            "model_selection"
        ]

        # Startujemy ładowanie po ułamku sekundy
        Clock.schedule_once(self.load_settings_step, 0.1)

    def load_settings_step(self, dt):
        if not self.settings_queue:
            return False

        setting_type = self.settings_queue.pop(0)

        if setting_type == "model_selection":
            self.btn_model = OneLineAvatarIconListItem(
                text=f"Model: {self.app.selected_model}",
                size_hint_x=0.8,
                pos_hint={"center_x": .5}
            )
            self.btn_model.bind(on_release=self.open_model_popup)
            self.layout_sett.add_widget(self.btn_model)

        # Jeśli masz więcej ustawień, return True sprawi, że załadują się w nast. klatce
        return True

    def open_model_popup(self, *_):
        def choose_model(model_name, *args):
            self.app.selected_model = model_name
            self.app.settings.set_model(model_name)
            self.btn_model.text = f"Model: {model_name}"
            dialog.dismiss()

        models = [
            ("GoogleTranslator", "google"),
            ("LingueeTranslator", "translate"),
            ("PonsTranslator", "book")
        ]

        model_list = MDList(adaptive_height=True)

        for name, icon in models:
            item = OneLineIconListItem(
                text=name,
                on_release=lambda _, n=name: choose_model(n)
            )
            item.add_widget(IconLeftWidget(icon=icon))
            model_list.add_widget(item)

        # Scroll dla wnętrza dialogu
        scroll_dialog = MDScrollView(
            size_hint_y=None,
            height=dp(200), 
        )
        scroll_dialog.add_widget(model_list)

        dialog = MDDialog(
            title="Choose Translation Model",
            type="custom",
            content_cls=scroll_dialog,
        )
        dialog.open()
        