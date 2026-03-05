import streamlit as st
import plotly.graph_objects as go
from services.evaluation_service import get_team_stats, get_team_score_trend, get_agent_skill_scores
from services.gamification_service import get_leaderboard
from components.score_card import render_metric_card
from components.leaderboard import render_leaderboard
from database.db import query
from config import LEVEL_NAMES
from utils.helpers import format_score


def render():
    user = st.session_state.get("user", {})

    st.markdown("""
    <h1 style="margin-bottom:4px;">Prehľad tímu</h1>
    <p style="color:#6b7280;">Dashboard pre manažérov — výkon tímu a agentov</p>
    """, unsafe_allow_html=True)

    # Date range filter
    period = st.radio(
        "Obdobie",
        ["Dnes", "7 dní", "30 dní", "Celkovo"],
        horizontal=True,
        index=2,
        label_visibility="collapsed",
    )
    period_map = {"Dnes": "day", "7 dní": "week", "30 dní": "month", "Celkovo": "all"}
    selected_period = period_map[period]

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats cards
    stats = get_team_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Agentov celkom", stats.get("total_agents", 0),
                          trend="+2", trend_direction="up", icon="group")
    with c2:
        render_metric_card("Priemerné skóre", format_score(stats.get("avg_score")),
                          trend="+4%", trend_direction="up", icon="analytics")
    with c3:
        render_metric_card("Sessions tento týždeň", stats.get("sessions_this_week", 0),
                          icon="call")
    with c4:
        render_metric_card("Aktívnych dnes", stats.get("active_today", 0), icon="person")

    st.markdown("<br>", unsafe_allow_html=True)

    # Two-column: chart + leaderboard
    col_chart, col_lb = st.columns([2, 1])

    with col_chart:
        st.subheader("Priemerné skóre tímu")
        trend_data = get_team_score_trend(days=30)
        if trend_data:
            dates = [d["day"] for d in trend_data]
            scores = [d["avg_score"] for d in trend_data]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=scores,
                mode="lines",
                line=dict(color="#137fec", width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(19, 127, 236, 0.1)",
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#f3f4f6"),
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(family="Inter, sans-serif"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zatiaľ žiadne dáta pre graf.")

    with col_lb:
        st.subheader("Top performeri")
        leaderboard_data = get_leaderboard(period=selected_period)
        render_leaderboard(leaderboard_data)

    st.markdown("<br>", unsafe_allow_html=True)

    # Skill Gap Heatmap
    st.subheader("Analýza zručností tímu")
    agents = query("SELECT id, name FROM users WHERE role = 'agent' ORDER BY name LIMIT 8")
    if agents:
        skills = ["Komunikácia", "Empatia", "Akt. počúvanie", "Prof. jazyk", "Štruktúra", "Riadenie", "Námietky"]
        skill_keys = ["communication_clarity", "empathy_rapport", "active_listening",
                      "professional_language", "call_structure", "call_control", "objection_handling"]

        z_data = []
        agent_names = []
        for agent in agents:
            agent_names.append(agent["name"])
            agent_skills = get_agent_skill_scores(agent["id"])
            if agent_skills:
                row = [round((agent_skills.get(k) or 5) * 10, 0) for k in skill_keys]
            else:
                row = [50] * 7
            z_data.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=list(map(list, zip(*z_data))),  # Transpose
            x=agent_names,
            y=skills,
            colorscale=[
                [0, "#fecaca"],
                [0.5, "#fde68a"],
                [1, "#bbf7d0"],
            ],
            zmin=0,
            zmax=100,
            text=list(map(list, zip(*z_data))),
            texttemplate="%{text:.0f}",
            textfont=dict(size=12),
        ))
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="white",
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Agent list (clickable)
    st.subheader("Agenti")
    agents_full = query("""
        SELECT u.*, COUNT(s.id) as session_count, COALESCE(AVG(e.overall_score), 0) as avg_score
        FROM users u
        LEFT JOIN sessions s ON s.user_id = u.id AND s.status = 'completed'
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE u.role = 'agent'
        GROUP BY u.id
        ORDER BY avg_score DESC
    """)

    for agent in agents_full:
        cols = st.columns([0.5, 2.5, 1, 1, 1, 0.5])
        with cols[0]:
            st.markdown(f"""
            <div style="width:36px;height:36px;background:#137fec;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">
                {agent['name'][0]}
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"**{agent['name']}**")
            st.markdown(f"<span style='color:#6b7280;font-size:0.8em;'>{agent.get('team', '')}</span>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"Lv.{agent.get('level', 1)} {LEVEL_NAMES.get(agent.get('level', 1), '')}")
        with cols[3]:
            st.markdown(f"**{format_score(agent.get('avg_score'))}**")
        with cols[4]:
            st.markdown(f"{agent.get('session_count', 0)} sessions")
        with cols[5]:
            if st.button("→", key=f"agent_{agent['id']}"):
                st.session_state["selected_agent_id"] = agent["id"]
                st.session_state["page"] = "agent_detail"
                st.rerun()
        st.divider()
