import streamlit as st
st.set_page_config(layout="wide")
import requests
import plotly.graph_objects as go

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
        
        lats = []
        lons = []
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
                                    lats.append(float(lat))
                                    lons.append(float(lon))
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

        if lats and lons:
            c1, c2 = st.columns([4, 2])
            with c1:
                st.subheader("Tracciato GPS")
            with c2:
                stile_mappa = st.selectbox(
                    "Stile Mappa",
                    ["Stradale (OpenStreetMap)", "Satellite (ArcGIS con etichette)"],
                    label_visibility="collapsed"
                )

            fig = go.Figure()

            # Tracciato GPS
            fig.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                line=dict(width=4, color='dodgerblue'),
                name='Tracciato'
            ))

            # Marker Partenza e Arrivo
            fig.add_trace(go.Scattermapbox(
                lat=[lats[0], lats[-1]],
                lon=[lons[0], lons[-1]],
                mode='markers',
                marker=dict(size=12, color=['green', 'red']),
                text=['Partenza', 'Arrivo'],
                name='Marker'
            ))

            if "Satellite" in stile_mappa:
                # Base satellitare + layer trasparente superiore con i nomi delle località (CartoDB labels)
                mapbox_config = dict(
                    style="white-bg",
                    center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)),
                    zoom=11,
                    layers=[
                        {
                            "sourcetype": "raster",
                            "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
                            "below": "traces"
                        },
                        {
                            "sourcetype": "raster",
                            "source": ["https://cartodb-basemaps-a.global.ssl.fastly.net/rastertiles/voyager_only_labels/{z}/{x}/{y}.png"],
                            "below": "traces"
                        }
                    ]
                )
            else:
                mapbox_config = dict(
                    style="open-street-map",
                    center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)),
                    zoom=11
                )

            fig.update_layout(
                mapbox=mapbox_config,
                margin=dict(l=0, r=0, t=0, b=0),
                height=600,
                showlegend=False
            )

            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={'displayModeBar': False, 'scrollZoom': True}
            )
        else:
            st.warning("Nessun punto di coordinate valido trovato nel tracciato.")

    else:
        st.error(f"Errore nel download del file dalla memoria (Status: {response.status_code}).")

except Exception as e:
    st.error(f"Errore durante l'elaborazione del tracciato: {e}")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
