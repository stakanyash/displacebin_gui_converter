class LanguageManager:
    _current_language = "En"
    
    @classmethod
    def set_language(cls, lang_code: str):
        cls._current_language = lang_code
    
    @classmethod
    def get_language(cls):
        return cls._current_language