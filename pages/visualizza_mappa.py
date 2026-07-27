import streamlit as st
import pandas as pd
import requests
import json
from supabase import create_client, Client

# --- 1. Configurazione pagina (deve essere la primissima chiamata) ---
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
    """Scarica il JSON e formatta correttamente le coordinate senza inversioni errate"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                return None
            
            # Se i dati sono una lista di coppie [lat, lon]
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], (list, tuple)) and len(data[0]) >= 2:
                df = pd.DataFrame(data, columns=['lat', 'lon'])
            
            # Se i dati sono una lista piatta di coordinate alternate
            elif isinstance(data, list) and len(data) > 0 and not isinstance(data[0], (list, tuple)):
                half = len(data) // 2
                # In Intervals.icu lo stream della mappa fornisce la longitudine prima e la latitudine dopo (o viceversa).
                # Proviamo a mappare esplicitamente colonna 1 = lat (seconda metà) e colonna 2 = lon (prima metà)
                lons = data[:half]
                lats = data[half:half*2]
                df = pd.DataFrame({'lat': lats, 'lon': lons})
            else:
                return None
                
            # Conversione in numerico e pulizia dei valori non validi
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna()
            
            return df if not df.empty else None
        else:
            return None
    except Exception as e:
        st.error(f"Errore nell'elaborazione della mappa: {e}")
        return None

# --- Logica della Pagina ---
st.title("🗺️ Visualizzazione Percorso Attività")

# Recuperiamo l'URL sia dalla sessione che dai query params (per massima compatibilità)
map_url = st.session_state.get("map_url_to_view")
if not map_url:
    map_url = st.query_params.get("map_url")

if map_url:
    st.info(f"Caricamento percorso in corso...")
    
    try:
        response = supabase.table("uscite").select("titolo, data").eq("mappa", map_url).execute()
        if response.data:
            act_info = response.data[0]
            st.subheader(f"{act_info['titolo']} - {act_info['data']}")
    except Exception as e:
        pass 

    df_coords = get_coordinates_from_json(map_url)
    
    if df_coords is not None and not df_coords.empty:
        st.map(df_coords, use_container_width=True)
        
        with st.expander("Dettagli Coordinate"):
            st.write(f"Numero di punti tracciati: {len(df_coords)}")
            st.dataframe(df_coords.head(10))
    else:
        st.warning("Impossibile caricare i dati della mappa o file vuoto.")

else:
    st.warning("⚠️ Nessun URL di mappa specificato.")
    st.info("Torna alla pagina **uscite** e seleziona un'attività cliccando su 'Apri Mappa Grafica'.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
