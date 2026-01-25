import os
from babel.support import Translations
from fastapi import Request

# Where translations are stored
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locales")

def get_locale(request: Request) -> str:
    # 1. Query Param
    lang = request.query_params.get("lang")
    if lang in ["en", "es", "hi", "mr", "sa"]:
        return lang

    # 2. Cookie (Could implement later)

    # 3. Headers
    # accept_language = request.headers.get("accept-language")
    # if accept_language:
    #     # Simple parsing for demo
    #     if "es" in accept_language:
    #         return "es"

    return "en" # Default

def get_translations(locale: str):
    translations = Translations.load(LOCALE_DIR, [locale])
    return translations

def install_i18n(app):
    """
    This is where we might hook into middleware if we wanted global request context,
    but for Jinja2 we handle it in main.py by adding the function to env.
    """
    pass
