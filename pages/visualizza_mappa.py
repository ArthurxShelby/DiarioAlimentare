import streamlit as st
st.set_page_config(layout="wide")
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("🗺️ Dettaglio Tracciato Interattivo")

# Recupera l'URL del file JSON salvato nella sessione
map_url = st.session_state.get("map_url_to_view")

if not map_url:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività.")
    if st.button("⬅️ Torna alla Gestione Uscite"):
        st.switch_page("pages/uscite.py")
    st.stop()

# Scarica e analizza il file JSON dal bucket
try:
    response = requests.get(map_url)
    if response.status_code == 200:
        data = response.json()
        
        # Estraiamo le coordinate dal flusso JSON di Intervals.icu
        latlons = []
        if isinstance(data, list):
            # Cerca il blocco latlng all'interno della lista dei flussi
            for stream in data:
                if isinstance(stream, dict) and stream.get("type") == "latlng":
                    latlons = stream.get("data", [])
                    break
            # Fallimento ricerca specifica? Proviamo a vedere se è direttamente una lista di coordinate
            if not latlons and len(data) > 0 and isinstance(data[0], (list, tuple)):
                latlons = data
        elif isinstance(data, dict):
            latlons = data.get("data", [])

        if not latlons:
            st.error("Il file JSON non contiene un tracciato di coordinate valido.")
            st.stop()

            
        # Filtriamo e puliamo i punti validi
        points = []
        for pt in latlons:
            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                lat, lon = pt[0], pt[1]
                if lat is not None and lon is not None:
                    points.append([lat, lon])

        if points:
            # Creazione della mappa con Folium centrata sul percorso
            start_coord = points[0]
            m = folium.Map(location=start_coord, zoom_start=13)
            
            # Aggiungiamo la linea del percorso
            folium.PolyLine(points, color="blue", weight=4, opacity=0.8).add_to(m)
            
            # Marker di inizio e fine
            folium.Marker(points[0], popup="Partenza", icon=folium.Icon(color="green", icon="play")).add_to(m)
            folium.Marker(points[-1], popup="Arrivo", icon=folium.Icon(color="red", icon="stop")).add_to(m)

            st_folium(m, width=1200, height=600)
        else:
            st.warning("Nessun punto di coordinate valido trovato nel tracciato.")

    else:
        st.error(f"Errore nel download del file JSON dalla memoria (Status: {response.status_code}).")

except Exception as e:
    st.error(fegg := f"Errore durante l'elaborazione del tracciato: {e}")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
