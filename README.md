# LinguoBook
Inteligent book reader app with translation feature for smartphones, built in Python using Kivy, KivyMD UI. 
Key features:
  Word Translation: You can translate any chosen word with GoogleTranslator, Linguee, Pons and save them in a dictionary (for now only english, polish, czech, ukrainian languages suport).
  Integrated Language Learning: Features a built-in DictionaryManager that allows for instant word lookups without breaking the reading flow.
  Smart Pagination Engine: A custom asynchronous pagination algorithm that dynamically calculates page layouts based on device screen metrics, ensuring a consistent reading experience.
  Advanced Library Management: A robust ShelfManager that handles book imports (FB2 format), tracks reading progress per title, and organizes your personal collection.

Tech Stack:
  Core: Python 3.11+
  UI Framework: Kivy & KivyMD (Material Design components)
  Data Handling: JSON-based state management for lightweight and fast persistence.
  Platform Support: Designed for Android
