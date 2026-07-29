import streamlit as st
import requests
import gpxpy
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🗺️ Visualizzazione Mappa Attività")

try:
    API_KEY = st.secrets["intervals"]["api_key"]
except Exception:
    st.error("Errore: Configura le credenziali di Intervals nei secrets.")
    st.stop()

act_id = st.session_state.get("selected_activity_id")
act_title = st.session_state.get("selected_activity_title", "Attività")
act_date = st.session_state.get("selected_activity_date", "")

if act_id:
    st.subheader(f"📍 {act_title} ({act_date})")
    
    url_gpx = f"https://intervals.icu/api/v1/activity/{act_id}.gpx"
    auth_gpx = ("API_KEY", API_KEY.strip())
    
    with st.spinner("Caricamento tracciato GPX in corso..."):
        try:
            response = requests.get(url_gpx, auth=auth_gpx)
            
            if response.status_code == 200 and response.content:
                gpx_content = response.content
                gpx = gpxpy.parse(gpx_content.decode('utf-8', errors='ignore'))
                
                coordinates = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            coordinates.append((point.latitude, point.longitude))
                
                if coordinates:
                    m = folium.Map(location=coordinates[0], zoom_start=13, tiles="CartoDB positron")
                    folium.PolyLine(
                        coordinates, 
                        color="#ff4b4b", 
                        weight=4, 
                        opacity=0.8
                    ).add_to(m)
                    st_folium(m, width=1000, height=550, key="folium_map_page_render")
                else:
                    st.warning("Il file GPX scaricato non contiene punti di coordinate validi.")
            else:
                st.warning(f"Impossibile scaricare il file GPX da Intervals (Codice: {response.status_code}).")
        except Exception as e:
            st.error(f"Errore durante l'elaborazione della mappa: {e}")
            
    if st.button("⬅️ Torna alla Gestione Uscite"):
        try:
            st.switch_page("uscite.py")
        except Exception:
            st.info("Usa il menu laterale a sinistra per tornare alla pagina Uscite.")
else:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività dal menu laterale.")
