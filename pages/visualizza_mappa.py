import streamlit as st
st.set_page_config(layout="wide")
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("🗺️ Dettaglio Tracciato Interattivo")

map_url = st.session_state.get("map_url_to_view")

if not map_url:
    st.warning("Nessun tracciato selezionato.")
    if st.button("⬅️ Torna alla Gestione Uscite"):
        st.switch_page("pages/uscite.py")
    st.stop()

try:
    response = requests.get(map_url)
    if response.status_code == 200:
        data = response.json()
        
        # DIAGNOSTICA: Stampiamo che tipo di dati sono e le chiavi principali
        st.write(f"Tipo di dato ricevuto: {type(data)}")
        if isinstance(data, list) and len(data) > 0:
            st.write(f"Il primo elemento è di tipo: {type(data[0])}")
            if isinstance(data[0], dict):
                st.write(f"Chiavi presenti nel dizionario: {list(data[0].keys())}")
                if "type" in data[0]:
                    st.write("Tipi di flussi presenti nella lista:", [item.get("type") for item in data if isinstance(item, dict)])
        elif isinstance(data, dict):
            st.write(f"Chiavi del dizionario radice: {list(data.keys())}")

    else:
        st.error(f"Errore download: {response.status_code}")
except Exception as e:
    st.error(f"Errore: {e}")

if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
