def fetch_gamma_data():
    # Wir nehmen einen etwas breiteren Endpunkt
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            events = response.json()
            data_list = []
            for e in events:
                # Wir versuchen erst volume24hr, dann normales volume, dann 0
                vol_24 = e.get('volume24hr')
                vol_total = e.get('volume')
                
                # Wir nehmen den Wert, der existiert
                volume = float(vol_24 if vol_24 is not None else (vol_total if vol_total is not None else 0))
                
                # TEST: Wir senken das Limit auf 0, um ÜBERHAUPT zu sehen, ob was kommt
                if volume >= 0:
                    data_list.append({
                        "Zeit": datetime.now().strftime("%H:%M:%S"),
                        "Name": e.get('title', e.get('question', 'Unbekannt'))[:40],
                        "Betrag": round(volume, 2),
                        "ID": str(e.get('id', 'N/A'))
                    })
            return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"API Fehler: {e}")
    return pd.DataFrame()
