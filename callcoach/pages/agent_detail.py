import streamlit as st
import plotly.graph_objects as go
from services.evaluation_service import get_user_stats, get_user_recent_sessions, get_agent_skill_scores
from services.gamification_service import get_level_name, get_earned_achievements
from components.radar_chart import create_radar_chart
from components.score_card import render_metric_card, render_xp_bar
from components.achievement_badge import render_achievement_row
from database.db import query
from config import LEVEL_THRESHOLDS, CATEGORIES
from utils.helpers import format_score, format_duration, category_badge_html, difficulty_stars


def render():
    agent_id = st.session_state.get("selected_agent_id")
    if not agent_id:
        st.warning("Žiadny agent vybraný.")
        return

    agent = query("SELECT * FROM users WHERE id = ?", (agent_id,), one=True)
    if not agent:
        st.error("Agent nenájdený.")
        return

    # Back button
    if st.button("← Späť na dashboard"):
        st.session_state["page"] = "manager_dashboard"
        st.rerun()

    # Header / Profile card
    level_name = get_level_name(agent.get("level", 1))
    st.markdown(f"""
    <div style="background:white;border:1px solid #e5e7eb;border-radius:16px;padding:24px;margin:16px 0;">
        <div style="display:flex;align-items:center;gap:20px;">
            <div style="width:80px;height:80px;background:linear-gradient(135deg,#137fec,#3b82f6);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:700;font-size:2em;">
                {agent['name'][0]}
            </div>
            <div>
                <h2 style="margin:0;">{agent['name']}</h2>
                <span style="background:#137fec15;color:#137fec;padding:2px 10px;border-radius:12px;
                             font-size:0.8em;font-weight:600;">Level {agent.get('level', 1)} — {level_name}</span>
                <p style="color:#6b7280;margin:8px 0 0;">
                    {agent.get('team', '')} | XP: {agent.get('xp', 0):,}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    stats = get_user_stats(agent_id)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Priemerné skóre", format_score(stats.get("avg_score")), icon="analytics")
    with c2:
        render_metric_card("Celkom sessions", stats.get("total_sessions", 0), icon="call")
    with c3:
        total_h = (stats.get("total_time", 0) or 0) / 3600
        render_metric_card("Tréningový čas", f"{total_h:.1f}h", icon="schedule")
    with c4:
        render_metric_card("Streak", f"{agent.get('streak_days', 0)} dní", icon="local_fire_department")

    st.markdown("<br>", unsafe_allow_html=True)

    # Coaching insight
    st.markdown(f"""
    <div class="coaching-tip-box" style="margin-bottom:24px;">
        <h4>💡 Odporúčanie pre agenta</h4>
        <p style="font-size:0.9em;opacity:0.95;">
            Na základe výsledkov odporúčame zamerať sa na scenáre z kategórie Reklamácie
            a precvičiť zvládanie námietok a empatickú komunikáciu.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Charts
    col_chart, col_radar = st.columns(2)

    with col_chart:
        st.subheader("Progres v čase")
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
                yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#f3f4f6"),
                paper_bgcolor="white",
                plot_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zatiaľ žiadne dáta.")

    with col_radar:
        st.subheader("Prehľad zručností")
        skill_scores = get_agent_skill_scores(agent_id)
        if skill_scores:
            fig = create_radar_chart(skill_scores, title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Zatiaľ žiadne dáta.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Achievements
    achievements = get_earned_achievements(agent_id)
    if achievements:
        st.subheader("Achievementy")
        render_achievement_row(achievements[:5])
        st.markdown("<br>", unsafe_allow_html=True)

    # Recent sessions table
    st.subheader("História sessions")
    recent = get_user_recent_sessions(agent_id, limit=20)
    if recent:
        for session in recent:
            cols = st.columns([3, 1.5, 1, 1, 1])
            with cols[0]:
                st.markdown(f"""
                <strong>{session.get('scenario_name', '')}</strong><br>
                <span style="font-size:0.8em;">{category_badge_html(session.get('category', ''))}</span>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(session.get("started_at", "")[:10])
            with cols[2]:
                score = session.get("overall_score")
                color = "#10b981" if score and score >= 80 else "#f59e0b" if score and score >= 50 else "#ef4444"
                st.markdown(f"<strong style='color:{color};'>{format_score(score)}</strong>", unsafe_allow_html=True)
            with cols[3]:
                st.markdown(format_duration(session.get("duration_seconds")))
            with cols[4]:
                goal = session.get("goal_achieved", "")
                if goal == "ACHIEVED":
                    st.markdown("✅")
                elif goal == "PARTIAL":
                    st.markdown("⚠️")
                elif goal == "FAILED":
                    st.markdown("❌")
            st.divider()
    else:
        st.info("Agent ešte nemá žiadne sessions.")
