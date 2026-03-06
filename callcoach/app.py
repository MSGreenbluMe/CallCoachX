import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from database.seed import run_all_seeds
from utils.helpers import inject_custom_css

st.set_page_config(
    page_title="CallCoach — AI Trenažér hovorů",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
run_all_seeds()

if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

inject_custom_css()


def render_sidebar():
    user = st.session_state.get("user")
    if not user:
        return

    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding:16px 8px 20px;">
            <span class="material-symbols-outlined" style="font-size:28px;color:var(--primary);">headset_mic</span>
            <div>
                <div style="font-weight:700;font-size:1em;color:var(--text);">CallCoach</div>
                <div style="font-size:0.75em;color:var(--text-secondary);">Trenažér hovorů</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        role = user.get("role", "agent")

        if role == "agent":
            nav_items = [
                ("agent_home", "home", "Domů"),
                ("scenario_browser", "target", "Tréninkové scénáře"),
                ("achievements", "emoji_events", "Úspěchy"),
            ]
        else:
            nav_items = [
                ("manager_dashboard", "dashboard", "Přehled týmu"),
                ("scenario_browser", "target", "Scénáře"),
            ]

        # Build all nav CSS upfront: icons via ::before + active state highlight
        nav_css = ""
        for page_key, icon, label in nav_items:
            is_active = st.session_state.get("page") == page_key
            mid = f"nav-marker-{page_key}"
            nav_css += f"""
            [data-testid="element-container"]:has(#{mid}) + [data-testid="element-container"] .stButton > button::before {{
                content: "{icon}";
                font-family: 'Material Symbols Outlined';
                font-size: 20px;
                margin-right: 10px;
                vertical-align: middle;
                font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
            }}
            """
            if is_active:
                nav_css += f"""
                [data-testid="element-container"]:has(#{mid}) + [data-testid="element-container"] .stButton > button {{
                    background: var(--primary-10) !important;
                    color: var(--primary) !important;
                    font-weight: 600 !important;
                }}
                """
        st.markdown(f"<style>{nav_css}</style>", unsafe_allow_html=True)

        for page_key, icon, label in nav_items:
            st.markdown(
                f'<span id="nav-marker-{page_key}" style="display:none"></span>',
                unsafe_allow_html=True,
            )
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()

        st.markdown("<div style='flex:1;'></div>", unsafe_allow_html=True)

        # Dark/Light toggle
        st.divider()
        dark = st.session_state["dark_mode"]
        mode_label = "Světlý režim" if dark else "Tmavý režim"
        mode_emoji = "☀️" if dark else "🌙"
        if st.button(f"{mode_emoji} {mode_label}", key="toggle_mode", use_container_width=True):
            st.session_state["dark_mode"] = not dark
            st.rerun()

        st.divider()

        # User info
        from config import LEVEL_NAMES
        level = user.get("level", 1)
        level_name = LEVEL_NAMES.get(level, "")

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:8px;">
            <div style="width:36px;height:36px;background:linear-gradient(135deg,var(--primary),#3b82f6);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:700;font-size:0.9em;">{user.get('name', 'U')[0]}</div>
            <div>
                <div style="font-weight:600;font-size:0.9em;color:var(--text);">{user.get('name', '')}</div>
                <div style="font-size:0.75em;color:var(--text-secondary);">Level {level}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Odhlásit se", key="logout_btn", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    page = st.session_state.get("page", "login")

    if page == "login" or "user" not in st.session_state:
        from views.login import render
        render()
        return

    render_sidebar()

    if page == "agent_home":
        from views.agent_home import render
        render()
    elif page == "scenario_browser":
        from views.scenario_browser import render
        render()
    elif page == "pre_call_briefing":
        from views.pre_call_briefing import render
        render()
    elif page == "active_call":
        from views.active_call import render
        render()
    elif page == "evaluating":
        from views.scorecard import render_evaluating
        render_evaluating()
    elif page == "scorecard":
        from views.scorecard import render
        render()
    elif page == "manager_dashboard":
        from views.manager_dashboard import render
        render()
    elif page == "agent_detail":
        from views.agent_detail import render
        render()
    elif page == "achievements":
        from views.achievements import render
        render()
    else:
        st.error(f"Neznámá stránka: {page}")


main()
