import streamlit as st
import pandas as pd
import requests
import plotly.express as px
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
    """Estrae le coordinate in modo pulito per Plotly"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            if not data or not isinstance(data, list):
                return None
            
            # Se è una lista di coppie
            if len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                df = pd.DataFrame(data, columns=['lat', 'lon'])
            # Se è la lista piatta
            elif len(data) > 0 and not isinstance(data[0], (list, tuple)):
                limit = (len(data) // 2) * 2
                half = limit // 2
                lons = data[:half]
                lats = data[half:limit]
                df = pd.DataFrame({'lat': lats, 'lon': lons})
            else:
                return None
                
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna()
            
            return df if not df.empty else None
        else:
            return None
    except Exception as e:
        st.error(f"Errore: {e}")
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
        # Usiamo Plotly Scattermapbox per disegnare il percorso in modo nativo e stabile
        fig = px.line_mapbox(
            df_coords, 
            lat="lat", 
            lon="lon", 
            zoom=12, 
            height=600
        )
        
        # Impostiamo uno stile scuro coordinato con il tema della tua app
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Impossibile caricare i dati della mappa o file vuoto.")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
