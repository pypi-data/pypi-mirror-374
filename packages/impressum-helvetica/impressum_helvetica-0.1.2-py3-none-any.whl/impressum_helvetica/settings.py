# Settings for the web capture tool

# Output directory
OUTPUT_DIR = "results"

# Browser settings
BROWSER_TYPE = "chrome"
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# Wait times (in milliseconds)
COOKIE_BANNER_WAIT = 2000
DYNAMIC_CONTENT_WAIT = 1500
COOKIE_CLICK_WAIT = 1000

# Cookie consent keywords
COOKIE_ACCEPT_KEYWORDS = [
    "akzeptieren",     # German
    "akzeptieren alle", # German
    "alles akzeptieren", # German
    "alle akzeptieren", # German
    "allen zustimmen", # German
    "accept",          # English
    "accept all",      # English
    "accept cookies",  # English
    "accepter",        # French
    "accepter tout",   # French
    "ok",              # Common
    "agree",           # English
    "consent",         # English
    "allow all",       # English
    "allow cookies",   # English
    "got it",          # English
    "i understand",    # English
    "continue",        # English
]

# Impressum/Legal notice keywords with priority
IMPRESSUM_KEYWORDS = [
    {"term": "impressum", "prio": 1},        # German - highest priority
    {"term": "legal notice", "prio": 2},    # English
    {"term": "legal", "prio": 2},           # English (short)
    {"term": "mentions légales", "prio": 2},# French
    {"term": "mentions legales", "prio": 2},# French (no accent)
    {"term": "notice légale", "prio": 2},   # French (variant)
    {"term": "notice legale", "prio": 2},   # French (no accent)
    {"term": "kontakt", "prio": 2},        # German
    {"term": "contact", "prio": 2},         # fallback, common legal/contact page
    {"term": "about us", "prio": 3},        # English
]

# File extensions
HTML_EXTENSION = ".html"
PNG_EXTENSION = ".png"

# Subfolder names
HTML_SUBFOLDER = "html"
IMG_SUBFOLDER = "img"

# URL normalization
DEFAULT_PROTOCOL = "https://" 