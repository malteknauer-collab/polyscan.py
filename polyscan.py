import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
from datetime import datetime

st.set_page_config(page_title="Polymarket Diagnostics", layout="wide")
st.title("🔍 API & Data Diagnose")

# Verbindung zu Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)

def fetch_diagnostics():
    url = "https://clob.polymarket.com/last-trades"
    # User-Agent hilft gegen Blockaden
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            trades = response.json()
            
            # --- DIAGNOSE BOXEN ---
            st.subheader("📡 API Antwort")
            col1, col2 = st.columns(2)
            col1.metric("Anzahl Trades von API", len(trades))
            col2.info("Status: Verbindung erfolgreich (200)")

            if len(trades) > 0:
                with st.expander("Rohdaten des ersten Trades ansehen"):
                    st.json(trades[0]) # Hier sehen wir die Feldnamen!
                
                data_list = []
                for t in trades:
                    # Wir versuchen verschiedene Feldnamen, falls die API sie geändert hat
                    p = float(t.get('price', t.get('p', 0)))
                    s = float(t.get('size', t.get('qty', 0)))
                    val = p * s
                    
                    data_list.append({
                        "Zeit": datetime.now().strftime("%H:%M:%S"),
                        "Name": t.get('asset_id', t.get('token_id', 'Unbekannt'))[:15],
                        "Betrag": round(val, 2),
                        "ID": t.get('order_id', t.get('id', 'N/A'))
                    })
                return pd.DataFrame(data_list)
            else:
                st.warning("Die API hat eine leere Liste geschickt.")
        else:
            st.error(f"API Fehler: Status {response.status_code}")
    except Exception as e:
        st.error(f"Kritischer Fehler: {e}")
    return pd.DataFrame()

# --- HAUPTPROGRAMM ---
if st.button('🧪 API-Check & Scan'):
    df = fetch_diagnostics()
    
    if not df.empty:
        st.subheader("Vorschau der verarbeiteten Daten")
        st.dataframe(df.head(10)) # Zeigt die ersten 10 Zeilen
        
        # Test-Schreiben ins Google Sheet
        try:
            conn.update(worksheet="Trades", data=df)
            st.success("✅ Test-Daten wurden ans Sheet gesendet!")
        except Exception as e:
            st.error(f"Google Sheet Schreibfehler: {e}")

# Zeige aktuelles Sheet an
st.divider()
st.subheader("Aktueller Inhalt im Google Sheet")
try:
    current = conn.read(worksheet="Trades", ttl=0)
    st.dataframe(current)
except:
    st.write("Sheet ist noch leer oder nicht erreichbar.")
