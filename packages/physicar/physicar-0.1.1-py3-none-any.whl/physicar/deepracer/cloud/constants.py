

CAR_NAME="PHYSICAR"

import os
DATA_PATH=os.path.abspath(os.path.expanduser(f"~/.physicar-deepracer-for-cloud/"))
CONFIG_PATH=os.path.join(DATA_PATH, "config.yml")
JOB_PATH=os.path.join(DATA_PATH, "job.pkl")
CONFIG_LOCK_PATH=os.path.join(DATA_PATH, "config.locked.yml")
REWARD_FUNCTION_PATH=os.path.join(DATA_PATH, "reward_function.py")
TRACK_PATH=os.path.join(DATA_PATH, "tracks")
TRACK_INFO_PATH=os.path.join(TRACK_PATH, "tracks_info.yml")
PARAMS_LOGS_PATH=os.path.join(DATA_PATH, "params_logs")
MODEL_PATH=os.path.join(DATA_PATH, "bucket/models")
IMAGE_PATH=os.path.join(DATA_PATH, "images")
DRFC_PATH=os.path.join(DATA_PATH, "deepracer-for-cloud")
DATA_URL="https://pub-9df64302e0d948ef8abaf49a17f2cbe3.r2.dev"


import pytz
DEFAULT_TIMEZONE = "UTC"
SUPPORTED_TIMEZONES = pytz.all_timezones

DEFAULT_LANG = "en"
SUPPORTED_LANGUAGES = {
  "en": "English",
  "ko": "한국어",
  "it": "Italiano",
  "nl": "Nederlands",
  "de": "Deutsch",
  "pt": "Português",
  "es": "Español",
  "fr": "Français",
  "hi": "हिन्दी",
  "vi": "Tiếng Việt",
  "ja": "日本語",
  "pl": "Polski",
  "ru": "Русский",
  "th": "ไทย",
  "tr": "Türkçe",
  "zh-hans": "简体中文",
  "zh-hant": "繁體中文",
  "id": "Bahasa Indonesia",
  "ar": "العربية",
  # "af": "Afrikaans",
  # "ar-dz": "العربية (الجزائر)",
  # "ast": "Asturianu",
  # "az": "Azərbaycanca",
  # "bg": "Български",
  # "be": "Беларуская",
  # "bn": "বাংলা",
  # "br": "Brezhoneg",
  # "bs": "Bosanski",
  # "ca": "Català",
  # "ckb": "کوردیی ناوەندی",
  # "cs": "Čeština",
  # "cy": "Cymraeg",
  # "da": "Dansk",
  # "dsb": "Dolnoserbšćina",
  # "el": "Ελληνικά",
  # "en-au": "Australian English",
  # "en-gb": "British English",
  # "eo": "Esperanto",
  # "es-ar": "Español de Argentina",
  # "es-co": "Español de Colombia",
  # "es-mx": "Español de México",
  # "es-ni": "Español de Nicaragua",
  # "es-ve": "Español de Venezuela",
  # "et": "Eesti",
  # "eu": "Euskara",
  # "fa": "فارسی",
  # "fi": "Suomi",
  # "fy": "Frysk",
  # "ga": "Gaeilge",
  # "gd": "Gàidhlig",
  # "gl": "Galego",
  # "he": "עברית",
  # "hr": "Hrvatski",
  # "hsb": "Hornjoserbšćina",
  # "hu": "Magyar",
  # "hy": "Հայերեն",
  # "ia": "Interlingua",
  # "ig": "Igbo",
  # "io": "Ido",
  # "is": "Íslenska",
  # "ka": "ქართული",
  # "kab": "Taqbaylit",
  # "kk": "Қазақ тілі",
  # "km": "ភាសាខ្មែរ",
  # "kn": "ಕನ್ನಡ",
  # "ky": "Кыргызча",
  # "lb": "Lëtzebuergesch",
  # "lt": "Lietuvių",
  # "lv": "Latviešu",
  # "mk": "Македонски",
  # "ml": "മലയാളം",
  # "mn": "Монгол",
  # "mr": "मराठी",
  # "ms": "Bahasa Melayu",
  # "my": "မြန်မာဘာသာ",
  # "nb": "Norsk bokmål",
  # "ne": "नेपाली",
  # "nn": "Norsk nynorsk",
  # "os": "Ирон",
  # "pa": "ਪੰਜਾਬੀ",
  # "pt-br": "Português do Brasil",
  # "ro": "Română",
  # "sk": "Slovenčina",
  # "sl": "Slovenščina",
  # "sq": "Shqip",
  # "sr": "Српски",
  # "sr-latn": "Srpski (latinica)",
  # "sv": "Svenska",
  # "sw": "Kiswahili",
  # "ta": "தமிழ்",
  # "te": "తెలుగు",
  # "tg": "Тоҷикӣ",
  # "tk": "Türkmençe",
  # "tt": "Татарча",
  # "udm": "Удмурт",
  # "uk": "Українська",
  # "ur": "اردو",
  # "uz": "O'zbek"
}
