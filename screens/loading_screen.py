from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivy.metrics import dp

class LoadingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(name="loading", **kwargs)
        self.layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(40),
            spacing=dp(20),
            adaptive_height=True,
            pos_hint={"center_x": .5, "center_y": .5}
        )
        # Ujednolicamy nazwy z main.py
        self.status_label = MDLabel(
            text="Loading...", 
            halign="center", 
            font_style="H6"
        )
        self.progress_bar = MDProgressBar(
            type="determinate", 
            value=0, 
            max=100,
            size_hint_x=0.8,
            pos_hint={"center_x": .5}
        )
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.progress_bar)
        self.add_widget(self.layout)

    def update_status(self, text, value):
        self.status_label.text = text
        self.progress_bar.value = value