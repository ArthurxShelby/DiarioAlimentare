import datetime
import json
import os
import pandas as pd
from supabase import create_client
import streamlit as st
from fpdf import FPDF  # Necessario per generare il PDF (assicurati di avere fpdf2 installato)

st.set_page_config(
    page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide"
)

# --- 0. CONTROLLO ACCESSO PROPRIETARIO ---
is_proprietario = (st.session_state.get("ruolo_corrente") == "Proprietario")

if not is_proprietario:
    st.error("🚨 Accesso Negato: questa sezione è riservata esclusivamente al proprietario.")
    st.info("Torna alla pagina principale del Diario Alimentare ed effettua il login con le credenziali da amministratore.")
    st.stop()

# --- 0. GESTIONE PERSISTENZA CLOUD (SUPABASE) ---

@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

def carica_database(db_iniziale):
    """Carica il database allenamenti dal cloud di Supabase, convertendo le liste in DataFrame."""
    try:
        response = supabase.table("app_data").select("payload").eq("id", 1).execute()
        if response.data and len(response.data) > 0:
            payload = response.data[0]["payload"]
            db_ricostruito = {}
            for anno, mesi in payload.items():
                db_ricostruito[anno] = {}
                for mese, val in mesi.items():
                    if isinstance(val, list):
                        db_ricostruito[anno][mese] = pd.DataFrame(val)
                    else:
                        db_ricostruito[anno][mese] = val
            return db_ricostruito
    except Exception as e:
        st.warning(f"Impossibile connettersi al cloud per il caricamento: {e}")
    return db_iniziale

def salva_database(dati=None):
    """Salva lo stato attuale degli allenamenti nel cloud di Supabase convertendo i DataFrame in liste."""
    if not is_proprietario:
        return
    try:
        if dati is None:
            dati = st.session_state.database_allenamenti
            
        dati_serializzabili = {}
        for anno, mesi in dati.items():
            dati_serializzabili[anno] = {}
            for mese, df_val in mesi.items():
                if isinstance(df_val, pd.DataFrame):
                    dati_serializzabili[anno][mese] = df_val.to_dict(orient="records")
                else:
                    dati_serializzabili[anno][mese] = df_val
                    
        supabase.table("app_data").upsert({"id": 1, "payload": dati_serializzabili}).execute()
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati sul cloud: {e}")

# --- 1. RIFERIMENTI FTP DINAMICI & SIDEBAR ---
st.sidebar.markdown("## Parametri Atleta & FTP")
ftp_atleta = st.sidebar.number_input(
    "FTP Corrente (Watt):", min_value=100, max_value=500, value=279, step=1
)

# Calcoli matematici dinamici basati sul ciclismo moderno
ss_min = int(ftp_atleta * 0.88)
ss_max = int(ftp_atleta * 0.93)
soglia_min = int(ftp_atleta * 0.91)
soglia_max = int(ftp_atleta * 1.05)

cadenza_soglia = "~90 RPM"
cadenza_ss = "~85 RPM"

st.sidebar.markdown(f"### Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {ss_min}-{ss_max}W")
st.sidebar.markdown(f"**Soglia Z4:** {soglia_min}-{soglia_max}W")
st.sidebar.markdown(f"**Cadenza Soglia:** {cadenza_soglia}")
st.sidebar.markdown(f"**Cadenza SS:** {cadenza_ss}")

st.sidebar.markdown("---")

# --- 1.1 MENU A DISCESA NELLA SIDEBAR PER CICLI ALLENAMENTI ---
st.sidebar.markdown("## Inserimento Cicli Allenamenti")
opzioni_cicli = [
    "Soglia Avanzata", 
    "Rilancio Aerobico", 
    "Mantenimento", 
    "Blocco Solido di Sweet Spot", 
    "Intervalli Lineari", 
    "VO2Max", 
    "Estensione Moderata", 
    "Richiami", 
    "2 Serie Ripetizioni", 
    "Scarico"
]
ciclo_selezionato_sidebar = st.sidebar.selectbox("Seleziona Ciclo da Inserire:", opzioni_cicli)
settimana_input = st.sidebar.text_input("Settimana di Riferimento", value="Settimana 1")
giorno_input = st.sidebar.selectbox("Giorno", ["Martedì", "Giovedì", "Sabato", "Domenica", "Lunedì", "Mercoledì", "Venerdì"])
watt_input = st.sidebar.number_input("Watt Target", min_value=50, max_value=500, value=250, step=1)
rpm_input = st.sidebar.number_input("Cadenza (RPM)", min_value=50, max_value=130, value=90, step=1)
ripetizioni_input = st.sidebar.number_input("Ripetizioni", min_value=1, max_value=20, value=3, step=1)
lavoro_input = st.sidebar.number_input("Lavoro (min)", min_value=1, max_value=180, value=15, step=1)
recupero_input = st.sidebar.number_input("Recupero (min)", min_value=0, max_value=60, value=5, step=1)

if st.sidebar.button("Conferma e Inserisci in Tabella"):
    # Recupera l'anno e mese correnti per associare il dato
    anno_corrente_str = str(datetime.date.today().year)
    mese_corrente_str = "Luglio"  # Mese di default o basato sulla selezione principale
    
    # Assicura che la struttura esista
    if anno_corrente_str not in st.session_state.get("database_allenamenti", {}):
        st.session_state.database_allenamenti[anno_corrente_str] = {}
    if "Luglio" not in st.session_state.database_allenamenti[anno_corrente_str]:
        st.session_state.database_allenamenti[anno_corrente_str]["Luglio"] = pd.DataFrame(
            columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"]
        )
        
    nuova_riga = pd.DataFrame([{
        "Settimana": settimana_input,
        "Giorno": giorno_input,
        "Esercizio / Nome": ciclo_selezionato_sidebar,
        "Watt": watt_input,
        "RPM": rpm_input,
        "Ripetizioni": ripetizioni_input,
        "Lavoro (min)": lavoro_input,
        "Recupero (min)": recupero_input
    }])
    
    df_attuale = st.session_state.database_allenamenti[anno_corrente_str]["Luglio"]
    st.session_state.database_allenamenti[anno_corrente_str]["Luglio"] = pd.concat([df_attuale, nuova_riga], ignore_index=True)
    salva_database()
    
    # Pop-up di avvenuto inserimento
    st.sidebar.success(f"✅ Inserimento effettuato con successo per '{ciclo_selezionato_sidebar}'!")

