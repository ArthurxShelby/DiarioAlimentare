import streamlit as st
st.set_page_config(layout="wide")
import requests
import folium
from branca.element import MacroElement, Template
from streamlit_folium import st_folium

map_url = st.session_state.get("map_url_to_view")
activity_title = st.session_state.get("activity_title_to_view", "Dettaglio Tracciato")
activity_date = st.session_state.get("activity_date_to_view", "")

titolo_completo = f"{activity_title} ({activity_date})" if activity_date else activity_title
st.title(f"🗺️ {titolo_completo}")

if not map_url:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività.")
    if st.button("⬅️ Torna alla Gestione Uscite"):
        st.switch_page("pages/uscite.py")
    st.stop()

try:
    response = requests.get(map_url)
    if response.status_code == 200:
        data = response.json()
        
        latlons = []
        distance_meters = 0
        moving_time = 0
        total_elevation_gain = 0
        
        if isinstance(data, list):
            for stream in data:
                if isinstance(stream, dict):
                    stype = stream.get("type")
                    if stype == "latlng":
                        lat_list = stream.get("data", [])
                        lon_list = stream.get("data2", [])
                        if isinstance(lat_list, list) and isinstance(lon_list, list):
                            for lat, lon in zip(lat_list, lon_list):
                                if lat is not None and lon is not None:
                                    latlons.append([lat, lon])
                    elif stype == "distance":
                        dist_data = stream.get("data", [])
                        if dist_data:
                            distance_meters = max(dist_data)
                    elif stype == "time":
                        time_data = stream.get("data", [])
                        if time_data:
                            moving_time = max(time_data)
                    elif stype == "altitude":
                        alt_data = stream.get("data", [])
                        if alt_data and len(alt_data) > 1:
                            gain = 0
                            for i in range(1, len(alt_data)):
                                diff = alt_data[i] - alt_data[i-1]
                                if diff > 0:
                                    gain += diff
                            total_elevation_gain = gain

        km_dist = f"{distance_meters / 1000:.2f} km" if distance_meters else "N/D"
        
        hours = int(moving_time // 3600)
        minutes = int((moving_time % 3600) // 60)
        seconds = int(moving_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if moving_time else "N/D"
        
        elev_str = f"{int(total_elevation_gain)} m" if total_elevation_gain else "N/D"

        col1, col2, col3 = st.columns(3)
        col1.metric("Distanza", km_dist)
        col2.metric("Dislivello Positivo (D+)", elev_str)
        col3.metric("Tempo di Percorrenza", time_str)

        st.markdown("---")

        if latlons:
            start_coord = latlons[0]
            
            # Mappa base con OpenStreetMap
            m = folium.Map(location=start_coord, zoom_start=13, zoom_control=False)
            
            # Layer aggiuntivi
            osm_layer = folium.TileLayer(
                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                attr='&copy; OpenStreetMap contributors',
                name='Stradale'
            ).add_to(m)

            topo_layer = folium.TileLayer(
                'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                attr='Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap (CC-BY-SA)',
                name='Topografica'
            ).add_to(m)

            sat_layer = folium.TileLayer(
                'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Tiles &copy; Esri',
                name='Satellite'
            ).add_to(m)

            # Tracciato e Marker
            folium.PolyLine(latlons, color="blue", weight=4, opacity=0.8).add_to(m)
            folium.Marker(latlons[0], popup="Partenza", icon=folium.Icon(color="green", icon="play")).add_to(m)
            folium.Marker(latlons[-1], popup="Arrivo", icon=folium.Icon(color="red", icon="stop")).add_to(m)

            # Controllo layer standard nascosto tramite CSS e sostituito da un selettore pulito in alto a destra
            folium.LayerControl(collapsed=True).add_to(m)

            # Aggiunta CSS personalizzato per posizionare il selettore stile Google Maps in alto a destra
            custom_css = MacroElement()
            custom_css._template = Template("""
            {% macro script(this, kwargs) %}
            <style>
                /* Posiziona il controllo layer in alto a destra stile Google Maps */
                .leaflet-top.leaflet-right {
                    top: 10px;
                    right: 10px;
                }
                .leaflet-control-layers {
                    border-radius: 8px !important;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
                    border: none !important;
                    background: white !important;
                    padding: 6px 10px;
                }
                .leaflet-control-layers-toggle {
                    width: 36px;
                    height: 36px;
                    background-size: 20px 20px;
                }
            </style>
            {% endmacro %}
            """)
            m.get_root().add_child(custom_css)

            st_folium(m, width=1200, height=600)
        else:
            st.warning("Nessun punto di coordinate valido trovato nel tracciato.")

    else:
        st.error(f"Errore nel download del file dalla memoria (Status: {response.status_code}).")

except Exception as e:
    st.error(f"Errore durante l'elaborazione del tracciato: {e}")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
