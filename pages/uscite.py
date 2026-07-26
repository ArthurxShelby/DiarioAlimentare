import streamlit as st
st.set_page_config(layout="wide")
import requests
from datetime import datetime
import pandas as pd

# --- Configurazione ---
st.title("🚴 Gestione Uscite da Intervals.icu")

try:
    API_KEY = st.secrets["intervals"]["api_key"]
    ATHLETE_ID = st.secrets["intervals"]["athlete_id"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Intervals nei secrets (sezione [intervals]).")
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
with st.spinner("Scaricamento delle attività da Intervals.icu in corso..."):
    activities = fetch_intervals_activities(ATHLETE_ID, API_KEY)

if activities:
    st.success(f"Trovate {len(activities)} attività recenti!")
    
    parsed_data = []
    
    for act in activities:
        avg_watts = act.get("average_watts") or act.get("icu_average_watts") or act.get("device_watts")
        norm_watts = act.get("icu_weighted_avg_watts") or act.get("normalized_watts")
        
        ctl = act.get("icu_ctl")
        atl = act.get("icu_atl")
        form_val = None
        if ctl is not None and atl is not None:
            form_val = int(round(float(ctl) - float(atl)))
        else:
            form_val = act.get("form") or act.get("icu_form") or act.get("icu_tsb")
        
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
    
    # --- AGGREGAZIONI E STATISTICHE ---
    # Convertiamo la colonna data in formato datetime per estrarre Anno e Mese
    df_activities["data_dt"] = pd.to_datetime(df_activities["data"])
    df_activities["anno"] = df_activities["data_dt"].dt.year
    df_activities["mese"] = df_activities["data_dt"].dt.strftime("%Y-%m") # es. "2025-11"
    
    st.markdown("---")
    st.subheader("📊 Riepilogo e Statistiche Generali")
    
    # 1. Totale Generale
    tot_km = round(df_activities["distanza"].sum(), 2)
    tot_dislivello = int(df_activities["dislivello"].fillna(0).sum())
    
    col1, col2 = st.columns(2)
    col1.metric("Km Totali (Raccolta)", f"{tot_km:,.2f} km")
    col2.metric("Dislivello Totale (Raccolta)", f"{tot_dislivello:,} m")
    
    # 2. Raggruppamento per Anno
    st.markdown("### 📅 Totali per Anno")
    df_anno = df_activities.groupby("anno")[["distanza", "dislivello"]].sum().reset_index()
    df_anno.columns = ["Anno", "Km Totali", "Dislivello Totale (m)"]
    st.dataframe(df_anno, use_container_width=True, hide_index=True)
    
    # 3. Raggruppamento per Mese
    st.markdown("### 📆 Totali per Mese")
    df_mese = df_activities.groupby("mese")[["distanza", "dislivello"]].sum().reset_index()
    df_mese.columns = ["Mese", "Km Totali", "Dislivello Totale (m)"]
    # Ordinati cronologicamente dal più vecchio al più recente (o viceversa invertendo ascending)
    df_mese = df_mese.sort_values("Mese", ascending=False)
    st.dataframe(df_mese, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📋 Dettaglio Completo Attività")
    # Mostriamo la tabella interattiva escludendo le colonne di servizio temporanee
    st.dataframe(df_activities.drop(columns=["data_dt", "anno", "mese"]), use_container_width=True)
    
    # Pulsante per salvare le attività su Supabase
    if st.button("💾 Salva le uscite su Supabase", key="btn_salva_uscite_supabase_aggregata", use_container_width=True):
        from supabase import create_client, Client
        
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        supabase: Client = create_client(supabase_url, supabase_key)
        
        success_count = 0
        with st.spinner("Salvataggio in corso su Supabase..."):
            for row in parsed_data:
                try:
                    supabase.table("uscite").upsert(row, on_conflict="activity_id").execute()
                    success_count += 1
                except Exception as ex:
                    st.warning(f"Errore nel salvataggio dell'attività {row['activity_id']}: {ex}")
                    
        if success_count == len(parsed_data):
            st.success(f"Tutte le {success_count} attività sono state salvate/aggiornate con successo su Supabase!")
        else:
            st.warning(f"Salvata/aggiornata con successo solo {success_count} su {len(parsed_data)} attività.")

else:
    st.info("Nessuna attività trovata nel periodo selezionato o errore di connessione.")
