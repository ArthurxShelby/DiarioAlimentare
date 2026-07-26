import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime, timedelta
import pandas as pd
import base64

st.title("🚴 Gestione Uscite da Intervals.icu")

# 1. Recupero delle credenziali dai secrets di Streamlit
try:
    API_KEY = st.secrets["intervals"]["api_key"]
    ATHLETE_ID = st.secrets["intervals"]["athlete_id"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Intervals nei secrets (sezione [intervals]).")
    st.stop()


# 2. Funzione per scaricare le attività da Intervals.icu

def timedelta_to_str(seconds):
    if not seconds:
        return "00:00:00"
    ore = int(seconds // 3600)
    minuti = int((seconds % 3600) // 60)
    secondi = int(seconds % 60)
    return f"{ore:02d}:{minuti:02d}:{secondi:02d}"

@st.cache_data(ttl=1)
def fetch_intervals_activities(athlete_id, api_key):
    oggi = datetime.today().strftime('%Y-%m-%d')
    data_inizio = "2025-11-15"  # <-- Fissata al 15 novembre 2025 compreso
    
    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/activities"
    params = {
        "oldest": data_inizio,
        "newest": oggi
    }
    
    auth = ("API_KEY", api_key.strip())
    
    response = requests.get(url, auth=auth, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Errore nella chiamata API a Intervals: {response.status_code} - {response.text}")
        return []
        
# Caricamento dati
with st.spinner("Scaricamento delle attività da Intervals.icu in corso..."):
    activities = fetch_intervals_activities(ATHLETE_ID, API_KEY)

if activities:
    st.success(f"Trovate {len(activities)} attività recenti!")
    
    # Elaboriamo i dati per mostrarli in un DataFrame pulito
    parsed_data = []
    for act in activities:
        # Estraiamo i campi principali (gestendo eventuali campi mancanti con .get)
        parsed_data.append({
            "activity_id": str(act.get("id")),
            "data": act.get("start_date_local", "").split("T")[0],
            "titolo": act.get("name", "Uscita senza titolo"),
            "distanza": round(act.get("distance", 0) / 1000, 2), # Convertito in km
            "tempo": str(timedelta_to_str(act.get("moving_time", 0))),
            "potenza_media": act.get("icu_weighted_avg_power") or act.get("average_watts"),
            "potenza_normalizzata": act.get("normalized_watts"),
            "fc_media": act.get("average_heartrate"),
            "tss": act.get("icu_training_load"),
            "dislivello": act.get("total_elevation_gain"),
            "forma": act.get("form") # se presente
        })
    
    df_activities = pd.DataFrame(parsed_data)
    
    # Mostriamo la tabella interattiva
    st.dataframe(df_activities, use_container_width=True)
    
    # Pulsante per salvare le attività su Supabase
    if st.button("💾 Salva le uscite su Supabase", use_container_width=True):
        from supabase import create_client, Client
        
        # Connessione a Supabase usando i secrets esistenti
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        supabase: Client = create_client(supabase_url, supabase_key)
        
        success_count = 0
        for row in parsed_data:
            # Eseguiamo un inserimento (o upsert basato su activity_id se vuoi evitare duplicati)
            try:
                response = supabase.table("uscite").upsert(row, on_conflict="activity_id").execute()
                success_count += 1
            except Exception as ex:
                st.warning(f"Errore nel salvataggio dell'attività {row['activity_id']}: {ex}")
                
        st.success(f"Processo completato! Salvate/aggiornate {success_count} attività su Supabase.")

else:
    st.info("Nessuna attività trovata o errore di connessione.")

# Funzione di supporto per formattare i secondi in formato leggibile (HH:MM:SS)
def timedelta_to_str(seconds):
    if not seconds:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
