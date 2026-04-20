import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- SETUP ---
st.set_page_config(page_title="Polymarket Whale Tracker", layout="wide")
st.title("🐳 Polymarket Megalodon Tracker")

def fetch_whale_trades():
    url = "https://clob.polymarket.com/trades-all"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            trades = r.json()
            whale_list = []
            for t in trades:
                usd_val = float(t.get('price', 0)) * float(t.get('size', 0))
                if usd_val >= 10000:
                    dt = datetime.fromtimestamp(int(t['timestamp'])/1000)
                    whale_list.append({
                        "Uhrzeit": dt.strftime('%H:%M:%S'),
                        "Betrag_USD": round(usd_val, 2),
                        "Preis": t['price'],
                        "Seite": t['side'],
                        "Token_ID": t['token_id']
                    })
            return pd.DataFrame(whale_list)
    except:
        return pd.DataFrame() # Gibt leere Tabelle zurück statt Absturz
    return pd.DataFrame()

# --- DASHBOARD ---
if st.button('Daten jetzt aktualisieren'):
    df = fetch_whale_trades()
    
    # Der Fix: Prüfen, ob df existiert UND nicht leer ist
    if df is not None and not df.empty:
        st.subheader("Aktuelle Großwetten")
        
        def highlight_megalodons(row):
            if row.Betrag_USD >= 100000: return ['background-color: #ff4b4b'] * len(row)
            return [''] * len(row)

        st.dataframe(df.style.apply(highlight_megalodons, axis=1), use_container_width=True)
    else:
        st.warning("Momentan wurden keine Trades über $10k gefunden. Probiere es in ein paar Sekunden nochmal!")
else:
    st.info("Klicke auf den Button, um die Suche zu starten.")
