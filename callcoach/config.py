import os

# ElevenLabs
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_DEFAULT_VOICE_ID = os.environ.get("ELEVENLABS_DEFAULT_VOICE_ID", "")

# Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# App
APP_SECRET_KEY = os.environ.get("APP_SECRET_KEY", "callcoach-dev-key")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "callcoach.db")
AUDIO_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "data", "audio")
MAX_CALL_DURATION_MINUTES = 15
DEFAULT_LANGUAGE = "cs"

# Gamification
LEVEL_THRESHOLDS = {
    1: 0,
    2: 200,
    3: 500,
    4: 1000,
    5: 2000,
    6: 4000,
    7: 7000,
    8: 11000,
    9: 16000,
    10: 25000,
}

LEVEL_NAMES = {
    1: "Nováčik",
    2: "Kadet",
    3: "Junior Agent",
    4: "Agent",
    5: "Senior Agent",
    6: "Expert",
    7: "Master",
    8: "Guru",
    9: "Legenda",
    10: "Call Center Jedi",
}

# Evaluation weights
DEFAULT_EVAL_WEIGHTS = {
    "weight_general": 0.35,
    "weight_checkpoints": 0.35,
    "weight_goal": 0.30,
}

# XP rewards
XP_BASE_CALL = 50
XP_PER_POINT_ABOVE_70 = 1
XP_PERFECT_BONUS = 100
XP_FIRST_SCENARIO = 25
XP_DAILY_STREAK = 20

# Categories
CATEGORIES = {
    "SALES": {"label": "Predaj", "color": "#10b981", "icon": "trending_up"},
    "RETENTION": {"label": "Retencia", "color": "#8b5cf6", "icon": "loyalty"},
    "TECH_SUPPORT": {"label": "Tech Support", "color": "#3b82f6", "icon": "support_agent"},
    "COMPLAINTS": {"label": "Reklamácie", "color": "#ef4444", "icon": "sentiment_dissatisfied"},
    "BILLING": {"label": "Fakturácia", "color": "#f59e0b", "icon": "receipt_long"},
    "ONBOARDING": {"label": "Onboarding", "color": "#06b6d4", "icon": "person_add"},
}

MOODS = {
    "CALM": {"label": "Pokojný", "icon": "😊"},
    "FRUSTRATED": {"label": "Frustrovaný", "icon": "😤"},
    "ANGRY": {"label": "Nahnevaný", "icon": "😡"},
    "CONFUSED": {"label": "Zmätený", "icon": "😕"},
    "IMPATIENT": {"label": "Netrpezlivý", "icon": "⏰"},
    "FRIENDLY": {"label": "Priateľský", "icon": "😄"},
}
