import streamlit as st
import requests
from supabase import create_client, Client

# --- 1. Configurazione pagina ---
st.set_page_config(page_title="Visualizza Percorso Attività", layout="wide")

# --- 2. Configurazione Supabase ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Supabase nei secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Logica della Pagina ---
st.title("🗺️ Dettaglio Percorso Attività")

map_url = st.session_state.get("map_url_to_view")
if not map_url:
    map_url = st.query_params.get("map_url")

if map_url:
    try:
        response = supabase.table("uscite").select("*").eq("mappa", map_url).execute()
        if response.data:
            act = response.data[0]
            st.subheader(f"{act.get('titolo', 'Attività')} - {act.get('data', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distanza", f"{act.get('distanza', 0)} km")
            with col2:
                st.metric("Tempo", str(act.get('tempo', 'N/D')))
            with col3:
                st.metric("Dislivello", f"{act.get('dislivello', 0)} m")
                
            st.markdown("---")
            
            # Alternativa pulita: invece di forzare coordinate errate, 
            # offriamo l'accesso diretto alla visualizzazione reale e perfetta della mappa
            st.info("💡 Per visualizzare il tracciato geografico dettagliato senza alterazioni geometriche, puoi aprire la mappa interattiva originale.")
            
            # Pulsante per aprire la mappa sorgente o la piattaforma di origine
            st.markdown(
                f'<a href="{map_url}" target="_blank"><button style="background-color:#FF4B4B; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">🌍 Apri Mappa Interattiva Originale</button></a>',
                unsafe_allow_html=True
            )
        else:
            st.warning("Nessuna informazione trovata per questa attività.")
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {e}")
else:
    st.warning("⚠️ Nessun URL specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
