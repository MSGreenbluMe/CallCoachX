import streamlit as st
import time
import json
from datetime import datetime
from services.scenario_service import get_scenario, get_scenario_checkpoints
from services.elevenlabs_service import get_signed_url, generate_system_prompt
from database.db import execute, query
from config import CATEGORIES, ELEVENLABS_API_KEY


def render():
    scenario_id = st.session_state.get("selected_scenario")
    if not scenario_id:
        st.warning("Žiadny scenár vybraný.")
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
        <span style="background:{cat.get('color', '#6b7280')}15;color:{cat.get('color', '#6b7280')};
                     padding:4px 12px;border-radius:12px;font-size:0.8em;font-weight:600;">
            {cat.get('label', '')}
        </span>
        <h2 style="margin:12px 0 4px;color:#1e293b;">{scenario['name']}</h2>
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:8px;">
            <span style="width:8px;height:8px;background:#ef4444;border-radius:50%;display:inline-block;
                         animation:pulse 1.5s infinite;"></span>
            <span style="color:#ef4444;font-weight:600;font-size:0.9em;">Hovor prebieha</span>
        </div>
    </div>
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # Timer
    if "call_start_time" in st.session_state:
        elapsed = int(time.time() - st.session_state["call_start_time"])
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_str = f"{minutes:02d}:{seconds:02d}"
    else:
        timer_str = "00:00"

    st.markdown(f"""
    <div style="text-align:center;margin:24px 0;">
        <div class="call-timer">{timer_str}</div>
    </div>
    """, unsafe_allow_html=True)

    # Audio waveform visualization (static representation)
    st.markdown("""
    <div style="text-align:center;margin:24px 0;">
        <svg width="300" height="60" viewBox="0 0 300 60" style="margin:0 auto;">
            <g fill="#137fec" opacity="0.6">
    """, unsafe_allow_html=True)

    import random
    bars_html = ""
    for i in range(30):
        h = random.randint(8, 50)
        x = i * 10
        bars_html += f'<rect x="{x}" y="{30 - h//2}" width="6" height="{h}" rx="3" />'

    st.markdown(f"""
            {bars_html}
            </g>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # Main layout
    col_main, col_side = st.columns([3, 1])

    with col_main:
        # ElevenLabs integration area
        if ELEVENLABS_API_KEY and scenario.get("elevenlabs_agent_id"):
            st.markdown("""
            <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;padding:20px;text-align:center;">
                <span class="material-symbols-outlined" style="font-size:32px;color:#137fec;">mic</span>
                <p style="color:#137fec;font-weight:600;">ElevenLabs Voice AI aktívna</p>
                <p style="color:#6b7280;font-size:0.85em;">Hovorte do mikrofónu — AI zákazník počúva</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Demo / text mode
            st.markdown("""
            <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;padding:20px;">
                <p style="color:#6b7280;font-size:0.9em;text-align:center;">
                    <strong>Demo mód</strong> — ElevenLabs API nie je nakonfigurované.<br>
                    Hovor prebieha v simulovanom režime.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Show first message from customer
            st.markdown(f"""
            <div style="background:#f0f0f0;border-radius:12px;padding:16px;margin-top:16px;">
                <div style="font-weight:600;color:#6b7280;font-size:0.8em;margin-bottom:6px;">
                    {scenario.get('persona_name', 'Zákazník')}:
                </div>
                <p style="color:#1e293b;margin:0;">"{scenario.get('first_message', '')}"</p>
            </div>
            """, unsafe_allow_html=True)

            # Text input for demo
            user_response = st.text_area(
                "Vaša odpoveď",
                placeholder="Napíšte svoju odpoveď zákazníkovi...",
                key="demo_response",
            )

    with col_side:
        # Objectives sidebar
        with st.expander("📋 Pripomienka cieľov", expanded=False):
            for cp in checkpoints:
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:8px;padding:6px 0;">
                    <span style="color:#d1d5db;">○</span>
                    <span style="font-size:0.85em;color:#374151;">{cp['name']}</span>
                </div>
                """, unsafe_allow_html=True)

        # AI analysis note
        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin-top:16px;">
            <span style="font-size:0.8em;color:#6b7280;">
                🤖 AI analyzuje váš tón a empatiu v reálnom čase
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # End call button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔴 Ukončiť hovor", type="primary", use_container_width=True):
            _end_call(scenario, checkpoints)


def _end_call(scenario, checkpoints):
    session_id = st.session_state.get("active_session_id")
    if not session_id:
        return

    elapsed = int(time.time() - st.session_state.get("call_start_time", time.time()))

    # Build demo transcript
    demo_response = st.session_state.get("demo_response", "")
    transcript = f"Zákazník ({scenario.get('persona_name', 'Zákazník')}): {scenario.get('first_message', '')}\n"
    if demo_response:
        transcript += f"Agent: {demo_response}\n"

    # Update session
    execute("""
        UPDATE sessions SET ended_at = ?, duration_seconds = ?, transcript = ?, status = 'completed'
        WHERE id = ?
    """, (datetime.now().isoformat(), elapsed, transcript, session_id))

    # Clean up
    st.session_state["completed_session_id"] = session_id
    if "active_session_id" in st.session_state:
        del st.session_state["active_session_id"]
    if "call_start_time" in st.session_state:
        del st.session_state["call_start_time"]

    st.session_state["page"] = "evaluating"
    st.rerun()
