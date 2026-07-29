import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🗺️ Visualizzazione Mappa e Dati Attività")

try:
    API_KEY = st.secrets["intervals"]["api_key"]
except Exception:
    st.error("Errore: Configura le credenziali di Intervals nei secrets.")
    st.stop()

# Recuperiamo l'ID dell'attività salvato in memoria
act_id = st.session_state.get("selected_activity_id")
act_title = st.session_state.get("selected_activity_title", "Attività")
act_date = st.session_state.get("selected_activity_date", "")

if not act_id:
    st.warning("⚠️ Nessuna attività selezionata. Torna alla pagina 'uscite' e clicca su 'Apri Mappa'.")
    if st.button("⬅️ Torna a Uscite"):
        st.switch_page("uscite.py")
    st.stop()

st.subheader(f"📍 {act_title} ({act_date})")

auth_credentials = ("API_KEY", API_KEY.strip())
coordinates = []
all_streams = []

with st.spinner("Caricamento flussi e tracciato GPS in corso..."):
    try:
        url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams"
        response = requests.get(url_streams, auth=auth_credentials)
        
        if response.status_code == 200:
            data = response.json()
            all_streams = data if isinstance(data, list) else [data]
            
            # 1. Cerchiamo il flusso 'latlng' o flussi separati di coordinate
            lat_list = []
            lon_list = []
            
            for stream in all_streams:
                if isinstance(stream, dict):
                    st_type = stream.get("type")
                    stream_data = stream.get("data", [])
                    
                    if st_type == "latlng":
                        for pt in stream_data:
                            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                coordinates.append((float(pt[0]), float(pt[1])))
                            elif isinstance(pt, (int, float)):
                                lat_list.append(float(pt))
                    elif st_type in ["lat", "latitude"]:
                        lat_list = [float(x) for x in stream_data if x is not None]
                    elif st_type in ["lng", "lon", "longitude"]:
                        lon_list = [float(x) for x in stream_data if x is not None]
            
            # Se abbiamo trovato coordinate separate (lat e lon in array distinti), le uniamo
            if not coordinates and lat_list and lon_list:
                min_len = min(len(lat_list), len(lon_list))
                coordinates = list(zip(lat_list[:min_len], lon_list[:min_len]))
                
        else:
            st.error(f"Errore di connessione a Intervals.icu (Codice: {response.status_code})")

    except Exception as e:
        st.error(f"Errore imprevisto durante il recupero dei dati: {e}")

# --- RENDER DELLA MAPPA O DEI GRAFICI ---
if len(coordinates) > 0:
    st.success(f"Tracciato GPS caricato con successo ({len(coordinates)} punti geografici).")
    
    # Creazione della mappa con Folium
    m = folium.Map(location=coordinates[0], zoom_start=13, tiles="CartoDB positron")
    folium.PolyLine(
        coordinates, 
        color="#ff4b4b", 
        weight=4, 
        opacity=0.8
    ).add_to(m)
    
    st_folium(m, width=1000, height=550, key="folium_map_render_pulito")
else:
    st.warning("⚠️ Tracciato GPS non disponibile per questa specifica attività. Vengono mostrate le metriche registrate:")

# Mostriamo comunque i grafici delle altre metriche (battito, altitudine, potenza, ecc.)
if all_streams:
    st.markdown("---")
    st.markdown("### 📊 Metriche e Flussi dell'Uscita:")
    for s in all_streams:
        if isinstance(s, dict):
            s_type = s.get("type")
            s_data = s.get("data")
            if s_type in ["watts", "heartrate", "cadence", "altitude", "velocity_smooth"] and s_data:
                st.line_chart(s_data, y_label=s_type)

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("uscite.py")
