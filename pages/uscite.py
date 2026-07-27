import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime
import pandas as pd
import os
from supabase import create_client, Client

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

# --- FUNZIONI DI SUPPORTO CON DEBUG AGGIORNATE ---
def fetch_activity_map(activity_id, api_key):
    """
    Recupera i dati della mappa/tracciato da Intervals.icu per l'attività specifica con debug.
    """
    url = f"https://intervals.icu/api/v1/activity/{activity_id}/streams"
    auth = ("API_KEY", api_key.strip())
    try:
        response = requests.get(url, auth=auth)
        if response.status_code == 200:
            streams = response.json()
            if isinstance(streams, list):
                lat = next((s.get("data") for s in streams if s.get("type") == "latlng"), None)
                return lat
            else:
                st.warning(f"Formato inatteso per i stream dell'attività {activity_id}")
        else:
            st.warning(f"Intervals API Stream error {response.status_code} per ID {activity_id}: {response.text}")
    except Exception as e:
        st.warning(f"Eccezione stream per ID {activity_id}: {e}")
    return None

def upload_map_to_supabase(activity_id, map_data):
    """
    Gestisce l'upload dei dati della mappa su Supabase Storage con gestione errori dettagliata.
    """
    if not map_data:
        return None
    
    file_path = f"map_{activity_id}.json"
    file_bytes = str(map_data).encode("utf-8")
    
    try:
        response = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": "application/json", "upsert": "true"}
        )
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        return public_url
    except Exception as e:
        st.error(f"Errore upload Supabase per {activity_id}: {e}")
        try:
            return supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        except Exception as ex:
            st.error(f"Impossibile recuperare URL pubblico per {activity_id}: {ex}")
            return None

@st.cache_data(ttl=1)
def fetch_intervals_activities(athlete_id, api_key):
    ...
