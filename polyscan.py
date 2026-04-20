# --- DASHBOARD ANZEIGE ---
st.divider()

# Wir erstellen die Spalten IMMER
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.subheader("🐟 Small Fish")
    if not existing_data.empty:
        df_fish = existing_data[(existing_data['Betrag'] >= 10) & (existing_data['Betrag'] < 10000)]
        st.dataframe(df_fish.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")

with c2:
    st.subheader("🐳 Whales")
    if not existing_data.empty:
        df_whale = existing_data[(existing_data['Betrag'] >= 10000) & (existing_data['Betrag'] < 100000)]
        st.dataframe(df_whale.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")

with c3:
    st.subheader("🐬 Dolphins")
    if not existing_data.empty:
        df_dolphin = existing_data[(existing_data['Betrag'] >= 100000) & (existing_data['Betrag'] < 500000)]
        st.dataframe(df_dolphin.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")

with c4:
    st.subheader("🚨 Megalodons")
    if not existing_data.empty:
        df_mega = existing_data[existing_data['Betrag'] >= 500000]
        st.dataframe(df_mega.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Warte auf Daten...")
