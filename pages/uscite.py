import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime
import pandas as pd
import base64

# --- Configurazione ---
st.title("🚴 Gestione Uscite da Intervals.icu")

# 1. Recupero delle credenziali dai secrets di Streamlit
try:
    API_KEY = st.secrets["intervals"]["api_key"]
    ATHLETE_ID = st.secrets["intervals"]["athlete_id"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Intervals nei secrets (sezione [intervals]).")
    st.stop()

# --- Funzioni di Supporto ---

# Formattare i secondi in formato leggibile (HH:MM:SS)
def timedelta_to_str(seconds):
    if not seconds:
        return "00:00:00"
    ore = int(seconds // 3600)
    minuti = int((seconds % 3600) // 60)
    secondi = int(seconds % 60)
    return f"{ore:02d}:{minuti:02d}:{secondi:02d}"

# Funzione di supporto sicura per convertire in intero evitando errori con None o decimali
def safe_int(val):
    try:
        # Se il valore è None o vuoto, restituisce None
        if val is None or val == "":
            return None
        # Prova a convertire in float (per gestire "593.0") e poi in int
        return int(float(val))
    except (ValueError, TypeError):
        return None

# Funzione per scaricare le attività da Intervals.icu
@st.cache_data(ttl=1)
def fetch_intervals_activities(athlete_id, api_key):
    oggi = datetime.today().strftime('%Y-%m-%d')
    data_inizio = "2025-11-15"  # Fissata come richiesto
    
    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/activities"
    params = {
        "oldest": data_inizio,
        "newest": oggi,
        "iw": True  # Include i dettagli di potenza per certezza
    }
    
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

# --- Logica Principale ---

# Caricamento dati
with st.spinner("Scaricamento delle attività da Intervals.icu in corso..."):
    activities = fetch_intervals_activities(ATHLETE_ID, API_KEY)

if activities:
    st.success(f"Trovate {len(activities)} attività recenti!")
    
    # Elaboriamo i dati per mostrarli in un DataFrame pulito
    parsed_data = []
    
    for act in activities:
        # Ricerca estesa per coprire tutte le varianti di chiavi di Intervals.icu
        avg_watts = act.get("average_watts") or act.get("icu_weighted_avg_watts")
        norm_watts = act.get("normalized_watts") or act.get("icu_normalized_watts") or act.get("weighted_average_watts")
        form_val = act.get("form") or act.get("icu_form") or act.get("ctl_ats") or act.get("tsb")
        
        parsed_data.append({
            "activity_id": str(act.get("id")),
            "data": act.get("start_date_local", "").split("T")[0],
            "titolo": act.get("name", "Uscita senza titolo"),
            "distanza": round(act.get("distance", 0) / 1000, 2),
            "tempo": str(timedelta_to_str(act.get("moving_time", 0))),
            "potenza_media": safe_int(avg_watts),
            "potenza_normalizzata": safe_int(norm_watts),
            "fc_media": safe_int(act.get("average_heartrate")),
            "tss": safe_int(act.get("icu_training_load")),
            "dislivello": safe_int(act.get("total_elevation_gain")),
            "forma": safe_int(form_val)
        })
        
    df_activities = pd.DataFrame(parsed_data)
    
    # Mostriamo la tabella interattiva
    st.dataframe(df_activities, use_container_width=True)
    
    # Pulsante per salvare le attività su Supabase
    if st.button("💾 Salva le uscite su Supabase", key="btn_salva_uscite_supabase", use_container_width=True):
        from supabase import create_client, Client
        
        # Connessione a Supabase
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        supabase: Client = create_client(supabase_url, supabase_key)
        
        success_count = 0
        with st.spinner("Salvataggio in corso su Supabase..."):
            for row in parsed_data:
                try:
                    # L'upsert richiede che activity_id sia UNIQUE su Supabase
                    supabase.table("uscite").upsert(row, on_conflict="activity_id").execute()
                    success_count += 1
                except Exception as ex:
                    # Mostra l'errore specifico per riga, se ce n'è uno
                    st.warning(f"Errore nel salvataggio dell'attività {row['activity_id']}: {ex}")
                    
        if success_count == len(parsed_data):
            st.success(f"Tutte le {success_count} attività sono state salvate/aggiornate con successo su Supabase!")
        else:
            st.warning(f"Salvata/aggiornata con successo solo {success_count} su {len(parsed_data)} attività. Controlla gli errori sopra.")

else:
    st.info("Nessuna attività trovata nel periodo selezionato o errore di connessione.")
