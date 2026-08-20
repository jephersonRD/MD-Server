import json
import os

from core import config

_strings = {}


def load(lang: str = None):
    global _strings
    if not lang:
        lang = config.get_config().get("language", "es")
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locales", f"{lang}.json")
    if not os.path.exists(path):
        lang = "es"
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locales", "es.json")
    with open(path, "r", encoding="utf-8") as f:
        _strings = json.load(f)
    config.set_config("language", lang)
    return lang


def t(key: str, default: str = None) -> str:
    return _strings.get(key, default if default is not None else key)