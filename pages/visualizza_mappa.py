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
    """Estrae i dati da una lista piatta di numeri alternati [lat, lon, lat, lon...]"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        if not data or not isinstance(data, list):
            return None
            
        # Caso A: Lista di coppie già strutturate [[lat, lon], [lat, lon], ...]
        if len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
            df = pd.DataFrame(data, columns=['lat', 'lon'])
            
        # Caso B: Lista piatta di numeri alternati [lat, lon, lat, lon, ...]
        elif len(data) > 0 and not isinstance(data[0], (list, tuple)):
            # Tronchiamo la lista se ha un numero dispari di elementi
            limit = (len(data) // 2) * 2
            clean_data = data[:limit]
            
            # Estraiamo gli elementi alternati
            lats = clean_data[0::2]  # Posizioni pari: 0, 2, 4...
            lons = clean_data[1::2]  # Posizioni dispari: 1, 3, 5...
            
            df = pd.DataFrame({'lat': lats, 'lon': lons})
        else:
            return None
            
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df.dropna()
        
        return df if not df.empty else None
        
    except Exception as e:
        st.error(f"Errore nel parsing: {e}")
        return None

# --- Logica della Pagina ---
st.title("🗺️ Visualizzazione Percorso Attività")

map_url = st.session_state.get("map_url_to_view")
if not map_url:
    map_url = st.query_params.get("map_url")

if map_url:
    try:
        response = supabase.table("uscite").select("titolo, data").eq("mappa", map_url).execute()
        if response.data:
            act_info = response.data[0]
            st.subheader(f"{act_info['titolo']} - {act_info['data']}")
    except:
        pass 

    df_coords = get_coordinates_from_json(map_url)
    
    if df_coords is not None and not df_coords.empty:
        # Mostriamo la mappa nativa con le coordinate estratte correttamente
        st.map(df_coords, use_container_width=True)
    else:
        st.warning("Impossibile interpretare la serie numerica come coordinate valide.")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
