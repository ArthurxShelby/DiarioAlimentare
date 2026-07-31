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

# --- 1. STATISTICHE DINAMICHE DIRETTAMENTE DA INTERVALS (Dal 15/11/2025) ---
with st.spinner("Sincronizzazione dati da Intervals.icu in corso..."):
    url_global = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
    params_global = {
        "oldest": "2025-11-15",
        "newest": date.today().strftime("%Y-%m-%d"),
        "iw": True
    }
    auth_global = ("API_KEY", API_KEY.strip())
    
    resp_global = requests.get(url_global, auth=auth_global, params=params_global)

if resp_global.status_code == 200:
    activities_net = resp_global.json()
    
    if activities_net:
        df_activities = pd.DataFrame(activities_net)
        
        tot_km = round(df_activities.get("distance", pd.Series([0])).fillna(0).sum() / 1000.0, 2)
        tot_dislivello = int(df_activities.get("total_elevation_gain", pd.Series([0])).fillna(0).sum())
        
        st.markdown("---")
        st.subheader("📊 Statistiche Dinamiche e Riepilogo (TCR - Dal 15/11/2025)")
        
        col_m1, col_m2, col_img = st.columns(3)
        
        with col_m1:
            st.metric("Km Totali (Raccolta)", f"{tot_km:,.2f} km")
        with col_m2:
            st.metric("D+ Totale (Raccolta)", f"{tot_dislivello:,} m")
        with col_img:
            st.subheader("TCR Advanced Pro 0")
            try:
                cartella_script = os.path.dirname(__file__)
                percorso_foto = os.path.join(cartella_script, "TCR.png")
                st.image(percorso_foto, use_container_width=True)
            except Exception:
                st.warning("Immagine TCR.png non trovata.")
        
        st.markdown("---")
    else:
        st.info("Nessuna attività trovata a partire dal 15/11/2025.")
else:
    st.error(f"Errore di connessione a Intervals.icu: {resp_global.status_code}")

# --- 2. ESPLORATORE STORICO ON-DEMAND DA INTERVALS (Persistenza su File per Riavvii) ---
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
                                            
                                            st.plotly_chart(fig, use_container_width=True, key=f"plotly_hist_{act_id}_{idx}", config={'scrollZoom': True, 'displaylogo': False})
                                            
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

# --- 3. CONTENITORE GRAFICI INTERATTIVI E DETTAGLIO USCITE (Range Persistente Indipendente) ---
st.markdown("---")

FILE_GRAFICO_INIZIO = "grafico_data_inizio.txt"
FILE_GRAFICO_FINE = "grafico_data_fine.txt"

if "grafico_start_val" not in st.session_state:
    st.session_state["grafico_start_val"] = carica_data_salvata(FILE_GRAFICO_INIZIO, date(2026, 1, 1))

if "grafico_end_val" not in st.session_state:
    st.session_state["grafico_end_val"] = carica_data_salvata(FILE_GRAFICO_FINE, date.today())

