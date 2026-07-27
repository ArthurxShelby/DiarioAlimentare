import streamlit as st
import pandas as pd
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

def get_coordinates_from_json(url):
    """Estrae lo stream latlng in modo sicuro e pulito"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        # Se i dati sono una lista di dizionari (formato stream tipico di Intervals)
        if isinstance(data, list):
            # Cerchiamo se c'è l'oggetto stream latlng
            latlng_data = None
            for item in data:
                if isinstance(item, dict) and item.get('type') == 'latlng':
                    latlng_data = item.get('data')
                    break
            
            # Se non è uno stream strutturato ma una lista diretta di coordinate
            if not latlng_data:
                latlng_data = data
                
            if latlng_data and isinstance(latlng_data, list):
                # Puliamo e formattiamo in DataFrame
                clean_points = []
                for pt in latlng_data:
                    if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                        clean_points.append([float(pt[0]), float(pt[1])])
                
                if clean_points:
                    df = pd.DataFrame(clean_points, columns=['lat', 'lon'])
                    return df.dropna()
                    
        return None
    except Exception as e:
        st.error(f"Errore nel parsing delle coordinate: {e}")
        return None

# --- Logica della Pagina ---
st.title("🗺️ Visualizzazione Percorso Attività")

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
    except:
        pass 

    df_coords = get_coordinates_from_json(map_url)
    
    if df_coords is not None and not df_coords.empty:
        st.success(f"Tracciato caricato correttamente ({len(df_coords)} punti GPS).")
        st.map(df_coords, use_container_width=True)
    else:
        st.warning("⚠️ Il link salvato non restituisce uno stream di coordinate valido. Verifica che l'URL in Supabase punti direttamente al file JSON/stream delle coordinate di Intervals.icu.")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
