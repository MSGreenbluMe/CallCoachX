import streamlit as st
from database.db import query


def render():
    st.markdown("""
    <div style="text-align:center;margin-top:60px;margin-bottom:40px;">
        <span class="material-symbols-outlined" style="font-size:48px;color:#137fec;">headset_mic</span>
        <h1 style="color:#137fec;margin:8px 0 4px;">CallCoach</h1>
        <p style="color:#6b7280;">Tréningový simulátor pre call centrá</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="background:white;border:1px solid #e5e7eb;border-radius:16px;padding:32px;">
            <h2 style="text-align:center;margin-bottom:4px;">Vitajte späť</h2>
            <p style="text-align:center;color:#6b7280;margin-bottom:24px;">Prihláste sa do tréningovej platformy</p>
        </div>
        """, unsafe_allow_html=True)

        role = st.radio(
            "Vyberte rolu",
            ["Agent", "Manažér"],
            horizontal=True,
            label_visibility="collapsed",
        )

        users = query(
            "SELECT * FROM users WHERE role = ? ORDER BY name",
            ("agent" if role == "Agent" else "manager",),
        )

        if not users:
            st.warning("Žiadni používatelia v databáze. Spustite seed.")
            return

        user_names = [u["name"] for u in users]
        selected_name = st.selectbox("Používateľ", user_names, label_visibility="collapsed",
                                      placeholder="Vyberte používateľa")

        team_code = st.text_input("Team kód", placeholder="Zadajte kód tímu", value="demo")

        if st.button("Prihlásiť sa", type="primary", use_container_width=True):
            selected_user = next((u for u in users if u["name"] == selected_name), None)
            if selected_user:
                st.session_state["user"] = dict(selected_user)
                st.session_state["page"] = "agent_home" if role == "Agent" else "manager_dashboard"
                st.rerun()
            else:
                st.error("Vyberte používateľa.")

        st.markdown("""
        <div style="text-align:center;margin-top:20px;">
            <p style="color:#9ca3af;font-size:0.85em;">Potrebujete prístup? Kontaktujte svojho administrátora.</p>
        </div>
        """, unsafe_allow_html=True)
