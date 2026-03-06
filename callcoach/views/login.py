import streamlit as st
from database.db import query


def render():
    st.markdown("""
    <div style="text-align:center;padding:20px 0 8px;">
        <span class="material-symbols-outlined" style="font-size:32px;color:var(--primary);">headset_mic</span>
        <h2 style="color:var(--primary);margin:4px 0;">CallCoach</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="cc-card" style="padding:32px;">
            <div style="text-align:center;margin-bottom:24px;">
                <h2 style="margin:0 0 4px;">Vítejte zpět</h2>
                <p style="color:var(--text-secondary);">Přihlaste se do tréninkové platformy</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        role = st.radio(
            "Role",
            ["Agent", "Manažer"],
            horizontal=True,
            label_visibility="collapsed",
        )

        users = query(
            "SELECT * FROM users WHERE role = ? ORDER BY name",
            ("agent" if role == "Agent" else "manager",),
        )

        if not users:
            st.warning("Žádní uživatelé v databázi.")
            return

        user_names = [u["name"] for u in users]
        selected_name = st.selectbox(
            "Uživatel",
            user_names,
            label_visibility="collapsed",
            placeholder="Vyberte uživatele...",
        )

        team_code = st.text_input(
            "Kód týmu",
            placeholder="Zadejte kód týmu",
            value="demo",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Přihlásit se", type="primary", use_container_width=True):
            selected_user = next((u for u in users if u["name"] == selected_name), None)
            if selected_user:
                st.session_state["user"] = dict(selected_user)
                st.session_state["page"] = "agent_home" if role == "Agent" else "manager_dashboard"
                st.rerun()
            else:
                st.error("Vyberte uživatele.")

        st.markdown("""
        <div style="text-align:center;margin-top:20px;padding-top:16px;border-top:1px solid var(--border);">
            <p style="color:var(--text-secondary);font-size:0.85em;">
                Potřebujete přístup? Kontaktujte svého administrátora.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        mode_label = "☀️ Světlý režim" if st.session_state.get("dark_mode") else "🌙 Tmavý režim"
        if st.button(mode_label, key="login_mode_toggle", use_container_width=True):
            st.session_state["dark_mode"] = not st.session_state.get("dark_mode", True)
            st.rerun()
