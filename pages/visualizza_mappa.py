import streamlit as st
import pandas as pd
import requests
import polyline
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
    """Estrae e decodifica le coordinate in modo robusto"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        # Caso 1: È una stringa codificata (Google Polyline Algorithm)
        if isinstance(data, str):
            decoded = polyline.decode(data)
            if decoded:
                return pd.DataFrame(decoded, columns=['lat', 'lon'])
                
        # Caso 2: È una lista
        if isinstance(data, list) and len(data) > 0:
            # Se è una lista di coppie [lat, lon]
            if isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                df = pd.DataFrame(data, columns=['lat', 'lon'])
                df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
                df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
                return df.dropna()
                
            # Se è una lista piatta numerica
            elif not isinstance(data[0], (list, tuple)):
                # Se Intervals passa un dizionario o array di oggetti lat/lon separati
                pass
                
        return None
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
        response = supabase.table("uscite").select("titolo, data, distanza, tempo, dislivello").eq("mappa", map_url).execute()
        if response.data:
            act = response.data[0]
            st.subheader(f"{act.get('titolo', 'Attività')} - {act.get('data', '')}")
    except:
        pass 

    df_coords = get_coordinates_from_json(map_url)
    
    if df_coords is not None and not df_coords.empty:
        # Visualizziamo la mappa nativa pulita con i punti decodificati correttamente
        st.map(df_coords, use_container_width=True)
    else:
        st.warning("Impossibile decodificare il tracciato con il formato corrente.")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
