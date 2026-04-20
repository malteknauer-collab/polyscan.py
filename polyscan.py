import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Polymarket Whale Tracker", layout="wide")
st.title("🐳 Polymarket Whale Monitor")

def get_market_name(token_id):
    try:
        r = requests.get(f"https://gamma-api.polymarket.com/markets?tokenID={token_id}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data: return data[0].get('question', 'Unbekannter Markt')
    except: pass
    return token_id[:10] + "..."

def fetch_data():
    url = "https://clob.polymarket.com/trades-all"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            trades = r.json()
            all_trades = []
            for t in trades:
                val = float(t.get('price', 0)) * float(t.get('size', 0))
                if val >= 10000:
                    dt = datetime.fromtimestamp(int(t['timestamp'])/1000).strftime('%H:%M:%S')
                    all_trades.append({
                        "Zeit": dt,
                        "Name": get_market_name(t['token_id']),
                        "Betrag": round(val, 2),
                        "ID": t['token_id'][:8]
                    })
            return pd.DataFrame(all_trades)
    except:
        return pd.DataFrame()
    return pd.DataFrame()

if st.button('🚀 Scan starten / Aktualisieren'):
    df = fetch_data()
    
    if not df.empty:
        # Aufteilung in 3 Kategorien
        t10 = df[(df['Betrag'] >= 10000) & (df['Betrag'] < 100000)]
        t100 = df[(df['Betrag'] >= 100000) & (df['Betrag'] < 500000)]
        t500 = df[df['Betrag'] >= 500000]

        # Spalten-Layout in Streamlit
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🐳 > $10k")
            st.dataframe(t10[['Zeit', 'Name', 'Betrag', 'ID']], use_container_width=True, hide_index=True)

        with col2:
            st.subheader("🐋 > $100k")
            st.dataframe(t100[['Zeit', 'Name', 'Betrag', 'ID']], use_container_width=True, hide_index=True)

        with col3:
            st.subheader("🚨 > $500k")
            # Hier machen wir den Hintergrund rot, wenn was drin ist
            if not t500.empty:
                st.dataframe(t500[['Zeit', 'Name', 'Betrag', 'ID']], use_container_width=True, hide_index=True)
            else:
                st.write("Keine Megalodons gesichtet.")
    else:
        st.warning("Aktuell keine Trades über $10k in den letzten API-Daten gefunden.")
