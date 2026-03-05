import streamlit as st


def render_achievement_badge(achievement, earned=False, show_date=True):
    opacity = "1" if earned else "0.4"
    grayscale = "" if earned else "filter: grayscale(1);"
    date_html = ""

    if earned and show_date and achievement.get("earned_at"):
        date_str = achievement["earned_at"][:10]
        date_html = f'<div style="font-size:0.7em;color:#9ca3af;margin-top:4px;">{date_str}</div>'
    elif not earned:
        date_html = f'<div style="font-size:0.7em;color:#9ca3af;margin-top:4px;">🔒 Zamknutý</div>'

    st.markdown(f"""
    <div style="
        display:inline-flex;flex-direction:column;align-items:center;
        padding:16px;border-radius:12px;text-align:center;
        background:white;border:1px solid #e5e7eb;
        min-width:120px;opacity:{opacity};{grayscale}
    ">
        <div style="font-size:2.2em;margin-bottom:6px;">{achievement.get('icon', '🏆')}</div>
        <div style="font-size:0.85em;font-weight:600;color:#1e293b;">{achievement.get('name', '')}</div>
        {date_html}
    </div>
    """, unsafe_allow_html=True)


def render_achievement_row(achievements, max_cols=5):
    cols = st.columns(min(len(achievements), max_cols))
    for i, ach in enumerate(achievements[:max_cols]):
        with cols[i]:
            earned = ach.get("earned_at") is not None
            render_achievement_badge(ach, earned=earned)


def render_achievement_popup(achievement):
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 16px 0;
        animation: pulse 0.5s ease;
    ">
        <div style="font-size: 3em; margin-bottom: 8px;">{achievement.get('icon', '🏆')}</div>
        <div style="font-size: 1.2em; font-weight: 700;">Nový odznak!</div>
        <div style="font-size: 1em; font-weight: 600; margin-top: 4px;">{achievement.get('name', '')}</div>
        <div style="font-size: 0.85em; opacity: 0.9; margin-top: 4px;">{achievement.get('description', '')}</div>
    </div>
    """, unsafe_allow_html=True)
