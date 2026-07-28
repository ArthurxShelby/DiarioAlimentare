import streamlit as st
st.set_page_config(layout="wide")
import requests

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
        
        # Cerchiamo il blocco latlng e stampiamo come è fatto dentro
        found = False
        if isinstance(data, list):
            for stream in data:
                if isinstance(stream, dict) and stream.get("type") == "latlng":
                    found = True
                    st.write("Trovato stream latlng! Ecco le sue chiavi o il tipo:", type(stream))
                    st.write("Contenuto del blocco latlng:", stream)
                    break
        if not found:
            st.write("Stream latlng non trovato nella lista. Radice del JSON:", type(data))
    else:
        st.error(f"Errore download: {response.status_code}")
except Exception as e:
    st.error(f"Errore: {e}")

if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
