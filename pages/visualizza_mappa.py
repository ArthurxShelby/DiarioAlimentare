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
            
            # Cerchiamo il flusso GPS (gestendo sia 'latlng' che il typo 'lating' restituito da Intervals)[cite: 1]
            for stream in all_streams:
                if isinstance(stream, dict) and stream.get("type") in ["latlng", "lating"]:
                    latlngs = stream.get("data", [])
                    for pt in latlngs:
                        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                            lat, lon = pt[0], pt[1]
                            if lat is not None and lon is not None:
                                coordinates.append((float(lat), float(lon)))
                    break
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
    st.warning("⚠️ Tracciato GPS non disponibile per questa attività. Vengono mostrate le metriche registrate:")
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
