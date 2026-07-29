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

act_id = st.session_state.get("selected_activity_id")
act_title = st.session_state.get("selected_activity_title", "Attività")
act_date = st.session_state.get("selected_activity_date", "")

if not act_id:
    st.warning("⚠️ Nessuna attività selezionata. Torna alla pagina delle uscite.")
    if st.button("⬅️ Torna a Uscite", key="btn_back_1"):
        try:
            st.switch_page("pages/uscite.py")
        except Exception:
            st.switch_page("uscite.py")
    st.stop()

st.subheader(f"📍 {act_title} ({act_date})")

auth_credentials = ("API_KEY", API_KEY.strip())
coordinates = []
all_streams = []

with st.spinner("Caricamento tracciato GPS in corso..."):
    try:
        url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams"
        response = requests.get(url_streams, auth=auth_credentials)
        
        if response.status_code == 200:
            data = response.json()
            all_streams = data if isinstance(data, list) else [data]
            
            lat_list = []
            lon_list = []
            
            for stream in all_streams:
                if isinstance(stream, dict):
                    st_type = stream.get("type")
                    stream_data = stream.get("data", [])
                    
                    if st_type in ["latlng", "lating"]:
                        for pt in stream_data:
                            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                coordinates.append((float(pt[0]), float(pt[1])))
                            elif isinstance(pt, (int, float)):
                                lat_list.append(float(pt))
                    elif st_type in ["lat", "latitude"]:
                        lat_list = [float(x) for x in stream_data if x is not None]
                    elif st_type in ["lng", "lon", "longitude"]:
                        lon_list = [float(x) for x in stream_data if x is not None]
            
            # Se abbiamo trovato coordinate separate (es. lating solo come latitudini) cerchiamo se c'è un altro flusso o le usiamo
            if not coordinates and lat_list:
                # Cerchiamo un flusso di longitudine alternativo se esiste, altrimenti controlliamo se lating alternava lat/lon
                for stream in all_streams:
                    if isinstance(stream, dict) and stream.get("type") in ["lng", "lon", "longitude", "lng_smooth"]:
                        lon_data = stream.get("data", [])
                        lon_list = [float(x) for x in lon_data if x is not None]
                        break
                
                if lon_list and len(lat_list) == len(lon_list):
                    coordinates = list(zip(lat_list, lon_list))
                else:
                    # Se lating conteneva solo la latitudine e non abbiamo la longitudine nei flussi, proviamo a vedere se i dati sono accoppiati in altro modo
                    pass
        else:
            st.error(f"Errore di connessione a Intervals.icu (Codice: {response.status_code})")

    except Exception as e:
        st.error(f"Errore imprevisto: {e}")

# Render della mappa o delle metriche alternative
if len(coordinates) > 0:
    st.success(f"Tracciato GPS caricato con successo ({len(coordinates)} punti).")
    m = folium.Map(location=coordinates[0], zoom_start=13, tiles="CartoDB positron")
    folium.PolyLine(
        coordinates, 
        color="#ff4b4b", 
        weight=4, 
        opacity=0.8
    ).add_to(m)
    st_folium(m, width=1000, height=550, key="folium_map_final_render")
else:
    st.warning("⚠️ Tracciato GPS non disponibile o incompleto per questa attività. Vengono mostrate le metriche registrate:")
    if all_streams:
        st.markdown("### 📊 Metriche e Flussi Registrati:")
        for s in all_streams:
            if isinstance(s, dict) and s.get("type") in ["watts", "heartrate", "cadence", "altitude", "velocity_smooth"]:
                st.line_chart(s.get("data", []), y_label=s.get("type"))

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite", key="btn_back_2"):
    try:
        st.switch_page("pages/uscite.py")
    except Exception:
        st.switch_page("uscite.py")
