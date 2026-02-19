from app.locales.en import EN
from app.locales.tl import TL

LOCALES = {
    'en': EN,
    'tl': TL,
}

def get_locale(lang='en'):
    return LOCALES.get(lang, EN)
