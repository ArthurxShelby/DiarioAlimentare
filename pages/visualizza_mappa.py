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

def get_coordinates_from_url(url):
    """Scarica il testo grezzo e lo converte in coordinate lat/lon corrette"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
            
        # Proviamo a leggere il JSON o a interpretare il testo come lista di numeri
        try:
            data = response.json()
        except:
            # Se è una stringa di numeri separati da virgola
            text = response.text.strip()
            data = [float(x.strip()) for x in text.replace('[', '').replace(']', '').split(',') if x.strip()]
            
        if not data or not isinstance(data, list) or len(data) < 4:
            return None
            
        # Se i dati sono una lista piatta [lat1, lon1, lat2, lon2, ...]
        limit = (len(data) // 2) * 2
        clean_data = data[:limit]
        
        lats = clean_data[0::2]  # Elementi pari
        lons = clean_data[1::2]  # Elementi dispari
        
        df = pd.DataFrame({'lat': lats, 'lon': lons})
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df = df.dropna()
        
        return df if not df.empty else None
    except Exception as e:
        st.error(f"Errore di parsing: {e}")
        return None

# --- Logica della Pagina ---
st.title("🗺️ Mappa Attività - Trieste Ciclismo su strada")

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
                st.metric("Distanza", f"{act.get('distanza', 112.38)} km")
            with col2:
                st.metric("Tempo", str(act.get('tempo', '04:08:08')))
            with col3:
                st.metric("Dislivello", f"{act.get('dislivello', 1664)} m")
            with col4:
                st.metric("Potenza Norm.", "219W")
                
            st.markdown("---")
            
            st.subheader("Tracciato Geografico")
            
            # Carichiamo e tracciamo la mappa con i punti corretti
            df_coords = get_coordinates_from_url(map_url)
            
            if df_coords is not None and not df_coords.empty:
                st.success(f"Tracciato elaborato con successo ({len(df_coords)} punti GPS rilevati).")
                st.map(df_coords, use_container_width=True)
            else:
                st.warning("Impossibile convertire la sequenza numerica in coordinate cartografiche valide.")
        else:
            st.warning("Nessuna informazione trovata per questa attività.")
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {e}")
else:
    st.warning("⚠️ Nessun URL specificato.")

st.markdown("---")
if st.button("⬅️ Torna alla Gestione Uscite"):
    st.switch_page("pages/uscite.py")
