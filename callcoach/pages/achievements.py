import streamlit as st
from services.gamification_service import get_user_achievements, get_earned_achievements
from components.achievement_badge import render_achievement_badge
from components.score_card import render_xp_bar
from services.gamification_service import get_xp_progress_pct
from config import LEVEL_THRESHOLDS


def render():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    all_achievements = get_user_achievements(user_id)
    earned = [a for a in all_achievements if a.get("earned_at")]
    locked = [a for a in all_achievements if not a.get("earned_at")]

    # Header
    total = len(all_achievements)
    earned_count = len(earned)
    pct = int((earned_count / total) * 100) if total > 0 else 0

    st.markdown(f"""
    <h1 style="margin-bottom:4px;">Vaše achievementy</h1>
    <p style="color:#6b7280;">{earned_count}/{total} odznakov získaných | {user.get('xp', 0):,} XP celkom</p>
    """, unsafe_allow_html=True)

    # Progress bar
    st.progress(pct / 100)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    filter_tab = st.radio(
        "Filter",
        ["Všetky", "Získané", "Zamknuté"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if filter_tab == "Získané":
        display = earned
    elif filter_tab == "Zamknuté":
        display = locked
    else:
        display = all_achievements

    st.markdown("<br>", unsafe_allow_html=True)

    # Earned section
    if filter_tab in ["Všetky", "Získané"] and earned:
        st.markdown("### Získané odznaky")
        cols = st.columns(min(len(earned), 4))
        for i, ach in enumerate(earned):
            with cols[i % 4]:
                render_achievement_badge(ach, earned=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Locked section
    if filter_tab in ["Všetky", "Zamknuté"] and locked:
        st.markdown("### Zamknuté odznaky")
        cols = st.columns(min(len(locked), 4))
        for i, ach in enumerate(locked):
            with cols[i % 4]:
                render_achievement_badge(ach, earned=False)
                st.markdown(f"""
                <div style="font-size:0.75em;color:#9ca3af;text-align:center;margin-top:4px;">
                    {ach.get('description', '')}
                </div>
                """, unsafe_allow_html=True)
