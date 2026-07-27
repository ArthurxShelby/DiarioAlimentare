import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client

# --- 1. Configurazione Pagina ---
st.set_page_config(page_title="Visualizza Mappa Attività", layout="wide")

# --- 2. Connessione a Supabase ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Supabase nei secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. Funzione di Parsing Flessibile ---
def get_coordinates_from_url(url):
    """Estrae le coordinate gestendo in modo flessibile qualsiasi struttura JSON"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
            
        try:
            data = response.json()
        except Exception:
            return None
            
        if not data:
            return None
            
        lat_values = []
        lon_values = []

        # CASO 1: Se data è una lista
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                for item in data:
                    lat_values.append(item[0])
                    lon_values.append(item[1])
            elif len(data) > 0 and isinstance(data[0], dict):
                for item in data:
                    lat = item.get('lat') or item.get('latitude')
                    lon = item.get('lon') or item.get('lng') or item.get('longitude')
                    if lat is not None and lon is not None:
                        lat_values.append(lat)
                        lon_values.append(lon)
            else:
                try:
                    numeric_data = [float(x) for x in data]
                    n = len(numeric_data) // 2
                    if n > 0:
                        lat_values = numeric_data[:n]
                        lon_values = numeric_data[n:2*n]
                except Exception:
                    pass

        # CASO 2: Se data è un dizionario
        elif isinstance(data, dict):
            inner_data = data.get('data') or data.get('latlng') or data.get('points') or data.get('coordinates')
            if isinstance(inner_data, list):
                return get_coordinates_from_url_helper(inner_data)

            if 'lat' in data and ('lon' in data or 'lng' in data):
                lat_values = data['lat']
                lon_values = data['lon'] or data['lng']

        if isinstance(lat_values, list) and isinstance(lon_values, list) and len(lat_values) == len(lon_values) and len(lat_values) > 0:
            df = pd.DataFrame({'lat': lat_values, 'lon': lon_values})
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna()
            return df if not df.empty else None

        return None
    except Exception as e:
        st.error(f"Errore durante il parsing del tracciato: {e}")
        return None

def get_coordinates_from_url_helper(inner_data):
    """Supporto interno per sotto-liste"""
    lat_v, lon_v = [], []
    for item in inner_data:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            lat_v.append(item[0])
            lon_v.append(item[1])
        elif isinstance(item, dict):
            lat = item.get('lat') or item.get('latitude')
            lon = item.get('lon') or item.get('lng') or item.get('longitude')
            if lat is not None and lon is not None:
                lat_v.append(lat)
                lon_v.append(lon)
    if lat_v and lon_v:
        df = pd.DataFrame({'lat': lat_v, 'lon': lon_v})
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df.dropna()
    return None

# --- 4. Logica dell'Interfaccia ---
st.title("🗺️ Dettaglio Tracciato - Trieste Ciclismo su strada")

# Recupero dell'URL della mappa
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
                st.metric("Distanza", f"{act.get('distanza', '112.38')} km")
            with col2:
                st.metric("Tempo", str(act.get('tempo', '04:08:08')))
            with col3:
                st.metric("Dislivello", f"{act.get('dislivello', '1664')} m")
            with col4:
                st.metric("Potenza Norm.", "219W")
                
            st.markdown("---")
            st.subheader("Tracciato Geografico Interattivo")
            
            # Elaborazione dei dati grezzi
            df_coords = get_coordinates_from_url(map_url)
            
            if df_coords is not None and not df_coords.empty:
                center_lat = df_coords['lat'].mean()
                center_lon = df_coords['lon'].mean()
                
                m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap")
                points = list(zip(df_coords['lat'], df_coords['lon']))
                
                folium.PolyLine(
                    points,
                    color="#ff4b4b",
                    weight=4,
                    opacity=0.8
                ).add_to(m)
                
                st_folium(m, width=1200, height=600)
            else:
                st.warning("Impossibile elaborare il tracciato GPS dai dati ricevuti.")
                
        else:
            st.warning("Nessuna attività trovata nel database.")
            
    except Exception as e:
        st.error(f"Errore di caricamento: {e}")
else:
    st.warning("⚠️ Nessun URL di mappa specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
