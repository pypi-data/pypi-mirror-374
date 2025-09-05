import gettext
import os
import configparser

# Verzeichnis, in dem die Übersetzungen liegen
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locales")
DEFAULT_LANG = "de"


def get_translator():
    """
    Liest die Konfigurationsdatei und gibt die korrekte Übersetzer-Funktion zurück.
    """
    config = configparser.ConfigParser()
    language_code = DEFAULT_LANG
    config_path = "config.ini"

    if os.path.exists(config_path):
        config.read(config_path)
        language_code = config.get("Settings", "language", fallback=DEFAULT_LANG)

    try:
        lang = gettext.translation(
            "base", localedir=LOCALE_DIR, languages=[language_code], fallback=True
        )
    except FileNotFoundError:
        # Fallback auf die Standardsprache, wenn die Übersetzungsdatei fehlt
        lang = gettext.translation(
            "base", localedir=LOCALE_DIR, languages=[DEFAULT_LANG], fallback=True
        )

    return lang.gettext


# Die globale Übersetzer-Funktion wird hier einmalig initialisiert
_ = get_translator()


def save_language_setting(language_code):
    """Speichert die ausgewählte Sprache in der Konfigurationsdatei."""
    config = configparser.ConfigParser()
    config["Settings"] = {"language": language_code}
    with open("config.ini", "w") as configfile:
        config.write(configfile)
