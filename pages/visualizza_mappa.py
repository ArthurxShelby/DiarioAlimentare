import streamlit as st
st.set_page_config(layout="wide")
import requests
import pydeck as pdk

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
                                    # Pydeck vuole le coordinate nel formato [lon, lat]
                                    latlons.append([lon, lat])
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
            # Selettore di stile pulito in alto a destra sopra la mappa
            c1, c2 = st.columns([4, 2])
            with c1:
                st.subheader("Tracciato GPS")
            with c2:
                stile_mappa = st.selectbox(
                    "Stile Mappa",
                    ["Stradale (Light)", "Satellite", "Scuro (Dark)"],
                    label_visibility="collapsed"
                )

            # Traduzione dello stile nei preset ufficiali di Mapbox/Pydeck
            if "Satellite" in stile_mappa:
                map_style = "mapbox://styles/mapbox/satellite-v9"
            elif "Scuro" in stile_mappa:
                map_style = "mapbox://styles/mapbox/dark-v10"
            else:
                map_style = "mapbox://styles/mapbox/light-v10"

            # Centro della mappa calcolato sul primo punto
            center_lon, center_lat = latlons[0]

            # Creazione del layer del percorso
            path_layer = pdk.Layer(
                "PathLayer",
                data=[{"path": latlons}],
                get_path="path",
                get_color="[30, 144, 255, 200]",
                get_width=5,
                width_scale=10,
                width_min_pixels=4,
            )

            # Layer per i marker di partenza e arrivo
            markers_data = [
                {"coordinates": latlons[0], "name": "Partenza", "color": [0, 200, 0]},
                {"coordinates": latlons[-1], "name": "Arrivo", "color": [200, 0, 0]}
            ]
            marker_layer = pdk.Layer(
                "ScatterplotLayer",
                data=markers_data,
                get_position="coordinates",
                get_color="color",
                get_radius=80,
                pickable=True,
            )

            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=12,
                pitch=0,
            )

            r = pdk.Deck(
                layers=[path_layer, marker_layer],
                initial_view_state=view_state,
                map_style=map_style,
                tooltip={"text": "{name}"}
            )

            st.pydeck_chart(r)
        else:
            st.warning("Nessun punto di coordinate valido trovato nel tracciato.")

    else:
        st.error(f"Errore nel download del file dalla memoria (Status: {response.status_code}).")

except Exception as e:
    st.error(f"Errore durante l'elaborazione del tracciato: {e}")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
