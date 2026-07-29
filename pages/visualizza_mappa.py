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
                
                for stream in all_streams:
                    if isinstance(stream, dict) and stream.get("type") == "latlng":
                        latlngs = stream.get("data", [])
                        st.write(f"📊 Numero di punti grezzi trovati in latlng: {len(latlngs)}")
                        for pt in latlngs:
                            if pt and isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                try:
                                    lat, lon = float(pt[0]), float(pt[1])
                                    coordinates.append((lat, lon))
                                except (ValueError, TypeError):
                                    continue
                            elif pt and isinstance(pt, dict): # Gestione alternativa se restituisce dizionari
                                lat = pt.get("lat") or pt.get("latitude")
                                lon = pt.get("lng") or pt.get("lon") or pt.get("longitude")
                                if lat is not None and lon is not None:
                                    coordinates.append((float(lat), float(lon)))
                        break
            
            # Se troviamo le coordinate, disegniamo la mappa con Folium
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
                st.warning("⚠️ Nessun tracciato GPS (latlng) rilevato per questa attività.")
                
                # Mostriamo comunque i grafici delle metriche disponibili (es. frequenza cardiaca, potenza, altitudine)
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
