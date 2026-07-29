import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime, date
import pandas as pd
import os
import gpxpy
import gpxpy.gpx
from supabase import create_client, Client
from requests.auth import HTTPBasicAuth

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
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Intervals e Supabase nei secrets.")
    st.stop()

# Inizializzazione client Supabase
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

# --- FUNZIONE GPX SICURA ---
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


# --- 1. CARICAMENTO DATI UFFICIALI TCR DA SUPABASE ---
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
    st.subheader("📊 Statistiche Dinamiche e Riepilogo (TCR - Dal 15/11/2025)")
    
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
            st.warning("Immagine TCR.png not found.")
    
    st.markdown("---")
    
    # --- 2. ESPLORATORE STORICO ON-DEMAND DA INTERVALS (Senza scrittura su Supabase) ---
    with st.expander("🔍 Esplora Archivio Storico da Intervals (Range Personalizzato)", expanded=False):
        st.write("Seleziona un periodo qualsiasi per estrarre dal flusso di Intervals tutte le attività, consultare i metri e aprire le relative mappe **senza popolare le tabelle di Supabase**.")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            data_inizio_custom = st.date_input("Data Inizio Range", value=date(2025, 7, 27), key="custom_start")
        with col_c2:
            data_fine_custom = st.date_input("Data Fine Range", value=date(2025, 8, 14), key="custom_end")
            
        if st.button("🚀 Estrai Dati dal Flusso", key="btn_calcola_custom"):
            with st.spinner("Interrogazione in corso..."):
                url_custom = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
                params_custom = {
                    "oldest": data_inizio_custom.strftime("%Y-%m-%d"),
                    "newest": data_fine_custom.strftime("%Y-%m-%d"),
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

        # Se abbiamo dati custom in memoria, mostriamo metriche e box interattivi con mappa
        if "custom_activities" in st.session_state and st.session_state["custom_activities"]:
            df_ext = pd.DataFrame(st.session_state["custom_activities"])
            
            distanza_tot_km = df_ext.get("distance", pd.Series([0])).fillna(0).sum() / 1000.0
            dislivello_tot_m = df_ext.get("total_elevation_gain", pd.Series([0])).fillna(0).sum()
            num_uscite = len(df_ext)
            
            st.markdown("---")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Km Totali Periodo", f"{distanza_tot_km:.1f} km")
            mc2.metric("Dislivello (D+) Periodo", f"{dislivello_tot_m:.0f} m")
            mc3.metric("Uscite Registrate", f"{num_uscite}")
            st.markdown("---")
            
            with st.container(height=550):
                for act in st.session_state["custom_activities"]:
                    act_id = str(act.get("id"))
                    act_title = act.get("name", "Uscita senza titolo")
                    act_date = act.get("start_date_local", "").split("T")[0]
                    act_dist = round(act.get("distance", 0) / 1000, 2)
                    act_time = timedelta_to_str(act.get("moving_time", 0))
                    act_elev = safe_int(act.get("total_elevation_gain")) or 0
                    
                    with st.container(border=True):
                        col_info, col_btn = st.columns([4, 1])
                        with col_info:
                            st.markdown(f"<h3 style='margin: 0; padding-bottom: 5px;'>{act_title} <span style='font-size: 1.1rem; color: #999;'>({act_date})</span></h3>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-size: 1.2rem; margin: 0;'>Distanza: <b>{act_dist} km</b> &nbsp;|&nbsp; D+: <b>{act_elev} m</b> &nbsp;|&nbsp; Tempo: <b>{act_time}</b></p>", unsafe_allow_html=True)
                        with col_btn:
                            st.write("") 
                            if st.button("🔍 Apri Mappa", key=f"map_custom_{act_id}", use_container_width=True):
                                with st.spinner("Caricamento mappa in corso..."):
                                    gpx_bytes = fetch_activity_gpx(act_id, API_KEY)
                                    public_url = upload_gpx_to_supabase(act_id, gpx_bytes) if gpx_bytes else None
                                    if public_url:
                                        st.session_state["map_url_to_view"] = public_url
                                        st.session_state["activity_title_to_view"] = act_title
                                        st.session_state["activity_date_to_view"] = act_date
                                        st.switch_page("pages/visualizza_mappa.py")
                                    else:
                                        st.error("Mappa non disponibile per questa attività.")

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

else:
    st.info("Nessuna attività trovata su Supabase.")
