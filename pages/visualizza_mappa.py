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

if act_id:
    st.subheader(f"📍 {act_title} ({act_date})")
    
    auth_credentials = ("API_KEY", API_KEY.strip())
    coordinates = []
    all_streams = []
    
    with st.spinner("Caricamento tracciato GPS in corso..."):
        try:
            # Interroghiamo direttamente l'endpoint streams di Intervals
            url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams"
            response = requests.get(url_streams, auth=auth_credentials)
            
            if response.status_code == 200:
                data = response.json()
                all_streams = data if isinstance(data, list) else [data]
                
                # Cerchiamo separatamente latitudini e longitudini se sono in flussi distinti
                lat_list = []
                lon_list = []
                
                for stream in all_streams:
                    if isinstance(stream, dict):
                        st_type = stream.get("type")
                        if st_type == "latlng":
                            data_points = stream.get("data", [])
                            st.write(jstr := f"Trovati {len(data_points)} elementi in latlng. Tipo primo elemento: {type(data_points[0]) if data_points else 'vuoto'}")
                            
                            # Se l'elemento è un numero singolo, significa che il JSON ha i flussi separati o una struttura piatta
                            for pt in data_points:
                                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                    coordinates.append((float(pt[0]), float(pt[1])))
                                elif isinstance(pt, (int, float)):
                                    # Accumuliamo temporaneamente se è un flusso monodimensionale
                                    lat_list.append(float(pt))
                
                # Se abbiamo trovato coordinate monodimensionali, cerchiamo il corrispettivo per la longitudine
                if not coordinates and lat_list:
                    for stream in all_streams:
                        if isinstance(stream, dict) and stream.get("type") in ["lng", "longitude", "lon"]:
                            lon_data = stream.get("data", [])
                            lon_list = [float(x) for x in lon_data if x is not None]
                            break
                    
                    # Se abbiamo sia lat che lon come liste separate, le uniamo
                    if lon_list and len(lat_list) == len(lon_list):
                        coordinates = list(zip(lat_list, lon_list))
                    elif lon_list:
                        # Se le lunghezze differiscono leggermente, prendiamo il minimo comune
                        min_len = min(len(lat_list), len(lon_list))
                        coordinates = list(zip(lat_list[:min_len], lon_list[:min_len]))
            
            # --- RENDER MAPPA O GRAFICI ---
            if len(coordinates) > 0:
                st.success(f"Tracciato GPS caricato con successo ({len(coordinates)} punti).")
                m = folium.Map(location=coordinates[0], zoom_start=13, tiles="CartoDB positron")
                folium.PolyLine(
                    coordinates, 
                    color="#ff4b4b", 
                    weight=4, 
                    opacity=0.8
                ).add_to(m)
                st_folium(m, width=1000, height=550, key="folium_map_page_render")
            else:
                st.warning("⚠️ Impossibile ricoppiare latitudine e longitudine dai flussi.")
                if all_streams:
                    st.markdown("### 📊 Metriche e Flussi Registrati:")
                    for s in all_streams:
                        if isinstance(s, dict) and s.get("type") in ["watts", "heartrate", "cadence", "altitude", "velocity_smooth"]:
                            st.line_chart(s.get("data", []), y_label=s.get("type"))

        except Exception as e:
            st.error(f"Errore durante l'elaborazione dei flussi GPS: {e}")
            
    if st.button("⬅️ Torna alla Gestione Uscite"):
        try:
            st.switch_page("uscite.py")
        except Exception:
            st.info("Usa il menu laterale a sinistra per tornare alla pagina Uscite.")
else:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività dal menu laterale.")
