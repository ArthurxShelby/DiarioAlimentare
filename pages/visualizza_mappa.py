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
    """Scarica il JSON e restituisce un DataFrame pronto per st.map()"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            if not data or not isinstance(data, list):
                return None
            
            # Formato A: Lista di coppie [lat, lon]
            if len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                df = pd.DataFrame(data, columns=['lat', 'lon'])
            
            # Formato B: Lista piatta di valori alternati
            elif len(data) > 0 and not isinstance(data[0], (list, tuple)):
                half = len(data) // 2
                lats = data[:half]
                lons = data[half:2*half]
                
                # Creiamo il DataFrame direttamente con le colonne standard di Streamlit
                df = pd.DataFrame({'lat': lats, 'lon': lons})
            else:
                return None
                
            # Pulizia e conversione numerica rigorosa
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna()
            
            return df if not df.empty else None
        else:
            return None
    except Exception as e:
        st.error(f"Errore nell'elaborazione: {e}")
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
        # st.map accetta nativamente un dataframe con colonne 'lat' e 'lon'
        st.map(df_coords, use_container_width=True)
        
        with st.expander("Dettagli Coordinate"):
            st.write(f"Punti totali tracciati: {len(df_coords)}")
            st.dataframe(df_coords.head(10))
    else:
        st.warning("Impossibile caricare i dati della mappa o file vuoto.")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
