import streamlit as st
st.set_page_config(layout="wide")
import requests
import plotly.graph_objects as go
import base64

# --- 0. CONTROLLO ACCESSO PROPRIETARIO ---
is_proprietario = (st.session_state.get("ruolo_corrente") == "Proprietario")

if not is_proprietario:
    st.error("🚨 Accesso Negato: questa sezione è riservata esclusivamente al proprietario.")
    st.info("Torna alla pagina principale del Diario Alimentare ed effettua il login con le credenziali da amministratore.")
    st.stop()

map_url = st.session_state.get("map_url_to_view") or st.session_state.get("selected_activity_id")
activity_title = st.session_state.get("activity_title_to_view") or st.session_state.get("selected_activity_title", "Dettaglio Tracciato")
activity_date = st.session_state.get("activity_date_to_view") or st.session_state.get("selected_activity_date", "")

titolo_completo = f"{activity_title} ({activity_date})" if activity_date else activity_title
st.title(f"🗺️ {titolo_completo}")

if not map_url:
    st.warning("Nessun tracciato selezionato. Torna alla pagina Uscite e seleziona un'attività.")
    if st.button("⬅️ Torna alla Gestione Uscite"):
        st.switch_page("pages/uscite.py")
    st.stop()

try:
    API_KEY = st.secrets["intervals"]["api_key"]
except Exception:
    st.error("Configura la chiave API nei secrets.")
    st.stop()

auth_credentials = ("API_KEY", API_KEY.strip())

activity_id = str(map_url).strip()
clean_id = ''.join(c for c in activity_id if c.isdigit())
if not clean_id:
    clean_id = activity_id

target_url = f"https://intervals.icu/api/v1/activity/{clean_id}/streams"

try:
    response = requests.get(target_url, auth=auth_credentials)
    if response.status_code == 404 and activity_id != clean_id:
        target_url = f"https://intervals.icu/api/v1/activity/{activity_id}/streams"
        response = requests.get(target_url, auth=auth_credentials)

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
                    if stype in ["latlng", "lating"]:
                        lat_data = stream.get("data", [])
                        lon_data = stream.get("data2", [])
                        
                        # Caso A: Coordinate separate (data e data2)
                        if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data) and len(lat_data) > 0:
                            for lat, lon in zip(lat_data, lon_data):
                                if lat is not None and lon is not None:
                                    lats.append(float(lat))
                                    lons.append(float(lon))
                        # Caso B: Coordinate in un unico array di coppie [lat, lon]
                        elif isinstance(lat_data, list) and len(lat_data) > 0:
                            for pt in lat_data:
                                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                    if pt[0] is not None and pt[1] is not None:
                                        lats.append(float(pt[0]))
                                        lons.append(float(pt[1]))
                                        
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
            # Creazione sicura del contenuto GPX riga per riga
            linee = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<gpx version="1.1" creator="Streamlit App" xmlns="http://www.topografix.com/GPX/1/1">',
                '  <trk>',
                f'    <name>{activity_title}</name>',
                '    <trkseg>'
            ]
            for lat, lon in zip(lats, lons):
                linee.append(f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>')
            linee.extend([
                '    </trkseg>',
                '  </trk>',
                '</gpx>'
            ])
            contenuto_gpx = "\n".join(linee)

            nome_file = "".join(c for c in activity_title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
            if not nome_file:
                nome_file = "tracciato"

            c1, c2 = st.columns([4, 2])
            with c1:
                st.subheader("Tracciato GPS")
            with c2:
                stile_mappa = st.selectbox(
                    "Stile Mappa",
                    ["Stradale (OpenStreetMap)", "Satellite (ArcGIS)"],
                    label_visibility="collapsed"
                )

            # Pulsante di download diretto tramite HTML/Base64 per massima compatibilità
            b64 = base64.b64encode(contenuto_gpx.encode()).decode()
            href = f'<a href="data:application/gpx+xml;base64,{b64}" download="{nome_file}.gpx" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 600; margin-bottom: 1rem;">📥 Scarica Tracciato GPX</div></a>'
            st.markdown(href, unsafe_allow_html=True)

            # Configurazione delle tile layer di sfondo per Plotly
            if "Satellite" in stile_mappa:
                basemap_style = "white-bg"
                tile_source = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            else:
                basemap_style = "open-street-map"
                tile_source = None

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

            mapbox_config = dict(
                style=basemap_style,
                center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)),
                zoom=11
            )

            if tile_source:
                mapbox_config["layers"] = [{
                    "sourcetype": "raster",
                    "source": [tile_source],
                    "below": "traces"
                }]

            fig.update_layout(
                mapbox=mapbox_config,
                margin=dict(l=0, r=0, t=0, b=0),
                height=750,
                showlegend=False
            )

            # Attiviamo la toolbar per consentire lo zoom a rotellina e la visualizzazione a schermo intero
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={
                    'displayModeBar': True,
                    'scrollZoom': True,
                    'displaylogo': False
                }
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
