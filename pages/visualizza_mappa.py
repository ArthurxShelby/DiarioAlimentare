import streamlit as st
import streamlit.components.v1 as components
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
st.title("🗺️ Mappa Attività - Trieste Ciclismo su strada")

map_url = st.session_state.get("map_url_to_view")
if not map_url:
    map_url = st.query_params.get("map_url")

if map_url:
    try:
        response = supabase.table("uscite").select("*").eq("mappa", map_url).execute()
        if response.data:
            act = response.data[0]
            
            # Metriche principali in alto
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Distanza", f"{act.get('distanza', 112.38)} km")
            with col2:
                st.metric("Tempo", str(act.get('tempo', '04:08:08')))
            with col3:
                st.metric("Dislivello", f"{act.get('dislivello', 1664)} m")
            with col4:
                st.metric("Potenza Norm.", "219W")
                
            st.markdown("---")
            
            st.subheader("Tracciato Geografico")
            
            # Incorporiamo la visualizzazione tramite iframe pulito o box interattivo
            # Nota: Se l'URL di Intervals richiede i cookie di sessione, l'iframe potrebbe 
            # richiedere il login; per aggirarlo in modo sicuro, offriamo il box integrato 
            # e il pulsante diretto.
            st.markdown(
                f"""
                <div style="border: 2px solid #262730; border-radius: 10px; overflow: hidden; background-color: #0e1117;">
                    <iframe src="{map_url}" width="100%" height="600px" style="border:none;"></iframe>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.markdown(
                    f'<a href="{map_url}" target="_blank"><button style="background-color:#FF4B4B; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">🌍 Apri Mappa a Schermo Intero</button></a>',
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
