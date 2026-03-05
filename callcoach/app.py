import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db
from database.seed import run_all_seeds
from utils.helpers import inject_custom_css

# Page config
st.set_page_config(
    page_title="CallCoach — AI Tréningový Simulátor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db()
run_all_seeds()

# Inject custom CSS
inject_custom_css()

# Initialize session state
if "page" not in st.session_state:
    st.session_state["page"] = "login"


def render_sidebar():
    user = st.session_state.get("user")
    if not user:
        return

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:16px 0;">
            <span class="material-symbols-outlined" style="font-size:36px;color:#137fec;">headset_mic</span>
            <h3 style="color:#137fec;margin:4px 0;">CallCoach</h3>
            <p style="color:#6b7280;font-size:0.8em;margin:0;">Tréningový simulátor</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        role = user.get("role", "agent")

        if role == "agent":
            nav_items = [
                ("agent_home", "home", "Dashboard"),
                ("scenario_browser", "school", "Scenáre"),
                ("achievements", "emoji_events", "Achievementy"),
            ]
        else:
            nav_items = [
                ("manager_dashboard", "dashboard", "Dashboard tímu"),
                ("scenario_browser", "school", "Scenáre"),
            ]

        for page_key, icon, label in nav_items:
            is_active = st.session_state.get("page") == page_key
            if st.button(
                f"{'→ ' if is_active else '   '}{label}",
                key=f"nav_{page_key}",
                use_container_width=True,
            ):
                st.session_state["page"] = page_key
                st.rerun()

        st.divider()

        # User info
        from config import LEVEL_NAMES
        level_name = LEVEL_NAMES.get(user.get("level", 1), "")

        st.markdown(f"""
        <div style="padding:8px 0;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:36px;height:36px;background:#137fec;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;
                            color:white;font-weight:700;">{user.get('name', 'U')[0]}</div>
                <div>
                    <div style="font-weight:600;font-size:0.9em;color:#1e293b;">{user.get('name', '')}</div>
                    <div style="font-size:0.75em;color:#6b7280;">Level {user.get('level', 1)} — {level_name}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if user.get("role") == "agent":
            streak = user.get("streak_days", 0)
            if streak > 0:
                st.markdown(f"""
                <div style="background:#fef3c7;border-radius:8px;padding:10px;margin-top:12px;text-align:center;">
                    <span style="font-size:1.2em;">🔥</span>
                    <span style="font-weight:600;color:#92400e;">{streak} dní streak</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Odhlásiť sa", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    page = st.session_state.get("page", "login")

    if page == "login" or "user" not in st.session_state:
        from pages.login import render
        render()
        return

    render_sidebar()

    if page == "agent_home":
        from pages.agent_home import render
        render()
    elif page == "scenario_browser":
        from pages.scenario_browser import render
        render()
    elif page == "pre_call_briefing":
        from pages.pre_call_briefing import render
        render()
    elif page == "active_call":
        from pages.active_call import render
        render()
    elif page == "evaluating":
        from pages.scorecard import render_evaluating
        render_evaluating()
    elif page == "scorecard":
        from pages.scorecard import render
        render()
    elif page == "manager_dashboard":
        from pages.manager_dashboard import render
        render()
    elif page == "agent_detail":
        from pages.agent_detail import render
        render()
    elif page == "achievements":
        from pages.achievements import render
        render()
    else:
        st.error(f"Neznáma stránka: {page}")


if __name__ == "__main__":
    main()
