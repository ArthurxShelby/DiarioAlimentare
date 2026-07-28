import streamlit as st
st.set_page_config(layout="wide")
import requests
import folium
from streamlit_folium import st_folium

st.title("🗺️ Dettaglio Tracciato Interattivo")

map_url = st.session_state.get("map_url_to_view")

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
        if isinstance(data, list):
            for stream in data:
                if isinstance(stream, dict) and stream.get("type") == "latlng":
                    raw_data = stream.get("data", [])
                    # Se raw_data è una lista di liste/chunk o una lista di coordinate dirette
                    if isinstance(raw_data, list):
                        for item in raw_data:
                            if isinstance(item, (list, tuple)):
                                # Controlliamo se è un punto singolo [lat, lon] o una lista di punti
                                if len(item) >= 2 and isinstance(item[0], (int, float)):
                                    latlons.append(item)
                                elif isinstance(item, list):
                                    for sub_item in item:
                                        if isinstance(sub_item, (list, tuple)) and len(sub_item) >= 2:
                                            latlons.append(sub_item)
                    break

        points = []
        for pt in latlons:
            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                lat, lon = pt[0], pt[1]
                if lat is not None and lon is not None:
                    points.append([lat, lon])

        if points:
            start_coord = points[0]
            m = folium.Map(location=start_coord, zoom_start=13)
            
            folium.PolyLine(points, color="blue", weight=4, opacity=0.8).add_to(m)
            
            folium.Marker(points[0], popup="Partenza", icon=folium.Icon(color="green", icon="play")).add_to(m)
            folium.Marker(points[-1], popup="Arrivo", icon=folium.Icon(color="red", icon="stop")).add_to(m)

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
