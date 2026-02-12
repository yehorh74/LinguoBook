import os
from kivy.storage.jsonstore import JsonStore
from localization.localization import Localization


class SettingsManager:
    def __init__(self, filename="settings.json"):
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, "..", "data")
        os.makedirs(data_dir, exist_ok=True)

        self.store = JsonStore(os.path.join(data_dir, filename))

    # ===== LANGUAGE =====
    def get_language(self):
        if self.store.exists("language"):
            return self.store.get("language").get("selected", "en")
        return "en"  

    def set_language(self, lang_code):
        self.store.put("language", selected=lang_code)

    def get_model(self):
        if self.store.exists("model"):
            return self.store.get("model").get("selected", "GoogleTranslator")
        return "GoogleTranslator"
    
    def set_model(self, model_code):
        self.store.put("model", selected=model_code)

    def get_theme(self):
        if self.store.exists("theme"):
            return self.store.get("theme").get("selected", "Light")
        return "Light"
    
    def set_theme(self, theme_name):
        self.store.put("theme", selected=theme_name)

    def get_palette(self):
        if self.store.exists("palette"):
            return self.store.get("palette").get("selected", "Gray")
        return "Gray"
    
    def set_palette(self, palette_name):
        self.store.put("palette", selected=palette_name)

    def get_open_last_book(self):
        if self.store.exists("open_last_book"):
            return self.store.get("open_last_book").get("active", False)
        return False

    def set_open_last_book(self, value):
        self.store.put("open_last_book", active=value)

    # === HIGHLIGHT ===
    def get_highlight_enabled(self):
        # Sprawdzamy czy klucz istnieje w JsonStore
        if self.store.exists("highlight_settings"):
            return self.store.get("highlight_settings").get("enabled", True)
        return True # Domyślnie włączone

    def set_highlight_enabled(self, value):
        # Zapisujemy do JsonStore (metoda put automatycznie zapisuje plik)
        self.store.put("highlight_settings", enabled=value)

    def set_localization(self, lang_data):
        self.store.put("localization", selected=lang_data)

    def get_localization(self):
        if self.store.exists("localization"):
            return self.store.get("localization").get("selected", "English")
        return "English"  # Domyślnie angielski
    
    # Dodaj to do klasy SettingsManager w Twoim pliku
    def get_target_lang(self):
        if self.store.exists("target_translation_lang"):
            return self.store.get("target_translation_lang").get("selected", "en")
        return "en"

    def set_target_lang(self, lang_code):
        # JsonStore automatycznie zapisze to do pliku .json
        self.store.put("target_translation_lang", selected=lang_code)
    

