import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime
import pandas as pd
import os
import gpxpy
import gpxpy.gpx
from supabase import create_client, Client

is_proprietario = (st.session_state.get("ruolo_corrente") == "Proprietario")

if not is_proprietario:
    st.error("🚨 Accesso Negato: questa sezione è riservata esclusivamente al proprietario.")
    st.info("Torna alla pagina principale del Diario Alimentare ed effettua il login con le credenziali da amministratore.")
    st.stop()

st.title("🚴 Gestione Uscite da Intervals.icu")

try:
    API_KEY = st.secrets["intervals"]["api_key"]
    ATHLETE_ID = st.secrets["intervals"]["athlete_id"]
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Intervals e Supabase nei secrets.")
    st.stop()

supabase: Client = create_client(supabase_url, supabase_key)
BUCKET_NAME = "mappe-uscite"

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

def fetch_activity_gpx(activity_id, api_key):
    url = f"https://intervals.icu/api/v1/activity/{activity_id}/streams"
    auth = ("API_KEY", api_key.strip())
    try:
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception:
        return None

def upload_gpx_to_supabase(activity_id, gpx_bytes):
    if not gpx_bytes:
        return None
    file_path = f"map_{activity_id}.json"
    try:
        response = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=gpx_bytes,
            file_options={"content-type": "application/json", "upsert": "true"}
        )
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        return public_url
    except Exception:
        try:
            return supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        except Exception:
            return None        

