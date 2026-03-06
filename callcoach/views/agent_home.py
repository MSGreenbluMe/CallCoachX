import streamlit as st
from services.evaluation_service import get_user_stats, get_user_recent_sessions
from services.gamification_service import (
    get_level_name, get_xp_progress_pct,
    get_earned_achievements,
)
from config import LEVEL_THRESHOLDS, CATEGORIES
from utils.helpers import format_duration, format_score


def render():
    user = st.session_state.get("user", {})
    user_id = user.get("id")
    level = user.get("level", 1)
    xp = user.get("xp", 0)

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <h1 style="margin:0;">Vítejte zpět, {user.get('name', 'Agent')}</h1>
        <p style="color:var(--text-secondary);">Připraveni na další tréninkovou relaci?</p>
        """, unsafe_allow_html=True)
    with col_h2:
        if st.button("▶ Zahájit trénink", type="primary", use_container_width=True):
            st.session_state["page"] = "scenario_browser"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # XP Progress bar
    next_level = level + 1
    next_threshold = LEVEL_THRESHOLDS.get(next_level, 25000)
    progress = get_xp_progress_pct(xp, level)

    st.markdown(f"""
    <div class="cc-xp-bar">
        <div class="header">
            <div class="level">
                <span class="material-symbols-outlined">military_tech</span>
                <strong>Level {level}</strong>
            </div>
            <div class="xp">{xp:,} / {next_threshold:,} XP</div>
        </div>
        <div class="bar">
            <div class="fill" style="width:{progress}%;"></div>
        </div>
        <div style="text-align:right;color:var(--text-muted);font-size:0.75em;margin-top:4px;">
            Další úroveň: {next_level}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats row
    stats = get_user_stats(user_id)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="cc-metric">
            <span class="material-symbols-outlined bg-icon">history</span>
            <div class="label">Celkem relací</div>
            <div class="value">{stats.get("total_sessions", 0)}</div>
            <div class="trend up">
                <span class="material-symbols-outlined" style="font-size:14px;">trending_up</span>
                +2 tento týden
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        avg = stats.get("avg_score", 0)
        st.markdown(f"""
        <div class="cc-metric">
            <span class="material-symbols-outlined bg-icon">score</span>
            <div class="label">Průměrné skóre</div>
            <div class="value">{format_score(avg)}</div>
            <div class="trend up">
                <span class="material-symbols-outlined" style="font-size:14px;">trending_up</span>
                +1,5%
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        streak = user.get("streak_days", 0)
        st.markdown(f"""
        <div class="cc-metric">
            <span class="material-symbols-outlined bg-icon">local_fire_department</span>
            <div class="label">Aktuální streak</div>
            <div class="value">{streak} dní</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two columns
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Recent Achievements
        achievements = get_earned_achievements(user_id)
        if achievements:
            st.markdown("<h3>Poslední úspěchy</h3>", unsafe_allow_html=True)
            ach_colors = ["amber", "emerald", "purple", "amber"]
            ach_html = '<div style="display:flex;gap:16px;overflow-x:auto;padding-bottom:8px;">'
            for i, ach in enumerate(achievements[:4]):
                color = ach_colors[i % len(ach_colors)]
                ach_html += f"""
                <div class="cc-achievement earned-{color}" style="min-width:160px;">
                    <div style="font-size:1.8em;">{ach.get('icon', '🏆')}</div>
                    <div class="ach-name">{ach.get('name', '')}</div>
                    <div class="ach-sub">{ach.get('description', '')[:30]}</div>
                </div>"""
            ach_html += """
            <div class="cc-achievement locked" style="min-width:120px;cursor:pointer;">
                <span class="material-symbols-outlined" style="font-size:24px;color:var(--text-muted);">lock</span>
                <div class="ach-sub">Zobrazit vše</div>
            </div></div>"""
            st.markdown(ach_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # Recent Sessions table
        st.markdown("<h3>Poslední relace</h3>", unsafe_allow_html=True)
        recent = get_user_recent_sessions(user_id, limit=5)
        if recent:
            table_html = """<table class="cc-table">
                <thead><tr>
                    <th>Název scénáře</th><th>Datum</th><th>Skóre</th><th>Délka</th>
                </tr></thead><tbody>"""
            for session in recent:
                cat = CATEGORIES.get(session.get("category", ""), {})
                score = session.get("overall_score")
                score_cls = "score-green" if score and score >= 80 else "score-amber" if score and score >= 60 else "score-red"
                date_str = session.get("started_at", "")[:10]
                table_html += f"""<tr>
                    <td><div class="name">{session.get('scenario_name', '')}</div>
                        <div class="sub">{cat.get('label', '')}</div></td>
                    <td style="color:var(--text-secondary);">{date_str}</td>
                    <td><span class="score-badge {score_cls}">{format_score(score)}</span></td>
                    <td style="color:var(--text-secondary);">{format_duration(session.get('duration_seconds'))}</td>
                </tr>"""
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("Zatím žádné relace. Zahajte trénink!")

    with col_right:
        # Active Milestones
        total = stats.get("total_sessions", 0)
        milestones = [
            ("Dokončit 5 prodejních scénářů", f"{min(total, 5)}/5", min(100, int((total / 5) * 100)), "var(--primary)"),
            ("Dosáhnout Level 15", f"Lv {level}", min(100, int((level / 15) * 100)), "#8b5cf6"),
            ("Udržet 90% průměrné skóre", format_score(stats.get("avg_score")), min(100, int((stats.get("avg_score", 0) or 0) / 90 * 100)), "#f59e0b"),
        ]

        st.markdown("""<div class="cc-card">
            <h3 style="display:flex;align-items:center;gap:8px;margin:0 0 16px;">
                <span class="material-symbols-outlined" style="color:var(--primary);">flag</span>
                Aktivní milníky
            </h3>""", unsafe_allow_html=True)

        for label, val, pct, color in milestones:
            st.markdown(f"""
            <div style="margin-bottom:16px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-size:0.9em;font-weight:500;color:var(--text);">{label}</span>
                    <span style="font-size:0.8em;color:var(--text-secondary);">{val}</span>
                </div>
                <div style="height:8px;border-radius:999px;background:var(--border);overflow:hidden;">
                    <div style="height:100%;border-radius:999px;background:{color};width:{pct}%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Pro Tip
        st.markdown("""
        <div class="cc-tip">
            <div class="tip-label">
                <span class="material-symbols-outlined">tips_and_updates</span>
                Pro Tip
            </div>
            <div class="tip-text">
                V poslední relaci AI zaznamenala mírné uspěchání při závěru. Zkuste po sdělení ceny
                udělat 2sekundovou pauzu, aby zákazník mohl informaci zpracovat.
            </div>
        </div>""", unsafe_allow_html=True)
