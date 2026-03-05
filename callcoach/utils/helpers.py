import streamlit as st
from config import CATEGORIES, MOODS, LEVEL_NAMES


def format_duration(seconds):
    if not seconds:
        return "0:00"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def format_score(score):
    if score is None:
        return "—"
    return f"{score:.0f}%"


def score_color(score):
    if score is None:
        return "#9ca3af"
    if score >= 80:
        return "#10b981"
    if score >= 50:
        return "#f59e0b"
    return "#ef4444"


def score_label(score):
    if score is None:
        return "Nehodnotený"
    if score >= 90:
        return "Vynikajúci"
    if score >= 80:
        return "Výborný"
    if score >= 70:
        return "Dobrý"
    if score >= 50:
        return "Priemerný"
    return "Nedostatočný"


def goal_badge(goal):
    badges = {
        "ACHIEVED": ("Dosiahnutý", "#10b981", "check_circle"),
        "PARTIAL": ("Čiastočne", "#f59e0b", "warning"),
        "FAILED": ("Nedosiahnutý", "#ef4444", "cancel"),
    }
    return badges.get(goal, ("Neznámy", "#9ca3af", "help"))


def category_badge_html(category):
    cat = CATEGORIES.get(category, {"label": category, "color": "#6b7280"})
    return f'<span style="background-color: {cat["color"]}15; color: {cat["color"]}; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600;">{cat["label"]}</span>'


def difficulty_stars(difficulty, max_stars=5):
    filled = "★" * difficulty
    empty = "☆" * (max_stars - difficulty)
    return filled + empty


def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined');

        .stApp {
            font-family: 'Inter', sans-serif;
        }

        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }
        .metric-card h3 {
            color: #6b7280;
            font-size: 0.85em;
            font-weight: 500;
            margin: 0 0 8px 0;
        }
        .metric-card .value {
            font-size: 2em;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }
        .metric-card .trend {
            font-size: 0.8em;
            margin-top: 4px;
        }
        .trend-up { color: #10b981; }
        .trend-down { color: #ef4444; }

        .scenario-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 0;
            overflow: hidden;
            transition: box-shadow 0.2s;
            cursor: pointer;
        }
        .scenario-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .scenario-card-header {
            padding: 20px 20px 12px;
        }
        .scenario-card-body {
            padding: 0 20px 20px;
        }

        .achievement-badge {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            min-width: 100px;
        }
        .achievement-badge .icon {
            font-size: 2em;
            margin-bottom: 6px;
        }
        .achievement-badge .name {
            font-size: 0.8em;
            font-weight: 600;
            color: #1e293b;
        }
        .achievement-badge.locked {
            opacity: 0.4;
            filter: grayscale(1);
        }

        .checkpoint-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .checkpoint-item.passed {
            background: #f0fdf4;
            border-left: 3px solid #10b981;
        }
        .checkpoint-item.failed {
            background: #fef2f2;
            border-left: 3px solid #ef4444;
        }

        .sidebar-nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 16px;
            border-radius: 8px;
            text-decoration: none;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 4px;
        }
        .sidebar-nav-item.active {
            background: #137fec15;
            color: #137fec;
        }

        .xp-bar {
            background: #e5e7eb;
            border-radius: 999px;
            height: 8px;
            overflow: hidden;
        }
        .xp-bar-fill {
            background: linear-gradient(90deg, #137fec, #3b82f6);
            height: 100%;
            border-radius: 999px;
            transition: width 0.5s ease;
        }

        .call-timer {
            font-size: 3em;
            font-weight: 700;
            font-family: 'Inter', monospace;
            color: #1e293b;
            letter-spacing: 4px;
        }

        .big-score {
            font-size: 4em;
            font-weight: 800;
            line-height: 1;
        }

        div[data-testid="stSidebar"] {
            background-color: #f8fafc;
        }

        .coaching-tip-box {
            background: linear-gradient(135deg, #137fec, #3b82f6);
            color: white;
            border-radius: 12px;
            padding: 20px;
        }
        .coaching-tip-box h4 {
            color: white;
            margin: 0 0 8px 0;
        }

        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)


def material_icon(name, size=20, color="#6b7280"):
    return f'<span class="material-symbols-outlined" style="font-size:{size}px;color:{color};vertical-align:middle;">{name}</span>'
