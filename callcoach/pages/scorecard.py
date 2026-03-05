import streamlit as st
import json
import time
from services.evaluation_service import get_session_evaluation, save_evaluation
from services.scenario_service import get_scenario, get_scenario_checkpoints
from services.gemini_service import evaluate_call
from services.gamification_service import calculate_xp_for_session, award_xp, check_and_award_achievements
from components.radar_chart import create_radar_chart
from components.score_card import render_big_score, render_metric_card
from components.achievement_badge import render_achievement_popup
from database.db import query
from utils.helpers import score_color, goal_badge, format_duration


def render_evaluating():
    """Loading screen while evaluation is happening."""
    session_id = st.session_state.get("completed_session_id")
    if not session_id:
        st.session_state["page"] = "agent_home"
        st.rerun()
        return

    session = query("SELECT * FROM sessions WHERE id = ?", (session_id,), one=True)
    if not session:
        st.error("Session nenájdená.")
        return

    scenario = get_scenario(session["scenario_id"])
    checkpoints = get_scenario_checkpoints(session["scenario_id"])

    st.markdown("""
    <div style="text-align:center;margin-top:80px;">
        <div style="margin-bottom:16px;">
            <span style="background:#e0e7ff;color:#4f46e5;padding:4px 12px;border-radius:12px;
                         font-size:0.8em;font-weight:600;">Powered by Gemini</span>
        </div>
        <h1 style="color:#1e293b;">Vyhodnocujem váš hovor...</h1>
        <p style="color:#6b7280;">AI analyzuje váš výkon</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress animation
    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = [
        (25, "📝 Spracovávam prepis hovoru..."),
        (50, "🎯 Analyzujem plnenie cieľov..."),
        (75, "📊 Vyhodnocujem kvalitu komunikácie..."),
        (90, "💡 Generujem spätnú väzbu..."),
    ]

    for pct, msg in steps:
        progress_bar.progress(pct)
        status_text.markdown(f"<p style='text-align:center;color:#6b7280;'>{msg}</p>", unsafe_allow_html=True)
        time.sleep(0.8)

    # Run evaluation
    transcript = session.get("transcript", "")
    eval_data = evaluate_call(transcript, scenario, checkpoints)
    eval_id, overall_score = save_evaluation(session_id, eval_data)

    # Calculate and award XP
    user = st.session_state.get("user", {})
    user_id = user.get("id")
    xp_total, xp_reasons = calculate_xp_for_session(user_id, session_id, overall_score, session["scenario_id"])
    new_level = award_xp(user_id, session_id, xp_total, "; ".join(xp_reasons))

    # Check achievements
    new_achievements = check_and_award_achievements(user_id)

    # Update user in session state
    updated_user = query("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if updated_user:
        st.session_state["user"] = dict(updated_user)

    # Store results for scorecard
    st.session_state["eval_xp_earned"] = xp_total
    st.session_state["eval_xp_reasons"] = xp_reasons
    st.session_state["eval_new_achievements"] = new_achievements
    st.session_state["eval_new_level"] = new_level

    progress_bar.progress(100)
    status_text.markdown("<p style='text-align:center;color:#10b981;font-weight:600;'>✅ Hotovo!</p>", unsafe_allow_html=True)
    time.sleep(0.5)

    st.session_state["page"] = "scorecard"
    st.rerun()


def render():
    session_id = st.session_state.get("completed_session_id")
    if not session_id:
        st.session_state["page"] = "agent_home"
        st.rerun()
        return

    session = query("SELECT * FROM sessions WHERE id = ?", (session_id,), one=True)
    evaluation = get_session_evaluation(session_id)
    if not session or not evaluation:
        st.error("Dáta nenájdené.")
        return

    scenario = get_scenario(session["scenario_id"])
    checkpoints = get_scenario_checkpoints(session["scenario_id"])

    xp_earned = st.session_state.get("eval_xp_earned", 0)
    new_achievements = st.session_state.get("eval_new_achievements", [])

    # Header
    st.markdown("<h1 style='text-align:center;'>Výsledky hodnotenia</h1>", unsafe_allow_html=True)

    # XP badge
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:24px;">
        <span style="background:#dcfce7;color:#16a34a;padding:6px 16px;border-radius:20px;font-weight:600;">
            ⭐ +{xp_earned} XP
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Achievement popups
    for ach in new_achievements:
        render_achievement_popup(ach)

    # Main layout
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Big score
        render_big_score(evaluation["overall_score"])
        st.markdown("<br>", unsafe_allow_html=True)

        # Radar chart
        scores = {
            "communication_clarity": evaluation.get("communication_clarity", 5),
            "empathy_rapport": evaluation.get("empathy_rapport", 5),
            "active_listening": evaluation.get("active_listening", 5),
            "professional_language": evaluation.get("professional_language", 5),
            "call_structure": evaluation.get("call_structure", 5),
            "call_control": evaluation.get("call_control", 5),
            "objection_handling": evaluation.get("objection_handling", 5),
        }
        fig = create_radar_chart(scores, title="Analýza zručností")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Goal status
        goal = evaluation.get("goal_achieved", "PARTIAL")
        label, color, icon = goal_badge(goal)
        st.markdown(f"""
        <div style="background:{color}15;border:1px solid {color}30;border-radius:10px;padding:14px;margin-bottom:16px;">
            <span class="material-symbols-outlined" style="color:{color};vertical-align:middle;">{icon}</span>
            <strong style="color:{color};margin-left:4px;">Cieľ hovoru: {label}</strong>
        </div>
        """, unsafe_allow_html=True)

        # Checkpoints
        st.markdown("### Plnenie checkpointov")
        checkpoint_results = []
        raw = evaluation.get("checkpoint_results")
        if raw:
            try:
                checkpoint_results = json.loads(raw) if isinstance(raw, str) else raw
            except (json.JSONDecodeError, TypeError):
                pass

        cp_map = {cp["id"]: cp for cp in checkpoints}
        for cr in checkpoint_results:
            cp_id = cr.get("checkpoint_id")
            passed = cr.get("passed", False)
            evidence = cr.get("evidence", "")
            cp = cp_map.get(cp_id, {})

            status_icon = "✅" if passed else "❌"
            bg_color = "#f0fdf4" if passed else "#fef2f2"
            border_color = "#10b981" if passed else "#ef4444"

            st.markdown(f"""
            <div class="checkpoint-item {'passed' if passed else 'failed'}">
                <span style="font-size:1.2em;">{status_icon}</span>
                <div>
                    <div style="font-weight:600;color:#1e293b;font-size:0.9em;">{cp.get('name', f'Checkpoint {cp_id}')}</div>
                    <div style="color:#6b7280;font-size:0.8em;font-style:italic;">"{evidence}"</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Strengths & Improvements
        col_s, col_i = st.columns(2)
        with col_s:
            st.markdown("### ✅ Silné stránky")
            strengths = evaluation.get("strengths", "[]")
            if isinstance(strengths, str):
                try:
                    strengths = json.loads(strengths)
                except (json.JSONDecodeError, TypeError):
                    strengths = []
            for s in strengths:
                st.markdown(f"- {s}")

        with col_i:
            st.markdown("### 🔧 Na zlepšenie")
            improvements = evaluation.get("improvements", "[]")
            if isinstance(improvements, str):
                try:
                    improvements = json.loads(improvements)
                except (json.JSONDecodeError, TypeError):
                    improvements = []
            for imp in improvements:
                st.markdown(f"- {imp}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Coaching tip
        coaching_tip = evaluation.get("coaching_tip", "")
        if coaching_tip:
            st.markdown(f"""
            <div class="coaching-tip-box">
                <h4>💡 Coaching tip</h4>
                <p style="font-size:0.9em;opacity:0.95;">{coaching_tip}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Transcript (expandable)
    with st.expander("📄 Prepis hovoru"):
        transcript = session.get("transcript", "")
        if transcript:
            for line in transcript.split("\n"):
                if line.strip():
                    if line.startswith("Agent:"):
                        st.markdown(f"""
                        <div style="background:#eff6ff;border-radius:8px;padding:10px 14px;margin:4px 0 4px 40px;">
                            <strong style="color:#137fec;">Agent</strong><br>
                            {line.replace('Agent: ', '')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:#f3f4f6;border-radius:8px;padding:10px 14px;margin:4px 40px 4px 0;">
                            <strong style="color:#6b7280;">Zákazník</strong><br>
                            {line.split(': ', 1)[-1] if ': ' in line else line}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Prepis nie je k dispozícii.")

    # Navigation buttons
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Domov", use_container_width=True):
            _cleanup_and_go("agent_home")
    with c2:
        if st.button("🔄 Skúsiť znova", use_container_width=True):
            st.session_state["page"] = "pre_call_briefing"
            st.rerun()
    with c3:
        if st.button("➡️ Ďalší scenár", use_container_width=True):
            _cleanup_and_go("scenario_browser")


def _cleanup_and_go(page):
    for key in ["completed_session_id", "eval_xp_earned", "eval_xp_reasons",
                "eval_new_achievements", "eval_new_level", "selected_scenario"]:
        st.session_state.pop(key, None)
    st.session_state["page"] = page
    st.rerun()