@st.cache_data(ttl=1)
def fetch_intervals_activities(athlete_id, api_key):
    oggi = datetime.today().strftime('%Y-%m-%d')
    data_inizio = "2025-11-15"
    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/activities"
    params = {"oldest": data_inizio, "newest": oggi, "iw": True}
    auth = ("API_KEY", api_key.strip())
    try:
        response = requests.get(url, auth=auth, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Errore API Intervals: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Errore di connessione a Intervals: {e}")
        return []

with st.spinner("Caricamento delle uscite da Supabase in corso..."):
    response = supabase.table("uscite").select("*").order("data", desc=True).execute()
    activities_db = response.data

if activities_db:
    st.success(f"Caricate {len(activities_db)} attività da Supabase!")
    df_activities = pd.DataFrame(activities_db)
    
    df_activities["data_dt"] = pd.to_datetime(df_activities["data"])
    df_activities["anno"] = df_activities["data_dt"].dt.year
    df_activities["mese"] = df_activities["data_dt"].dt.strftime("%Y-%m")
    
    st.markdown("---")
    st.subheader("📊 Riepilogo e Statistiche Generali")
    
    tot_km = round(df_activities["distanza"].sum(), 2)
    tot_dislivello = int(df_activities["dislivello"].fillna(0).sum())
    
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
    
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.subheader("📅 Totali per Anno")
        df_anno = df_activities.groupby("anno")[["distanza", "dislivello"]].sum().reset_index()
        df_anno.columns = ["Anno", "Km Totali", "Dislivello Totale (m)"]
        df_anno = df_anno.sort_values("Anno", ascending=False)
        st.dataframe(df_anno, use_container_width=True, hide_index=True)
        
    with col_tab2:
        st.subheader("📆 Totali per Mese")
        df_mese = df_activities.groupby("mese")[["distanza", "dislivello"]].sum().reset_index()
        df_mese.columns = ["Mese", "Km Totali", "Dislivello Totale (m)"]
        df_mese = df_mese.sort_values("Mese", ascending=False)
        st.dataframe(df_mese, use_container_width=True, hide_index=True, height=450)
    
    st.markdown("---")
    
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.subheader("📋 Dettaglio Completo Attività e Mappe")
    with col_head2:
        if st.button("🔄 Aggiorna da Intervals", key="btn_aggiorna_intervals", use_container_width=True):
            with st.spinner("Sincronizzazione in corso..."):
                activities_ext = fetch_intervals_activities(ATHLETE_ID, API_KEY)
                if activities_ext:
                    for act in activities_ext:
                        act_id = str(act.get("id"))
                        avg_watts = act.get("average_watts") or act.get("icu_average_watts") or act.get("device_watts")
                        norm_watts = act.get("icu_weighted_avg_watts") or act.get("normalized_watts")
                        ctl = act.get("icu_ctl")
                        atl = act.get("icu_atl")
                        form_val = None
                        if ctl is not None and atl is not None:
                            form_val = int(round(float(ctl) - float(atl)))
                        else:
                            form_val = act.get("form") or act.get("icu_form") or act.get("icu_tsb")
                        gpx_bytes = fetch_activity_gpx(act_id, API_KEY)
                        public_url = upload_gpx_to_supabase(act_id, gpx_bytes) if gpx_bytes else None
                        row_data = {
                            "activity_id": act_id,
                            "data": act.get("start_date_local", "").split("T")[0],
                            "titolo": act.get("name", "Uscita senza titolo"),
                            "distanza": round(act.get("distance", 0) / 1000, 2),
                            "tempo": str(timedelta_to_str(act.get("moving_time", 0))),
                            "potenza_media": safe_int(avg_watts),
                            "potenza_normalizzata": safe_int(norm_watts),
                            "fc_media": safe_int(act.get("average_heartrate")),
                            "tss": safe_int(act.get("icu_training_load")),
                            "dislivello": safe_int(act.get("total_elevation_gain")),
                            "forma": safe_int(form_val),
                            "mappa": public_url
                        }
                        supabase.table("uscite").upsert(row_data, on_conflict="activity_id").execute()
                    st.success("Sincronizzazione completata! Ricarica la pagina.")
                    st.rerun()

    # --- FILTRI DI RICERCA (TESTO + RANGE DI DATE LIBERO) ---
    c_filtro1, c_filtro2 = st.columns([2, 2])
    
    with c_filtro1:
        ricerca = st.text_input(
            "🔍 Cerca per nome o data specifica",
            placeholder="Es. 'Soglia' o '2026-07-11'..."
        ).lower().strip()
        
    with c_filtro2:
        min_data = df_activities["data_dt"].min().date()
        max_data = df_activities["data_dt"].max().date()
        
        # Senza min_value e max_value rigidi, il calendario permette di navigare qualsiasi anno
        intervallo_date = st.date_input(
            "📅 Filtra per periodo",
            value=(min_data, max_data)
        )

    # Applicazione dei filtri combinati
    df_filtrato = df_activities.copy()

    # Filtro testuale
    if ricerca:
        df_filtrato = df_filtrato[
            df_filtrato["titolo"].str.lower().str.contains(ricerca, na=False) | 
            df_filtrato["data"].str.contains(ricerca, na=False)
        ]

    # Filtro per intervallo date
    if isinstance(intervallo_date, tuple) and len(intervallo_date) == 2:
        data_inizio, data_fine = intervallo_date
        df_filtrato = df_filtrato[
            (df_filtrato["data_dt"].dt.date >= data_inizio) & 
            (df_filtrato["data_dt"].dt.date <= data_fine)
        ]

    # Lista attività con scroll e caratteri ingranditi
    with st.container(height=650):
        if len(df_filtrato) == 0:
            st.info("Nessuna uscita corrisponde ai filtri di ricerca selezionati.")
        else:
            for index, row in df_filtrato.iterrows():
                act_title = row.get("titolo", "Uscita senza titolo")
                act_date = row.get("data", "")
                act_dist = row.get("distanza", 0)
                act_time = row.get("tempo", "00:00:00")
                act_elev = row.get("dislivello", 0)
                map_url = row.get("mappa")
                
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"<h3 style='margin: 0; padding-bottom: 5px;'>{act_title} <span style='font-size: 1.1rem; color: #999;'>({act_date})</span></h3>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 1.2rem; margin: 0;'>Distanza: <b>{act_dist} km</b> &nbsp;|&nbsp; D+: <b>{act_elev} m</b> &nbsp;|&nbsp; Tempo: <b>{act_time}</b></p>", unsafe_allow_html=True)
                    with col_btn:
                        st.write("") 
                        if map_url:
                            if st.button("🔍 Apri Mappa", key=f"map_btn_{row['activity_id']}", use_container_width=True):
                                st.session_state["map_url_to_view"] = map_url
                                st.session_state["activity_title_to_view"] = act_title
                                st.session_state["activity_date_to_view"] = act_date
                                st.switch_page("pages/visualizza_mappa.py")
                        else:
                            st.caption("Mappa non disponibile")

else:
    st.info("Nessuna attività trovata su Supabase. Sincronizza i dati.")
