import streamlit as st
from config import CATEGORIES, MOODS, LEVEL_NAMES


def format_duration(seconds):
    if not seconds:
        return "0:00"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}m {secs:02d}s"


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


def score_color_css(score):
    if score is None:
        return "clr-muted"
    if score >= 90:
        return "score-green"
    if score >= 80:
        return "score-green"
    if score >= 60:
        return "score-amber"
    return "score-red"


def score_label(score):
    if score is None:
        return "Nehodnoceno"
    if score >= 90:
        return "Vynikající"
    if score >= 80:
        return "Výborný"
    if score >= 70:
        return "Dobrý"
    if score >= 50:
        return "Průměrný"
    return "Nedostatečný"


def goal_badge(goal):
    badges = {
        "ACHIEVED": ("Splněno", "#10b981", "check_circle"),
        "PARTIAL": ("Částečně", "#f59e0b", "warning"),
        "FAILED": ("Nesplněno", "#ef4444", "cancel"),
    }
    return badges.get(goal, ("Neznámý", "#9ca3af", "help"))


def category_badge_html(category):
    cat = CATEGORIES.get(category, {"label": category, "color": "#6b7280"})
    return f'<span class="cc-cat-badge" style="--cat-color:{cat["color"]};">{cat["label"]}</span>'


def difficulty_stars_html(difficulty, max_stars=5):
    html = '<span class="cc-stars">'
    for i in range(max_stars):
        if i < difficulty:
            html += '<span class="material-symbols-outlined filled">star</span>'
        else:
            html += '<span class="material-symbols-outlined empty">star</span>'
    html += '</span>'
    return html


def difficulty_stars(difficulty, max_stars=5):
    filled = "★" * difficulty
    empty = "☆" * (max_stars - difficulty)
    return filled + empty


