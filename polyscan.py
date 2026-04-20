import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
from datetime import datetime

# 1. SEITEN KONFIGURATION (Muss ganz oben stehen!)
st.set_page_config(page_title="Polymarket Tracker", layout="wide")

st.title("🚀 Polymarket Whale Tracker")

# 2. VERBINDUNG
try:
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
except Exception as e:
    st.error(f"Verbindungsfehler zum Sheet: {e}")

# 3. DATEN-FUNKTION
def fetch_gamma_data():
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            events = response.json()
            data_list = []
            for e in events:
                # Wir prüfen flexibel auf Volumen-Felder
                vol = e.get('volume24hr') or e.get('volume') or 0
                
                data_list.append({
                    "Zeit": datetime.now().strftime("%H:%M:%S"),
                    "Name": str(e.get('title', e.get('question', 'Unbekannt')))[:40],
                    "Betrag": round(float(vol), 2),
                    "ID": str(e.get('id', 'N/A'))
                })
            return pd.DataFrame(data_list)
    except Exception as e:
        st.warning(f"API temporär nicht erreichbar: {e}")
    return pd.DataFrame()

# 4. DATEN LADEN
try:
    existing_data = conn.read(worksheet="Trades", ttl=0)
    if existing_data is None or existing_data.empty:
        existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])
except:
    existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])

# 5. BUTTON & LOGIK
if st.button('🚀 Scan & Archivieren'):
    with st.spinner('Suche Daten...'):
        new_data = fetch_gamma_data()
        
    if not new_data.empty:
        # ID-Check gegen Duplikate
        existing_ids = existing_data['ID'].astype(str).unique()
        new_unique = new_data[~new_data['ID'].astype(str).isin(existing_ids)]

        if not new_unique.empty:
            updated_df = pd.concat([existing_data, new_unique], ignore_index=True)
            conn.update(worksheet="Trades", data=updated_df)
            st.success(f"✅ {len(new_unique)} neue Einträge gespeichert!")
            st.rerun()
        else:
            st.info("Keine neuen Daten gefunden.")

# 6. DASHBOARD
st.divider()
cols = st.columns(4)
titles = ["🐟 Fish", "🐬 Dolphin", "🐳 Whale", "🚨 Megalodon"]
limits = [(0, 10000), (10000, 100000), (100000, 500000), (500000, None)]

for col, title, (low, high) in zip(cols, titles, limits):
    with col:
        st.subheader(title)
        if not existing_data.empty:
            if high:
                mask = (existing_data['Betrag'] >= low) & (existing_data['Betrag'] < high)
            else:
                mask = (existing_data['Betrag'] >= low)
            
            df_cat = existing_data[mask]
            st.dataframe(df_cat.sort_values(by="Zeit", ascending=False), 
                         use_container_width=True, hide_index=True)
        else:
            st.write("Keine Daten")
