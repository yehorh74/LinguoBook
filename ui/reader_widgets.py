from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App
from deep_translator import GoogleTranslator, LingueeTranslator, PonsTranslator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget

PONS_LANG_MAP = {
            "en": "english",
            "de": "german",
            "pl": "polish",
            "fr": "french",
            "es": "spanish",
            "cs": "czech",
            "uk": "ukrainian"
        }

class ReaderTextInput(TextInput):
    swipe_x_threshold = dp(80)
    popup_open = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # === TRYB CZYTNIKA ===
        self.readonly = True
        self.multiline = True

        # kursor logiczny (niewidoczny)
        self.cursor_blink = False
        self.allow_selection = True
        self.selection_color = (0, 0, 0, 0)

        # brak menu systemowego
        self.use_bubble = False
        self.use_handles = False

    # 🚫 blokada menu „Select / Copy / Paste”
    def show_cut_copy_paste(self, *args):
        return

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        self._start_x = touch.x
        self._start_y = touch.y

        # 🔑 POZWALAMY TextInput ustawić kursor
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if not hasattr(self, "_start_x"):
            return super().on_touch_up(touch)

        dx = touch.x - self._start_x
        dy = touch.y - self._start_y

        del self._start_x
        del self._start_y

        if abs(dx) > self.swipe_x_threshold and abs(dx) > abs(dy):
            self.cancel_selection()
            if hasattr(self, 'reader_screen') and self.reader_screen:
                if dx < 0:
                    self.reader_screen.next_page()
                else:
                    self.reader_screen.prev_page()
            return True

        super().on_touch_up(touch)

        if self.popup_open:
            return True

        idx = self.cursor_index(self.cursor)
        text = self.text or ""

        if not (0 < idx <= len(text)):
            return True

        # 🔑 KOREKTA: kliknięcie na spacji / za literą
        if idx < len(text) and not text[idx].isalpha():
            idx -= 1

        if idx < 0 or not text[idx].isalpha():
            return True

        # wycinanie całego słowa
        s = e = idx
        while s > 0 and text[s - 1].isalpha():
            s -= 1
        while e < len(text) and text[e].isalpha():
            e += 1

        word = text[s:e]
        if word:
            self.show_word_popup(word)

        self.cancel_selection()
        return True

    def translate_word(self, word):
        app = App.get_running_app()
        target_lang = getattr(app, "selected_language", "en")
        model = getattr(app, "selected_model", "GoogleTranslator")

        try:
            if model == "GoogleTranslator":
                return GoogleTranslator(source="auto", target=target_lang).translate(word)

            elif model == "PonsTranslator":
                target_lang = PONS_LANG_MAP.get(target_lang)
                return PonsTranslator(source="en", target=target_lang).translate(word)

            elif model == "LingueeTranslator":
                target_lang = PONS_LANG_MAP.get(target_lang)
                return LingueeTranslator(source="english", target=target_lang).translate(word)

        except Exception as e:
            print(f"Translation error: {e}")
            return "[Translation error]"

    def show_word_popup(self, word):
        if self.popup_open:
            return

        self.popup_open = True
        app = App.get_running_app()
        translated_word = self.translate_word(word)

        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(16),
            padding=(dp(16), dp(16), dp(16), dp(8)),
        )

        content.add_widget(
            MDLabel(
                text=word,
                font_style="H6",
                halign="center",
                size_hint_y=None,
                height=dp(32),
            )
        )

        content.add_widget(
            MDLabel(
                text=translated_word,
                font_style="Body1",
                halign="center",
                size_hint_y=None,
                height=dp(28),
            )
        )

        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(12),
            padding=(0, 0, 0, 0),
        )

        btn_add = MDRaisedButton(
            text="ADD TO DICTIONARY",
            on_release=lambda *_: (
                app.dictionary.add(word, translated_word),
                self.dialog.dismiss()
            )
        )

        buttons_layout.add_widget(Widget()) 
        buttons_layout.add_widget(btn_add)

        content.add_widget(buttons_layout)

        self.dialog = MDDialog(
            title="Translation",
            type="custom",
            content_cls=content,
            auto_dismiss=True,
        )

        self.dialog.bind(
            on_dismiss=lambda *_: setattr(self, "popup_open", False)
        )

        self.dialog.open()
