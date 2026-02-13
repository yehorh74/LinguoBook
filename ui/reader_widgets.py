from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App
from deep_translator import GoogleTranslator, LingueeTranslator, PonsTranslator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.widget import Widget
from kivy.clock import Clock
import threading
from kivymd.uix.spinner import MDSpinner

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

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.l = self.app.lang

        # === TRYB CZYTNIKA ===
        self.readonly = True
        self.multiline = True

        # kursor logiczny (niewidoczny)
        self.cursor_blink = False
        self.allow_selection = True
        self.selection_color = (0.2, 0.5, 0.8, 0.5)

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

        # 1. LOGIKA SWIPE (zmiana strony)
        if abs(dx) > self.swipe_x_threshold and abs(dx) > abs(dy):
            self.cancel_selection()
            if hasattr(self, 'reader_screen') and self.reader_screen:
                if dx < 0: self.reader_screen.next_page()
                else: self.reader_screen.prev_page()
            del self._start_x
            del self._start_y
            return True

        # 2. BAZA (pozwól Kivy ustawić kursor na końcu dotyku)
        res = super().on_touch_up(touch)

        # 3. FILTR: Czy to był Tap, czy Swipe?
        # Jeśli palec przesunął się o więcej niż np. 20dp, to nie tłumaczymy
        is_accidental_move = abs(dx) > dp(20) or abs(dy) > dp(20)
        
        if self.popup_open or is_accidental_move:
            self.cancel_selection() # Sprzątamy ewentualne niechciane zaznaczenie
            if hasattr(self, "_start_x"):
                del self._start_x
                del self._start_y
            return res

        # 4. LOGIKA TŁUMACZENIA (tylko dla czystego Tapnięcia)
        idx = self.cursor_index(self.cursor)
        text = self.text or ""

        # Znajdowanie granic słowa 
        if idx < len(text) and not text[idx].isalpha():
            idx -= 1
        if idx < 0 or not text[idx].isalpha():
            return res

        s = e = idx
        while s > 0 and text[s - 1].isalpha(): s -= 1
        while e < len(text) and text[e].isalpha(): e += 1

        word = text[s:e]
        if word:
            app = App.get_running_app()
            if app.settings.get_highlight_enabled(): 
                Clock.schedule_once(lambda dt: self.select_text(s, e), 0)
            self.show_word_popup(word)

        if hasattr(self, "_start_x"):
            del self._start_x
            del self._start_y
        return res
    
    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos) or not hasattr(self, "_start_x"):
            return super().on_touch_move(touch)

        dx = touch.x - self._start_x
        # Jeśli przesunięcie jest większe niż mały margines błędu (np. 10dp),
        # traktujemy to jako początek gestu i czyścimy zaznaczenie systemowe
        if abs(dx) > dp(10):
            self.cancel_selection()
        
        return super().on_touch_move(touch)

    def translate_word(self, word):
        app = App.get_running_app()
        
        # FIX: Pobieramy KOD języka (np. "uk"), a nie NAZWĘ ("Українська")
        target_lang = app.reader_state.target_lang
        
        # Zabezpieczenie, gdyby target_lang był pusty
        if not target_lang:
            target_lang = "en"
            
        model = getattr(app, "selected_model", "GoogleTranslator")
        l = self.app.lang

        try:
            if model == "GoogleTranslator":
                # GoogleTranslator przyjmuje kody typu "uk", "pl", "en"
                return GoogleTranslator(source="auto", target=target_lang).translate(word)

            elif model == "PonsTranslator":
                # PONS wymaga pełniejszych nazw z Twojego PONS_LANG_MAP
                pons_lang = PONS_LANG_MAP.get(target_lang, "english")
                return PonsTranslator(source="en", target=pons_lang).translate(word)

            elif model == "LingueeTranslator":
                # Linguee również potrzebuje mapowania z kodów na nazwy
                linguee_lang = PONS_LANG_MAP.get(target_lang, "english")
                return LingueeTranslator(source="english", target=linguee_lang).translate(word)

        except Exception as e:
            print(f"Translation error: {e}")
            # Zwracamy błąd z lokalizacji interfejsu
            return l.get("translation_error", "Error")

    def show_word_popup(self, word):
        if self.popup_open:
            return
        self.popup_open = True

        l = self.app.lang

        # 1. Tworzymy kontener z kółkiem ładowania
        self.popup_content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(16),
            padding=(dp(16), dp(16), dp(16), dp(16)),
        )

        self.word_label = MDLabel(
            text=word, font_style="H6", halign="center",
            size_hint_y=None, height=dp(32)
        )
        
        # Kółko ładowania
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'center_x': .5},
            active=True
        )

        self.translation_label = MDLabel(
            text=l["translating"], font_style="Body1", halign="center",
            theme_text_color="Hint", size_hint_y=None, height=dp(28)
        )

        self.popup_content.add_widget(self.word_label)
        self.popup_content.add_widget(self.spinner)
        self.popup_content.add_widget(self.translation_label)

        # 2. Tworzymy i otwieramy Dialog
        self.dialog = MDDialog(
            title=l["translation_popup_title"],
            type="custom",
            content_cls=self.popup_content,
            auto_dismiss=True,
        )
        self.dialog.bind(on_dismiss=lambda *_: self._on_dialog_dismiss())
        self.dialog.open()

        # 3. URUCHAMIAMY TŁUMACZENIE W TLE (Wątek)
        threading.Thread(target=self._async_translate, args=(word,), daemon=True).start()

    def _async_translate(self, word):
        # Ta metoda działa w tle
        translated_text = self.translate_word(word)
        # Po zakończeniu wracamy do głównego wątku Kivy, aby zaktualizować UI
        Clock.schedule_once(lambda dt: self._update_popup_with_translation(translated_text, word))

    def _update_popup_with_translation(self, translated_text, word):
        # Sprawdzamy, czy popup nie został zamknięty zanim przyszło tłumaczenie
        if not self.popup_open:
            return

        l = self.app.lang

        # Usuwamy spinner i zmieniamy tekst
        self.popup_content.remove_widget(self.spinner)
        self.translation_label.text = translated_text
        self.translation_label.theme_text_color = "Primary"

        # Dodajemy przycisk (teraz, gdy mamy już tłumaczenie)
        app = App.get_running_app()
        btn_add = MDRaisedButton(
            text=l["add_to_dict"],
            pos_hint={'center_x': .5},
            on_release=lambda *_: (
                app.dictionary.add(word, translated_text),
                self.dialog.dismiss()
            )
        )
        self.popup_content.add_widget(btn_add)

    def _on_dialog_dismiss(self):
        self.popup_open = False
        # Odznaczamy tekst, gdy użytkownik zamknie okno
        self.cancel_selection()
    
    def refresh_localization(self):
        """Aktualizuje lokalne odniesienie do języka."""
        self.l = self.app.lang