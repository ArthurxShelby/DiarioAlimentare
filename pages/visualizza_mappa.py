import streamlit as st
import requests
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
    
    url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams.json?types=latlng"
    auth_streams = ("API_KEY", API_KEY.strip())
    
    with st.spinner("Caricamento tracciato GPS in corso..."):
        try:
            resp_streams = requests.get(url_streams, auth=auth_streams)
            decoded_coordinates = []
            
            if resp_streams.status_code == 200:
                streams_data = resp_streams.json()
                streams_list = streams_data if isinstance(streams_data, list) else [streams_data]
                
                for stream in streams_list:
                    if isinstance(stream, dict) and stream.get("type") == "latlng":
                        latlngs = stream.get("data", [])
                        for pt in latlngs:
                            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                if pt[0] is not None and pt[1] is not None:
                                    decoded_coordinates.append((float(pt[0]), float(pt[1])))
                        break

            if decoded_coordinates:
                m = folium.Map(location=decoded_coordinates[0], zoom_start=13, tiles="CartoDB positron")
                folium.PolyLine(
                    decoded_coordinates, 
                    color="#ff4b4b", 
                    weight=4, 
                    opacity=0.8
                ).add_to(m)
                st_folium(m, width=1000, height=550, key="folium_map_page_render")
            else:
                st.warning("Nessun flusso di coordinate GPS (latlng) disponibile per questa attività su Intervals.")
        except Exception as e:
            st.error(f"Errore durante il recupero della mappa: {e}")
    
    if st.button("⬅️ Torna alla Gestione Uscite"):
        st.switch_page("uscite.py")
else:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività.")
    if st.button("⬅️ Torna a Uscite"):
        st.switch_page("uscite.py")
