import streamlit as st


def render_achievement_badge(achievement, earned=False, show_date=True):
    icon = achievement.get("icon", "🏆")
    name = achievement.get("name", "")

    if earned:
        date_html = ""
        if show_date and achievement.get("earned_at"):
            date_html = f'<div class="ach-sub">Získáno {achievement["earned_at"][:10]}</div>'
        st.markdown(f"""
        <div class="cc-achievement earned-amber">
            <div style="font-size:2em;">{icon}</div>
            <div class="ach-name">{name}</div>
            {date_html}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="cc-achievement locked">
            <div style="font-size:2em;filter:grayscale(1);opacity:0.5;">{icon}</div>
            <div class="ach-name" style="color:var(--text-muted);">{name}</div>
            <div class="ach-sub">🔒 Zamknuto</div>
        </div>""", unsafe_allow_html=True)


def render_achievement_row(achievements, max_cols=5):
    cols = st.columns(min(len(achievements), max_cols))
    for i, ach in enumerate(achievements[:max_cols]):
        with cols[i]:
            earned = ach.get("earned_at") is not None
            render_achievement_badge(ach, earned=earned)


def render_achievement_popup(achievement):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:white;
                border-radius:12px;padding:20px;text-align:center;margin:16px 0;">
        <div style="font-size:3em;margin-bottom:8px;">{achievement.get('icon', '🏆')}</div>
        <div style="font-size:1.2em;font-weight:700;">Nový odznak!</div>
        <div style="font-size:1em;font-weight:600;margin-top:4px;">{achievement.get('name', '')}</div>
        <div style="font-size:0.85em;opacity:0.9;margin-top:4px;">{achievement.get('description', '')}</div>
    </div>""", unsafe_allow_html=True)
