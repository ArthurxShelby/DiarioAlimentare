import datetime
import pandas as pd
import streamlit as st
import pickle  # <-- NUOVO: Modulo necessario per salvare i dati su file fisico
import os

st.set_page_config(
    page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide"
)

# --- 0. IMPOSTAZIONE FILE DI SALVATAGGIO ---
FILE_DATI = "memoria_allenamenti.pkl"

def carica_dati_locali():
    """Carica i dati dal file fisico se esiste, altrimenti carica quelli di default."""
    if os.path.exists(FILE_DATI):
        try:
            with open(FILE_DATI, "rb") as f:
                return pickle.load(f)
        except Exception:
            return database_iniziale
    return database_iniziale

def salva_dati_locali():
    """Sovrascrive il file fisico con i dati attuali presenti in memoria."""
    with open(FILE_DATI, "wb") as f:
        pickle.dump(st.session_state.database_allenamenti, f)

# --- 1. RIFERIMENTI FTP & SIDEBAR ---
ftp_atleta = 279
st.sidebar.markdown(f"## Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM")
st.sidebar.markdown("**Cadenza SS:** ~85 RPM")

# --- 2. DATABASE INIZIALE (Metti qui il tuo dizionario completo di Agosto-Dicembre) ---
database_iniziale = {
    # ... Inserisci qui il dizionario con i mesi aggiornati ...
}

elenco_mesi_completo = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

# --- 3. INIZIALIZZAZIONE DELLA MEMORIA CON SALVATAGGIO LOCALE ---
if "database_allenamenti" not in st.session_state:
    # Invece di caricare il database iniziale, legge dal file salvato sul PC
    st.session_state.database_allenamenti = carica_dati_locali()

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

col_anno, col_mese = st.columns(2)

with col_anno:
    anno_selezionato = st.number_input(
        "Anno Solare Corrente:", min_value=2020, max_value=2100, value=2026, step=1
    )

with col_mese:
    mese_selezionato = st.selectbox("Mese Corrente:", elenco_mesi_completo)

st.markdown("---")

# Creazione dell'anno e mese se non esistono nella memoria caricata
if anno_selezionato not in st.session_state.database_allenamenti:
    st.session_state.database_allenamenti[anno_selezionato] = {}

if mese_selezionato not in st.session_state.database_allenamenti[anno_selezionato]:
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = pd.DataFrame(
        columns=[
            "Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM",
            "Ripetizioni", "Lavoro (min)", "Recupero (min)",
        ]
    )

# Estrazione e formattazione dei dati correnti
dati_correnti = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]

if isinstance(dati_correnti, dict):
    # Logica di conversione dict -> DataFrame (se necessario al primo avvio)
    # ... (Mantieni la logica precedente qui se hai dizionari annidati)
    pass
elif isinstance(dati_correnti, list):
    # Se il database iniziale è strutturato come lista di dizionari (come ti ho passato sopra)
    df_base_mese = pd.DataFrame(dati_correnti)
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_base_mese
else:
    df_base_mese = dati_correnti


# --- 5. TABELLA INTERATTIVA DI MODIFICA ---
st.subheader(f"✍️ Gestione e Modifica Allenamenti: **{mese_selezionato} {anno_selezionato}**")

df_modificato = st.data_editor(
    df_base_mese,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_{anno_selezionato}_{mese_selezionato}",
    column_config={
        "Watt": st.column_config.NumberColumn(min_value=50, max_value=500, step=1),
        "RPM": st.column_config.NumberColumn(min_value=60, max_value=120, step=1),
        "Ripetizioni": st.column_config.NumberColumn(min_value=1, max_value=20, step=1),
        "Lavoro (min)": st.column_config.NumberColumn(min_value=1, max_value=180, step=1),
        "Recupero (min)": st.column_config.NumberColumn(min_value=0, max_value=60, step=1),
    },
)

# --- NUOVO: TRIGGER DI SALVATAGGIO AUTOMATICO ---
# Se rileva che hai modificato anche solo un numero, aggiorna la memoria e salva su disco!
if not df_modificato.equals(df_base_mese):
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_modificato
    salva_dati_locali()
