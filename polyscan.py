import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
from datetime import datetime

# --- SEITEN KONFIGURATION ---
st.set_page_config(page_title="Polymarket Tracker v2", layout="wide")
st.title("🚀 Polymarket Whale Tracker (Gamma Edition)")

# Verbindung zu Google Sheets (ohne Cache)
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)

# --- FUNKTION: DATEN VON GAMMA HOLEN ---
def fetch_gamma_data():
    # Wir holen die aktivsten Events (Märkte)
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true&sort=volume24hr&order=desc"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            data_list = []
            for e in events:
                # Wir nutzen das 24h Volumen als Indikator für die "Größe"
                volume = float(e.get('volume24hr', 0))
                
                # Wir filtern hier nach deinem Wunsch (z.B. alles ab 10$ für den Test)
                if volume >= 10:
                    data_list.append({
                        "Zeit": datetime.now().strftime("%H:%M:%S"),
                        "Name": e.get('title', 'Unbekannt')[:40],
                        "Betrag": round(volume, 2),
                        "ID": str(e.get('id', 'N/A'))
                    })
            return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"API Fehler: {e}")
    return pd.DataFrame()

# --- HAUPTLOGIK: LESEN & SCHREIBEN ---
# Bestehende Daten aus dem Sheet laden
try:
    existing_data = conn.read(worksheet="Trades", ttl=0)
    # Sicherstellen, dass die Spalten existieren
    if existing_data.empty:
        existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])
except:
    existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])

if st.button('🚀 Scan & Archivieren'):
    with st.spinner('Suche nach neuen Marktdaten...'):
        new_data = fetch_gamma_data()
        
    if not new_data.empty:
        try:
            # Duplikate anhand der ID verhindern
            if not existing_data.empty:
                existing_ids = existing_data['ID'].astype(str).tolist()
                new_unique = new_data[~new_data['ID'].astype(str).isin(existing_ids)]
            else:
                new_unique = new_data

            if not new_unique.empty:
                updated_df = pd.concat([existing_data, new_unique], ignore_index=True)
                # Ab ins Google Sheet
                conn.update(worksheet="Trades", data=updated_df)
                st.success(f"✅ {len(new_unique)} neue Märkte/Trades archiviert!")
                existing_data = updated_df
                st.rerun() # Seite neu laden für Anzeige
            else:
                st.info("Keine neuen Daten seit dem letzten Scan gefunden.")
        except Exception as e:
            st.error(f"❌ Google Fehler: {e}")
    else:
        st.warning("Momentan keine Daten in der API gefunden.")

# --- DASHBOARD ANZEIGE ---
st.divider()
c1, c2, c3, c4 = st.columns(4)

# Hilfsfunktion für die Anzeige
def show_category(col, title, min_val, max_val, color):
    with col:
        st.subheader(title)
        if not existing_data.empty:
            # Filterung nach Betrag
            if max_val:
                df_filtered = existing_data[(existing_data['Betrag'] >= min_val) & (existing_data['Betrag'] < max_val)]
            else:
                df_filtered = existing_data[existing_data['Betrag'] >= min_val]
            
            st.dataframe(df_filtered.sort_values(by="Zeit", ascending=False), 
                         use_container_width=True, hide_index=True)
        else:
            st.info("Noch keine Daten.")

# Kategorien anzeigen (Gleiche Logik wie vorher)
show_category(c1, "🐟 Fish", 10, 10000, "blue")
show_category(c2, "🐬 Dolphin", 10000, 100000, "green")
show_category(c3, "🐳 Whale", 100000, 500000, "orange")
show_category(c4, "🚨 Megalodon", 500000, None, "red")
