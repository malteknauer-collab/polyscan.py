import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="Polymarket Whale Tracker", layout="wide")
st.title("🐳 Polymarket High-Stakes Tracker")
st.markdown("---")

# Verbindung zu Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
except Exception as e:
    st.error(f"Verbindung zum Sheet fehlgeschlagen: {e}")

# 2. WHALE-LOGIK (Activity API)
def fetch_whale_trades():
    url = "https://gamma-api.polymarket.com/activity?limit=100"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            activities = response.json()
            data_list = []
            for a in activities:
                # Echter USD-Wert = Shares * Preis
                size = float(a.get('size', 0))
                price = float(a.get('price', 0))
                usd_value = size * price
                
                # DER FILTER: Nur Trades ab 10k
                if usd_value >= 10000:
                    data_list.append({
                        "Zeit": datetime.now().strftime("%H:%M:%S"),
                        "Name": a.get('title', 'Unbekannter Markt')[:50],
                        "Betrag": round(usd_value, 2),
                        "ID": str(a.get('id', 'N/A'))
                    })
            return pd.DataFrame(data_list)
    except Exception as e:
        st.warning(f"API Scan fehlgeschlagen: {e}")
    return pd.DataFrame()

# 3. DATEN-VERARBEITUNG
try:
    existing_data = conn.read(worksheet="Trades", ttl=0)
    if existing_data is None or existing_data.empty:
        existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])
except:
    existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])

if st.button('🔍 Nach Walen scannen'):
    with st.spinner('Scanne Activity-Feed...'):
        new_whales = fetch_whale_trades()
        
    if not new_whales.empty:
        existing_ids = existing_data['ID'].astype(str).unique()
        unique_whales = new_whales[~new_whales['ID'].astype(str).isin(existing_ids)]

        if not unique_whales.empty:
            updated_df = pd.concat([existing_data, unique_whales], ignore_index=True)
            conn.update(worksheet="Trades", data=updated_df)
            st.success(f"🚨 WAL-ALARM: {len(unique_whales)} neue Groß-Trades gefunden!")
            st.rerun()
        else:
            st.info("Keine neuen Wale gesichtet.")

# 4. DAS DASHBOARD MIT k-ABKÜRZUNGEN
st.divider()
c1, c2, c3 = st.columns(3)

# Deine Logik mit den sauberen 10k/50k Überschriften
categories = [
    (c1, "🐬 Dolphins", "10k - 50k", 10000, 50000),
    (c2, "🐳 Whales", "50k - 200k", 50000, 200000),
    (c3, "🚨 Megalodons", "> 200k", 200000, None)
]

for col, title, subtitle, low, high in categories:
    with col:
        st.subheader(title)
        st.caption(f"Limit: {subtitle}")
        
        if not existing_data.empty:
            if high:
                mask = (existing_data['Betrag'] >= low) & (existing_data['Betrag'] < high)
            else:
                mask = (existing_data['Betrag'] >= low)
            
            df_cat = existing_data[mask].copy()
            
            if not df_cat.empty:
                df_cat = df_cat.sort_values(by="Betrag", ascending=False)
                # Schöne Darstellung für die Tabelle
                df_cat['Anzeige_Betrag'] = df_cat['Betrag'].map('{:,.2f} $'.format)
                
                st.dataframe(
                    df_cat[['Zeit', 'Name', 'Anzeige_Betrag']], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.info("Keine Einträge.")
        else:
            st.write("Warte auf Scan...")
