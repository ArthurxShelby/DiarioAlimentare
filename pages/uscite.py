import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime, date
import pandas as pd
import os

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

# --- FUNZIONE GPX STREAM ---
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
import os
from datetime import datetime, date

FILE_DATA_INIZIO = "ultima_data_inizio.txt"
FILE_DATA_FINE = "ultima_data_fine.txt"

# Funzioni di utilità per leggere/scrivere su file locale
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

# Inizializziamo le date leggendole dal file locale (o usiamo i default se il file non esiste)
# Inizializziamo le date leggendole dal file locale (o usiamo i default se il file non esiste)
if "saved_start" not in st.session_state:
    st.session_state["saved_start"] = carica_data_salvata(FILE_DATA_INIZIO, date(2026, 1, 1))

if "saved_end" not in st.session_state:
    st.session_state["saved_end"] = carica_data_salvata(FILE_DATA_FINE, date.today())

# === INCOLLA QUI IL CSS PER INGRANDIRE IL CALENDARIO ===
st.markdown("""
    <style>
        /* Aumenta la dimensione dei caratteri dei giorni, dei mesi e delle intestazioni nel calendario */
        div[data-baseweb="calendar"] * {
            font-size: 1.15rem !important;
        }
        /* Aumenta la dimensione del testo del selettore anno/mese */
        div[data-baseweb="calendar"] select {
            font-size: 1.1rem !important;
        }
    </style>
""", unsafe_allow_html=True)

with st.expander("🔍 Esplora Archivio Storico da Intervals (Range Personalizzato)", expanded=False):
    st.write("Seleziona un periodo qualsiasi per estrarre dal flusso di Intervals tutte le attività, consultare i metri e aprire le relative mappe in tempo reale.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        data_inizio_custom = st.date_input("Data Inizio Range", value=st.session_state["saved_start"], key="widget_start")
    with col_c2:
        data_fine_custom = st.date_input("Data Fine Range", value=st.session_state["saved_end"], key="widget_end")
        
    if st.button("🚀 Estrai Dati dal Flusso", key="btn_calcola_custom"):
        # Salviamo in memoria e scriviamo fisicamente sul file (sopravvive ai riavvii!)
        st.session_state["saved_start"] = data_inizio_custom
        st.session_state["saved_end"] = data_fine_custom
        salva_data_su_file(FILE_DATA_INIZIO, data_inizio_custom)
        salva_data_su_file(FILE_DATA_FINE, data_fine_custom)
        
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
        
        distanza_tot_km = round(df_ext.get("distance", pd.Series([0])).fillna(0).sum() / 1000.0, 2)
        dislivello_tot_m = int(df_ext.get("total_elevation_gain", pd.Series([0])).fillna(0).sum())
        num_uscite = len(df_ext)
        
        st.markdown("---")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Km Totali Periodo", f"{distanza_tot_km:,.2f} km")
        mc2.metric("Dislivello (D+) Periodo", f"{dislivello_tot_m:,} m")
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
                                if gpx_bytes:
                                    st.session_state["map_bytes_to_view"] = gpx_bytes
                                    st.session_state["activity_title_to_view"] = act_title
                                    st.session_state["activity_date_to_view"] = act_date
                                    st.switch_page("pages/visualizza_mappa.py")
                                else:
                                    st.error("Mappa non disponibile per questa attività.")
