import streamlit as st
from utils.helpers import score_color, score_label


def render_big_score(score, size="4em"):
    color = score_color(score)
    label = score_label(score)
    st.markdown(f"""
    <div style="text-align:center;">
        <div style="font-size:{size};font-weight:800;color:{color};line-height:1;">
            {score:.0f}%
        </div>
        <div style="color:{color};font-weight:600;margin-top:4px;font-size:1.1em;">
            {label}
        </div>
    </div>""", unsafe_allow_html=True)


def render_metric_card(title, value, trend=None, trend_direction="up", icon=None):
    trend_html = ""
    if trend is not None:
        cls = "up" if trend_direction == "up" else "down"
        arrow_icon = "trending_up" if trend_direction == "up" else "trending_down"
        trend_html = f'<div class="trend {cls}"><span class="material-symbols-outlined" style="font-size:14px;">{arrow_icon}</span> {trend}</div>'

    icon_html = ""
    if icon:
        icon_html = f'<span class="material-symbols-outlined bg-icon">{icon}</span>'

    st.markdown(f"""
    <div class="cc-metric">
        {icon_html}
        <div class="label">{title}</div>
        <div class="value">{value}</div>
        {trend_html}
    </div>""", unsafe_allow_html=True)


def render_xp_bar(current_xp, current_level, max_xp_for_level, progress_pct):
    from config import LEVEL_NAMES
    level_name = LEVEL_NAMES.get(current_level, "")

    st.markdown(f"""
    <div class="cc-xp-bar">
        <div class="header">
            <div class="level">
                <span class="material-symbols-outlined">military_tech</span>
                <strong>Level {current_level}</strong>
                <span style="color:var(--text-secondary);margin-left:4px;">{level_name}</span>
            </div>
            <div class="xp">{current_xp:,} / {max_xp_for_level:,} XP</div>
        </div>
        <div class="bar">
            <div class="fill" style="width:{progress_pct}%;"></div>
        </div>
    </div>""", unsafe_allow_html=True)
