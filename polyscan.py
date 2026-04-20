import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Polymarket Whale Monitor", layout="wide")
st.title("🐳 Polymarket Megalodon Monitor")

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

# --- DASHBOARD STRUKTUR ---
if st.button('🚀 Scan starten / Aktualisieren'):
    df = fetch_data()
    
    # Erstelle die Spalten IMMER
    col1, col2, col3 = st.columns(3)
    
    # Daten filtern (auch wenn df leer ist, funktionieren diese Filter)
    if not df.empty:
        t10 = df[(df['Betrag'] >= 10000) & (df['Betrag'] < 100000)]
        t100 = df[(df['Betrag'] >= 100000) & (df['Betrag'] < 500000)]
        t500 = df[df['Betrag'] >= 500000]
    else:
        t10 = t100 = t500 = pd.DataFrame(columns=['Zeit', 'Name', 'Betrag', 'ID'])

    # Spalte 1: Whales
    with col1:
        st.subheader("🐬 Dolphins (> $10k)")
        if not t10.empty:
            st.dataframe(t10, use_container_width=True, hide_index=True)
        else:
            st.info("Keine Trades in dieser Klasse.")

    # Spalte 2: Kraken
    with col2:
        st.subheader("🐋 Whales (> $100k)")
        if not t100.empty:
            st.dataframe(t100, use_container_width=True, hide_index=True)
        else:
            st.info("Keine Trades in dieser Klasse.")

    # Spalte 3: Megalodons
    with col3:
        st.subheader("🚨 Megalodons (> $500k)")
        if not t500.empty:
            # Roter Style für die ganz dicken Fische
            st.dataframe(t500.style.background_gradient(cmap='Reds'), use_container_width=True, hide_index=True)
        else:
            st.info("Keine Trades in dieser Klasse.")
            
    if df.empty:
        st.divider()
        st.caption("Letzter Scan ergab keine Treffer über $10k. Die API liefert nur die aktuellsten Trades der Plattform.")
else:
    st.info("Klicke auf den Button, um den Monitor zu aktivieren.")
