import datetime
import json
import os
import pandas as pd
from supabase import create_client
import streamlit as st
from fpdf import FPDF

st.set_page_config(
    page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide"
)

# --- 0. CONTROLLO ACCESSO PROPRIETARIO ---
is_proprietario = (st.session_state.get("ruolo_corrente") == "Proprietario")

if not is_proprietario:
    st.error("🚨 Accesso Negato: questa sezione è riservata esclusivamente al proprietario.")
    st.info("Torna alla pagina principale ed effettua il login con le credenziali da amministratore.")
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
                    if isinstance(val, dict):
                        db_ricostruito[anno][mese] = {
                            "principale": pd.DataFrame(val.get("principale", [])) if isinstance(val.get("principale"), list) else val.get("principale"),
                            "cicli": pd.DataFrame(val.get("cicli", [])) if isinstance(val.get("cicli"), list) else val.get("cicli")
                        }
                    elif isinstance(val, list):
                        db_ricostruito[anno][mese] = {
                            "principale": pd.DataFrame(val),
                            "cicli": pd.DataFrame(columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"])
                        }
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
            for mese, val in mesi.items():
                if isinstance(val, dict):
                    df_princ = val.get("principale")
                    df_cicli = val.get("cicli")
                    dati_serializzabili[anno][mese] = {
                        "principale": df_princ.to_dict(orient="records") if isinstance(df_princ, pd.DataFrame) else df_princ,
                        "cicli": df_cicli.to_dict(orient="records") if isinstance(df_cicli, pd.DataFrame) else df_cicli
                    }
                elif isinstance(val, pd.DataFrame):
                    dati_serializzabili[anno][mese] = {
                        "principale": val.to_dict(orient="records"),
                        "cicli": []
                    }
                    
        supabase.table("app_data").upsert({"id": 1, "payload": dati_serializzabili}).execute()
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati sul cloud: {e}")

# --- 2. DATABASE INIZIALE & STATO ---
database_iniziale = {
    "2026": {
        "Gennaio": {
            "principale": pd.DataFrame([
                {"Settimana": "Settimana 1 (Rientro e Agilità)", "Giorno": "Martedì", "Esercizio / Nome": "Fondo Z2 Agile post-stop", "Watt": 195, "RPM": 95, "Ripetizioni": 1, "Lavoro (min)": 50, "Recupero (min)": 0},
                {"Settimana": "Settimana 1 (Rientro e Agilità)", "Giorno": "Giovedì", "Esercizio / Nome": "Fondo Z2 con Allunghi Z3", "Watt": 210, "RPM": 90, "Ripetizioni": 3, "Lavoro (min)": 10, "Recupero (min)": 5},
                {"Settimana": "Settimana 2 (Progressione Aerobica)", "Giorno": "Martedì", "Esercizio / Nome": "Fondo Medio Z3 graduale: 2 x 12 min", "Watt": 225, "RPM": 90, "Ripetizioni": 2, "Lavoro (min)": 12, "Recupero (min)": 5},
                {"Settimana": "Settimana 2 (Progressione Aerobica)", "Giorno": "Giovedì", "Esercizio / Nome": "Fondo Z2 e Variazioni Cadenza", "Watt": 215, "RPM": 95, "Ripetizioni": 3, "Lavoro (min)": 15, "Recupero (min)": 5},
                {"Settimana": "Settimana 3 (Sweet Spot Moderato)", "Giorno": "Martedì", "Esercizio / Nome": "Sweet Spot Moderato: 2 x 12 min", "Watt": 240, "RPM": 88, "Ripetizioni": 2, "Lavoro (min)": 12, "Recupero (min)": 5},
                {"Settimana": "Settimana 3 (Sweet Spot Moderato)", "Giorno": "Giovedì", "Esercizio / Nome": "Fondo Medio Z3: 2 x 15 min", "Watt": 230, "RPM": 90, "Ripetizioni": 2, "Lavoro (min)": 15, "Recupero (min)": 5},
                {"Settimana": "Settimana 4 (Scarico e Test Ricalibrazione)", "Giorno": "Martedì", "Esercizio / Nome": "Scioltezza e Agilità Z1-Z2", "Watt": 190, "RPM": 95, "Ripetizioni": 1, "Lavoro (min)": 45, "Recupero (min)": 0},
                {"Settimana": "Settimana 4 (Scarico e Test Ricalibrazione)", "Giorno": "Giovedì", "Esercizio / Nome": "Test FTP 20 min di Verifica", "Watt": 270, "RPM": 92, "Ripetizioni": 1, "Lavoro (min)": 20, "Recupero (min)": 0}
            ]),
            "cicli": pd.DataFrame(columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"])
        }
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
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = {
        "principale": pd.DataFrame(columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"]),
        "cicli": pd.DataFrame(columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"])
    }

struttura_mese = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]
if not isinstance(struttura_mese, dict):
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = {
        "principale": struttura_mese if isinstance(struttura_mese, pd.DataFrame) else pd.DataFrame(),
        "cicli": pd.DataFrame(columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"])
    }

df_base_mese = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]["principale"]
df_cicli_mese = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]["cicli"]


# --- 1. RIFERIMENTI FTP DINAMICI & SIDEBAR ---
st.sidebar.markdown("## Parametri Atleta & FTP")
ftp_atleta = st.sidebar.number_input(
    "FTP Corrente (Watt):", min_value=100, max_value=500, value=279, step=1
)

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

# --- 1.1 MENU A DISCESA NELLA SIDEBAR PER CICLI ALLENAMENTI (PERMANENTE) ---
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
    if anno_selezionato not in st.session_state.database_allenamenti:
        st.session_state.database_allenamenti[anno_selezionato] = {}
    if mese_selezionato not in st.session_state.database_allenamenti[anno_selezionato]:
        st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = {
            "principale": pd.DataFrame(),
            "cicli": pd.DataFrame(columns=["Settimana", "Giorno", "Esercizio / Nome", "Watt", "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)"])
        }
        
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
    
    df_cicli_attuale = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]["cicli"]
    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]["cicli"] = pd.concat([df_cicli_attuale, nuova_riga], ignore_index=True)
    
    # Salvataggio immediato e permanente nel Cloud Supabase
    salva_database()
    st.sidebar.success(f"✅ Ciclo inserito e salvato in modo permanente per {mese_selezionato} {anno_selezionato}!")
    st.rerun()


# --- 4. TABELLA PRINCIPALE ---
st.subheader(f"📋 Pianificazione Principale: **{mese_selezionato} {anno_selezionato}**")

if is_proprietario:
    df_modificato = st.data_editor(
        df_base_mese,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_principale_{anno_selezionato}_{mese_selezionato}",
        column_config={
            "Watt": st.column_config.NumberColumn(min_value=50, max_value=500, step=1),
            "RPM": st.column_config.NumberColumn(min_value=60, max_value=120, step=1),
            "Ripetizioni": st.column_config.NumberColumn(min_value=1, max_value=20, step=1),
            "Lavoro (min)": st.column_config.NumberColumn(min_value=1, max_value=180, step=1),
            "Recupero (min)": st.column_config.NumberColumn(min_value=0, max_value=60, step=1),
        },
    )

    if not df_modificato.equals(df_base_mese):
        st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]["principale"] = df_modificato
        salva_database()

st.markdown("<br>", unsafe_allow_html=True)

# --- 4.1 SECONDA TABELLA: CICLI ALLENAMENTI (Permanente e Sincronizzata) ---
st.subheader(f"⚙️ Cicli Allenamenti Aggiuntivi: **{mese_selezionato} {anno_selezionato}**")
st.write("Tabella dedicata ai cicli inseriti tramite il menu laterale (salvataggio permanente Cloud):")

if is_proprietario:
    df_cicli_modificato = st.data_editor(
        df_cicli_mese,
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

    if not df_cicli_modificato.equals(df_cicli_mese):
        st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]["cicli"] = df_cicli_modificato
        salva_database()

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. FUNZIONE E BOTTONE PER DOWNLOAD IN PDF ---
def genera_pdf(df_princ, df_cicli, mese, anno):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Report Allenamenti - {mese} {anno}", 0, 1, "C")
    pdf.ln(5)
    
    col_widths = [25, 22, 45, 15, 15, 20, 25, 23]
    headers = ["Settimana", "Giorno", "Esercizio", "Watt", "RPM", "Rip.", "Lavoro", "Rec."]
    
    if not df_princ.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Pianificazione Principale", 0, 1, "L")
        pdf.set_font("Arial", "B", 10)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, 1, 0, "C")
        pdf.ln()
        
        pdf.set_font("Arial", "", 9)
        for _, row in df_princ.iterrows():
            pdf.cell(col_widths[0], 7, str(row.get("Settimana", "")), 1)
            pdf.cell(col_widths[1], 7, str(row.get("Giorno", "")), 1)
            pdf.cell(col_widths[2], 7, str(row.get("Esercizio / Nome", "")), 1)
            pdf.cell(col_widths[3], 7, str(row.get("Watt", "")), 1, 0, "C")
            pdf.cell(col_widths[4], 7, str(row.get("RPM", "")), 1, 0, "C")
            pdf.cell(col_widths[5], 7, str(row.get("Ripetizioni", "")), 1, 0, "C")
            pdf.cell(col_widths[6], 7, str(row.get("Lavoro (min)", "")), 1, 0, "C")
            pdf.cell(col_widths[7], 7, str(row.get("Recupero (min)", "")), 1, 0, "C")
            pdf.ln()
        pdf.ln(5)

    if not df_cicli.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Cicli Allenamenti Aggiuntivi", 0, 1, "L")
        pdf.set_font("Arial", "B", 10)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, 1, 0, "C")
        pdf.ln()
        
        pdf.set_font("Arial", "", 9)
        for _, row in df_cicli.iterrows():
            pdf.cell(col_widths[0], 7, str(row.get("Settimana", "")), 1)
            pdf.cell(col_widths[1], 7, str(row.get("Giorno", "")), 1)
            pdf.cell(col_widths[2], 7, str(row.get("Esercizio / Nome", "")), 1)
            pdf.cell(col_widths[3], 7, str(row.get("Watt", "")), 1, 0, "C")
            pdf.cell(col_widths[4], 7, str(row.get("RPM", "")), 1, 0, "C")
            pdf.cell(col_widths[5], 7, str(row.get("Ripetizioni", "")), 1, 0, "C")
            pdf.cell(col_widths[6], 7, str(row.get("Lavoro (min)", "")), 1, 0, "C")
            pdf.cell(col_widths[7], 7, str(row.get("Recupero (min)", "")), 1, 0, "C")
            pdf.ln()
        
    output = pdf.output()
    if isinstance(output, str):
        return output.encode("latin1")
    return bytes(output)

if not df_base_mese.empty or not df_cicli_mese.empty:
    pdf_data = genera_pdf(df_base_mese, df_cicli_mese, mese_selezionato, anno_selezionato)
    st.download_button(
        label="📥 Scarica Report completo in PDF",
        data=pdf_data,
        file_name=f"Report_Allenamenti_{mese_selezionato}_{anno_selezionato}.pdf",
        mime="application/pdf"
    )
else:
    st.info("Nessun dato presente nelle tabelle per abilitare il download in PDF.")
