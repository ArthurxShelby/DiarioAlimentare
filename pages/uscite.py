
import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime, date
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import base64

# --- 0. CONTROLLO ACCESSO PROPRIETARIO ---

is_proprietario = (st.session_state.get("ruolo_corrente") == "Proprietario")

if not is_proprietario:
    st.error("🚨 Accesso Negato: questa sezione è riservata esclusivamente al proprietario.")
    st.info("Torna alla pagina principale del Diario Alimentare ed effettua il login con le credenziali da amministratore.")
    st.stop()

# --- Configurazione ---
st.title("🚴 Gestione Uscite da Intervals.icu")

try:
    API_KEY = st.secrets["intervals"]["api_key"]
    ATHLETE_ID = st.secrets["intervals"]["athlete_id"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Intervals nei secrets.")
    st.stop()

def timedelta_to_str(seconds):
    if not seconds:
        return "00:00:00"
    ore = int(seconds // 3600)
    minuti = int((seconds % 3600) // 60)
    secondi = int(seconds % 60)
    return f"{ore:02d}:{minuti:02d}:{secondi:02d}"

def safe_int(val):
    try:
        if val is None or val == "":
            return None
        return int(float(val))
    except (ValueError, TypeError):
        return None

# --- 1. CONFIGURAZIONE E PULSANTI RANGE GRAFICO ---
with st.container(border=True):
    st.subheader("📈 Analisi Grafica e Uscite per Metrica")
    st.write("Filtra il periodo temporale, seleziona la metrica e analizza i grafici interattivi con le relative uscite e mappe.")

    col_gr1, col_gr2, col_gr3 = st.columns([2, 2, 1])
    with col_gr1:
        graf_start = st.date_input("Inizio Range Grafico", value=date(2025, 11, 15), key="graf_start_date")
    with col_gr2:
        graf_end = st.date_input("Fine Range Grafico", value=date.today(), key="graf_end_date")
    with col_gr3:
        st.write("")
        st.write("")
        applica_filtro_grafici = st.button("Aggiorna Grafico", use_container_width=True)

    col_g_sel1, col_g_sel2 = st.columns(2)
    with col_g_sel1:
        tipo_metrica = st.selectbox("Seleziona Metrica Grafico", ["Chilometri (km)", "Dislivello (m)", "Ore in sella"])
    with col_g_sel2:
        tipo_periodo = st.selectbox("Raggruppamento Temporale", ["Mese", "Settimana"])

    # Chiamata API dinamica basata sul range del contenitore grafico
    with st.spinner("Sincronizzazione dati da Intervals.icu in corso..."):
        url_global = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
        params_global = {
            "oldest": graf_start.strftime("%Y-%m-%d"),
            "newest": graf_end.strftime("%Y-%m-%d"),
            "iw": True
        }
        auth_global = ("API_KEY", API_KEY.strip())
        resp_global = requests.get(url_global, auth=auth_global, params=params_global)

    df_activities_global = pd.DataFrame()
    if resp_global.status_code == 200:
        activities_net = resp_global.json()
        if activities_net:
            df_activities_global = pd.DataFrame(activities_net)
            df_activities_global["date_parsed"] = pd.to_datetime(df_activities_global["start_date_local"]).dt.date
            
            tot_km = round(df_activities_global.get("distance", pd.Series([0])).fillna(0).sum() / 1000.0, 2)
            tot_dislivello = int(df_activities_global.get("total_elevation_gain", pd.Series([0])).fillna(0).sum())
            
            st.markdown("---")
            st.subheader(f"📊 Statistiche del Periodo ({graf_start} al {graf_end}) (TCR)")
            
            col_m1, col_m2, col_img = st.columns(3)
            with col_m1:
                st.metric("Km Totali Periodo", f"{tot_km:,.2f} km")
            with col_m2:
                st.metric("D+ Totale Periodo", f"{tot_dislivello:,} m")
            with col_img:
                st.subheader("TCR Advanced Pro 0")
                try:
                    cartella_script = os.path.dirname(__file__)
                    percorso_foto = os.path.join(cartella_script, "TCR.png")
                    st.image(percorso_foto, use_container_width=True)
                except Exception:
                    st.warning("Immagine TCR.png non trovata.")
            st.markdown("---")

        # Generazione Grafico e Selettori Dettaglio Uscite
        if not df_activities_global.empty:
            df_grafico = df_activities_global.copy()
            df_grafico["km"] = df_grafico.get("distance", 0).fillna(0) / 1000.0
            df_grafico["d_plus"] = df_grafico.get("total_elevation_gain", 0).fillna(0)
            df_grafico["ore"] = df_grafico.get("moving_time", 0).fillna(0) / 3600.0

            if tipo_periodo == "Mese":
                df_grafico["periodo_chiave"] = pd.to_datetime(df_grafico["date_parsed"]).dt.to_period("M").astype(str)
            else:
                df_grafico["periodo_chiave"] = pd.to_datetime(df_grafico["date_parsed"]).dt.to_period("W").astype(str)

            colonna_valore = "km"
            titolo_asse_y = "Km"
            if tipo_metrica == "Dislivello (m)":
                colonna_valore = "d_plus"
                titolo_asse_y = "Metri (D+)"
            elif tipo_metrica == "Ore in sella":
                colonna_valore = "ore"
                titolo_asse_y = "Ore"

            df_agg = df_grafico.groupby("periodo_chiave")[colonna_valore].sum().reset_index()

            fig_ana = go.Figure(data=[
                go.Bar(
                    x=df_agg["periodo_chiave"],
                    y=df_agg[colonna_valore],
                    marker_color='dodgerblue',
                    text=df_agg[colonna_valore].round(1),
                    textposition='auto'
                )
            ])
            fig_ana.update_layout(
                title=f"Andamento {tipo_metrica} per {tipo_periodo}",
                xaxis_title="Periodo",
                yaxis_title=titolo_asse_y,
                margin=dict(l=20, r=20, t=40, b=20),
                height=350,
                clickmode='event+select'
            )

            c_chart, c_details = st.columns([3, 2])
            with c_chart:
                event_data = st.plotly_chart(fig_ana, use_container_width=True, on_select="rerun", key="plot_analitico")
                if event_data and "selection" in event_data and "points" in event_data["selection"]:
                    points = event_data["selection"]["points"]
                    if points:
                        st.session_state["active_chart_period"] = points[0]["x"]

            with c_details:
                st.markdown("#### 🔍 Uscite del Periodo Selezionato")
                lista_periodi_disponibili = df_agg["periodo_chiave"].tolist()
                periodo_attivo = st.session_state.get("active_chart_period", lista_periodi_disponibili[-1] if lista_periodi_disponibili else None)

                if periodo_attivo not in lista_periodi_disponibili and lista_periodi_disponibili:
                    periodo_attivo = lista_periodi_disponibili[-1]

                if lista_periodi_disponibili:
                    scelta_periodo_dropdown = st.selectbox(
                        "Seleziona Periodo", 
                        lista_periodi_disponibili, 
                        index=lista_periodi_disponibili.index(periodo_attivo) if periodo_attivo in lista_periodi_disponibili else 0,
                        key="dropdown_periodo_grafico"
                    )
                    
                    uscite_periodo = df_grafico[df_grafico["periodo_chiave"] == scelta_periodo_dropdown]
                    
                    if not uscite_periodo.empty:
                        options_uscite = {f"{row['start_date_local'].split('T')[0]} - {row.get('name', 'Uscita')}": row for _, row in uscite_periodo.iterrows()}
                        scelta_uscita_key = st.selectbox("Seleziona Uscita specifica", list(options_uscite.keys()), key="select_uscita_dettaglio")
                        
                        uscita_selezionata = options_uscite[scelta_uscita_key]
                        act_id = str(uscita_selezionata.get("id"))
                        act_title = uscita_selezionata.get("name", "Uscita senza titolo")
                        act_date = uscita_selezionata.get("start_date_local", "").split("T")[0]
                        act_dist = round(uscita_selezionata.get("distance", 0) / 1000, 2)
                        act_time = timedelta_to_str(uscita_selezionata.get("moving_time", 0))
                        act_elev = safe_int(uscita_selezionata.get("total_elevation_gain")) or 0

                        st.markdown(f"**{act_title}** ({act_date})")
                        st.write(f"Distanza: **{act_dist} km** | D+: **{act_elev} m** | Tempo: **{act_time}**")

                        if st.button("🔍 Apri Pagina Dedicata Mappa", key=f"btn_page_{act_id}", use_container_width=True):
                            st.session_state["selected_activity_id"] = act_id
                            st.session_state["selected_activity_title"] = act_title
                            st.session_state["selected_activity_date"] = act_date
                            st.switch_page("pages/visualizza_mappa.py")

                        # Anteprima mappa rapida
                        clean_id = ''.join(c for c in act_id if c.isdigit())
                        target_url = f"https://intervals.icu/api/v1/activity/{clean_id}/streams"
                        auth_streams = ("API_KEY", API_KEY.strip())
                        try:
                            resp_streams = requests.get(target_url, auth=auth_streams)
                            if resp_streams.status_code == 200:
                                data_stream = resp_streams.json()
                                lats, lons = [], []
                                if isinstance(data_stream, list):
                                    for stream in data_stream:
                                        if isinstance(stream, dict) and stream.get("type") in ["latlng", "lating"]:
                                            lat_data = stream.get("data", [])
                                            lon_data = stream.get("data2", [])
                                            if len(lat_data) == len(lon_data):
                                                for lat, lon in zip(lat_data, lon_data):
                                                    if lat and lon:
                                                        lats.append(float(lat))
                                                        lons.append(float(lon))
                                if lats and lons:
                                    fig_map = go.Figure(go.Scattermapbox(lat=lats, lon=lons, mode='lines', line=dict(width=3, color='red')))
                                    fig_map.update_layout(
                                        mapbox=dict(style="open-street-map", center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)), zoom=10),
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        height=200,
                                        showlegend=False
                                    )
                                    st.plotly_chart(fig_map, use_container_width=True, config={'displaylogo': False})
                        except Exception:
                            pass
                    else:
                        st.info("Nessuna uscita in questo periodo.")
        else:
            st.warning("Nessuna attività trovata nell'intervallo di date selezionato per il grafico.")
    else:
        st.error(f"Errore di connessione a Intervals.icu: {resp_global.status_code}")

# --- 2. ESPLORATORE STORICO ON-DEMAND DA INTERVALS (Esplora Archivio) ---
FILE_DATA_INIZIO = "ultima_data_inizio.txt"
FILE_DATA_FINE = "ultima_data_fine.txt"

def carica_data_salvata(file_path, default_val):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                val = f.read().strip()
                return datetime.strptime(val, "%Y-%m-%d").date()
        except Exception:
            pass
    return default_val

def salva_data_su_file(file_path, data_val):
    try:
        with open(file_path, "w") as f:
            f.write(data_val.strftime("%Y-%m-%d"))
    except Exception:
        pass

if "saved_start" not in st.session_state:
    st.session_state["saved_start"] = carica_data_salvata(FILE_DATA_INIZIO, date(2026, 1, 1))

if "saved_end" not in st.session_state:
    st.session_state["saved_end"] = carica_data_salvata(FILE_DATA_FINE, date.today())

with st.expander("🔍 Esplora Archivio Storico da Intervals (Range Personalizzato e Filtri)", expanded=False):
    st.write("Seleziona un periodo, filtra per data specifica o cerca per nome dell'uscita all'interno del flusso di Intervals.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        data_inizio_custom = st.date_input("Data Inizio Range", value=st.session_state["saved_start"], key="widget_start")
    with col_c2:
        data_fine_custom = st.date_input("Data Fine Range", value=st.session_state["saved_end"], key="widget_end")
        
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_nome = st.text_input("Filtra per Nome Uscita (opzionale):", value="", placeholder="Es. Giro Samu, Salita...")
    with col_f2:
        attiva_data_singola = st.checkbox("Filtra per una data singola specifica")
        
    data_singola_specifica = None
    if attiva_data_singola:
        data_singola_specifica = st.date_input("Seleziona Data Specifica", value=date.today(), key="widget_single_date")

    if st.button("🚀 Estrai Dati dal Flusso", key="btn_calcola_custom"):
        st.session_state["saved_start"] = data_inizio_custom
        st.session_state["saved_end"] = data_fine_custom
        salva_data_su_file(FILE_DATA_INIZIO, data_inizio_custom)
        salva_data_su_file(FILE_DATA_FINE, data_fine_custom)
        
        with st.spinner("Interrogazione in corso..."):
            if attiva_data_singola and data_singola_specifica:
                oldest_param = data_singola_specifica.strftime("%Y-%m-%d")
                newest_param = data_singola_specifica.strftime("%Y-%m-%d")
            else:
                oldest_param = data_inizio_custom.strftime("%Y-%m-%d")
                newest_param = data_fine_custom.strftime("%Y-%m-%d")

            url_custom = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
            params_custom = {
                "oldest": oldest_param,
                "newest": newest_param,
                "iw": True
            }
            auth_custom = ("API_KEY", API_KEY.strip())
            
            resp_custom = requests.get(url_custom, auth=auth_custom, params=params_custom)
            
            if resp_custom.status_code == 200:
                attivita_ext_custom = resp_custom.json()
                if attivita_ext_custom:
                    st.session_state["custom_activities"] = attivita_ext_custom
                else:
                    st.session_state["custom_activities"] = []
                    st.info("Nessuna attività trovata in questo intervallo nel flusso di Intervals.")
            else:
                st.error(f"Errore di connessione a Intervals.icu: {resp_custom.status_code}")

    if "custom_activities" in st.session_state and st.session_state["custom_activities"]:
        attivita_da_mostrare = st.session_state["custom_activities"]
        if filtro_nome.strip():
            query_testo = filtro_nome.strip().lower()
            attivita_da_mostrare = [
                act for act in attivita_da_mostrare 
                if query_testo in act.get("name", "").lower()
            ]

        if not attivita_da_mostrare:
            st.warning("Nessuna attività corrisponde al filtro di ricerca inserito.")
        else:
            df_filtrato_vista = pd.DataFrame(attivita_da_mostrare)
            distanza_tot_km = round(df_filtrato_vista.get("distance", pd.Series([0])).fillna(0).sum() / 1000.0, 2)
            dislivello_tot_m = int(df_filtrato_vista.get("total_elevation_gain", pd.Series([0])).fillna(0).sum())
            num_uscite = len(df_filtrato_vista)
            
            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Km Totali Periodo", f"{distanza_tot_km:,.2f} km")
            mc2.metric("Dislivello (D+) Periodo", f"{dislivello_tot_m:,} m")
            mc3.metric("Uscite Registrate", f"{num_uscite}")
            st.markdown("---")
            
            with st.container(height=650):
                for idx, act in enumerate(attivita_da_mostrare):
                    act_id = str(act.get("id"))
                    act_title = act.get("name", "Uscita senza titolo")
                    act_date = act.get("start_date_local", "").split("T")[0]
                    act_dist = round(act.get("distance", 0) / 1000, 2)
                    act_time = timedelta_to_str(act.get("moving_time", 0))
                    act_elev = safe_int(act.get("total_elevation_gain")) or 0
                    
                    key_toggle = f"show_map_{act_id}_{idx}"
                    if key_toggle not in st.session_state:
                        st.session_state[key_toggle] = False
                    
                    with st.container(border=True):
                        col_info, col_btn1, col_btn2 = st.columns([3, 1, 1])
                        with col_info:
                            st.markdown(f"<h3 style='margin: 0; padding-bottom: 5px;'>{act_title} <span style='font-size: 1.1rem; color: #999;'>({act_date})</span></h3>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-size: 1.2rem; margin: 0;'>Distanza: <b>{act_dist} km</b> &nbsp;|&nbsp; D+: <b>{act_elev} m</b> &nbsp;|&nbsp; Tempo: <b>{act_time}</b></p>", unsafe_allow_html=True)
                        with col_btn1:
                            st.write("") 
                            btn_label = "🗺️ Nascondi Mappa" if st.session_state[key_toggle] else "🗺️ Anteprima Mappa"
                            if st.button(btn_label, key=f"btn_preview_{act_id}_{idx}", use_container_width=True):
                                st.session_state[key_toggle] = not st.session_state[key_toggle]
                                st.rerun()
                        with col_btn2:
                            st.write("") 
                            if st.button("🔍 Pagina Dedicata", key=f"btn_custom_{act_id}_{idx}", use_container_width=True):
                                st.session_state["selected_activity_id"] = act_id
                                st.session_state["selected_activity_title"] = act_title
                                st.session_state["selected_activity_date"] = act_date
                                st.switch_page("pages/visualizza_mappa.py")

                        if st.session_state[key_toggle]:
                            st.markdown("---")
                            
                            clean_id = ''.join(c for c in act_id if c.isdigit())
                            target_url = f"https://intervals.icu/api/v1/activity/{clean_id}/streams"
                            auth_streams = ("API_KEY", API_KEY.strip())
                            
                            with st.spinner("Caricamento tracciato in corso..."):
                                try:
                                    resp_streams = requests.get(target_url, auth=auth_streams)
                                    if resp_streams.status_code == 404 and act_id != clean_id:
                                        target_url = f"https://intervals.icu/api/v1/activity/{act_id}/streams"
                                        resp_streams = requests.get(target_url, auth=auth_streams)
                                        
                                    if resp_streams.status_code == 200:
                                        data = resp_streams.json()
                                        lats, lons = [], []
                                        
                                        if isinstance(data, list):
                                            for stream in data:
                                                if isinstance(stream, dict):
                                                    stype = stream.get("type")
                                                    if stype in ["latlng", "lating"]:
                                                        lat_data = stream.get("data", [])
                                                        lon_data = stream.get("data2", [])
                                                        
                                                        if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data) and len(lat_data) > 0:
                                                            for lat, lon in zip(lat_data, lon_data):
                                                                if lat is not None and lon is not None:
                                                                    lats.append(float(lat))
                                                                    lons.append(float(lon))
                                                        elif isinstance(lat_data, list) and len(lat_data) > 0:
                                                            for pt in lat_data:
                                                                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                                                    if pt[0] is not None and pt[1] is not None:
                                                                        lats.append(float(pt[0]))
                                                                        lons.append(float(pt[1]))
                                                                        
                                        if lats and lons:
                                            c_map_title, c_map_style = st.columns([4, 2])
                                            with c_map_title:
                                                st.markdown("#### 🗺️ Percorso Attività")
                                            with c_map_style:
                                                stile_mappa_prev = st.selectbox(
                                                    "Stile Mappa",
                                                    ["Stradale (OpenStreetMap)", "Satellite (ArcGIS)"],
                                                    key=f"style_{act_id}_{idx}",
                                                    label_visibility="collapsed"
                                                )
                                            
                                            if "Satellite" in stile_mappa_prev:
                                                basemap_style = "white-bg"
                                                tile_source = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                                labels_source = "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                                            else:
                                                basemap_style = "open-street-map"
                                                tile_source = None
                                                labels_source = None

                                            fig = go.Figure()
                                            fig.add_trace(go.Scattermapbox(
                                                lat=lats, lon=lons, mode='lines',
                                                line=dict(width=4, color='dodgerblue'), name='Tracciato'
                                            ))
                                            fig.add_trace(go.Scattermapbox(
                                                lat=[lats[0], lats[-1]], lon=[lons[0], lons[-1]], mode='markers',
                                                marker=dict(size=10, color=['green', 'red']), text=['Partenza', 'Arrivo'], name='Marker'
                                            ))
                                            
                                            mapbox_config = dict(
                                                style=basemap_style,
                                                center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)),
                                                     zoom=11
                                            )

                                            layers_list = []
                                            if tile_source:
                                                layers_list.append({
                                                    "sourcetype": "raster",
                                                    "source": [tile_source],
                                                    "below": "traces"
                                                })
                                            if labels_source:
                                                layers_list.append({
                                                    "sourcetype": "raster",
                                                    "source": [labels_source],
                                                    "below": "traces"
                                                })
                                                
                                            if layers_list:
                                                mapbox_config["layers"] = layers_list

                                            fig.update_layout(
                                                mapbox=mapbox_config,
                                                margin=dict(l=0, r=0, t=0, b=0),
                                                height=450,
                                                showlegend=False
                                            )
                                            
                                            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displaylogo': False})
                                            
                                            linee = [
                                                '<?xml version="1.0" encoding="UTF-8"?>',
                                                '<gpx version="1.1" creator="Streamlit App" xmlns="http://www.topografix.com/GPX/1/1">',
                                                '  <trk>',
                                                f'    <name>{act_title}</name>',
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
                                            nome_file = "".join(c for c in act_title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                                            if not nome_file:
                                                nome_file = "tracciato"

                                            b64 = base64.b64encode(contenuto_gpx.encode()).decode()
                                            href = f'<a href="data:application/gpx+xml;base64,{b64}" download="{nome_file}.gpx" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 600; margin-top: 0.5rem; margin-bottom: 0.5rem;">📥 Scarica Tracciato GPX</div></a>'
                                            st.markdown(href, unsafe_allow_html=True)
                                        else:
                                            st.warning("Nessun punto di coordinate valido trovato in questa attività.")
                                    else:
                                        st.error(f"Errore nel recupero flussi da Intervals (Status: {resp_streams.status_code})")
                                except Exception as e:
                                    st.error(f"Errore durante il caricamento della mappa: {e}")
