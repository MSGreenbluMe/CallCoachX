import streamlit as st
from services.gamification_service import get_user_achievements


def render():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    all_achievements = get_user_achievements(user_id)
    earned = [a for a in all_achievements if a.get("earned_at")]
    locked = [a for a in all_achievements if not a.get("earned_at")]

    total = len(all_achievements)
    earned_count = len(earned)
    pct = int((earned_count / total) * 100) if total > 0 else 0

    st.markdown(f"""
    <h1 style="margin-bottom:4px;">Vaše úspěchy</h1>
    <p style="color:var(--text-secondary);">
        {earned_count}/{total} odznaky získány • {user.get('xp', 0):,} celkem XP
    </p>
    """, unsafe_allow_html=True)

    st.progress(pct / 100)

    st.markdown("<br>", unsafe_allow_html=True)

    filter_tab = st.radio(
        "Filtr",
        ["Všechny", "Získané", "Zamknuté"],
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

    milestones = [a for a in display if a.get("category") == "milestone"]
    skills = [a for a in display if a.get("category") != "milestone"]

    if milestones:
        st.markdown("<h3>Milníky</h3>", unsafe_allow_html=True)
        _render_achievement_grid(milestones)
        st.markdown("<br>", unsafe_allow_html=True)

    if skills:
        st.markdown("<h3>Dovednosti</h3>", unsafe_allow_html=True)
        _render_achievement_grid(skills)


def _render_achievement_grid(achievements):
    ach_colors = ["amber", "emerald", "purple", "amber", "emerald", "purple"]
    grid_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;">'
    for i, ach in enumerate(achievements):
        is_earned = ach.get("earned_at") is not None
        color = ach_colors[i % len(ach_colors)]

        if is_earned:
            date_str = ach["earned_at"][:10] if ach.get("earned_at") else ""
            grid_html += f"""
            <div class="cc-achievement earned-{color}">
                <div style="font-size:2em;">{ach.get('icon', '🏆')}</div>
                <div class="ach-name">{ach.get('name', '')}</div>
                <div class="ach-sub">Získáno {date_str}</div>
            </div>"""
        else:
            grid_html += f"""
            <div class="cc-achievement locked">
                <div style="font-size:2em;filter:grayscale(1);opacity:0.5;">{ach.get('icon', '🏆')}</div>
                <div class="ach-name" style="color:var(--text-muted);">{ach.get('name', '')}</div>
                <div class="ach-sub">🔒 Zamknuto</div>
                <div style="font-size:0.75em;color:var(--text-muted);margin-top:4px;">{ach.get('description', '')}</div>
            </div>"""
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)
