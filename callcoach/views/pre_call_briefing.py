import streamlit as st
from services.scenario_service import get_scenario, get_scenario_checkpoints
from config import CATEGORIES
from utils.helpers import difficulty_stars, category_badge_html


def render():
    scenario_id = st.session_state.get("selected_scenario")
    if not scenario_id:
        st.warning("Žiadny scenár vybraný.")
        if st.button("Späť na scenáre"):
            st.session_state["page"] = "scenario_browser"
            st.rerun()
        return

    scenario = get_scenario(scenario_id)
    checkpoints = get_scenario_checkpoints(scenario_id)

    if not scenario:
        st.error("Scenár nebol nájdený.")
        return

    cat = CATEGORIES.get(scenario["category"], {"label": scenario["category"], "color": "#6b7280"})

    # Header
    if st.button("← Späť na scenáre"):
        st.session_state["page"] = "scenario_browser"
        st.rerun()

    st.markdown(f"""
    <div style="margin-top:16px;">
        {category_badge_html(scenario['category'])}
        <h1 style="margin:12px 0 8px;">{scenario['name']}</h1>
        <div style="color:#f59e0b;margin-bottom:16px;">
            {difficulty_stars(scenario['difficulty'])}
            <span style="color:#6b7280;margin-left:12px;">Obtiažnosť {scenario['difficulty']}/5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Two columns
    col_left, col_right = st.columns(2)

    with col_left:
        # Context
        st.markdown(f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:20px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span class="material-symbols-outlined" style="color:#137fec;">info</span>
                <h3 style="margin:0;color:#1e293b;">Kontext</h3>
            </div>
            <p style="color:#374151;line-height:1.6;">{scenario.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Customer info (without revealing mood/patience)
        st.markdown(f"""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:20px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:48px;height:48px;background:linear-gradient(135deg,#e5e7eb,#d1d5db);
                            border-radius:50%;display:flex;align-items:center;justify-content:center;
                            font-weight:700;color:#6b7280;font-size:1.2em;">
                    {scenario.get('persona_name', 'Z')[0]}
                </div>
                <div>
                    <h3 style="margin:0;">{scenario.get('persona_name', 'Zákazník')}</h3>
                    <span style="color:#6b7280;font-size:0.85em;">Zákazník</span>
                </div>
            </div>
            <p style="color:#374151;font-size:0.9em;line-height:1.5;">
                {_get_public_background(scenario)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Goal
        st.markdown(f"""
        <div style="background:white;border-left:4px solid #137fec;border-radius:0 12px 12px 0;
                     padding:20px;margin-bottom:16px;border:1px solid #e5e7eb;border-left:4px solid #137fec;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span class="material-symbols-outlined" style="color:#137fec;">flag</span>
                <h3 style="margin:0;color:#1e293b;">Váš cieľ</h3>
            </div>
            <p style="color:#1e293b;font-weight:600;font-size:1.05em;line-height:1.5;">
                {scenario.get('primary_goal', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Checkpoints
        st.markdown("""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:20px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                <span class="material-symbols-outlined" style="color:#137fec;">checklist</span>
                <h3 style="margin:0;color:#1e293b;">Povinné body</h3>
            </div>
        """, unsafe_allow_html=True)

        for cp in checkpoints:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;">
                <span style="color:#d1d5db;font-size:1.2em;">○</span>
                <div>
                    <div style="font-weight:600;color:#1e293b;font-size:0.9em;">{cp['name']}</div>
                    <div style="color:#6b7280;font-size:0.8em;">{cp.get('description', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Footer
    col_note, col_btn = st.columns([2, 1])
    with col_note:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;color:#6b7280;font-size:0.85em;">
            <span class="material-symbols-outlined" style="font-size:18px;">info</span>
            Tento hovor bude nahrávaný a vyhodnotený AI
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button("📞 Spustiť hovor", type="primary", use_container_width=True):
            st.session_state["page"] = "active_call"
            st.rerun()


def _get_public_background(scenario):
    """Return a public-safe version of persona background (no mood/patience reveal)."""
    bg = scenario.get("persona_background", "")
    # Just show the background story without hidden details
    return bg
