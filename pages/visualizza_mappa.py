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
                    lat_list = stream.get("data", [])
                    lon_list = stream.get("data2", [])
                    
                    # Uniamo le due liste elemento per elemento
                    if isinstance(lat_list, list) and isinstance(lon_list, list):
                        for lat, lon in zip(lat_list, lon_list):
                            if lat is not None and lon is not None:
                                latlons.append([lat, lon])
                    break

        if latlons:
            start_coord = latlons[0]
            m = folium.Map(location=start_coord, zoom_start=13)
            
            folium.PolyLine(latlons, color="blue", weight=4, opacity=0.8).add_to(m)
            
            folium.Marker(latlons[0], popup="Partenza", icon=folium.Icon(color="green", icon="play")).add_to(m)
            folium.Marker(latlons[-1], popup="Arrivo", icon=folium.Icon(color="red", icon="stop")).add_to(m)

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