with st.expander("📈 Analisi Grafica e Dettaglio Uscite per Metrica", expanded=False):
    st.write("Fissa il range temporale di ricerca, il livello di aggregazione (Settimane/Mesi) e seleziona il parametro da analizzare.")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns([2, 2, 2, 2])
    with col_r1:
        range_inizio = st.date_input("Inizio Range Grafico", value=st.session_state["grafico_start_val"], key="grafico_start_input")
    with col_r2:
        range_fine = st.date_input("Fine Range Grafico", value=st.session_state["grafico_end_val"], key="grafico_end_input")
    with col_r3:
        tipo_aggregazione = st.selectbox(
            "Raggruppa per",
            ["Giornaliero", "Settimanale", "Mensile"],
            key="selettore_aggregazione"
        )
    with col_r4:
        scelta_metrica = st.selectbox(
            "Seleziona Dato Grafico",
            ["Km", "D+", "Ore in sella"],
            key="selettore_metrica_grafico"
        )

    if range_inizio != st.session_state["grafico_start_val"] or range_fine != st.session_state["grafico_end_val"]:
        st.session_state["grafico_start_val"] = range_inizio
        st.session_state["grafico_end_val"] = range_fine
        salva_data_su_file(FILE_GRAFICO_INIZIO, range_inizio)
        salva_data_su_file(FILE_GRAFICO_FINE, range_fine)

    url_grafico = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
    params_grafico = {
        "oldest": range_inizio.strftime("%Y-%m-%d"),
        "newest": range_fine.strftime("%Y-%m-%d"),
        "iw": True
    }
    resp_grafico = requests.get(url_grafico, auth=("API_KEY", API_KEY.strip()), params=params_grafico)

    if resp_grafico.status_code == 200:
        dati_raw_grafico = resp_grafico.json()
        if dati_raw_grafico:
            df_g = pd.DataFrame(dati_raw_grafico)
            
            df_g['data_fmt'] = pd.to_datetime(df_g['start_date_local'])
            df_g['data_solo'] = df_g['data_fmt'].dt.date
            df_g['Km'] = df_g.get('distance', 0).fillna(0) / 1000.0
            df_g['D+'] = df_g.get('total_elevation_gain', 0).fillna(0)
            df_g['Ore in sella'] = df_g.get('moving_time', 0).fillna(0) / 3600.0
            df_g['titolo_uscita'] = df_g.get('name', 'Uscita senza nome')
            df_g['id_str'] = df_g.get('id').astype(str)

            if tipo_aggregazione == "Settimanale":
                df_g['periodo_chiave'] = df_g['data_fmt'].dt.to_period('W').dt.start_time.dt.date
                df_aggregato = df_g.groupby('periodo_chiave').agg({
                    'Km': 'sum',
                    'D+': 'sum',
                    'Ore in sella': 'sum',
                    'titolo_uscita': lambda x: f"Totale Settimanale ({len(x)} uscite)"
                }).reset_index().rename(columns={'periodo_chiave': 'asse_x'})
            elif tipo_aggregazione == "Mensile":
                df_g['periodo_chiave'] = df_g['data_fmt'].dt.to_period('M').dt.start_time.dt.date
                df_aggregato = df_g.groupby('periodo_chiave').agg({
                    'Km': 'sum',
                    'D+': 'sum',
                    'Ore in sella': 'sum',
                    'titolo_uscita': lambda x: f"Totale Mensile ({len(x)} uscite)"
                }).reset_index().rename(columns={'periodo_chiave': 'asse_x'})
            else:
                df_g['periodo_chiave'] = df_g['data_solo']
                df_aggregato = df_g.copy().rename(columns={'data_solo': 'asse_x'})

            fig_stat = go.Figure()
            
            fig_stat.add_trace(go.Bar(
                x=df_aggregato['asse_x'],
                y=df_aggregato[scelta_metrica],
                name=scelta_metrica,
                marker=dict(color='dodgerblue'),
                customdata=df_aggregato['asse_x'].astype(str).values
            ))

            fig_stat.update_layout(
                title=f"Andamento {tipo_aggregazione.lower()}: {scelta_metrica}",
                xaxis_title="Periodo",
                yaxis_title=scelta_metrica,
                margin=dict(l=20, r=20, t=40, b=20),
                height=350,
                clickmode='event+select'
            )

            event_selezionato = st.plotly_chart(fig_stat, use_container_width=True, on_select="rerun", key="chart_uscite_interattivo")

            periodo_selezionato = None
            if event_selezionato and "selection" in event_selezionato and event_selezionato["selection"]["points"]:
                punto = event_selezionato["selection"]["points"][0]
                if "customdata" in punto:
                    periodo_selezionato = punto["customdata"]

            if periodo_selezionato:
                p_date = datetime.strptime(periodo_selezionato, "%Y-%m-%d").date()
                df_filtrato_periodo = df_g[df_g['periodo_chiave'] == p_date]
            else:
                df_filtrato_periodo = df_g

            if df_filtrato_periodo.empty:
                df_filtrato_periodo = df_g

            tot_km_periodo = df_filtrato_periodo['Km'].sum()
            tot_d_periodo = df_filtrato_periodo['D+'].sum()
            tot_ore_periodo = df_filtrato_periodo['Ore in sella'].sum()

            st.markdown("---")
            
            if periodo_selezionato:
                p_date_str = datetime.strptime(periodo_selezionato, "%Y-%m-%d").strftime("%d/%m/%Y")
                if tipo_aggregazione == "Settimanale":
                    etichetta_periodo = f"Settimana dal {p_date_str}"
                elif tipo_aggregazione == "Mensile":
                    etichetta_periodo = f"Mese di {datetime.strptime(periodo_selezionato, '%Y-%m-%d').strftime('%B %Y')}"
                else:
                    etichetta_periodo = f"Giorno {p_date_str}"
                titolo_totali = f"Totale Selezionato ({etichetta_periodo})"
            else:
                titolo_totali = "Totale Intero Periodo"

            st.markdown(f"#### 📊 {titolo_totali}")
            
            col_tot1, col_tot2, col_tot3 = st.columns(3)
            col_tot1.metric("Km", f"{tot_km_periodo:,.2f} km")
            col_tot2.metric("D+", f"{tot_d_periodo:,.0f} m")
            col_tot3.metric("Ore in sella", f"{timedelta_to_str(tot_ore_periodo * 3600)}")

            st.markdown("---")
            
            # --- CALENDARIO / SELETTORE TEMPORALE INDIPENDENTE E PERSISTENTE ---
            st.markdown("#### 📅 Calendario Selezione Uscite")
            st.write("Seleziona una data specifica per richiamare l'uscita effettuata in quel giorno (o scegli direttamente dal menu correlato se ci sono più uscite).")
            
            df_ordinato_periodo = df_filtrato_periodo.sort_values('data_fmt', ascending=False)
            
            # Estraiamo le date disponibili per abilitare/guidare il calendario
            date_disponibili = sorted(list(df_ordinato_periodo['data_solo'].unique()))
            
            if date_disponibili:
                min_data_Uscita = min(date_disponibili)
                max_data_Uscita = max(date_disponibili)
                
                # Default calendar date recuperato dallo stato o impostato sull'ultima data disponibile
                if "calendario_uscita_val" not in st.session_state:
                    st.session_state["calendario_uscita_val"] = max_data_Uscita
                
                col_cal1, col_cal2 = st.columns([1, 1])
                with col_cal1:
                    data_calendario_scelta = st.date_input(
                        "Seleziona la data dell'uscita",
                        value=st.session_state["calendario_uscita_val"],
                        min_value=min_data_Uscita,
                        max_value=max_data_Uscita,
                        key="widget_calendario_uscita"
                    )
                    st.session_state["calendario_uscita_val"] = data_calendario_scelta
                
                # Filtriamo le uscite effettuate esattamente nel giorno selezionato nel calendario
                df_giorno_scelto = df_ordinato_periodo[df_ordinato_periodo['data_solo'] == data_calendario_scelta]
                
                if not df_giorno_scelto.empty:
                    opzioni_giorno = {
                        f"{row['titolo_uscita']} ({row[scelta_metrica]:.1f} {scelta_metrica})": row['id_str'] 
                        for _, row in df_giorno_scelto.iterrows()
                    }
                    
                    with col_cal2:
                        scelta_utente_tendina = st.selectbox(
                            f"Uscite nel giorno ({len(opzioni_giorno)} disponibili)",
                            options=list(opzioni_giorno.keys()),
                            key="select_uscita_da_calendario"
                        )
                    
                    id_attivita_scelta = opzioni_giorno[scelta_utente_tendina]
                    st.session_state["id_uscita_selezionata_pers"] = id_attivita_scelta
                else:
                    with col_cal2:
                        st.info(f"Nessuna uscita registrata il giorno {data_calendario_scelta.strftime('%d/%m/%Y')}.")
                    # Fallback sull'ultima uscita salvata se esiste
                    id_attivita_scelta = st.session_state.get("id_uscita_selezionata_pers", df_ordinato_periodo.iloc[0]['id_str'])
            else:
                st.warning("Nessuna data disponibile nel periodo corrente.")
                id_attivita_scelta = None
            
            if id_attivita_scelta:
                dati_uscita_corrente = df_g[df_g['id_str'] == id_attivita_scelta].iloc[0]

                st.markdown(f"#### 🚴 Dettaglio: {dati_uscita_corrente['titolo_uscita']} ({dati_uscita_corrente['data_solo']})")
                
                clean_id_g = ''.join(c for c in id_attivita_scelta if c.isdigit())
                target_url_g = f"https://intervals.icu/api/v1/activity/{clean_id_g}/streams"
                
                with st.spinner("Caricamento traccia GPS in corso..."):
                    resp_str_g = requests.get(target_url_g, auth=("API_KEY", API_KEY.strip()))
                    if resp_str_g.status_code == 404 and id_attivita_scelta != clean_id_g:
                        target_url_g = f"https://intervals.icu/api/v1/activity/{id_attivita_scelta}/streams"
                        resp_str_g = requests.get(target_url_g, auth=("API_KEY", API_KEY.strip()))

                    if resp_str_g.status_code == 200:
                        stream_data_g = resp_str_g.json()
                        lats_g, lons_g = [], []
                        
                        if isinstance(stream_data_g, list):
                            for stream in stream_data_g:
                                if isinstance(stream, dict):
                                    stype = stream.get("type")
                                    if stype in ["latlng", "lating"]:
                                        lat_data = stream.get("data", [])
                                        lon_data = stream.get("data2", [])
                                        
                                        if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data) and len(lat_data) > 0:
                                            for lat, lon in zip(lat_data, lon_data):
                                                if lat is not None and lon is not None:
                                                    lats_g.append(float(lat))
                                                    lons_g.append(float(lon))
                                        break

                        if lats_g and lons_g and len(lats_g) > 0:
                            with st.expander("🗺️ Visualizza Mappa e Download GPX", expanded=False):
                                tipo_mappa = st.radio(
                                    "Stile Mappa",
                                    ["Satellite", "Standard"],
                                    horizontal=True,
                                    key=f"stile_mappa_{id_attivita_scelta}"
                                )

                                fig_map = go.Figure()
                                fig_map.add_trace(go.Scattermapbox(
                                    lat=lats_g, lon=lons_g, mode='lines',
                                    line=dict(width=4, color='dodgerblue'), name='Tracciato'
                                ))
                                fig_map.add_trace(go.Scattermapbox(
                                    lat=[lats_g[0], lats_g[-1]], lon=[lons_g[0], lons_g[-1]], mode='markers',
                                    marker=dict(size=10, color=['green', 'red']), text=['Partenza', 'Arrivo'], name='Marker'
                                ))
                                
                                if tipo_mappa == "Satellite":
                                    mapbox_config = dict(
                                        style="white-bg",
                                        layers=[
                                            {
                                                "below": 'traces',
                                                "sourcetype": "raster",
                                                "source": [
                                                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                                ]
                                            },
                                            {
                                                "below": 'traces',
                                                "sourcetype": "raster",
                                                "source": [
                                                    "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                                                ]
                                            }
                                        ],
                                        center=dict(lat=sum(lats_g)/len(lats_g), lon=sum(lons_g)/len(lons_g)),
                                        zoom=11
                                    )
                                else:
                                    mapbox_config = dict(
                                        style="open-street-map",
                                        center=dict(lat=sum(lats_g)/len(lats_g), lon=sum(lons_g)/len(lons_g)),
                                        zoom=11
                                    )

                                fig_map.update_layout(
                                    mapbox=mapbox_config,
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    height=450,
                                    showlegend=False
                                )
                                
                                st.plotly_chart(fig_map, use_container_width=True, key=f"plotly_grafico_det_{id_attivita_scelta}", config={'scrollZoom': True, 'displaylogo': False})

                                linee_gpx = [
                                    '<?xml version="1.0" encoding="UTF-8"?>',
                                    '<gpx version="1.1" creator="Streamlit App" xmlns="http://www.topografix.com/GPX/1/1">',
                                    '  <trk>',
                                    f'    <name>{dati_uscita_corrente["titolo_uscita"]}</name>',
                                    '    <trkseg>'
                                ]
                                for lat, lon in zip(lats_g, lons_g):
                                    linee_gpx.append(f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>')
                                linee_gpx.extend([
                                    '    </trkseg>',
                                    '  </trk>',
                                    '</gpx>'
                                ])
                                contenuto_gpx_uscita = "\n".join(linee_gpx)
                                nome_file_gpx = "".join(c for c in dati_uscita_corrente["titolo_uscita"] if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                                if not nome_file_gpx:
                                    nome_file_gpx = "tracciato_uscita"

                                b64_gpx = base64.b64encode(contenuto_gpx_uscita.encode()).decode()
                                href_gpx = f'<a href="data:application/gpx+xml;base64,{b64_gpx}" download="{nome_file_gpx}.gpx" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 600; margin-top: 0.5rem; margin-bottom: 0.5rem;">📥 Scarica Tracciato GPX</div></a>'
                                st.markdown(href_gpx, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Nessuna coordinata GPS valida disponibile per questa specifica uscita su Intervals.icu.")
                    else:
                        st.error(f"Errore nel recupero flussi da Intervals (Status: {resp_str_g.status_code})")
        else:
            st.info("Nessuna attività trovata nel range temporale selezionato per il grafico.")
    else:
        st.error("Errore nel recupero dati per il grafico da Intervals.icu.")

# --- 4. REINTEGRO NUTRIZIONALE E ANALISI ENERGETICA POST-USCITA ---
st.markdown("---")
with st.expander("🍽️ Reintegro Nutrizionale e Bilancio Energetico Post-Uscita", expanded=True):
    st.write("Seleziona un'uscita specifica per analizzare il dispendio energetico reale e calcolare i carboidrati e l'idratazione necessari per il recupero.")
    
    if 'df_g' in locals() and not df_g.empty:
        df_nutri_source = df_g.sort_values('data_fmt', ascending=False)
    elif 'df_activities' in locals() and not df_activities.empty:
        df_nutri_source = df_activities.copy()
        df_nutri_source['data_fmt'] = pd.to_datetime(df_nutri_source['start_date_local'])
        df_nutri_source['data_solo'] = df_nutri_source['data_fmt'].dt.date
        df_nutri_source['Km'] = df_nutri_source.get('distance', 0).fillna(0) / 1000.0
        df_nutri_source['D+'] = df_nutri_source.get('total_elevation_gain', 0).fillna(0)
        df_nutri_source['Ore in sella'] = df_nutri_source.get('moving_time', 0).fillna(0) / 3600.0
        df_nutri_source['titolo_uscita'] = df_nutri_source.get('name', 'Uscita')
        df_nutri_source['id_str'] = df_nutri_source.get('id').astype(str)
        df_nutri_source = df_nutri_source.sort_values('data_fmt', ascending=False)
    else:
        df_nutri_source = pd.DataFrame()

    if not df_nutri_source.empty:
        opzioni_nutri = {
            f"{row['data_solo']} - {row['titolo_uscita']} ({row['Km']:.1f} km)": row['id_str']
            for _, row in df_nutri_source.iterrows()
        }
        
        lista_chiavi_nutri = list(opzioni_nutri.keys())
        indice_default_nutri = 0
        if "id_uscita_nutri_pers" in st.session_state:
            for i, (k, v) in enumerate(opzioni_nutri.items()):
                if v == st.session_state["id_uscita_nutri_pers"]:
                    indice_default_nutri = i
                    break

        scelta_chiave_nutri = st.selectbox(
            "Seleziona Uscita per il Calcolo Nutrizionale",
            options=lista_chiavi_nutri,
            index=indice_default_nutri,
            key="selettore_uscita_nutrizione"
        )
        
        id_sel_nutri = opzioni_nutri[scelta_chiave_nutri]
        st.session_state["id_uscita_nutri_pers"] = id_sel_nutri

        act_nutri = df_nutri_source[df_nutri_source['id_str'] == id_sel_nutri].iloc[0]
        
        raw_energy = act_nutri.get('energy', 0)
        if pd.isna(raw_energy) or raw_energy == 0:
            ore_mov = act_nutri.get('Ore in sella', 1)
            raw_energy = ore_mov * 650
            
        kcal_consumate = float(raw_energy)
        durata_ore = act_nutri.get('Ore in sella', 0)
        dist_km = act_nutri.get('Km', 0)
        titolo_att = act_nutri.get('titolo_uscita', 'Uscita')
        data_att = act_nutri.get('data_solo', date.today())

        carb_recupero_immediato = int(durata_ore * 50) if durata_ore > 0 else int(kcal_consumate * 0.15 / 4)
        litri_acqua = round(durata_ore * 0.8, 1)

        st.markdown(f"### 🎯 Resoconto Nutrizionale per: *{titolo_att}* ({data_att})")
        
        col_n1, col_n2, col_n3, col_n4 = st.columns(4)
        col_n1.metric("🔥 Dispendio Energetico", f"{kcal_consumate:,.0f} kcal")
        col_n2.metric("⏱️ Tempo in Sella", f"{timedelta_to_str(durata_ore * 3600)}")
        col_n3.metric("🍞 Carboidrati Post (Stima)", f"~{carb_recupero_immediato} g")
        col_n4.metric("💧 Reidratazione Consigliata", f"~{litri_acqua} L")

        st.info(
            f"**Linee guida nutrizionali post-allenamento:** Per recuperare le **{kcal_consumate:,.0f} kcal** consumate in {dist_km:.1f} km, "
            f"è consigliato assumere un pasto o uno shake di recupero ricco di carboidrati ad alto indice glicemico nelle prime 2 ore "
            f"(circa **{carb_recupero_immediato}g di carboidrati**) insieme a una quota proteica adeguata. "
            f"Reteidratarsi bevendo almeno **{litri_acqua} litri** di acqua con aggiunta di elettroliti (sodio/magnesio) persi durante lo sforzo."
        )

        clean_id_n = ''.join(c for c in id_sel_nutri if c.isdigit())
        target_url_n = f"https://intervals.icu/api/v1/activity/{clean_id_n}/streams"
        
        with st.spinner("Caricamento mappa e tracciato GPS in corso..."):
            resp_str_n = requests.get(target_url_n, auth=("API_KEY", API_KEY.strip()))
            if resp_str_n.status_code == 404 and id_sel_nutri != clean_id_n:
                target_url_n = f"https://intervals.icu/api/v1/activity/{id_sel_nutri}/streams"
                resp_str_n = requests.get(target_url_n, auth=("API_KEY", API_KEY.strip()))

            if resp_str_n.status_code == 200:
                stream_data_n = resp_str_n.json()
                lats_n, lons_n = [], []
                
                if isinstance(stream_data_n, list):
                    for stream in stream_data_n:
                        if isinstance(stream, dict):
                            stype = stream.get("type")
                            if stype in ["latlng", "lating"]:
                                lat_data = stream.get("data", [])
                                lon_data = stream.get("data2", [])
                                
                                if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data) and len(lat_data) > 0:
                                    for lat, lon in zip(lat_data, lon_data):
                                        if lat is not None and lon is not None:
                                            lats_n.append(float(lat))
                                            lons_n.append(float(lon))
                                break

                if lats_n and lons_n and len(lats_n) > 0:
                    st.markdown("#### 🗺️ Tracciato GPS dell'Uscita")
                    tipo_mappa_n = st.radio(
                        "Stile Mappa",
                        ["Satellite", "Standard"],
                        horizontal=True,
                        key=f"stile_mappa_nutri_{id_sel_nutri}"
                    )

                    fig_map_n = go.Figure()
                    fig_map_n.add_trace(go.Scattermapbox(
                        lat=lats_n, lon=lons_n, mode='lines',
                        line=dict(width=4, color='dodgerblue'), name='Tracciato'
                    ))
                    fig_map_n.add_trace(go.Scattermapbox(
                        lat=[lats_n[0], lats_n[-1]], lon=[lons_n[0], lons_n[-1]], mode='markers',
                        marker=dict(size=10, color=['green', 'red']), text=['Partenza', 'Arrivo'], name='Marker'
                    ))
                    
                    if tipo_mappa_n == "Satellite":
                        mapbox_config_n = dict(
                            style="white-bg",
                            layers=[
                                {
                                    "below": 'traces',
                                    "sourcetype": "raster",
                                    "source": [
                                        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                    ]
                                },
                                {
                                    "below": 'traces',
                                    "sourcetype": "raster",
                                    "source": [
                                        "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                                    ]
                                }
                            ],
                            center=dict(lat=sum(lats_n)/len(lats_n), lon=sum(lons_n)/len(lons_n)),
                            zoom=11
                        )
                    else:
                        mapbox_config_n = dict(
                            style="open-street-map",
                            center=dict(lat=sum(lats_n)/len(lats_n), lon=sum(lons_n)/len(lons_n)),
                            zoom=11
                        )

                    fig_map_n.update_layout(
                        mapbox=mapbox_config_n,
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=450,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_map_n, use_container_width=True, key=f"plotly_nutri_{id_sel_nutri}", config={'scrollZoom': True, 'displaylogo': False})

                    linee_gpx_n = [
                        '<?xml version="1.0" encoding="UTF-8"?>',
                        '<gpx version="1.1" creator="Streamlit App" xmlns="http://www.topografix.com/GPX/1/1">',
                        '  <trk>',
                        f'    <name>{titolo_att}</name>',
                        '    <trkseg>'
                    ]
                    for lat, lon in zip(lats_n, lons_n):
                        linee_gpx_n.append(f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>')
                    linee_gpx_n.extend([
                        '    </trkseg>',
                        '  </trk>',
                        '</gpx>'
                    ])
                    contenuto_gpx_nutri = "\n".join(linee_gpx_n)
                    nome_file_nutri = "".join(c for c in titolo_att if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                    if not nome_file_nutri:
                        nome_file_nutri = "tracciato_nutrizione"

                    b64_nutri = base64.b64encode(contenuto_gpx_nutri.encode()).decode()
                    href_nutri = f'<a href="data:application/gpx+xml;base64,{b64_nutri}" download="{nome_file_nutri}.gpx" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 600; margin-top: 0.5rem; margin-bottom: 0.5rem;">📥 Scarica Tracciato GPX</div></a>'
                    st.markdown(href_nutri, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Nessuna coordinata GPS valida disponibile per questa specifica uscita su Intervals.icu.")
            else:
                st.error("Errore nel recupero flussi GPS da Intervals.icu.")
    else:
        st.warning("Nessuna attività disponibile per il calcolo nutrizionale.")
