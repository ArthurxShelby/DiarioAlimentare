import streamlit as st
import pandas as pd
import requests
from supabase import create_client, Client

# --- 1. Configurazione Pagina ---
st.set_page_config(page_title="Visualizza Attività", layout="wide")

# --- 2. Connessione a Supabase ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Supabase nei secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. Logica Principale ---
st.title("🗺️ Dettaglio Uscita in Bicicletta")

# Recuperiamo l'URL della mappa dalla sessione o dai parametri della query
map_url = st.session_state.get("map_url_to_view")
if not map_url:
    map_url = st.query_params.get("map_url")

if map_url:
    try:
        # Cerchiamo i dati dell'uscita associata su Supabase
        response = supabase.table("uscite").select("*").eq("mappa", map_url).execute()
        
        if response.data:
            act = response.data[0]
            
            # Mostriamo le metriche principali dell'attività in alto
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distanza", f"{act.get('distanza', 'N/D')} km")
            with col2:
                st.metric("Tempo", str(act.get('tempo', 'N/D')))
            with col3:
                st.metric("Dislivello", f"{act.get('dislivello', 'N/D')} m")
                
            st.markdown("---")
            
            # Pulsante pulito per consultare direttamente la sorgente originale su Intervals.icu
            st.markdown("### Accesso Rapido alla Piattaforma")
            st.markdown(
                f'<a href="{map_url}" target="_blank"><button style="background-color:#FF4B4B; color:white; border:none; padding:12px 24px; border-radius:6px; cursor:pointer; font-weight:bold; font-size:16px;">🌍 Apri Attività Completa su Intervals.icu</button></a>',
                unsafe_allow_html=True
            )
        else:
            st.warning("Nessuna attività trovata nel database corrispondente a questo link.")
            
    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
