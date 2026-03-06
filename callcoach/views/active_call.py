import streamlit as st
import time
from datetime import datetime
from services.scenario_service import get_scenario, get_scenario_checkpoints
from services.elevenlabs_service import get_signed_url, generate_system_prompt
from database.db import execute
from config import CATEGORIES, ELEVENLABS_API_KEY


def render():
    scenario_id = st.session_state.get("selected_scenario")
    if not scenario_id:
        st.warning("Žádný scénář vybrán.")
        return

    scenario = get_scenario(scenario_id)
    checkpoints = get_scenario_checkpoints(scenario_id)
    user = st.session_state.get("user", {})
    cat = CATEGORIES.get(scenario["category"], {"label": scenario["category"], "color": "#6b7280"})

    # Create session if not exists
    if "active_session_id" not in st.session_state:
        session_id = execute("""
            INSERT INTO sessions (user_id, scenario_id, started_at, status)
            VALUES (?, ?, ?, 'in_progress')
        """, (user.get("id"), scenario_id, datetime.now().isoformat()))
        st.session_state["active_session_id"] = session_id
        st.session_state["call_start_time"] = time.time()

    # Header
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0;">
        <h2 style="margin:0 0 8px;">{scenario['name']}</h2>
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
            <span class="cc-pulse"></span>
            <span style="color:var(--red);font-weight:600;font-size:0.9em;">Hovor probíhá</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Timer
    if "call_start_time" in st.session_state:
        elapsed = int(time.time() - st.session_state["call_start_time"])
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_str = f"{minutes:02d}:{seconds:02d}"
    else:
        timer_str = "00:00"

    st.markdown(f'<div class="cc-timer">{timer_str}</div>', unsafe_allow_html=True)

    # Audio waveform visualization
    import random
    bars = "".join(
        f'<rect x="{i * 10}" y="{30 - random.randint(4, 25)}" width="6" height="{random.randint(8, 50)}" rx="3" />'
        for i in range(30)
    )
    st.markdown(f"""
    <div style="text-align:center;margin:24px 0;">
        <svg width="300" height="60" viewBox="0 0 300 60" style="margin:0 auto;">
            <g fill="var(--primary)" opacity="0.6">{bars}</g>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # Main layout
    col_main, col_side = st.columns([3, 1])

    with col_main:
        if ELEVENLABS_API_KEY and scenario.get("elevenlabs_agent_id"):
            st.markdown("""
            <div class="cc-card" style="text-align:center;">
                <span class="material-symbols-outlined" style="font-size:32px;color:var(--primary);">mic</span>
                <p style="color:var(--primary);font-weight:600;">ElevenLabs Voice AI aktivní</p>
                <p style="color:var(--text-secondary);font-size:0.85em;">Mluvte do mikrofonu — AI zákazník poslouchá</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="cc-card" style="text-align:center;">
                <p style="color:var(--text-secondary);font-size:0.9em;">
                    <strong>Demo režim</strong> — ElevenLabs API není nakonfigurováno.<br>
                    Hovor probíhá v simulovaném režimu.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # First message from customer
            st.markdown(f"""
            <div class="cc-card" style="margin-top:16px;background:var(--bg-hover);">
                <div style="font-weight:600;color:var(--text-secondary);font-size:0.8em;margin-bottom:6px;">
                    {scenario.get('persona_name', 'Zákazník')}:
                </div>
                <p style="color:var(--text);margin:0;">„{scenario.get('first_message', '')}"</p>
            </div>
            """, unsafe_allow_html=True)

            st.text_area(
                "Vaše odpověď",
                placeholder="Napište svou odpověď zákazníkovi...",
                key="demo_response",
            )

    with col_side:
        # Objectives sidebar
        st.markdown("""
        <div class="cc-card">
            <h4 style="display:flex;align-items:center;gap:8px;margin:0 0 12px;">
                <span class="material-symbols-outlined" style="color:var(--primary);">checklist</span>
                Cíle
            </h4>
        """, unsafe_allow_html=True)
        for cp in checkpoints:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:8px;padding:6px 0;">
                <span style="color:var(--text-muted);">○</span>
                <span style="font-size:0.85em;color:var(--text);">{cp['name']}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="cc-card" style="margin-top:16px;padding:12px;">
            <span style="font-size:0.8em;color:var(--text-secondary);">
                🤖 AI analyzuje váš tón a empatii v reálném čase
            </span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # End call button
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🔴 Ukončit hovor", type="primary", use_container_width=True):
            _end_call(scenario, checkpoints)


def _end_call(scenario, checkpoints):
    session_id = st.session_state.get("active_session_id")
    if not session_id:
        return

    elapsed = int(time.time() - st.session_state.get("call_start_time", time.time()))

    demo_response = st.session_state.get("demo_response", "")
    transcript = f"Zákazník ({scenario.get('persona_name', 'Zákazník')}): {scenario.get('first_message', '')}\n"
    if demo_response:
        transcript += f"Agent: {demo_response}\n"

    execute("""
        UPDATE sessions SET ended_at = ?, duration_seconds = ?, transcript = ?, status = 'completed'
        WHERE id = ?
    """, (datetime.now().isoformat(), elapsed, transcript, session_id))

    st.session_state["completed_session_id"] = session_id
    st.session_state.pop("active_session_id", None)
    st.session_state.pop("call_start_time", None)

    st.session_state["page"] = "evaluating"
    st.rerun()
