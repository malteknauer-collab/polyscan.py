import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Polymarket Whale Archive", layout="wide")
st.title("🐳 Whale Tracker & Historie")

# Verbindung zu Google Sheets aufbauen
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_current_trades():
    url = "https://clob.polymarket.com/trades-all"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            trades = r.json()
            found = []
            for t in trades:
                val = float(t.get('price', 0)) * float(t.get('size', 0))
                if val >= 10000:
                    dt = datetime.fromtimestamp(int(t['timestamp'])/1000).strftime('%Y-%m-%d %H:%M')
                    found.append({
                        "Zeit": dt,
                        "Name": t['token_id'][:15], # Vereinfacht für den Anfang
                        "Betrag": round(val, 2),
                        "ID": str(t['id'])
                    })
            return pd.DataFrame(found)
    except:
        return pd.DataFrame()

# 1. Bestehende Historie laden
existing_data = conn.read(worksheet="Trades")

if st.button('🚀 Scan & Speichern'):
    new_trades = fetch_current_trades()
    
    if not new_trades.empty:
        # Nur Trades hinzufügen, deren ID noch nicht im Sheet ist
        if not existing_data.empty:
            new_unique_trades = new_trades[~new_trades['ID'].isin(existing_data['ID'])]
        else:
            new_unique_trades = new_trades

        if not new_unique_trades.empty:
            updated_df = pd.concat([existing_data, new_unique_trades], ignore_index=True)
            # Hier schreiben wir zurück ins Google Sheet
            conn.update(worksheet="Trades", data=updated_df)
            st.success(f"{len(new_unique_trades)} neue Whales archiviert!")
            existing_data = updated_df
        else:
            st.info("Keine neuen Trades seit dem letzten Scan.")
    
# --- DASHBOARD ANZEIGE ---
st.divider()
if not existing_data.empty:
    # Sortierung: Neueste oben
    df_display = existing_data.sort_values(by="Zeit", ascending=False)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🐳 > $10k")
        st.dataframe(df_display[df_display['Betrag'] < 100000], use_container_width=True)
    with c2:
        st.subheader("🐬 > $100k")
        st.dataframe(df_display[(df_display['Betrag'] >= 100000) & (df_display['Betrag'] < 500000)], use_container_width=True)
    with c3:
        st.subheader("🚨 > $500k")
        st.dataframe(df_display[df_display['Betrag'] >= 500000], use_container_width=True)
else:
    st.write("Noch keine Daten in der Historie.")
