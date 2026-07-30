
import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime, date
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
import plotly.express as px
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

# Colore blu coerente con il diario alimentare
BLU_DIARIO = "#2b5c8f"

# --- 1. STATISTICHE DINAMICHE GLOBALI & MACRO INDIPENDENTE ---
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
        
        tot_km = round((df_activities.get("distance") if "distance" in df_activities else pd.Series([0])).fillna(0).sum() / 1000.0, 2)
        tot_dislivello = int((df_activities.get("total_elevation_gain") if "total_elevation_gain" in df_activities else pd.Series([0])).fillna(0).sum())
        
        st.markdown("---")
        st.subheader("📊 Statistiche Dinamiche e Riepilogo (TCR - Dal 15/11/2025)")
        
        # Layout principale: Colonna sinistra per le metriche, Colonna destra per la foto della bici
        col_m_sinistra, col_m_destra = st.columns([2, 1])
        
        with col_m_destra:
            st.subheader("TCR Advanced Pro 0")
            try:
                cartella_script = os.path.dirname(__file__)
                percorso_foto = os.path.join(cartella_script, "TCR.png")
                st.image(percorso_foto, use_container_width=True)
            except Exception:
                st.warning("Immagine TCR.png non trovata.")
                
        with col_m_sinistra:
            # Metriche globali cumulative (crescono uscita per uscita)
            col_met1, col_met2 = st.columns(2)
            col_met1.metric("Km Totali (Raccolta)", f"{tot_km:,.2f} km")
            col_met2.metric("D+ Totale (Raccolta)", f"{tot_dislivello:,} m")
            
            st.markdown("---")
            st.markdown("#### 🎯 Statistiche Personalizzate (Range Dedicato)")
            
            # Sub-container o selettori dedicati esclusivamente alla nuova macro
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                sub_start = st.date_input("Data Inizio Range", value=date(date.today().year, 1, 1), key="macro_start_date")
            with col_d2:
                sub_end = st.date_input("Data Fine Range", value=date.today(), key="macro_end_date")
                
            # Chiamata API autonoma per la macro con il suo range esclusivo
            try:
                url_macro = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
                params_macro = {
                    "oldest": sub_start.strftime("%Y-%m-%d"),
                    "newest": sub_end.strftime("%Y-%m-%d"),
                    "iw": True
                }
                resp_macro = requests.get(url_macro, auth=("API_KEY", API_KEY.strip()), params=params_macro)
                
                if resp_macro.status_code == 200:
                    dati_macro = resp_macro.json()
                    if dati_macro:
                        df_macro = pd.DataFrame(dati_macro)
                        km_macro = round((df_macro.get("distance") if "distance" in df_macro else pd.Series([0])).fillna(0).sum() / 1000.0, 2)
                        d_macro = int((df_macro.get("total_elevation_gain") if "total_elevation_gain" in df_macro else pd.Series([0])).fillna(0).sum())
                        sec_macro = (df_macro.get("moving_time") if "moving_time" in df_macro else pd.Series([0])).fillna(0).sum()
                        ore_macro = round(sec_macro / 3600.0, 1)
                        
                        m_c1, m_c2, m_c3 = st.columns(3)
                        m_c1.metric("Km Totali", f"{km_macro:,.2f} km")
                        m_c2.metric("D+ Totale", f"{d_macro:,} m")
                        m_c3.metric("Ore in Sella", f"{ore_macro} h")
                        
                        # --- SEZIONE DIAGRAMMA E SELETTORI ---
                        st.markdown("---")
                        c_diag_titolo, c_metrica_scelta, c_aggruppa_scelta = st.columns([1.5, 2.2, 2.2])
                        with c_diag_titolo:
                            st.markdown("##### 📈 Analisi Grafica")
                        with c_metrica_scelta:
                            tipo_metrica = st.selectbox(
                                "Metrica Grafico",
                                ["Chilometri (km)", "Dislivello (D+ m)"],
                                key="selettore_metrica_grafico",
                                label_visibility="collapsed"
                            )
                        with c_aggruppa_scelta:
                            tipo_aggruppamento = st.selectbox(
                                "Raggruppa per",
                                ["Mesi", "Settimane"],
                                key="selettore_raggruppamento",
                                label_visibility="collapsed"
                            )
                        
                        # Layout espanso a larghezza piena: [1, 1] per distribuire equamente lo spazio della pagina
                        col_grafico_principale, col_elenco_lato = st.columns([1, 1])
                        
                        if "start_date_local" in df_macro.columns:
                            df_macro["data_dt"] = pd.to_datetime(df_macro["start_date_local"].apply(lambda x: x.split("T")[0]))
                            df_macro["distanza_km"] = (df_macro.get("distance", pd.Series([0])).fillna(0)) / 1000.0
                            df_macro["dislivello_m"] = df_macro.get("total_elevation_gain", pd.Series([0])).fillna(0)
                            
                            if tipo_aggruppamento == "Mesi":
                                df_macro["periodo"] = df_macro["data_dt"].dt.strftime("%Y-%m")
                            else:
                                df_macro["periodo"] = df_macro["data_dt"].dt.strftime("%Y-W%V")
                                
                            if "Chilometri" in tipo_metrica:
                                df_agg = df_macro.groupby("periodo")["distanza_km"].sum().reset_index()
                                y_col = "distanza_km"
                                y_label = "km"
                                text_format = ".1f"
                            else:
                                df_agg = df_macro.groupby("periodo")["dislivello_m"].sum().reset_index()
                                y_col = "dislivello_m"
                                y_label = "m"
                                text_format = ",d"
                            
                            fig_bar = px.bar(
                                df_agg,
                                x="periodo",
                                y=y_col,
                                text_auto=text_format,
                                labels={"periodo": "Periodo", y_col: y_label}
                            )
                            fig_bar.update_traces(marker_color=BLU_DIARIO, textfont_size=12, textangle=0, textposition="outside")
                            fig_bar.update_layout(
                                margin=dict(l=10, r=10, t=10, b=10),
                                height=520,
                                xaxis_title="",
                                yaxis_title=y_label,
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                clickmode="event+select"
                            )
                            
                            with col_grafico_principale:
                                evento_clicca = st.plotly_chart(
                                    fig_bar, 
                                    use_container_width=True, 
                                    on_select="rerun", 
                                    selection_mode="points",
                                    key="grafico_macro_attivita", 
                                    config={'displaylogo': False}
                                )
                                
                            # Gestione interattività al click sulla barra del diagramma
                            periodo_selezionato = None
                            if evento_clicca and "selection" in evento_clicca and "points" in evento_clicca["selection"]:
                                punti = evento_clicca["selection"]["points"]
                                if punti:
                                    punto = punti[0]
                                    x_val = punto.get("x")
                                    if x_val:
                                        try:
                                            dt_parsed = pd.to_datetime(x_val, format="%b %Y")
                                            if tipo_aggruppamento == "Mesi":
                                                periodo_selezionato = dt_parsed.strftime("%Y-%m")
                                            else:
                                                periodo_selezionato = dt_parsed.strftime("%Y-W%V")
                                        except Exception:
                                            try:
                                                dt_parsed = pd.to_datetime(x_val)
                                                if tipo_aggruppamento == "Mesi":
                                                    periodo_selezionato = dt_parsed.strftime("%Y-%m")
                                                else:
                                                    periodo_selezionato = dt_parsed.strftime("%Y-W%V")
                                            except Exception:
                                                periodo_selezionato = str(x_val)
                                                
                                    st.session_state["ultimo_periodo_cliccato"] = periodo_selezionato
                            
                            if "ultimo_periodo_cliccato" in st.session_state and not periodo_selezionato:
                                periodo_selezionato = st.session_state["ultimo_periodo_cliccato"]

                            with col_elenco_lato:
                                st.markdown("##### 📌 Uscite del Periodo")
                                if periodo_selezionato:
                                    st.caption(f"Filtro attivo: **{periodo_selezionato}**")
                                    
                                    df_uscite_periodo = df_macro[df_macro["periodo"] == periodo_selezionato]
                                    
                                    if not df_uscite_periodo.empty:
                                        with st.container(height=520):
                                            for idx, row in df_uscite_periodo.iterrows():
                                                act_id = str(row.get("id"))
                                                act_title = row.get("name", "Uscita senza titolo")
                                                act_date = row.get("start_date_local", "").split("T")[0]
                                                km_uscita = round((row.get("distance") or 0) / 1000.0, 1)
                                                d_uscita = safe_int(row.get("total_elevation_gain")) or 0
                                                act_time = timedelta_to_str(row.get("moving_time", 0))
                                                
                                                key_toggle_macro = f"show_map_macro_{act_id}_{idx}"
                                                if key_toggle_macro not in st.session_state:
                                                    st.session_state[key_toggle_macro] = False
                                                
                                                with st.container(border=True):
                                                    st.markdown(f"**{act_title}** ({act_date})")
                                                    st.markdown(f"📏 {km_uscita} km &nbsp;|&nbsp; ⛰️ {d_uscita} m &nbsp;|&nbsp; ⏱️ {act_time}")
                                                    
                                                    c_b1, c_b2 = st.columns(2)
                                                    with c_b1:
                                                        lbl_map = "🗺️ Nascondi Mappa" if st.session_state[key_toggle_macro] else "🗺️ Anteprima Mappa"
                                                        if st.button(lbl_map, key=f"btn_macro_map_{act_id}_{idx}", use_container_width=True):
                                                            st.session_state[key_toggle_macro] = not st.session_state[key_toggle_macro]
                                                            st.rerun()
                                                    with c_b2:
                                                        if st.button("🔍 Pagina Dedicata", key=f"btn_macro_page_{act_id}_{idx}", use_container_width=True):
                                                            st.session_state["selected_activity_id"] = act_id
                                                            st.session_state["selected_activity_title"] = act_title
                                                            st.session_state["selected_activity_date"] = act_date
                                                            st.switch_page("pages/visualizza_mappa.py")
                                                            
                                                    if st.session_state[key_toggle_macro]:
                                                        st.markdown("---")
                                                        clean_id = ''.join(c for c in act_id if c.isdigit())
                                                        target_url = f"https://intervals.icu/api/v1/activity/{clean_id}/streams"
                                                        auth_streams = ("API_KEY", API_KEY.strip())
                                                        
                                                        with st.spinner("Caricamento tracciato..."):
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
                                                                            if isinstance(stream, dict) and stream.get("type") in ["latlng", "lating"]:
                                                                                lat_data = stream.get("data", [])
                                                                                lon_data = stream.get("data2", [])
                                                                                if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data):
                                                                                    for lat, lon in zip(lat_data, lon_data):
                                                                                        if lat is not None and lon is not None:
                                                                                            lats.append(float(lat))
                                                                                            lons.append(float(lon))
                                                                    
                                                                    if lats and lons:
                                                                        fig_m = go.Figure()
                                                                        fig_m.add_trace(go.Scattermapbox(
                                                                            lat=lats, lon=lons, mode='lines',
                                                                            line=dict(width=4, color='dodgerblue'), name='Tracciato'
                                                                        ))
                                                                        fig_m.update_layout(
                                                                            mapbox=dict(
                                                                                style="open-street-map",
                                                                                center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)),
                                                                                zoom=11
                                                                            ),
                                                                            margin=dict(l=0, r=0, t=0, b=0),
                                                                            height=300,
                                                                            showlegend=False
                                                                        )
                                                                        st.plotly_chart(fig_m, use_container_width=True, key=f"map_plot_macro_{act_id}_{idx}", config={'displaylogo': False})
                                                                    else:
                                                                        st.warning("Coordinate GPS non disponibili per questa uscita.")
                                                                else:
                                                                    st.error("Errore nel recupero dei flussi GPS.")
                                                            except Exception as ex:
                                                                st.error(f"Errore caricamento mappa: {ex}")
                                    else:
                                        with st.container(height=520):
                                            st.info("Nessuna uscita trovata per questo periodo.")
                                else:
                                    with st.container(height=520):
                                        st.info("👆 Clicca su una barra del diagramma per visualizzare qui le relative uscite in dettaglio.")
                        # ----------------------------------------------------------------------
                        
                    else:
                        st.info("Nessuna attività trovata in questo range personalizzato.")
                else:
                    st.warning("Impossibile recuperare i dati dedicati da Intervals.")
            except Exception as e:
                st.error(f"Errore nel calcolo della macro: {e}")
                
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
            distanza_tot_km = round((df_filtrato_vista.get("distance") if "distance" in df_filtrato_vista else pd.Series([0])).fillna(0).sum() / 1000.0, 2)
            dislivello_tot_m = int((df_filtrato_vista.get("total_elevation_gain") if "total_elevation_gain" in df_filtrato_vista else pd.Series([0])).fillna(0).sum())
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
                    act_dist = round((act.get("distance") or 0) / 1000, 2)
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
