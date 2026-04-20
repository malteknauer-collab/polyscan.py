import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Polymarket Tracker", layout="wide")
st.title("🐳 Polymarket Whale & Fish Tracker")

# Verbindung zu Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection, ttl=0))

def get_market_name(token_id):
    try:
        r = requests.get(f"https://gamma-api.polymarket.com/markets?tokenID={token_id}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data: return data[0].get('question', 'Unbekannter Markt')
    except: pass
    return token_id[:15] + "..."

def fetch_current_trades():
    url = "https://clob.polymarket.com/trades-all"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            trades = r.json()
            found = []
            for t in trades:
                val = float(t.get('price', 0)) * float(t.get('size', 0))
                # TEST-FILTER: Jetzt ab 1.000 USD
                if val >= 1000:
                    dt = datetime.fromtimestamp(int(t['timestamp'])/1000).strftime('%Y-%m-%d %H:%M')
                    found.append({
                        "Zeit": dt,
                        "Name": get_market_name(t['token_id']),
                        "Betrag": round(val, 2),
                        "ID": str(t['id'])
                    })
            return pd.DataFrame(found)
    except:
        return pd.DataFrame()

# Historie laden
try:
    existing_data = conn.read(worksheet="Trades")
except:
    existing_data = pd.DataFrame(columns=['Zeit', 'Name', 'Betrag', 'ID'])

if st.button('🚀 Scan & Archivieren'):
    new_trades = fetch_current_trades()
    
    if new_trades is not None and not new_trades.empty:
        if not existing_data.empty:
            new_unique_trades = new_trades[~new_trades['ID'].isin(existing_data['ID'])]
        else:
            new_unique_trades = new_trades

        if not new_unique_trades.empty:
            updated_df = pd.concat([existing_data, new_unique_trades], ignore_index=True)
            conn.update(worksheet="Trades", data=updated_df)
            st.success(f"{len(new_unique_trades)} neue Trades archiviert!")
            existing_data = updated_df
        else:
            st.info("Keine neuen Trades gefunden.")
    else:
        st.warning("Keine Trades über $1.000 im aktuellen Fenster.")
    
# --- DASHBOARD ANZEIGE ---
st.divider()
if not existing_data.empty:
    df_display = existing_data.sort_values(by="Zeit", ascending=False)
    
    # Jetzt 4 Spalten
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.subheader("🐟 Small Fish (>$1k)")
        st.dataframe(df_display[(df_display['Betrag'] >= 1000) & (df_display['Betrag'] < 10000)], use_container_width=True, hide_index=True)
    
    with c2:
        st.subheader("🐳 Whales (>$10k)")
        st.dataframe(df_display[(df_display['Betrag'] >= 10000) & (df_display['Betrag'] < 100000)], use_container_width=True, hide_index=True)
        
    with c3:
        st.subheader("🐬 Dolphins (>$100k)")
        st.dataframe(df_display[(df_display['Betrag'] >= 100000) & (df_display['Betrag'] < 500000)], use_container_width=True, hide_index=True)
        
    with c4:
        st.subheader("🚨 Megalodons (>$500k)")
        st.dataframe(df_display[df_display['Betrag'] >= 500000], use_container_width=True, hide_index=True)
else:
    st.write("Noch keine Daten vorhanden.")
