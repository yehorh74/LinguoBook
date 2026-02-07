import os
from kivy.storage.jsonstore import JsonStore


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