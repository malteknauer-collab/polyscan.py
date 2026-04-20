import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time

# --- SETUP & STYLING ---
st.set_page_config(page_title="Polymarket Whale Tracker", layout="wide")
st.title("🐳 Polymarket Megalodon Tracker")
st.write("Echtzeit-Analyse von Großwetten (> $10k)")

# --- TRACKING LOGIK ---
def fetch_whale_trades():
    url = "https://clob.polymarket.com/trades-all"
    min_value = 10000 # Deine Grenze
    
    try:
        r = requests.get(url)
        if r.status_code == 200:
            trades = r.json()
            whale_list = []
            
            for t in trades:
                usd_val = float(t['price']) * float(t['size'])
                if usd_val >= min_value:
                    # Zeitstempel umwandeln
                    dt = datetime.fromtimestamp(int(t['timestamp'])/1000)
                    
                    whale_list.append({
                        "Uhrzeit": dt.strftime('%H:%M:%S'),
                        "Betrag_USD": round(usd_val, 2),
                        "Preis": t['price'],
                        "Seite": t['side'],
                        "Token_ID": t['token_id']
                    })
            return pd.DataFrame(whale_list)
    except Exception as e:
        st.error(f"Fehler beim Abruf: {e}")
        return pd.DataFrame()

# --- DASHBOARD BEREICH ---
# Button zum manuellen Aktualisieren
if st.button('Daten jetzt aktualisieren'):
    df = fetch_whale_trades()
    if not df.empty:
        # Hervorhebung für riesige Trades
        def highlight_megalodons(row):
            if row.Betrag_USD >= 100000:
                return ['background-color: #ff4b4b; color: white'] * len(row)
            elif row.Betrag_USD >= 50000:
                return ['background-color: #ffa500; color: black'] * len(row)
            return [''] * len(row)

        st.subheader("Aktuelle Großwetten (Letzte Trades)")
        st.dataframe(df.style.apply(highlight_megalodons, axis=1), use_container_width=True)
        
        # Statistik
        col1, col2 = st.columns(2)
        col1.metric("Größter Trade", f"${df['Betrag_USD'].max():,.2f}")
        col2.metric("Anzahl Whales", len(df))
    else:
        st.info("Gerade keine Whales unterwegs...")
else:
    st.info("Klicke auf den Button, um die aktuellen Megalodons zu laden.")

# Automatischer Refresh alle 5 Minuten (optional)
st.empty()
