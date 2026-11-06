import os
import json
import logging
import sys
from localization import translations

class SettingsManager:
    def __init__(self):
        self._defaults = {
            "language": "En",
            "theme": "dark",
            "last_dir": "",
            "first_run": True
        }
        self._settings = self._defaults.copy()
        self._config_dir = self._get_config_dir()
        self._config_file = os.path.join(self._config_dir, "settings.json")
        self.load()

    def _get_config_dir(self):
        if sys.platform == "win32":
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        elif sys.platform == "darwin":
            base = os.path.expanduser('~/Library/Application Support')
        else:
            base = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))

        app_dir = os.path.join(base, "DisplaceBox")
        if not os.path.exists(app_dir):
            try:
                os.makedirs(app_dir)
            except Exception as e:
                logging.error(f"Failed to create config directory: {e}")
        return app_dir

    def load(self):
        if not os.path.exists(self._config_file):
            self.save()
            return

        try:
            with open(self._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, dict):
                    lang = data.get("language")
                    if lang in translations:
                        self._settings["language"] = lang

                    theme = data.get("theme")
                    if theme in ["dark", "light"]:
                        self._settings["theme"] = theme

                    last_dir = data.get("last_dir")
                    if isinstance(last_dir, str) and os.path.isdir(last_dir):
                        self._settings["last_dir"] = last_dir

                    first_run = data.get("first_run")
                    if isinstance(first_run, bool):
                        self._settings["first_run"] = first_run

        except Exception as e:
            logging.error(f"Failed to load settings: {e}. Using defaults.")
            self._settings = self._defaults.copy()

    def save(self):
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value
        self.save()

settings = SettingsManager()