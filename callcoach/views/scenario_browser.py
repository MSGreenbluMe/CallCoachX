import streamlit as st
from services.scenario_service import get_all_scenarios, get_user_best_score, get_user_scenario_attempts
from config import CATEGORIES
from utils.helpers import difficulty_stars, category_badge_html


def render():
    user = st.session_state.get("user", {})
    user_id = user.get("id")

    st.markdown("""
    <h1 style="margin-bottom:4px;">Knižnica scenárov</h1>
    <p style="color:#6b7280;">Vyberte si AI tréningový scenár</p>
    """, unsafe_allow_html=True)

    # Filters
    all_cats = ["Všetky"] + [v["label"] for v in CATEGORIES.values()]
    cat_keys = ["ALL"] + list(CATEGORIES.keys())

    col_f1, col_f2, col_f3 = st.columns([3, 1, 1])
    with col_f1:
        selected_cat_label = st.radio(
            "Kategória",
            all_cats,
            horizontal=True,
            label_visibility="collapsed",
        )
    with col_f2:
        diff_filter = st.selectbox("Obtiažnosť", ["Všetky", "1 ★", "2 ★★", "3 ★★★", "4 ★★★★", "5 ★★★★★"], label_visibility="collapsed")
    with col_f3:
        sort_by = st.selectbox("Zoradiť", ["Odporúčané", "Obtiažnosť ↑", "Obtiažnosť ↓", "Názov"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    # Get scenarios
    scenarios = get_all_scenarios()

    # Filter by category
    selected_idx = all_cats.index(selected_cat_label)
    if selected_idx > 0:
        selected_cat_key = cat_keys[selected_idx]
        scenarios = [s for s in scenarios if s["category"] == selected_cat_key]

    # Filter by difficulty
    if diff_filter != "Všetky":
        diff_val = int(diff_filter[0])
        scenarios = [s for s in scenarios if s["difficulty"] == diff_val]

    # Sort
    if sort_by == "Obtiažnosť ↑":
        scenarios.sort(key=lambda s: s["difficulty"])
    elif sort_by == "Obtiažnosť ↓":
        scenarios.sort(key=lambda s: s["difficulty"], reverse=True)
    elif sort_by == "Názov":
        scenarios.sort(key=lambda s: s["name"])

    if not scenarios:
        st.info("Žiadne scenáre pre vybraný filter.")
        return

    # Scenario grid (3 columns)
    cols = st.columns(3)
    for i, scenario in enumerate(scenarios):
        with cols[i % 3]:
            cat = CATEGORIES.get(scenario["category"], {"label": scenario["category"], "color": "#6b7280"})
            best_score = get_user_best_score(user_id, scenario["id"])
            attempts = get_user_scenario_attempts(user_id, scenario["id"])

            # Status badge
            if best_score and best_score >= 80:
                status_html = f'<span style="color:#10b981;font-weight:600;">✓ Zvládnutý ({best_score:.0f}%)</span>'
            elif attempts > 0:
                status_html = f'<span style="color:#f59e0b;font-weight:600;">Absolvovaný ({best_score:.0f}%)</span>'
            else:
                status_html = '<span style="background:#137fec;color:white;padding:2px 8px;border-radius:4px;font-size:0.75em;font-weight:600;">NOVÝ</span>'

            # Card header gradient
            gradient_colors = {
                "SALES": "linear-gradient(135deg, #10b981, #059669)",
                "RETENTION": "linear-gradient(135deg, #8b5cf6, #6d28d9)",
                "TECH_SUPPORT": "linear-gradient(135deg, #3b82f6, #2563eb)",
                "COMPLAINTS": "linear-gradient(135deg, #ef4444, #dc2626)",
                "BILLING": "linear-gradient(135deg, #f59e0b, #d97706)",
                "ONBOARDING": "linear-gradient(135deg, #06b6d4, #0891b2)",
            }
            gradient = gradient_colors.get(scenario["category"], "linear-gradient(135deg, #6b7280, #4b5563)")

            st.markdown(f"""
            <div class="scenario-card" style="margin-bottom:16px;">
                <div style="background:{gradient};padding:24px 20px 16px;position:relative;">
                    <span style="background:rgba(255,255,255,0.2);color:white;padding:2px 8px;
                                 border-radius:4px;font-size:0.75em;font-weight:600;">
                        {cat['label']}
                    </span>
                    <span style="position:absolute;right:16px;top:16px;background:rgba(255,255,255,0.2);
                                 color:white;padding:2px 8px;border-radius:4px;font-size:0.75em;">
                        ~{scenario.get('estimated_duration_min', '?')} min
                    </span>
                </div>
                <div style="padding:16px 20px;">
                    <h3 style="margin:0 0 8px;font-size:1.05em;color:#1e293b;">{scenario['name']}</h3>
                    <div style="color:#f59e0b;margin-bottom:8px;">{difficulty_stars(scenario['difficulty'])}</div>
                    <p style="color:#6b7280;font-size:0.85em;margin-bottom:12px;
                              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
                        {scenario.get('description', '')}
                    </p>
                    <div style="margin-bottom:12px;">{status_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_label = "Opakovať scenár" if attempts > 0 else "Začať tréning"
            if st.button(btn_label, key=f"start_{scenario['id']}", use_container_width=True):
                st.session_state["selected_scenario"] = scenario["id"]
                st.session_state["page"] = "pre_call_briefing"
                st.rerun()
