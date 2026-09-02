import streamlit as st
import requests
from datetime import datetime, date
import pandas as pd
import os
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
        num_uscite_totali = int(len(df_activities))
        
        # Calcolo delle ore totali in sella (da moving_time in secondi)
        tot_secondi_sella = df_activities.get("moving_time", pd.Series([0])).fillna(0).sum()
        ore_totali = int(tot_secondi_sella // 3600)
        minuti_totali = int((tot_secondi_sella % 3600) // 60)
        stringa_ore_sella = f"{ore_totali}h {minuti_totali:02d}m"
        
        st.markdown("---")
        st.subheader("📊 Statistiche Dinamiche e Riepilogo (TCR - Dal 15/11/2025)")
        
        # Portato a 4 colonne per includere anche le Uscite + 1 colonna per l'immagine
        col_m1, col_m2, col_m3, col_m4, col_img = st.columns([1.5, 1.5, 1.5, 1.5, 3])
        
        with col_m1:
            st.metric("Km Totali", f"{tot_km:,.2f} km")
        with col_m2:
            st.metric("D+ Totale", f"{tot_dislivello:,} m")
        with col_m3:
            st.metric("Ore in sella", stringa_ore_sella)
        with col_m4:
            st.metric("Uscite", str(num_uscite_totali))
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
