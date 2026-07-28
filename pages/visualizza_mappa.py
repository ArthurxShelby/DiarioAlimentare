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
        
        # Stampiamo l'intero contenuto del file o la sua struttura principale per vederlo chiaro
        st.write("JSON radice - Tipo:", type(data))
        if isinstance(data, list):
            for i, stream in enumerate(data):
                if isinstance(stream, dict) and stream.get("type") == "latlng":
                    st.write(f"Trovato latlng all'indice {i}. Chiavi del dizionario:", list(stream.keys()))
                    st.write("Valore di 'data':", stream.get("data")[:5] if isinstance(stream.get("data"), list) else stream.get("data"))
                    break
        elif isinstance(data, dict):
            st.write("Chiavi del dizionario principale:", list(data.keys()))
    else:
        st.error(f"Errore download: {response.status_code}")
except Exception as e:
    st.error(f"Errore: {e}")

if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
