import streamlit as st
from utils.helpers import score_color, score_label


def render_big_score(score, size="4em"):
    color = score_color(score)
    label = score_label(score)
    st.markdown(f"""
    <div style="text-align:center;">
        <div style="font-size:{size}; font-weight:800; color:{color}; line-height:1;">
            {score:.0f}%
        </div>
        <div style="color:{color}; font-weight:600; margin-top:4px; font-size:1.1em;">
            {label}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title, value, trend=None, trend_direction="up", icon=None):
    trend_html = ""
    if trend is not None:
        trend_class = "trend-up" if trend_direction == "up" else "trend-down"
        arrow = "↑" if trend_direction == "up" else "↓"
        trend_html = f'<div class="trend {trend_class}">{arrow} {trend}</div>'

    icon_html = ""
    if icon:
        icon_html = f'<span class="material-symbols-outlined" style="font-size:24px;color:#137fec;margin-bottom:8px;">{icon}</span><br>'

    st.markdown(f"""
    <div class="metric-card">
        {icon_html}
        <h3>{title}</h3>
        <p class="value">{value}</p>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)


def render_xp_bar(current_xp, current_level, max_xp_for_level, progress_pct):
    from config import LEVEL_NAMES
    level_name = LEVEL_NAMES.get(current_level, "")

    st.markdown(f"""
    <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div>
                <span style="font-weight:700;color:#137fec;">Level {current_level}</span>
                <span style="color:#6b7280;margin-left:6px;">{level_name}</span>
            </div>
            <div style="color:#6b7280;font-size:0.85em;">{current_xp} / {max_xp_for_level} XP</div>
        </div>
        <div class="xp-bar">
            <div class="xp-bar-fill" style="width:{progress_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
