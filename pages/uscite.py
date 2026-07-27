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
    oggi = datetime.today().strftime('%Y-%m-%d')
    data_inizio = "2025-11-15"
    
    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/activities"
    params = {
        "oldest": data_inizio,
        "newest": oggi,
        "iw": True
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
with st.spinner("Caricamento delle uscite da Supabase in corso..."):
    response = supabase.table("uscite").select("*").order("data", desc=True).execute()
    activities_db = response.data

if activities_db:
    df_activities = pd.DataFrame(activities_db)
    st.success(f"Caricate {len(df_activities)} attività da Supabase!")
    
    parsed_data = []
    
    for act in activities:
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
            
        map_url = None
        
        parsed_data.append({
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
            "mappa": map_url
        })
        
    df_activities = pd.DataFrame(parsed_data)
    
    # --- AGGREGAZIONI E STATISTICHE ---
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
    st.subheader("📋 Dettaglio Completo Attività")
    df_activities = df_activities.sort_values("data", ascending=False)
    st.dataframe(df_activities.drop(columns=["data_dt", "anno", "mese"]), use_container_width=True)
    
    # Pulsante per salvare le attività e le mappe su Supabase
    if st.button("💾 Salva le uscite e le mappe su Supabase", key="btn_salva_uscite_supabase_aggregata", use_container_width=True):
        success_count = 0
        with st.spinner("Salvataggio attività e caricamento mappe su Supabase in corso..."):
            for row in parsed_data:
                try:
                    act_id = row["activity_id"]
                    # 1. Recupera le coordinate da Intervals e carica il file nel bucket 'mappe-uscite'
                    map_stream = fetch_activity_map(act_id, API_KEY)
                    if map_stream:
                        public_url = upload_map_to_supabase(act_id, map_stream)
                        row["mappa"] = public_url
                    
                    # 2. Upsert sulla tabella uscite inclusa la colonna 'mappa'
                    supabase.table("uscite").upsert(row, on_conflict="activity_id").execute()
                    success_count += 1
                except Exception as ex:
                    st.warning(f"Errore nel salvataggio dell'attività {row['activity_id']}: {ex}")
                    
        if success_count == len(parsed_data):
            st.success(f"Tutte le {success_count} attività e relative mappe sono state salvate/aggiornate con successo su Supabase!")
        else:
            st.warning(f"Salvata/aggiornata con successo solo {success_count} su {len(parsed_data)} attività.")

else:
    st.info("Nessuna attività trovata nel periodo selezionato o errore di connessione.")
