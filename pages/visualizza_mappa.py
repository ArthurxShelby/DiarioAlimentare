import streamlit as st
import requests
import gpxpy
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🗺️ Visualizzazione Mappa e Dati Attività")

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
    
    auth_credentials = ("API_KEY", API_KEY.strip())
    coordinates = []
    
    with st.spinner("Caricamento dati attività in corso..."):
        try:
            # 1. Tentativo di download tramite GPX
            url_gpx = f"https://intervals.icu/api/v1/activity/{act_id}.gpx"
            response_gpx = requests.get(url_gpx, auth=auth_credentials)
            
            if response_gpx.status_code == 200 and response_gpx.content:
                gpx = gpxpy.parse(response_gpx.content.decode('utf-8', errors='ignore'))
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            coordinates.append((point.latitude, point.longitude))
            
            # 2. Se il GPX fallisce, proviamo con gli streams latlng
            if not coordinates:
                url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams.json?types=latlng"
                response_streams = requests.get(url_streams, auth=auth_credentials)
                
                if response_streams.status_code == 200:
                    streams_data = response_streams.json()
                    streams_list = streams_data if isinstance(streams_data, list) else [streams_data]
                    
                    for stream in streams_list:
                        if isinstance(stream, dict) and stream.get("type") == "latlng":
                            latlngs = stream.get("data", [])
                            for pt in latlngs:
                                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                    if pt[0] is not None and pt[1] is not None:
                                        coordinates.append((float(pt[0]), float(pt[1])))
                            break

            # Render della mappa se abbiamo trovato coordinate
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
                st.warning("⚠️ Questa attività non contiene dati di geolocalizzazione GPS (potrebbe essere un allenamento indoor o un caricamento manuale).")
                
                # Recuperiamo tutti gli altri flussi disponibili (es. potenza, frequenza cardiaca, cadenza)
                url_all_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams"
                resp_all = requests.get(url_all_streams, auth=auth_credentials)
                
                if resp_all.status_code == 200:
                    all_streams = resp_all.json()
                    st.markdown("### 📊 Metriche e Flussi Registrati:")
                    
                    stream_types_found = []
                    for s in all_streams:
                        if isinstance(s, dict) and "type" in s:
                            stream_types_found.append(s["type"])
                    
                    if stream_types_found:
                        st.info( اقتصادي / Tipi di dati disponibili: " + ", ".join(stream_types_found))
                        
                        # Mostriamo grafici rapidi se ci sono dati di potenza o frequenza cardiaca
                        for s in all_streams:
                            if isinstance(s, dict) and s.get("type") in ["watts", "heartrate", "cadence"]:
                                st.line_chart(s.get("data", []), y_label=s.get("type"))
                    else:
                        st.text("Nessun flusso aggiuntivo disponibile per questa attività.")

        except Exception as e:
            st.error(f"Errore durante il recupero dei dati dell'attività: {e}")
            
    if st.button("⬅️ Torna alla Gestione Uscite"):
        try:
            st.switch_page("uscite.py")
        except Exception:
            st.info("Usa il menu laterale a sinistra per tornare alla pagina Uscite.")
else:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività dal menu laterale.")
