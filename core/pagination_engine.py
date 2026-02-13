from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

class PaginationEngine:
    def __init__(self, app, structured_data, on_progress, on_complete):
        self.app = app
        self._elements = structured_data 
        self._element_index = 0
        self._current_page_content = []
        self._pages = []
        
        self.on_progress = on_progress
        self.on_complete = on_complete

        # USTALAMY MARGINESY (np. 20dp z każdej strony)
        side_margin = dp(20)
        
        self._ti = TextInput(
            font_size=dp(18),
            # Padding: [lewo, góra, prawo, dół]
            padding=[side_margin, dp(10), side_margin, dp(10)],
            size_hint=(None, None),
            # Wypełniamy całą szerokość okna
            width=Window.width,
            height=self.app.get_reader_height(),
            readonly=True, 
            multiline=True,
            # Wyłączamy zbędne elementy, by przyspieszyć pomiar
            use_bubble=False,
            use_handles=False,
            cursor_width=0
        )

    def start(self):
        if not self._elements:
            self.on_complete([])
            return
        Clock.schedule_once(self._paginate_step, 0)

    def _format_element(self, element):
        content = element.get('content', '')
        if element.get('type') == 'title':
            return f"\n{content.upper()}\n\n"
        # 4 spacje wcięcia dla akapitu FB2
        return f"    {content}\n"

    def _paginate_step(self, dt):
        MAX_STEPS = 40 
        total = len(self._elements)

        for _ in range(MAX_STEPS):
            if self._element_index >= total:
                if self._current_page_content:
                    self._pages.append("".join(self._current_page_content))
                self.on_complete(self._pages)
                return

            element = self._elements[self._element_index]
            formatted_text = self._format_element(element)
            
            # Pomiar: czy element mieści się na stronie
            self._ti.text = "".join(self._current_page_content) + formatted_text
            self._ti._trigger_refresh_text()

            if self._ti.minimum_height <= self._ti.height:
                self._current_page_content.append(formatted_text)
                self._element_index += 1
            else:
                if self._current_page_content:
                    # Zamykamy stronę, element przechodzi na następną
                    self._pages.append("".join(self._current_page_content))
                    self._current_page_content = []
                else:
                    # Obsługa akapitu dłuższego niż ekran
                    words = formatted_text.split(" ")
                    temp_page_words = []
                    
                    for i, w in enumerate(words):
                        # Sprawdzamy tekst z nowym słowem (dodajemy spację ręcznie)
                        test_str = " ".join(temp_page_words + [w])
                        self._ti.text = test_str
                        self._ti._trigger_refresh_text()
                        
                        if self._ti.minimum_height <= self._ti.height:
                            temp_page_words.append(w)
                        else:
                            # Strona pełna - zapisujemy i resztę słów wracamy do listy elementów
                            self._pages.append(" ".join(temp_page_words))
                            
                            # WAŻNE: Aktualizujemy element w liście, by nie zgubić słów
                            remaining_text = " ".join(words[i:])
                            self._elements[self._element_index] = {
                                'type': element['type'],
                                'content': remaining_text
                            }
                            temp_page_words = []
                            break
                    else:
                        # Jeśli akapit się skończył (pętla for-else)
                        self._current_page_content = [" ".join(temp_page_words)]
                        self._element_index += 1

        if total > 0:
            self.on_progress((self._element_index / total) * 100)
        
        Clock.schedule_once(self._paginate_step, 0.005)