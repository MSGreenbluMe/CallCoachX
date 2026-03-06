import streamlit as st
import json
import time
from services.evaluation_service import get_session_evaluation, save_evaluation
from services.scenario_service import get_scenario, get_scenario_checkpoints
from services.gemini_service import evaluate_call
from services.gamification_service import calculate_xp_for_session, award_xp, check_and_award_achievements
from components.radar_chart import create_radar_chart
from database.db import query
from utils.helpers import score_color, goal_badge, format_duration


def render_evaluating():
    session_id = st.session_state.get("completed_session_id")
    if not session_id:
        st.session_state["page"] = "agent_home"
        st.rerun()
        return

    session = query("SELECT * FROM sessions WHERE id = ?", (session_id,), one=True)
    if not session:
        st.error("Relace nenalezena.")
        return

    scenario = get_scenario(session["scenario_id"])
    checkpoints = get_scenario_checkpoints(session["scenario_id"])

    st.markdown("""
    <div style="text-align:center;margin-top:80px;">
        <div style="margin-bottom:16px;">
            <span style="background:var(--primary-10);color:var(--primary);padding:4px 14px;border-radius:12px;
                         font-size:0.8em;font-weight:600;">Powered by Gemini</span>
        </div>
        <h1>Vyhodnocuji váš hovor...</h1>
        <p style="color:var(--text-secondary);">AI analyzuje váš výkon</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress
    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = [
        (25, "📝 Přepisuji audio..."),
        (50, "🎯 Analyzuji plnění cílů..."),
        (75, "📊 Hodnotím kvalitu komunikace..."),
        (90, "💡 Generuji zpětnou vazbu..."),
    ]

    for pct, msg in steps:
        progress_bar.progress(pct)
        status_text.markdown(f"<p style='text-align:center;color:var(--text-secondary);'>{msg}</p>", unsafe_allow_html=True)
        time.sleep(0.8)

    # Run evaluation
    transcript = session.get("transcript", "")
    eval_data = evaluate_call(transcript, scenario, checkpoints)
    eval_id, overall_score = save_evaluation(session_id, eval_data)

    # XP
    user = st.session_state.get("user", {})
    user_id = user.get("id")
    xp_total, xp_reasons = calculate_xp_for_session(user_id, session_id, overall_score, session["scenario_id"])
    new_level = award_xp(user_id, session_id, xp_total, "; ".join(xp_reasons))

    # Achievements
    new_achievements = check_and_award_achievements(user_id)

    # Update session state
    updated_user = query("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if updated_user:
        st.session_state["user"] = dict(updated_user)

    st.session_state["eval_xp_earned"] = xp_total
    st.session_state["eval_xp_reasons"] = xp_reasons
    st.session_state["eval_new_achievements"] = new_achievements
    st.session_state["eval_new_level"] = new_level

    progress_bar.progress(100)
    status_text.markdown("<p style='text-align:center;color:var(--emerald);font-weight:600;'>✅ Hotovo!</p>", unsafe_allow_html=True)
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
        st.error("Data nenalezena.")
        return

    scenario = get_scenario(session["scenario_id"])
    checkpoints = get_scenario_checkpoints(session["scenario_id"])

    xp_earned = st.session_state.get("eval_xp_earned", 0)
    new_achievements = st.session_state.get("eval_new_achievements", [])

    # Header
    st.markdown("<h1 style='text-align:center;'>Výsledky hodnocení</h1>", unsafe_allow_html=True)

    # XP badge
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:24px;">
        <span class="score-badge score-green" style="padding:6px 16px;font-size:1em;">
            ⭐ Level Up! +{xp_earned} XP
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Achievement popups
    for ach in new_achievements:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fbbf24,#f59e0b);color:white;
                    border-radius:12px;padding:20px;text-align:center;margin:16px 0;">
            <div style="font-size:3em;margin-bottom:8px;">{ach.get('icon', '🏆')}</div>
            <div style="font-size:1.2em;font-weight:700;">Nový odznak!</div>
            <div style="font-size:1em;font-weight:600;margin-top:4px;">{ach.get('name', '')}</div>
        </div>""", unsafe_allow_html=True)

    # Main layout
    col_left, col_right = st.columns([1, 2])

    with col_left:
        # Big score
        overall = evaluation["overall_score"]
        color = score_color(overall)
        from utils.helpers import score_label
        label = score_label(overall)
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:4em;font-weight:800;color:{color};line-height:1;">{overall:.0f}%</div>
            <div style="color:{color};font-weight:600;margin-top:4px;font-size:1.1em;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Radar chart
        scores = {k: evaluation.get(k, 5) for k in [
            "communication_clarity", "empathy_rapport", "active_listening",
            "professional_language", "call_structure", "call_control", "objection_handling",
        ]}
        dark = st.session_state.get("dark_mode", True)
        fig = create_radar_chart(scores, title="Analýza dovedností")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)" if dark else "white",
            polar=dict(bgcolor="rgba(0,0,0,0)" if dark else "white"),
            font=dict(color="#f1f5f9" if dark else "#0f172a"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Goal status
        goal = evaluation.get("goal_achieved", "PARTIAL")
        glabel, gcolor, gicon = goal_badge(goal)
        st.markdown(f"""
        <div style="background:color-mix(in srgb, {gcolor} 15%, transparent);border:1px solid color-mix(in srgb, {gcolor} 30%, transparent);
                    border-radius:10px;padding:14px;margin-bottom:16px;">
            <span class="material-symbols-outlined" style="color:{gcolor};vertical-align:middle;">{gicon}</span>
            <strong style="color:{gcolor};margin-left:4px;">Cíl hovoru: {glabel}</strong>
        </div>
        """, unsafe_allow_html=True)

        # Checkpoints
        st.markdown("<h3>Plnění kontrolních bodů</h3>", unsafe_allow_html=True)
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
            cls = "passed" if passed else "failed"

            st.markdown(f"""
            <div class="cc-checkpoint {cls}">
                <span class="cp-icon">{status_icon}</span>
                <div>
                    <div class="cp-name">{cp.get('name', f'Bod {cp_id}')}</div>
                    <div class="cp-evidence">„{evidence}"</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Strengths & Improvements
        col_s, col_i = st.columns(2)
        with col_s:
            st.markdown("""<div class="cc-card">
                <h4 style="display:flex;align-items:center;gap:8px;margin:0 0 12px;">
                    <span class="material-symbols-outlined" style="color:var(--emerald);">thumb_up</span>
                    Silné stránky
                </h4>""", unsafe_allow_html=True)
            strengths = evaluation.get("strengths", "[]")
            if isinstance(strengths, str):
                try:
                    strengths = json.loads(strengths)
                except (json.JSONDecodeError, TypeError):
                    strengths = []
            for s in strengths:
                st.markdown(f'<div style="padding:4px 0;font-size:0.9em;color:var(--text);">• {s}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_i:
            st.markdown("""<div class="cc-card">
                <h4 style="display:flex;align-items:center;gap:8px;margin:0 0 12px;">
                    <span class="material-symbols-outlined" style="color:var(--amber);">construction</span>
                    Oblasti ke zlepšení
                </h4>""", unsafe_allow_html=True)
            improvements = evaluation.get("improvements", "[]")
            if isinstance(improvements, str):
                try:
                    improvements = json.loads(improvements)
                except (json.JSONDecodeError, TypeError):
                    improvements = []
            for imp in improvements:
                st.markdown(f'<div style="padding:4px 0;font-size:0.9em;color:var(--text);">• {imp}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Coaching tip
        coaching_tip = evaluation.get("coaching_tip", "")
        if coaching_tip:
            st.markdown(f"""
            <div class="cc-tip">
                <div class="tip-label">
                    <span class="material-symbols-outlined">psychology</span>
                    AI Coaching Tip
                </div>
                <div class="tip-text">{coaching_tip}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Transcript
    with st.expander("📄 Přepis hovoru"):
        transcript = session.get("transcript", "")
        if transcript:
            for line in transcript.split("\n"):
                if line.strip():
                    if line.startswith("Agent:"):
                        st.markdown(f"""
                        <div class="cc-card" style="margin:4px 0 4px 40px;background:var(--primary-10);">
                            <strong style="color:var(--primary);">Agent</strong><br>
                            {line.replace('Agent: ', '')}
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="cc-card" style="margin:4px 40px 4px 0;">
                            <strong style="color:var(--text-secondary);">Zákazník</strong><br>
                            {line.split(': ', 1)[-1] if ': ' in line else line}
                        </div>""", unsafe_allow_html=True)
        else:
            st.info("Přepis není k dispozici.")

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Domů", use_container_width=True):
            _cleanup_and_go("agent_home")
    with c2:
        if st.button("🔄 Zkusit znovu", use_container_width=True):
            st.session_state["page"] = "pre_call_briefing"
            st.rerun()
    with c3:
        if st.button("➡️ Další scénář", use_container_width=True):
            _cleanup_and_go("scenario_browser")


def _cleanup_and_go(page):
    for key in ["completed_session_id", "eval_xp_earned", "eval_xp_reasons",
                "eval_new_achievements", "eval_new_level", "selected_scenario"]:
        st.session_state.pop(key, None)
    st.session_state["page"] = page
    st.rerun()