def inject_custom_css():
    dark = st.session_state.get("dark_mode", True)
    mode = "dark" if dark else "light"

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet"/>

    <style>
    :root {{
        --bg: {('#101922' if dark else '#f6f7f8')};
        --bg-card: {('#15212c' if dark else '#ffffff')};
        --bg-sidebar: {('#15212c' if dark else '#ffffff')};
        --bg-input: {('#101922' if dark else '#ffffff')};
        --bg-hover: {('#1a2d36' if dark else '#f1f5f9')};
        --bg-table-head: {('rgba(30,41,59,0.5)' if dark else '#f8fafc')};
        --border: {('#1e293b' if dark else '#e2e8f0')};
        --border-light: {('#334155' if dark else '#f1f5f9')};
        --text: {('#f1f5f9' if dark else '#0f172a')};
        --text-secondary: {('#94a3b8' if dark else '#64748b')};
        --text-muted: {('#64748b' if dark else '#94a3b8')};
        --primary: #137fec;
        --primary-10: {('rgba(19,127,236,0.2)' if dark else 'rgba(19,127,236,0.1)')};
        --primary-hover: #1070d0;
        --emerald: #10b981;
        --amber: #f59e0b;
        --red: #ef4444;
        --purple: #8b5cf6;
        --shadow: {('0 1px 3px rgba(0,0,0,0.3)' if dark else '0 1px 3px rgba(0,0,0,0.08)')};
    }}

    .stApp {{
        font-family: 'Inter', sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }}

    .stApp > header {{
        background-color: var(--bg-card) !important;
        border-bottom: 1px solid var(--border);
    }}

    /* Sidebar */
    div[data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border) !important;
    }}
    div[data-testid="stSidebar"] * {{
        color: var(--text) !important;
    }}
    div[data-testid="stSidebar"] .stButton > button {{
        background-color: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        text-align: left !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.9em !important;
    }}
    div[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: var(--bg-hover) !important;
    }}
    div[data-testid="stSidebar"] hr {{
        border-color: var(--border) !important;
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s !important;
    }}
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {{
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(19,127,236,0.2) !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {{
        background-color: var(--primary-hover) !important;
    }}

    /* Cards */
    .cc-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        box-shadow: var(--shadow);
    }}

    /* Metric cards - from Stitch agent_training_dashboard */
    .cc-metric {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow);
    }}
    .cc-metric .bg-icon {{
        position: absolute;
        right: -16px;
        top: -16px;
        font-size: 100px !important;
        color: {('rgba(30,41,59,0.5)' if dark else 'rgba(241,245,249,1)')};
    }}
    .cc-metric .label {{
        color: var(--text-secondary);
        font-size: 0.85em;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }}
    .cc-metric .value {{
        font-size: 2em;
        font-weight: 700;
        color: var(--text);
        position: relative;
        z-index: 1;
        margin-top: 4px;
    }}
    .cc-metric .trend {{
        display: inline-flex;
        align-items: center;
        gap: 2px;
        font-size: 0.85em;
        font-weight: 500;
        margin-top: 4px;
        position: relative;
        z-index: 1;
    }}
    .cc-metric .trend.up {{ color: var(--emerald); }}
    .cc-metric .trend.down {{ color: var(--red); }}

    /* Scenario cards - from Stitch scenario_library_browser */
    .cc-scenario-card {{
        display: flex;
        flex-direction: column;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--bg-card);
        overflow: hidden;
        transition: box-shadow 0.2s;
    }}
    .cc-scenario-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }}
    .cc-scenario-card .card-header {{
        height: 160px;
        position: relative;
        display: flex;
        align-items: flex-start;
        padding: 12px;
    }}
    .cc-scenario-card .card-header .cat-badge {{
        background: rgba(0,0,0,0.5);
        backdrop-filter: blur(8px);
        color: white;
        font-size: 0.75em;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }}
    .cc-scenario-card .card-header .dur-badge {{
        position: absolute;
        top: 12px;
        right: 12px;
        background: {'rgba(26,38,50,0.9)' if dark else 'rgba(255,255,255,0.9)'};
        backdrop-filter: blur(8px);
        color: var(--text);
        font-size: 0.75em;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
    }}
    .cc-scenario-card .card-body {{
        padding: 20px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }}
    .cc-scenario-card .card-body h3 {{
        color: var(--text);
        font-size: 1.1em;
        font-weight: 700;
        margin: 0 0 8px;
        line-height: 1.3;
    }}
    .cc-scenario-card .card-body .desc {{
        color: var(--text-secondary);
        font-size: 0.85em;
        line-height: 1.4;
        margin-bottom: 16px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}
    .cc-scenario-card .card-footer {{
        margin-top: auto;
        padding-top: 16px;
        border-top: 1px solid var(--border-light);
    }}
    .cc-scenario-card .card-footer .best {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85em;
        margin-bottom: 12px;
    }}
    .cc-scenario-card .card-footer .best .lbl {{ color: var(--text-secondary); }}
    .cc-scenario-card .card-footer .best .val {{ font-weight: 700; }}

    /* Stars */
    .cc-stars {{
        display: inline-flex;
        gap: 2px;
        align-items: center;
    }}
    .cc-stars .material-symbols-outlined {{
        font-size: 16px !important;
    }}
    .cc-stars .filled {{
        color: #fbbf24;
        font-variation-settings: 'FILL' 1;
    }}
    .cc-stars .empty {{
        color: {('#334155' if dark else '#d1d5db')};
    }}

    /* Category badge */
    .cc-cat-badge {{
        background: color-mix(in srgb, var(--cat-color) 15%, transparent);
        color: var(--cat-color);
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }}

    /* NEW badge */
    .cc-new-badge {{
        background: var(--primary);
        color: white;
        font-size: 0.7em;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-left: 6px;
    }}

    /* XP Progress bar - from Stitch */
    .cc-xp-bar {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: var(--shadow);
    }}
    .cc-xp-bar .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    .cc-xp-bar .header .level {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .cc-xp-bar .header .level .material-symbols-outlined {{
        color: var(--primary);
        font-size: 20px;
    }}
    .cc-xp-bar .header .level strong {{
        color: var(--text);
        font-weight: 700;
    }}
    .cc-xp-bar .header .xp {{
        color: var(--text-secondary);
        font-size: 0.85em;
        font-weight: 500;
    }}
    .cc-xp-bar .bar {{
        height: 10px;
        border-radius: 999px;
        background: {('#1e293b' if dark else '#e2e8f0')};
        overflow: hidden;
    }}
    .cc-xp-bar .bar .fill {{
        height: 100%;
        border-radius: 999px;
        background: var(--primary);
        position: relative;
        transition: width 0.5s ease;
    }}

    /* Table - from Stitch */
    .cc-table {{
        width: 100%;
        border-collapse: collapse;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow);
    }}
    .cc-table thead tr {{
        background: var(--bg-table-head);
        border-bottom: 1px solid var(--border);
    }}
    .cc-table thead th {{
        padding: 12px 16px;
        color: var(--text-secondary);
        font-size: 0.75em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-align: left;
    }}
    .cc-table tbody tr {{
        border-bottom: 1px solid var(--border);
        transition: background 0.15s;
    }}
    .cc-table tbody tr:hover {{
        background: var(--bg-hover);
    }}
    .cc-table tbody tr:last-child {{
        border-bottom: none;
    }}
    .cc-table td {{
        padding: 12px 16px;
        font-size: 0.9em;
    }}
    .cc-table .name {{
        color: var(--text);
        font-weight: 500;
    }}
    .cc-table .sub {{
        color: var(--text-secondary);
        font-size: 0.8em;
    }}
    .cc-table .score-badge {{
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.8em;
        font-weight: 600;
    }}

    /* Score badges */
    .score-green {{
        background: {('rgba(16,185,129,0.15)' if dark else '#ecfdf5')};
        color: {('#34d399' if dark else '#065f46')};
    }}
    .score-amber {{
        background: {('rgba(245,158,11,0.15)' if dark else '#fffbeb')};
        color: {('#fbbf24' if dark else '#92400e')};
    }}
    .score-red {{
        background: {('rgba(239,68,68,0.15)' if dark else '#fef2f2')};
        color: {('#f87171' if dark else '#991b1b')};
    }}

    /* Achievement badges - from Stitch */
    .cc-achievement {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid var(--border);
        min-width: 160px;
        text-align: center;
    }}
    .cc-achievement.earned-amber {{
        background: {('rgba(217,119,6,0.1)' if dark else '#fffbeb')};
        border-color: {('rgba(217,119,6,0.3)' if dark else '#fde68a')};
    }}
    .cc-achievement.earned-emerald {{
        background: {('rgba(16,185,129,0.1)' if dark else '#ecfdf5')};
        border-color: {('rgba(16,185,129,0.3)' if dark else '#a7f3d0')};
    }}
    .cc-achievement.earned-purple {{
        background: {('rgba(139,92,246,0.1)' if dark else '#f5f3ff')};
        border-color: {('rgba(139,92,246,0.3)' if dark else '#ddd6fe')};
    }}
    .cc-achievement.locked {{
        border-style: dashed;
        opacity: 0.5;
    }}
    .cc-achievement .ach-icon {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .cc-achievement .ach-name {{
        color: var(--text);
        font-size: 0.9em;
        font-weight: 700;
    }}
    .cc-achievement .ach-sub {{
        color: var(--text-secondary);
        font-size: 0.75em;
    }}

    /* Checkpoint items - from Stitch scorecard */
    .cc-checkpoint {{
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 14px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
    }}
    .cc-checkpoint.passed {{
        background: {('rgba(16,185,129,0.1)' if dark else '#f0fdf4')};
        border-left: 3px solid var(--emerald);
    }}
    .cc-checkpoint.failed {{
        background: {('rgba(239,68,68,0.1)' if dark else '#fef2f2')};
        border-left: 3px solid var(--red);
    }}
    .cc-checkpoint .cp-icon {{
        font-size: 1.2em;
        margin-top: 2px;
    }}
    .cc-checkpoint .cp-name {{
        color: var(--text);
        font-weight: 600;
        font-size: 0.9em;
    }}
    .cc-checkpoint .cp-evidence {{
        color: var(--text-secondary);
        font-size: 0.8em;
        font-style: italic;
        margin-top: 2px;
    }}

    /* Coaching tip - from Stitch */
    .cc-tip {{
        background: linear-gradient(135deg, rgba(19,127,236,0.1), transparent);
        border: 1px solid rgba(19,127,236,0.2);
        border-radius: 12px;
        padding: 20px;
        position: relative;
        overflow: hidden;
    }}
    .cc-tip .tip-label {{
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--primary);
        font-weight: 700;
        margin-bottom: 8px;
    }}
    .cc-tip .tip-text {{
        color: {('#cbd5e1' if dark else '#475569')};
        font-size: 0.9em;
        line-height: 1.5;
    }}

    /* Call timer - from Stitch active_call */
    .cc-timer {{
        font-size: 3em;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        color: var(--text);
        letter-spacing: 4px;
        text-align: center;
    }}

    /* Pulse animation */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}
    .cc-pulse {{
        width: 8px;
        height: 8px;
        background: var(--red);
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }}

    /* Progress bar overrides */
    .stProgress > div > div > div {{
        background-color: var(--primary) !important;
    }}

    /* Radio buttons */
    div[role="radiogroup"] {{
        background: {('#0c151a' if dark else '#f1f5f9')} !important;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 4px;
    }}

    /* Text input overrides */
    .stTextInput input,
    .stSelectbox select,
    .stTextArea textarea {{
        background-color: var(--bg-input) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
        border-radius: 8px !important;
    }}

    /* Dividers */
    hr {{
        border-color: var(--border) !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
    }}

    /* Plotly chart bg */
    .js-plotly-plot .plotly .bg {{
        fill: var(--bg-card) !important;
    }}

    /* Selectbox */
    div[data-baseweb="select"] {{
        background: var(--bg-input) !important;
    }}

    /* Tab overrides */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 999px !important;
        padding: 6px 20px !important;
        font-weight: 500 !important;
    }}

    /* Hide Streamlit branding */
    #MainMenu, footer {{visibility: hidden;}}

    /* Dark mode toggle button */
    .cc-mode-toggle {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: {('#1e293b' if dark else '#f1f5f9')};
        color: var(--text-secondary);
        cursor: pointer;
        border: none;
    }}

    /* Heading overrides */
    h1, h2, h3, h4, h5 {{
        color: var(--text) !important;
    }}
    p, span, div {{
        color: var(--text);
    }}

    /* Heatmap label colors */
    .cc-heatmap-cell {{
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        font-weight: 600;
        font-size: 0.85em;
    }}
    .cc-heatmap-cell.excellent {{ background: {('rgba(16,185,129,0.2)' if dark else '#dcfce7')}; color: var(--emerald); }}
    .cc-heatmap-cell.average {{ background: {('rgba(245,158,11,0.2)' if dark else '#fef9c3')}; color: var(--amber); }}
    .cc-heatmap-cell.needs-work {{ background: {('rgba(239,68,68,0.2)' if dark else '#fee2e2')}; color: var(--red); }}

    /* Leaderboard */
    .cc-leaderboard {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        box-shadow: var(--shadow);
    }}
    .cc-lb-row {{
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid var(--border);
        gap: 12px;
    }}
    .cc-lb-row:last-child {{ border-bottom: none; }}
    .cc-lb-row .rank {{ width: 30px; font-weight: 700; font-size: 0.9em; }}
    .cc-lb-row .avatar {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 0.8em;
    }}
    .cc-lb-row .agent-name {{ flex: 1; font-weight: 500; font-size: 0.9em; }}
    .cc-lb-row .agent-level {{ color: var(--text-secondary); font-size: 0.8em; }}
    .cc-lb-row .agent-score {{ font-weight: 700; font-size: 0.9em; }}
    </style>
    """, unsafe_allow_html=True)


def material_icon(name, size=20, color=None):
    color_style = f"color:{color};" if color else ""
    return f'<span class="material-symbols-outlined" style="font-size:{size}px;{color_style}vertical-align:middle;">{name}</span>'
