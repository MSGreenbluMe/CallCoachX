import streamlit as st
from config import LEVEL_NAMES
from utils.helpers import format_score


def render_leaderboard(data, show_rank=True):
    if not data:
        st.info("Zatiaľ žiadne dáta pre leaderboard.")
        return

    header_cols = st.columns([0.5, 2.5, 1, 1, 1])
    with header_cols[0]:
        st.markdown("**#**")
    with header_cols[1]:
        st.markdown("**Agent**")
    with header_cols[2]:
        st.markdown("**Level**")
    with header_cols[3]:
        st.markdown("**Skóre**")
    with header_cols[4]:
        st.markdown("**Sessions**")

    st.divider()

    colors = ["#fbbf24", "#c0c0c0", "#cd7f32"]

    for i, agent in enumerate(data[:10]):
        rank = i + 1
        rank_color = colors[i] if i < 3 else "#6b7280"
        level_name = LEVEL_NAMES.get(agent.get("level", 1), "")

        cols = st.columns([0.5, 2.5, 1, 1, 1])
        with cols[0]:
            if rank <= 3:
                medals = ["🥇", "🥈", "🥉"]
                st.markdown(medals[i])
            else:
                st.markdown(f"**{rank}**")
        with cols[1]:
            st.markdown(f"**{agent['name']}**")
        with cols[2]:
            st.markdown(f"Lv.{agent.get('level', 1)} {level_name}")
        with cols[3]:
            score = agent.get("avg_score", 0)
            st.markdown(f"**{format_score(score)}**")
        with cols[4]:
            st.markdown(str(agent.get("session_count", 0)))
