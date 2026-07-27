import streamlit as st
import pandas as pd
import requests
import json
from supabase import create_client, Client

# --- Configurazione Supabase (copiala dal tuo file principale) ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except Exception as e:
    st.error("Errore: Configura le credenziali di Supabase nei secrets.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Visualizza Percorso Attività", layout="wide")

def get_coordinates_from_json(url):
    """Scarica il JSON dal bucket e lo converte in un DataFrame Pandas per st.map"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Il file è una lista di liste: [[lat, lon], [lat, lon], ...]
            intervals_data = response.json()
            if not intervals_data:
                return None
            
            # Convertiamo in DataFrame per st.map()
            df = pd.DataFrame(intervals_data, columns=['lat', 'lon'])
            return df
        else:
            st.error(f"Errore nel download della mappa. Codice: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Eccezione durante l'elaborazione della mappa: {e}")
        return None

# --- Logica della Pagina ---
st.title("🗺️ Visualizzazione Percorso Attività")

# Recuperiamo l'URL dell'attività dai parametri della URL (query parameters)
query_params = st.query_params
map_url = query_params.get("map_url")

if map_url:
    st.info(f"Caricamento percorso in corso...")
    
    # 1. Recuperiamo i dettagli dell'attività dal DB (facoltativo, solo per titolo/data)
    try:
        # Eseguiamo una query per trovare l'attività con questo URL di mappa
        response = supabase.table("uscite").select("titolo, data").eq("mappa", map_url).execute()
        if response.data:
            act_info = response.data[0]
            st.subheader(f"{act_info['titolo']} - {act_info['data']}")
    except Exception as e:
        pass # Se fallisce, mostriamo solo la mappa

    # 2. Elaboriamo il JSON e mostriamo la mappa
    df_coords = get_coordinates_from_json(map_url)
    
    if df_coords is not None and not df_coords.empty:
        st.map(df_coords, use_container_width=True)
        
        # Info aggiuntive
        with st.expander("Dettagli Coordinate"):
            st.write(f"Numero di punti tracciati: {len(df_coords)}")
            st.dataframe(df_coords.head(10))
    else:
        st.warning("Impossibile caricare i dati della mappa o file vuoto.")

else:
    st.error("Nessun URL di mappa specificato. Torna alla pagina delle Uscite e clicca su 'Visualizza Mappa'.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
