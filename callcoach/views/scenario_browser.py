import streamlit as st
from services.scenario_service import get_all_scenarios, get_user_best_score, get_user_scenario_attempts
from config import CATEGORIES
from utils.helpers import difficulty_stars_html


def render():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.markdown("""
    <h1 style="margin-bottom:4px;">Knihovna scénářů</h1>
    <p style="color:var(--text-secondary);">Prohlížejte a spouštějte AI tréninkové scénáře</p>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Category tabs
    all_cats = ["Všechny scénáře"] + [v["label"] for v in CATEGORIES.values()]
    cat_keys = ["ALL"] + list(CATEGORIES.keys())

    selected_cat_label = st.radio(
        "Kategorie",
        all_cats,
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Get scenarios
    scenarios = get_all_scenarios()

    selected_idx = all_cats.index(selected_cat_label)
    if selected_idx > 0:
        selected_cat_key = cat_keys[selected_idx]
        scenarios = [s for s in scenarios if s["category"] == selected_cat_key]

    if not scenarios:
        st.info("Žádné scénáře pro vybraný filtr.")
        return

    # Gradient colors per category
    gradients = {
        "SALES": "linear-gradient(135deg, #10b981, #059669)",
        "RETENTION": "linear-gradient(135deg, #8b5cf6, #6d28d9)",
        "TECH_SUPPORT": "linear-gradient(135deg, #3b82f6, #2563eb)",
        "COMPLAINTS": "linear-gradient(135deg, #ef4444, #dc2626)",
        "BILLING": "linear-gradient(135deg, #f59e0b, #d97706)",
        "ONBOARDING": "linear-gradient(135deg, #06b6d4, #0891b2)",
    }
    cat_icons = {
        "SALES": "sell",
        "RETENTION": "loyalty",
        "TECH_SUPPORT": "devices",
        "COMPLAINTS": "warning",
        "BILLING": "receipt_long",
        "ONBOARDING": "person_add",
    }

    # Scenario grid
    cols = st.columns(3)
    for i, scenario in enumerate(scenarios):
        with cols[i % 3]:
            cat = CATEGORIES.get(scenario["category"], {"label": scenario["category"], "color": "#6b7280"})
            cat_icon = cat_icons.get(scenario["category"], "school")
            gradient = gradients.get(scenario["category"], "linear-gradient(135deg, #6b7280, #4b5563)")
            best_score = get_user_best_score(user_id, scenario["id"])
            attempts = get_user_scenario_attempts(user_id, scenario["id"])
            stars_html = difficulty_stars_html(scenario["difficulty"])

            # Status
            if best_score and best_score >= 95:
                best_html = f"""<span style="font-weight:700;color:#eab308;display:flex;align-items:center;gap:4px;">
                    <span class="material-symbols-outlined" style="font-size:16px;">workspace_premium</span>
                    {best_score:.0f}%</span>"""
                btn_label = "Opakovat scénář"
            elif best_score and best_score > 0:
                best_html = f'<span style="font-weight:700;color:#10b981;">{best_score:.0f}%</span>'
                btn_label = "Zahájit trénink"
            else:
                best_html = '<span style="color:var(--text-muted);">Nevyzkoušeno</span>'
                btn_label = "Zahájit trénink"

            # NEW badge for unattempted
            new_badge = ""
            if attempts == 0:
                new_badge = '<span class="cc-new-badge">NOVÝ</span>'

            st.markdown(f"""
            <div class="cc-scenario-card" style="margin-bottom:16px;">
                <div class="card-header" style="background:{gradient};">
                    <div style="display:flex;gap:8px;align-items:center;">
                        <span class="cat-badge">
                            <span class="material-symbols-outlined" style="font-size:14px;">{cat_icon}</span>
                            {cat['label']}
                        </span>
                        {new_badge}
                    </div>
                    <span class="dur-badge">~{scenario.get('estimated_duration_min', '?')} min</span>
                </div>
                <div class="card-body">
                    <h3>{scenario['name']}</h3>
                    <div style="margin-bottom:12px;">{stars_html}</div>
                    <div class="desc">{scenario.get('description', '')}</div>
                    <div class="card-footer">
                        <div class="best">
                            <span class="lbl">Osobní rekord</span>
                            {best_html}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(btn_label, key=f"start_{scenario['id']}", use_container_width=True):
                st.session_state["selected_scenario"] = scenario["id"]
                st.session_state["page"] = "pre_call_briefing"
                st.rerun()
