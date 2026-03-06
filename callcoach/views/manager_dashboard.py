import streamlit as st
import plotly.graph_objects as go
from services.evaluation_service import get_team_stats, get_team_score_trend, get_agent_skill_scores
from services.gamification_service import get_leaderboard
from database.db import query
from config import LEVEL_NAMES
from utils.helpers import format_score


def render():
    user = st.session_state.get("user", {})
    dark = st.session_state.get("dark_mode", True)

    st.markdown("""
    <h1 style="margin-bottom:4px;">Přehled týmu</h1>
    <p style="color:var(--text-secondary);">Dashboard pro manažery — výkon týmu a agentů</p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats cards
    stats = get_team_stats()
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, "Agentů celkem", stats.get("total_agents", 0), "+2", "group"),
        (c2, "Průměrné skóre týmu", format_score(stats.get("avg_score")), "+4%", "analytics"),
        (c3, "Relací tento týden", stats.get("sessions_this_week", 0), None, "call"),
        (c4, "Aktivních dnes", stats.get("active_today", 0), None, "person"),
    ]
    for col, label, value, trend, icon in metrics:
        with col:
            trend_html = f'<div class="trend up"><span class="material-symbols-outlined" style="font-size:14px;">trending_up</span> {trend}</div>' if trend else ""
            st.markdown(f"""
            <div class="cc-metric">
                <span class="material-symbols-outlined bg-icon">{icon}</span>
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                {trend_html}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two columns: chart + leaderboard
    col_chart, col_lb = st.columns([2, 1])

    with col_chart:
        st.markdown("<h3>Průměrné skóre týmu — trend</h3>", unsafe_allow_html=True)
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
                xaxis=dict(showgrid=False, color="var(--text-secondary)"),
                yaxis=dict(range=[0, 100], showgrid=True,
                           gridcolor="#1e293b" if dark else "#f3f4f6",
                           color="#94a3b8" if dark else "#64748b"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color="#94a3b8" if dark else "#64748b"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zatím žádná data pro graf.")

    with col_lb:
        st.markdown("<h3>Top performeři</h3>", unsafe_allow_html=True)
        leaderboard_data = get_leaderboard()
        if leaderboard_data:
            colors = ["#f59e0b", "#94a3b8", "#cd7f32", "#137fec", "#8b5cf6"]
            lb_html = '<div class="cc-leaderboard">'
            for i, agent in enumerate(leaderboard_data[:5]):
                bg = colors[i % len(colors)]
                score = agent.get("avg_score", 0)
                lb_html += f"""
                <div class="cc-lb-row">
                    <div class="rank">{i + 1}</div>
                    <div class="avatar" style="background:{bg};">{agent['name'][0]}</div>
                    <div class="agent-name">{agent['name']}</div>
                    <div class="agent-level">{LEVEL_NAMES.get(agent.get('level', 1), '')}</div>
                    <div class="agent-score" style="color:{'var(--emerald)' if score >= 80 else 'var(--amber)'};">{format_score(score)}</div>
                </div>"""
            lb_html += "</div>"
            st.markdown(lb_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Skill Gap Heatmap
    st.markdown("<h3>Analýza dovedností týmu</h3>", unsafe_allow_html=True)
    agents = query("SELECT id, name FROM users WHERE role = 'agent' ORDER BY name LIMIT 5")
    if agents:
        skills = ["Empatie", "Komunikace", "Řešení", "Profesionalita"]
        skill_keys = ["empathy_rapport", "communication_clarity", "call_control", "professional_language"]

        heatmap_html = '<div class="cc-card" style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;">'
        heatmap_html += '<tr><th style="padding:8px;color:var(--text-secondary);font-size:0.8em;text-align:left;"></th>'
        for agent in agents:
            heatmap_html += f'<th style="padding:8px;color:var(--text);font-size:0.85em;text-align:center;">{agent["name"].split()[0]}</th>'
        heatmap_html += '</tr>'

        for skill_label, skill_key in zip(skills, skill_keys):
            heatmap_html += f'<tr><td style="padding:8px;color:var(--text-secondary);font-size:0.85em;font-weight:500;">{skill_label}</td>'
            for agent in agents:
                agent_skills = get_agent_skill_scores(agent["id"])
                val = round((agent_skills.get(skill_key) or 5) * 10) if agent_skills else 50
                cls = "excellent" if val >= 80 else "average" if val >= 60 else "needs-work"
                heatmap_html += f'<td style="padding:4px;"><div class="cc-heatmap-cell {cls}">{val}</div></td>'
            heatmap_html += '</tr>'

        heatmap_html += '</table></div>'
        st.markdown(heatmap_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Agent list
    st.markdown("<h3>Agenti</h3>", unsafe_allow_html=True)
    agents_full = query("""
        SELECT u.*, COUNT(s.id) as session_count, COALESCE(AVG(e.overall_score), 0) as avg_score
        FROM users u
        LEFT JOIN sessions s ON s.user_id = u.id AND s.status = 'completed'
        LEFT JOIN evaluations e ON e.session_id = s.id
        WHERE u.role = 'agent'
        GROUP BY u.id
        ORDER BY avg_score DESC
    """)

    if agents_full:
        table_html = """<table class="cc-table">
            <thead><tr>
                <th>Agent</th><th>Level</th><th>Skóre</th><th>Relace</th><th></th>
            </tr></thead><tbody>"""
        for agent in agents_full:
            level_name = LEVEL_NAMES.get(agent.get("level", 1), "")
            score = agent.get("avg_score", 0)
            score_cls = "score-green" if score >= 80 else "score-amber" if score >= 60 else "score-red"
            table_html += f"""<tr>
                <td>
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="width:32px;height:32px;background:var(--primary);border-radius:50%;
                                    display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.8em;">
                            {agent['name'][0]}</div>
                        <div>
                            <div class="name">{agent['name']}</div>
                            <div class="sub">{agent.get('team', '')}</div>
                        </div>
                    </div>
                </td>
                <td style="color:var(--text-secondary);">Lv.{agent.get('level', 1)} {level_name}</td>
                <td><span class="score-badge {score_cls}">{format_score(score)}</span></td>
                <td style="color:var(--text-secondary);">{agent.get('session_count', 0)} relací</td>
                <td style="text-align:center;">→</td>
            </tr>"""
            table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # Agent click buttons
        for agent in agents_full:
            if st.button(f"Detail: {agent['name']}", key=f"agent_{agent['id']}"):
                st.session_state["selected_agent_id"] = agent["id"]
                st.session_state["page"] = "agent_detail"
                st.rerun()
