class Localization():
    def __init__(self, app):
        self.app = app
        # Słownik mapujący wybraną nazwę języka na funkcję zwracającą teksty
        self.languages = {
            "English": self.english,
            "Українська": self.ukrainian
        }

    def get_text(self):
        """Zwraca słownik UI dla aktualnego języka aplikacji."""
        # Pobieramy nazwę z aplikacji (np. "English")
        lang_name = getattr(self.app, 'selected_language', "English")
        # Wywołujemy odpowiednią funkcję
        return self.languages.get(lang_name, self.english)()
    
    def english(self):
        ui_lang = self.app.selected_language
        theme = self.app.theme_cls.theme_style
        color = self.app.theme_cls.primary_palette
        model = self.app.selected_model
        language = self.app.selected_language
        version = self.app.app_version
        return {
            "language": f"Language: {ui_lang}",
            "choose_lang": "Choose Interface Language",

            "home_screen": "----------------------------",

            "welcome_message": "Welcome to LinguoBook!",
            "recent_book": "Your recent book will appear here.",
            "open_book": "Open Book",
            "continue_book": "Continue",
            "menu": "Menu",
            "book_shelf_menu": "Bookshelf",
            "dictionary_menu": "Dictionary",
            "settings_menu": "Settings",
            "exit_menu": "Exit",

            "reader_screen": "----------------------------",

            "menu": "Menu",
            "home_menu": "Home",
            "book_shelf_menu": "Bookshelf",
            "dictionary_menu": "Dictionary",
            "settings_menu": "Settings",
            "exit_menu": "Exit",
            "page_number": "Page",
            "lang_menu_english": "English",
            "lang_menu_ukrainian": "Ukrainian",
            "lang_menu_polish": "Polish",
            "lang_menu_czech": "Czech",
            "translation_popup_title": "Translation",
            "add_to_dict": "ADD TO DICTIONARY",
            "translating": "Translating...",
            "translation_error": "Translation error",

            "shelf_screen": "----------------------------",

            "book_shelf": "BOOKSHELF",
            "progress": "Progress",
            "sort_menu_AZ": "Sort (A-Z)",
            "sort_menu_newest": "Sort (Newest)",
            "sort_menu_oldest": "Sort (Oldest)",
            "delete_book_menu": "Delete Book",
            "delete_confirm": "Are you sure you want to delete {book_title}?",
            "delete_book_menu_cancel": "CANCEL",
            "delete_book_menu_confirm_button": "DELETE",

            "dictionary_screen": "----------------------------",

            "dictionary": "DICTIONARY",
            "sort_menu_AZ": "Sort (A-Z)",
            "sort_menu_newest": "Sort (Newest)",
            "sort_menu_oldest": "Sort (Oldest)",

            "settings_screen": "----------------------------",

            "settings": "SETTINGS",
            "interface_lable": "INTERFACE",
            "language": f"Language: {language}",
            "theme": f"Theme: {theme}",
            "color": f"Primary Color: {color}",
            "translation_lable": "TRANSLATION",
            "model": f"Model: {model}",
            "advanced_lable": "ADVANCED",
            "open_last_book": "Open last book on start",
            "highlight_new_words": "Highlight selected word",
            "app_info_lable": "APP INFO",
            "app_version": f"App Version: {version}",
            "choose_lang": "Choose Language",
            "choose_theme": "Choose Theme",
            "choose_color": "Choose Primary Color",
            "choose_model": "Translation Model"
        }

    def ukrainian(self):
        ui_lang = "Українська"
        theme = self.app.theme_cls.theme_style
        color = self.app.theme_cls.primary_palette
        model = self.app.selected_model
        language = self.app.selected_language
        version = self.app.app_version
        return {
            "language": f"Мова: {ui_lang}",
            "choose_lang": "Виберіть мову інтерфейсу",

            "home_screen": "----------------------------",

            "welcome_message": "Вітаємо у LinguoBook!",
            "recent_book": "Ваша остання відкрита книжка з'явиться тут.",
            "open_book": "Відкрити Книгу",
            "continue_book": "Продовжити",
            "menu": "Меню",
            "book_shelf_menu": "Бібліотека",
            "dictionary_menu": "Cловник",
            "settings_menu": "Налаштування",
            "exit_menu": "Вихід",

            "reader_screen": "----------------------------",

            "menu": "Меню",
            "home_menu": "Головна",
            "book_shelf_menu": "Бібліотека",
            "dictionary_menu": "Cловник",
            "settings_menu": "Налаштування",
            "exit_menu": "Вихід",
            "page_number": "Сторінка",
            "lang_menu_english": "Англійська",
            "lang_menu_ukrainian": "Українська",
            "lang_menu_polish": "Польська",
            "lang_menu_czech": "Чеська",
            "translation_popup_title": "Переклад",
            "add_to_dict": "ДОДАТИ В СЛОВНИК",
            "translating": "Перекладаємо...",
            "translation_error": "Помилка перекладу",

            "shelf_screen": "----------------------------",

            "book_shelf": "БІБЛІОТЕКА",
            "progress": "Прогрес",
            "sort_menu_AZ": "Сортувати (A-Z)",
            "sort_menu_newest": "Сортувати (Новіші)",
            "sort_menu_oldest": "Сортувати (Старіші)",
            "delete_book_menu": "Видалити Книгу",
            "delete_confirm": "Ви впевнені, що хочете видалити {book_title}?",
            "delete_book_menu_cancel": "СКАСУВАТИ",
            "delete_book_menu_confirm_button": "ВИДАЛИТИ",

            "dictionary_screen": "----------------------------",

            "dictionary": "СЛОВНИК",
            "sort_menu_AZ": "Сортувати (A-Z)",
            "sort_menu_newest": "Сортувати (Новіші)",
            "sort_menu_oldest": "Сортувати (Старіші)",

            "settings_screen": "----------------------------",

            "settings": "НАЛАШТУВАННЯ",
            "interface_lable": "ІНТЕРФЕЙС",
            "language": f"Мова: {language}",
            "theme": f"Тема: {theme}",
            "color": f"Колір: {color}",
            "translation_lable": "ПЕРЕКЛАД",
            "model": f"Модель: {model}",
            "advanced_lable": "ДОДАТКОВО",
            "open_last_book": "Відкрити останню книгу при запуску",
            "highlight_new_words": "Виділити обране слово",
            "app_info_lable": "ІНФОРМАЦІЯ ПРО ДОДАТОК",
            "app_version": f"Версія: {version}", 
            "choose_lang": "Виберіть мову",
            "choose_theme": "Виберіть тему",
            "choose_color": "Виберіть колір",
            "choose_model": "Модель перекладу"
        }