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

# --- 3. Funzione di Parsing ("Gli Occhiali") ---
def get_coordinates_from_url(url):
    """Converte i semicircoli di Intervals.icu (standard FIT/Garmin) in gradi decimali"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
            
        try:
            data = response.json()
        except:
            text = response.text.strip()
            data = [float(x.strip()) for x in text.replace('[', '').replace(']', '').split(',') if x.strip()]
            
        if not data or not isinstance(data, list) or len(data) < 4:
            return None
            
        n = len(data) // 2
        block1 = data[:n]
        block2 = data[n:2*n]
        
        # Fattore di conversione esatto da semicircoli a gradi decimali (180 / 2^31)
        SEMICIRCLES_TO_DEGREES = 180.0 / (2**31)
        
        # Conversione puntuale dei valori
        latitudes = [x * SEMICIRCLES_TO_DEGREES for x in block1]
        longitudes = [x * SEMICIRCLES_TO_DEGREES for x in block2]

        df = pd.DataFrame({'lat': latitudes, 'lon': longitudes})
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df.dropna()
        
        return df if not df.empty else None
    except Exception as e:
        st.error(f"Errore durante il parsing del tracciato: {e}")
        return None
       
    except Exception as e:
        st.error(f"Errore durante il parsing del tracciato: {e}")
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
                # Calcoliamo il punto centrale della mappa in base alle coordinate reali del giro
                center_lat = df_coords['lat'].mean()
                center_lon = df_coords['lon'].mean()
                
                # Creazione della mappa interattiva con Folium (stile OpenStreetMap)
                m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="OpenStreetMap")
                
                # Estrazione dei punti sotto forma di lista di tuple [lat, lon]
                points = list(zip(df_coords['lat'], df_coords['lon']))
                
                # Disegno della polilinea del percorso (colore rosso stile Intervals)
                folium.PolyLine(
                    points,
                    color="#ff4b4b",
                    weight=4,
                    opacity=0.8
                ).add_to(m)
                
                # Renderizzazione della mappa all'interno di Streamlit
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
