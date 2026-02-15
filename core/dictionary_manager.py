from kivy.storage.jsonstore import JsonStore
import os

class DictionaryManager:
    def __init__(self, filename="dictionary.json"):
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, "..", "data")
        os.makedirs(data_dir, exist_ok=True)

        self.store = JsonStore(os.path.join(data_dir, filename))

        if not self.store.exists("words"):
            self.store.put("words", data={})

    def get_all(self):
        return self.store.get("words")["data"]

    def add(self, word, translation):
        data = self.get_all()
        data[word] = {"translation": translation}
        self.store.put("words", data=data)

    def delete(self, word):
        data = self.get_all()
        if word in data:
            del data[word]
            self.store.put("words", data=data)
