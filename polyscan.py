# --- DASHBOARD ANZEIGE ---
st.divider()

# Wir erstellen 4 Spalten mit deinen neuen Namen
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.subheader("🐟 Fish") # Vorher "Small Fish"
    if not existing_data.empty:
        # Filter: 10$ bis 10.000$
        df_fish = existing_data[(existing_data['Betrag'] >= 10) & (existing_data['Betrag'] < 10000)]
        st.dataframe(df_fish.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")

with c2:
    st.subheader("🐬 Dolphin") # Vorher "Whale"
    if not existing_data.empty:
        # Filter: 10.000$ bis 100.000$
        df_dolphin = existing_data[(existing_data['Betrag'] >= 10000) & (existing_data['Betrag'] < 100000)]
        st.dataframe(df_dolphin.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")

with c3:
    st.subheader("🐳 Whale") # Vorher "Dolphin"
    if not existing_data.empty:
        # Filter: 100.000$ bis 500.000$
        df_whale = existing_data[(existing_data['Betrag'] >= 100000) & (existing_data['Betrag'] < 500000)]
        st.dataframe(df_whale.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")

with c4:
    st.subheader("🚨 Megalodon")
    if not existing_data.empty:
        # Filter: Über 500.000$
        df_mega = existing_data[existing_data['Betrag'] >= 500000]
        st.dataframe(df_mega.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")
