import streamlit as st
from services.scenario_service import get_scenario, get_scenario_checkpoints
from config import CATEGORIES
from utils.helpers import difficulty_stars_html, category_badge_html


def render():
    scenario_id = st.session_state.get("selected_scenario")
    if not scenario_id:
        st.warning("Žádný scénář vybrán.")
        if st.button("Zpět na scénáře"):
            st.session_state["page"] = "scenario_browser"
            st.rerun()
        return

    scenario = get_scenario(scenario_id)
    checkpoints = get_scenario_checkpoints(scenario_id)

    if not scenario:
        st.error("Scénář nebyl nalezen.")
        return

    cat = CATEGORIES.get(scenario["category"], {"label": scenario["category"], "color": "#6b7280"})

    # Back button
    if st.button("← Zpět na scénáře"):
        st.session_state["page"] = "scenario_browser"
        st.rerun()

    # Header
    st.markdown(f"""
    <div style="margin-top:16px;">
        {category_badge_html(scenario['category'])}
        <h1 style="margin:12px 0 8px;">{scenario['name']}</h1>
        <div style="margin-bottom:16px;">
            {difficulty_stars_html(scenario['difficulty'])}
            <span style="color:var(--text-secondary);margin-left:12px;">Obtížnost {scenario['difficulty']}/5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Two columns
    col_left, col_right = st.columns(2)

    with col_left:
        # Context
        st.markdown(f"""
        <div class="cc-card" style="margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span class="material-symbols-outlined" style="color:var(--primary);">info</span>
                <h3 style="margin:0;">Kontext</h3>
            </div>
            <p style="color:var(--text-secondary);line-height:1.6;">{scenario.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Customer info
        st.markdown(f"""
        <div class="cc-card">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:48px;height:48px;background:linear-gradient(135deg,var(--border),var(--text-muted));
                            border-radius:50%;display:flex;align-items:center;justify-content:center;
                            font-weight:700;color:var(--bg);font-size:1.2em;">
                    {scenario.get('persona_name', 'Z')[0]}
                </div>
                <div>
                    <h3 style="margin:0;">{scenario.get('persona_name', 'Zákazník')}</h3>
                    <span style="color:var(--text-secondary);font-size:0.85em;">Zákazník</span>
                </div>
            </div>
            <p style="color:var(--text-secondary);font-size:0.9em;line-height:1.5;">
                {_get_public_background(scenario)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Goal
        st.markdown(f"""
        <div class="cc-card" style="border-left:4px solid var(--primary);margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <span class="material-symbols-outlined" style="color:var(--primary);">flag</span>
                <h3 style="margin:0;">Váš cíl</h3>
            </div>
            <p style="font-weight:600;font-size:1.05em;line-height:1.5;color:var(--text);">
                {scenario.get('primary_goal', '')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Checkpoints
        cp_html = """
        <div class="cc-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
                <span class="material-symbols-outlined" style="color:var(--primary);">checklist</span>
                <h3 style="margin:0;">Povinné body</h3>
            </div>"""
        for cp in checkpoints:
            cp_html += f"""
            <div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);">
                <span style="color:var(--text-muted);font-size:1.2em;margin-top:2px;">○</span>
                <div>
                    <div style="font-weight:600;font-size:0.9em;color:var(--text);">{cp['name']}</div>
                    <div style="color:var(--text-secondary);font-size:0.8em;">{cp.get('description', '')}</div>
                </div>
            </div>"""
        cp_html += "</div>"
        st.markdown(cp_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Footer
    col_note, col_btn = st.columns([2, 1])
    with col_note:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;color:var(--text-secondary);font-size:0.85em;">
            <span class="material-symbols-outlined" style="font-size:18px;">info</span>
            Tento hovor bude nahráván a vyhodnocen AI
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button("📞 Zahájit tréninkový hovor", type="primary", use_container_width=True):
            st.session_state["page"] = "active_call"
            st.rerun()


def _get_public_background(scenario):
    return scenario.get("persona_background", "")
