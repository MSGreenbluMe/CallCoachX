import streamlit as st
from services.evaluation_service import get_user_stats, get_user_recent_sessions
from services.gamification_service import (
    get_level_name, get_xp_to_next_level, get_xp_progress_pct,
    get_earned_achievements, get_user_achievements,
)
from components.score_card import render_metric_card, render_xp_bar
from components.achievement_badge import render_achievement_row
from config import LEVEL_THRESHOLDS, CATEGORIES
from utils.helpers import format_duration, format_score, difficulty_stars, category_badge_html


def render():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        level_name = get_level_name(user.get("level", 1))
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="width:56px;height:56px;background:linear-gradient(135deg,#137fec,#3b82f6);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        color:white;font-weight:700;font-size:1.4em;">
                {user.get('name', 'U')[0]}
            </div>
            <div>
                <h2 style="margin:0;">Vitajte, {user.get('name', 'Agent')}!</h2>
                <span style="color:#6b7280;">Level {user.get('level', 1)} — {level_name}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        if st.button("🎯 Začať tréning", type="primary", use_container_width=True):
            st.session_state["page"] = "scenario_browser"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # XP Bar
    xp = user.get("xp", 0)
    level = user.get("level", 1)
    next_level = level + 1
    next_threshold = LEVEL_THRESHOLDS.get(next_level, 25000)
    progress = get_xp_progress_pct(xp, level)
    render_xp_bar(xp, level, next_threshold, progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    stats = get_user_stats(user_id)
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Celkom sessions", stats.get("total_sessions", 0), icon="call")
    with c2:
        render_metric_card("Priemerné skóre", format_score(stats.get("avg_score")), icon="analytics")
    with c3:
        render_metric_card("Aktuálny streak", f"{user.get('streak_days', 0)} dní", icon="local_fire_department")

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent achievements
    achievements = get_earned_achievements(user_id)
    if achievements:
        st.subheader("Posledné achievementy")
        render_achievement_row(achievements[:5])
        st.markdown("<br>", unsafe_allow_html=True)

    # Two-column layout
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Posledné sessions")
        recent = get_user_recent_sessions(user_id, limit=5)
        if recent:
            for session in recent:
                cat = CATEGORIES.get(session.get("category", ""), {})
                score = session.get("overall_score")
                score_color = "#10b981" if score and score >= 80 else "#f59e0b" if score and score >= 50 else "#ef4444"

                cols = st.columns([3, 1.5, 1, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div>
                        <strong>{session.get('scenario_name', '')}</strong><br>
                        <span style="font-size:0.8em;color:#6b7280;">
                            {category_badge_html(session.get('category', ''))}
                            {difficulty_stars(session.get('difficulty', 1))}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    date_str = session.get("started_at", "")[:10]
                    st.markdown(f"<span style='color:#6b7280;font-size:0.9em;'>{date_str}</span>", unsafe_allow_html=True)
                with cols[2]:
                    if score is not None:
                        st.markdown(f"<strong style='color:{score_color};'>{score:.0f}%</strong>", unsafe_allow_html=True)
                with cols[3]:
                    st.markdown(f"<span style='color:#6b7280;font-size:0.9em;'>{format_duration(session.get('duration_seconds'))}</span>", unsafe_allow_html=True)
                st.divider()
        else:
            st.info("Zatiaľ žiadne sessions. Začnite trénovať!")

    with col_right:
        st.subheader("Milestones")

        # Milestone 1: Complete 10 calls
        total = stats.get("total_sessions", 0)
        pct1 = min(100, int((total / 10) * 100))
        st.markdown(f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:10px;padding:14px;margin-bottom:12px;">
            <div style="font-weight:600;font-size:0.9em;color:#1e293b;">Dokončiť 10 hovorov</div>
            <div style="color:#6b7280;font-size:0.8em;margin:4px 0;">{total}/10</div>
            <div class="xp-bar"><div class="xp-bar-fill" style="width:{pct1}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # Milestone 2: Reach Level 5
        pct2 = min(100, int((level / 5) * 100))
        st.markdown(f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:10px;padding:14px;margin-bottom:12px;">
            <div style="font-weight:600;font-size:0.9em;color:#1e293b;">Dosiahnuť Level 5</div>
            <div style="color:#6b7280;font-size:0.8em;margin:4px 0;">Level {level}/5</div>
            <div class="xp-bar"><div class="xp-bar-fill" style="width:{pct2}%;background:linear-gradient(90deg,#8b5cf6,#a855f7);"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # Milestone 3: 5 achievements
        earned_count = len(achievements) if achievements else 0
        pct3 = min(100, int((earned_count / 5) * 100))
        st.markdown(f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:10px;padding:14px;margin-bottom:12px;">
            <div style="font-weight:600;font-size:0.9em;color:#1e293b;">Získať 5 achievementov</div>
            <div style="color:#6b7280;font-size:0.8em;margin:4px 0;">{earned_count}/5</div>
            <div class="xp-bar"><div class="xp-bar-fill" style="width:{pct3}%;background:linear-gradient(90deg,#f59e0b,#fbbf24);"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # Pro Tip
        st.markdown("""
        <div class="coaching-tip-box" style="margin-top:16px;">
            <h4>💡 Tip dňa</h4>
            <p style="font-size:0.9em;opacity:0.9;">Skúste parafrázovať to, čo zákazník hovorí. Pomáha to budovať dôveru.</p>
        </div>
        """, unsafe_allow_html=True)