# --- 2. DATABASE INIZIALE STRUTTURATO ---
database_iniziale = {
    "2026": {
        "Luglio": {
            "Settimana 1": {
                "Martedì": {
                    "Esercizio": "Soglia Avanzata",
                    "Watt": 275,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 15,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Blocco Solido di Sweet Spot",
                    "Watt": 250,
                    "RPM": 85,
                    "Ripetizioni": 2,
                    "Lavoro_m": 20,
                    "Recupero_m": 5,
                },
            }
        },
    }
}

elenco_mesi_completo = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

if "database_allenamenti" not in st.session_state:
    st.session_state.database_allenamenti = carica_database(database_iniziale)
    if is_proprietario:
        salva_database()

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

# --- 3. SELEZIONE ANNO E MESE ---
col_anno, col_mese = st.columns(2)

with col_anno:
    anno_selezionato_num = st.number_input(
        "Anno Solare Corrente:", min_value=2020, max_value=2100, value=2026, step=1
    )
    anno_selezionato = str(anno_selezionato_num)

with col_mese:
    mese_selezionato = st.selectbox("Mese Corrente:", elenco_mesi_completo)

st.markdown("---")

if anno_selezionato not in st.session_state.database_allenamenti:
    st.session_state.database_allenamenti[anno_selezionato] = {}

if mese_selezionato not in st.session_state.database_allenamenti[anno_selezionato]:
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = pd.DataFrame(
        columns=[
            "Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM",
            "Ripetizioni", "Lavoro (min)", "Recupero (min)",
        ]
    )

dati_correnti = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]

if not isinstance(dati_correnti, pd.DataFrame):
    if isinstance(dati_correnti, list):
        df_base_mese = pd.DataFrame(dati_correnti)
    else:
        df_base_mese = pd.DataFrame(
            columns=[
                "Settimana", "Giorno", "Esercizio / Nome", "Watt",
                "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)",
            ]
        )
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_base_mese
else:
    df_base_mese = dati_correnti

# --- 4. TABELLA PRINCIPALE: CICLI ALLENAMENTI (Con Modifiche e Cancellazioni) ---
st.subheader(f"📋 Cicli Allenamenti: **{mese_selezionato} {anno_selezionato}**")
st.write("Le voci sottostanti possono essere modificate direttamente o cancellate (selezionando e rimuovendo le righe).")

if is_proprietario:
    df_modificato = st.data_editor(
        df_base_mese,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_cicli_{anno_selezionato}_{mese_selezionato}",
        column_config={
            "Watt": st.column_config.NumberColumn(min_value=50, max_value=500, step=1),
            "RPM": st.column_config.NumberColumn(min_value=60, max_value=120, step=1),
            "Ripetizioni": st.column_config.NumberColumn(min_value=1, max_value=20, step=1),
            "Lavoro (min)": st.column_config.NumberColumn(min_value=1, max_value=180, step=1),
            "Recupero (min)": st.column_config.NumberColumn(min_value=0, max_value=60, step=1),
        },
    )

    if not df_modificato.equals(df_base_mese):
        st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_modificato
        salva_database()

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. FUNZIONE E BOTTONE PER DOWNLOAD IN PDF ---
def genera_pdf(df, mese, anno):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Cicli Allenamenti - {mese} {anno}", 0, 1, "C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 10)
    col_widths = [25, 22, 45, 15, 15, 20, 25, 23]
    headers = ["Settimana", "Giorno", "Esercizio", "Watt", "RPM", "Rip.", "Lavoro", "Rec."]
    
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, 1, 0, "C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 9)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 7, str(row.get("Settimana", "")), 1)
        pdf.cell(col_widths[1], 7, str(row.get("Giorno", "")), 1)
        pdf.cell(col_widths[2], 7, str(row.get("Esercizio / Nome", "")), 1)
        pdf.cell(col_widths[3], 7, str(row.get("Watt", "")), 1, 0, "C")
        pdf.cell(col_widths[4], 7, str(row.get("RPM", "")), 1, 0, "C")
        pdf.cell(col_widths[5], 7, str(row.get("Ripetizioni", "")), 1, 0, "C")
        pdf.cell(col_widths[6], 7, str(row.get("Lavoro (min)", "")), 1, 0, "C")
        pdf.cell(col_widths[7], 7, str(row.get("Recupero (min)", "")), 1, 0, "C")
        pdf.ln()
        
    # Forza la generazione in bytes compatibile con Streamlit
    output = pdf.output()
    if isinstance(output, str):
        return output.encode("latin1")
    return bytes(output)

if not df_base_mese.empty:
    pdf_data = genera_pdf(df_base_mese, mese_selezionato, anno_selezionato)
    st.download_button(
        label="📥 Scarica Tabella in PDF",
        data=pdf_data,
        file_name=f"Cicli_Allenamenti_{mese_selezionato}_{anno_selezionato}.pdf",
        mime="application/pdf"
    )
else:
    st.info("Nessun dato presente nella tabella per abilitare il download in PDF.")
