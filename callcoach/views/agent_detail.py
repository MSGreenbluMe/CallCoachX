import streamlit as st
import plotly.graph_objects as go
from services.evaluation_service import get_user_stats, get_user_recent_sessions, get_agent_skill_scores
from services.gamification_service import get_level_name, get_earned_achievements
from components.radar_chart import create_radar_chart
from database.db import query
from config import LEVEL_THRESHOLDS, CATEGORIES
from utils.helpers import format_score, format_duration, category_badge_html


def render():
    agent_id = st.session_state.get("selected_agent_id")
    if not agent_id:
        st.warning("Žádný agent vybrán.")
        return

    agent = query("SELECT * FROM users WHERE id = ?", (agent_id,), one=True)
    if not agent:
        st.error("Agent nenalezen.")
        return

    dark = st.session_state.get("dark_mode", True)

    if st.button("← Zpět na dashboard"):
        st.session_state["page"] = "manager_dashboard"
        st.rerun()

    # Profile card
    level_name = get_level_name(agent.get("level", 1))
    st.markdown(f"""
    <div class="cc-card" style="margin:16px 0;">
        <div style="display:flex;align-items:center;gap:20px;">
            <div style="width:80px;height:80px;background:linear-gradient(135deg,var(--primary),#3b82f6);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:700;font-size:2em;">{agent['name'][0]}</div>
            <div>
                <h2 style="margin:0;">{agent['name']}</h2>
                <span class="score-badge score-green" style="margin:4px 0 8px;display:inline-block;">
                    Level {agent.get('level', 1)} — {level_name}
                </span>
                <p style="color:var(--text-secondary);margin:0;">{agent.get('team', '')} | XP: {agent.get('xp', 0):,}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    stats = get_user_stats(agent_id)
    c1, c2, c3, c4 = st.columns(4)
    stat_data = [
        (c1, "Průměrné skóre", format_score(stats.get("avg_score")), "analytics"),
        (c2, "Celkem relací", stats.get("total_sessions", 0), "call"),
        (c3, "Čas tréninku", f"{(stats.get('total_time', 0) or 0) / 3600:.1f}h", "schedule"),
        (c4, "Streak", f"{agent.get('streak_days', 0)} dní", "local_fire_department"),
    ]
    for col, label, value, icon in stat_data:
        with col:
            st.markdown(f"""
            <div class="cc-metric">
                <span class="material-symbols-outlined bg-icon">{icon}</span>
                <div class="label">{label}</div>
                <div class="value">{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Coaching insight
    st.markdown("""
    <div class="cc-tip">
        <div class="tip-label">
            <span class="material-symbols-outlined">psychology</span>
            Doporučení pro agenta
        </div>
        <div class="tip-text">
            Na základě výsledků doporučujeme zaměřit se na scénáře z kategorie Reklamace
            a procvičit zvládání námitek a empatickou komunikaci.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    col_chart, col_radar = st.columns(2)

    with col_chart:
        st.markdown("<h3>Progres v čase</h3>", unsafe_allow_html=True)
        sessions_all = query("""
            SELECT date(s.started_at) as day, AVG(e.overall_score) as avg_score
            FROM sessions s
            JOIN evaluations e ON e.session_id = s.id
            WHERE s.user_id = ? AND s.status = 'completed'
            GROUP BY date(s.started_at)
            ORDER BY day
        """, (agent_id,))

        if sessions_all:
            dates = [s["day"] for s in sessions_all]
            scores = [s["avg_score"] for s in sessions_all]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=scores,
                mode="lines+markers",
                line=dict(color="#137fec", width=2, shape="spline"),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(19, 127, 236, 0.08)",
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(range=[0, 100], showgrid=True,
                           gridcolor="#1e293b" if dark else "#f3f4f6"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8" if dark else "#64748b"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zatím žádná data.")

    with col_radar:
        st.markdown("<h3>Přehled dovedností</h3>", unsafe_allow_html=True)
        skill_scores = get_agent_skill_scores(agent_id)
        if skill_scores:
            fig = create_radar_chart(skill_scores, title="")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                polar=dict(bgcolor="rgba(0,0,0,0)"),
                font=dict(color="#f1f5f9" if dark else "#0f172a"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zatím žádná data.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent sessions
    st.markdown("<h3>Historie relací</h3>", unsafe_allow_html=True)
    recent = get_user_recent_sessions(agent_id, limit=10)
    if recent:
        table_html = """<table class="cc-table">
            <thead><tr><th>Scénář</th><th>Datum</th><th>Skóre</th><th>Délka</th><th>Cíl</th></tr></thead><tbody>"""
        for session in recent:
            cat = CATEGORIES.get(session.get("category", ""), {})
            score = session.get("overall_score")
            score_cls = "score-green" if score and score >= 80 else "score-amber" if score and score >= 60 else "score-red"
            goal = session.get("goal_achieved", "")
            goal_icon = "✅" if goal == "ACHIEVED" else "⚠️" if goal == "PARTIAL" else "❌" if goal == "FAILED" else ""

            table_html += f"""<tr>
                <td><div class="name">{session.get('scenario_name', '')}</div>
                    <div class="sub">{cat.get('label', '')}</div></td>
                <td style="color:var(--text-secondary);">{session.get("started_at", "")[:10]}</td>
                <td><span class="score-badge {score_cls}">{format_score(score)}</span></td>
                <td style="color:var(--text-secondary);">{format_duration(session.get("duration_seconds"))}</td>
                <td style="text-align:center;">{goal_icon}</td>
            </tr>"""
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("Agent zatím nemá žádné relace.")
