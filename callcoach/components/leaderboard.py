import streamlit as st
from config import LEVEL_NAMES
from utils.helpers import format_score


def render_leaderboard(data, show_rank=True):
    if not data:
        st.info("Zatím žádná data pro žebříček.")
        return

    colors = ["#f59e0b", "#94a3b8", "#cd7f32", "#137fec", "#8b5cf6"]
    lb_html = '<div class="cc-leaderboard">'
    for i, agent in enumerate(data[:10]):
        bg = colors[i % len(colors)]
        score = agent.get("avg_score", 0)
        level_name = LEVEL_NAMES.get(agent.get("level", 1), "")

        lb_html += f"""
        <div class="cc-lb-row">
            <div class="rank">{i + 1}</div>
            <div class="avatar" style="background:{bg};">{agent['name'][0]}</div>
            <div class="agent-name">{agent['name']}</div>
            <div class="agent-level">{level_name}</div>
            <div class="agent-score" style="color:{'var(--emerald)' if score >= 80 else 'var(--amber)'};">
                {format_score(score)}
            </div>
        </div>"""
    lb_html += "</div>"
    st.markdown(lb_html, unsafe_allow_html=True)
