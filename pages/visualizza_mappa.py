import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🗺️ Diagnostica Totale Flussi Intervals")

try:
    API_KEY = st.secrets["intervals"]["api_key"]
except Exception:
    st.error("Configura la chiave nei secrets.")
    st.stop()

act_id = st.session_state.get("selected_activity_id")
if not act_id:
    st.warning("Seleziona un'attività da Uscite.")
    st.stop()

auth_credentials = ("API_KEY", API_KEY.strip())
url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams"

with st.spinner("Scaricamento dati grezzi da Intervals..."):
    response = requests.get(url_streams, auth=auth_credentials)
    
    if response.status_code == 200:
        data = response.json()
        
        # Mostriamo la struttura principale ricevuta
        st.write(f"Tipo del JSON ricevuto: {type(data)}")
        
        if isinstance(data, list):
            st.write(f"Numero di flussi trovati nell'array principale: {len(data)}")
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    st.write(f"--- Flusso indice {i} ---")
                    st.write(f"  - 'type': {item.get('type')}")
                    st.write(f"  - 'data length': {len(item.get('data', [])) if isinstance(item.get('data'), list) else 'Non è una lista'}")
                    if item.get('data') and isinstance(item.get('data'), list) and len(item.get('data')) > 0:
                        st.write(f"  - Esempio primo elemento data: {item.get('data')[0]}")
        elif isinstance(data, dict):
            st.write("Il JSON è un dizionario con chiavi:", list(data.keys()))
    else:
        st.error(f"Errore API: {response.status_code}")

if st.button("⬅️ Torna a Uscite"):
    st.switch_page("uscite.py")
