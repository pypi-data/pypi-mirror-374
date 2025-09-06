"""
Core API for AI Text Humanizer (English & Persian)
"""
from app.app import AcademicTextHumanizer
from app.fa_hazm import PersianHazmHumanizer
from app.fa_stanza import PersianStanzaHumanizer
from app.fa_combo import PersianComboHumanizer

def get_humanizer(language="en", engine="default"):
    if language == "en":
        return AcademicTextHumanizer()
    elif language == "fa":
        if engine == "hazm":
            return PersianHazmHumanizer()
        elif engine == "stanza":
            return PersianStanzaHumanizer()
        elif engine == "combo":
            return PersianComboHumanizer()
        else:
            return PersianComboHumanizer()
    else:
        raise ValueError("Unsupported language")

def humanize_text(text, language="en", engine="default", **kwargs):
    humanizer = get_humanizer(language, engine)
    return humanizer.humanize_text(text, **kwargs)
