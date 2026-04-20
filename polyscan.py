import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
from datetime import datetime

# --- SEITEN KONFIGURATION ---
st.set_page_config(page_title="Polymarket Tracker", layout="wide")
st.title("🚀 Polymarket Whale & Fish Tracker")

# Verbindung zu Google Sheets (ohne Cache)
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)

# --- FUNKTION: DATEN VON POLYMARKET HOLEN ---
def fetch_current_trades():
    url = "https://clob.polymarket.com/last-trades"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            trades = response.json()
            data_list = []
            for t in trades:
                # Wir rechnen die Größe aus (Preis * Menge)
                val = float(t.get('price', 0)) * float(t.get('size', 0))
                
                # TEST-LIMIT: Ab 10$ (später wieder auf 1000 ändern)
                if val >= 0.1:
                    data_list.append({
                        "Zeit": datetime.now().strftime("%H:%M:%S"),
                        "Name": t.get('asset_id', 'Unbekannt')[:15], # Gekürzt für Übersicht
                        "Betrag": round(val, 2),
                        "ID": t.get('order_id', 'N/A')
                    })
            return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"API Fehler: {e}")
    return pd.DataFrame()

# --- HAUPTLOGIK: LESEN & SCHREIBEN ---
# Bestehende Daten aus dem Sheet laden
try:
    existing_data = conn.read(worksheet="Trades", ttl=0)
except:
    existing_data = pd.DataFrame(columns=["Zeit", "Name", "Betrag", "ID"])

if st.button('🚀 Scan & Archivieren'):
    with st.spinner('Suche nach Trades...'):
        new_trades = fetch_current_trades()
        
    if not new_trades.empty:
        try:
            # Nur echte Neuheiten filtern (ID-Check)
            if not existing_data.empty:
                existing_ids = existing_data['ID'].astype(str).tolist()
                new_unique = new_trades[~new_trades['ID'].astype(str).isin(existing_ids)]
            else:
                new_unique = new_trades

            if not new_unique.empty:
                updated_df = pd.concat([existing_data, new_unique], ignore_index=True)
                # Ab ins Google Sheet
                conn.update(worksheet="Trades", data=updated_df)
                st.success(f"✅ {len(new_unique)} neue Trades archiviert!")
                existing_data = updated_df
            else:
                st.info("Keine neuen Trades seit dem letzten Scan.")
        except Exception as e:
            st.error(f"❌ Google Fehler: {e}")
    else:
        st.warning("Momentan keine Trades über $10 gefunden.")

# --- DASHBOARD ANZEIGE ---
st.divider()
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.subheader("🐟 Fish")
    df_fish = existing_data[(existing_data['Betrag'] >= 10) & (existing_data['Betrag'] < 10000)]
    st.dataframe(df_fish.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)

with c2:
    st.subheader("🐬 Dolphin")
    df_dolphin = existing_data[(existing_data['Betrag'] >= 10000) & (existing_data['Betrag'] < 100000)]
    st.dataframe(df_dolphin.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)

with c3:
    st.subheader("🐳 Whale")
    df_whale = existing_data[(existing_data['Betrag'] >= 100000) & (existing_data['Betrag'] < 500000)]
    st.dataframe(df_whale.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)

with c4:
    st.subheader("🚨 Megalodon")
    df_mega = existing_data[existing_data['Betrag'] >= 500000]
    st.dataframe(df_mega.sort_values(by="Zeit", ascending=False), use_container_width=True, hide_index=True)
