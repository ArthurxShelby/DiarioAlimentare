import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
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

def get_latlon_pairs(url):
    """Estrae le coppie pulite gestendo sia liste di tuple che liste separate"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        
        data = response.json()
        if not data or not isinstance(data, list):
            return []
            
        coords = []
        # Se sono già coppie [lat, lon]
        if len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
            for pt in data:
                try:
                    lat, lon = float(pt[0]), float(pt[1])
                    coords.append((lat, lon))
                except:
                    continue
        # Se è una lista piatta
        elif len(data) > 0 and not isinstance(data[0], (list, tuple)):
            half = len(data) // 2
            lats = data[:half]
            lons = data[half:2*half]
            for lat, lon in zip(lats, lons):
                try:
                    coords.append((float(lat), float(lon)))
                except:
                    continue
        return coords
    except Exception as e:
        st.error(f"Errore nel parsing: {e}")
        return []

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

    coords = get_latlon_pairs(map_url)
    
    if coords:
        # Centriamo la mappa sul primo punto del percorso
        m = folium.Map(location=coords[0], zoom_start=11, tiles="CartoDB dark_matter")
        
        # Disegniamo la linea del percorso
        folium.PolyLine(coords, color="red", weight=4, opacity=0.8).add_to(m)
        
        # Renderizziamo in Streamlit
        st_folium(m, width=1100, height=600)
    else:
        st.warning("Impossibile caricare i dati della mappa o file vuoto.")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
