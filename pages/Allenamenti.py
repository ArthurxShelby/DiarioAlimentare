import datetime
import json
import os
import pandas as pd
from supabase import create_client
import streamlit as st

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

ss_min = int(ftp_atleta * 0.88)
ss_max = int(ftp_atleta * 0.93)
soglia_min = int(ftp_atleta * 0.91)
soglia_max = int(ftp_atleta * 1.05)

st.sidebar.markdown(f"### Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {ss_min}-{ss_max}W")
st.sidebar.markdown(f"**Soglia Z4:** {soglia_min}-{soglia_max}W")

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

# --- 2. SELEZIONE ANNO E MESE ---
col_anno, col_mese = st.columns(2)

with col_anno:
    anno_selezionato_num = st.number_input(
        "Anno Solare Corrente:", min_value=2020, max_value=2100, value=2026, step=1
    )
    anno_selezionato = str(anno_selezionato_num)

elenco_mesi_completo = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

with col_mese:
    mese_selezionato = st.selectbox("Mese Corrente:", elenco_mesi_completo)

st.markdown("---")

database_iniziale = {
    "2026": {
        "Gennaio": pd.DataFrame(
            columns=[
                "Settimana", "Giorno", "Esercizio / Nome", "Watt",
                "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)",
            ]
        )
    }
}

if "database_allenamenti" not in st.session_state:
    st.session_state.database_allenamenti = carica_database(database_iniziale)
    if is_proprietario:
        salva_database()

if "version_editor" not in st.session_state:
    st.session_state.version_editor = 0

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
if isinstance(dati_correnti, pd.DataFrame):
    df_base_mese = dati_correnti.copy()
elif isinstance(dati_correnti, list):
    df_base_mese = pd.DataFrame(dati_correnti)
else:
    df_base_mese = pd.DataFrame(
        columns=[
            "Settimana", "Giorno", "Esercizio / Nome", "Watt",
            "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)",
        ]
    )

st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_base_mese
df_da_mostrare = df_base_mese

# --- 3. PRIMA TABELLA: GESTIONE E MODIFICA ALLENAMENTI (CSV & EDITOR) ---
st.subheader(f"✍️ Gestione e Modifica Allenamenti: **{mese_selezionato} {anno_selezionato}**")

if is_proprietario:
    with st.expander("📂 Integra o carica piano di lavoro tramite file CSV", expanded=False):
        st.write(f"Stai caricando i dati per: **{mese_selezionato} {anno_selezionato}**.")
        file_caricato = st.file_uploader(
            "Seleziona il file CSV",
            type=["csv"],
            key=f"uploader_{anno_selezionato}_{mese_selezionato}_{st.session_state.version_editor}",
        )

        if file_caricato is not None:
            try:
                df_caricato = pd.read_csv(file_caricato, sep=None, engine="python")
                df_caricato.columns = df_caricato.columns.str.strip()

                colonne_attese = [
                    "Settimana", "Giorno", "Esercizio / Nome", "Watt",
                    "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)",
                ]

                if all(col in df_caricato.columns for col in colonne_attese):
                    df_filtrato = df_caricato[colonne_attese].copy()
                    st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_filtrato
                    salva_database()
                    st.toast(f"File CSV caricato e salvato per {mese_selezionato} {anno_selezionato}!", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Il file CSV non contiene le colonne corrette: {colonne_attese}")
            except Exception as e:
                st.error(f"Errore nella lettura del file CSV: {e}")

if is_proprietario:
    df_modificato = st.data_editor(
        df_da_mostrare,
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_finale_{anno_selezionato}_{mese_selezionato}_{st.session_state.version_editor}",
        column_config={
            "Settimana": st.column_config.TextColumn("Settimana", required=True),
            "Giorno": st.column_config.TextColumn("Giorno", required=True),
            "Esercizio / Nome": st.column_config.TextColumn("Esercizio / Nome", required=True),
            "Watt": st.column_config.NumberColumn("Watt", min_value=0, max_value=1000, step=1, format="%d"),
            "RPM": st.column_config.NumberColumn("RPM", min_value=0, max_value=200, step=1, format="%d"),
            "Ripetizioni": st.column_config.NumberColumn("Ripetizioni", min_value=0, max_value=100, step=1, format="%d"),
            "Lavoro (min)": st.column_config.NumberColumn("Lavoro (min)", min_value=0, max_value=1440, step=1, format="%d"),
            "Recupero (min)": st.column_config.NumberColumn("Recupero (min)", min_value=0, max_value=1440, step=1, format="%d"),
        },
    )

    if not df_modificato.equals(df_da_mostrare):
        st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_modificato.copy()
        salva_database()
        st.rerun()

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- 4. SECONDA TABELLA: PROGRAMMAZIONE CICLI (CAMPI STATICI + DINAMICI ALIMENTATI DALLA TABELLA SOPRA) ---
st.subheader("📋 Programmazione Cicli di Allenamento (Perpetua)")
st.write("I campi di sinistra sono fissi/statici, mentre le colonne di destra (*Watt, Ripetizioni, Lavoro, Recupero*) si popolano automaticamente dai dati della tabella superiore.")

col_macro1, col_macro2 = st.columns(2)
with col_macro1:
    mese_cicli = st.selectbox(
        "Mese di Riferimento (Cicli)", 
        elenco_mesi_completo,
        key="macro_mese_cicli"
    )
with col_macro2:
    anno_cicli_num = st.number_input(
        "Anno di Riferimento (Cicli)", 
        min_value=2020, 
        max_value=2050, 
        value=int(anno_selezionato), 
        step=1,
        key="macro_anno_cicli"
    )
    anno_cicli = str(anno_cicli_num)

st.markdown(f"**Macrociclo Attuale:** {mese_cicli} {anno_cicli}")

# Struttura fissa statica (Screen 1)
df_struttura_fissa = pd.DataFrame([
    {"Cicli": "I°", "Allenamento": "Soglia", "Tipo": "Soglia Avanzata"},
    {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Rilancio Aerobico"},
    {"Cicli": "II°", "Allenamento": "Soglia", "Tipo": "Blocco Solido di Soglia"},
    {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Estensione Moderata"},
    {"Cicli": "III°", "Allenamento": "Soglia", "Tipo": "Intervalli Lineari VO2Max"},
    {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Blocco di tenuta"},
    {"Cicli": "IV°", "Allenamento": "Richiami Soglia", "Tipo": "Scarico"},
    {"Cicli": "", "Allenamento": "Richiami Mantenimento", "Tipo": "Scarico"},
])

# Recuperiamo i dati della tabella sopra per il mese/anno selezionato per popolare le colonne dinamiche
df_fonte_dati = st.session_state.database_allenamenti.get(anno_cicli, {}).get(mese_cicli, pd.DataFrame())
if isinstance(df_fonte_dati, list):
    df_fonte_dati = pd.DataFrame(df_fonte_dati)

# Creazione delle colonne dinamiche attingendo dalla tabella superiore (o lasciandole vuote se mancano i dati)
colonne_dinamiche = ["Watt", "Ripetizioni", "Lavoro (min)", "Recupero (min)"]
for col in colonne_dinamiche:
    valori = []
    for i in range(len(df_struttura_fissa)):
        if not df_fonte_dati.empty and i < len(df_fonte_dati) and col in df_fonte_dati.columns:
            val = df_fonte_dati.loc[i, col]
            valori.append("" if pd.isna(val) else val)
        else:
            valori.append("")
    df_struttura_fissa[col] = valori

# Visualizzazione della tabella unificata (Campi statici + dinamici)
st.data_editor(
    df_struttura_fissa,
    num_rows="fixed",
    use_container_width=True,
    key=f"editor_cicli_sincro_{anno_cicli}_{mese_cicli}",
    disabled=["Cicli", "Allenamento", "Tipo", "Watt", "Ripetizioni", "Lavoro (min)", "Recupero (min)"],
    column_config={
        "Cicli": st.column_config.TextColumn("Cicli"),
        "Allenamento": st.column_config.TextColumn("Allenamento"),
        "Tipo": st.column_config.TextColumn("Tipo"),
        "Watt": st.column_config.TextColumn("Watt"),
        "Ripetizioni": st.column_config.TextColumn("Ripetizioni"),
        "Lavoro (min)": st.column_config.TextColumn("Lavoro (min)"),
        "Recupero (min)": st.column_config.TextColumn("Recupero (min)"),
    },
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. ESPORTAZIONE PDF ---
if st.button("📥 Esporta Tabella Cicli in PDF", use_container_width=True, key="btn_pdf_sincro"):
    from fpdf import FPDF
    import tempfile

    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, "Programmazione Cicli di Allenamento", ln=True, align="L")
    
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, f"Macrociclo: {mese_cicli} {anno_cicli}", ln=True, align="L")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(43, 108, 176)
    pdf.set_text_color(255, 255, 255)
    
    headers = ["Cicli", "Allenamento", "Tipo", "Watt", "Ripetizioni", "Lavoro", "Recupero"]
    widths = [18, 38, 48, 18, 22, 22, 24]
    
    for i, h in enumerate(headers):
        pdf.cell(widths[i], 8, h, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    
    df_export = df_struttura_fissa.fillna("")
    for _, row in df_export.iterrows():
        pdf.cell(widths[0], 7, str(row.get('Cicli', '')), border=1, align="C")
        pdf.cell(widths[1], 7, str(row.get('Allenamento', '')), border=1, align="L")
        pdf.cell(widths[2], 7, str(row.get('Tipo', '')), border=1, align="L")
        pdf.cell(widths[3], 7, str(row.get('Watt', '')), border=1, align="C")
        pdf.cell(widths[4], 7, str(row.get('Ripetizioni', '')), border=1, align="C")
        pdf.cell(widths[5], 7, str(row.get('Lavoro (min)', '')), border=1, align="C")
        pdf.cell(widths[6], 7, str(row.get('Recupero (min)', '')), border=1, align="C")
        pdf.ln()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf_path = tmp_pdf.name
        pdf.output(pdf_path)

    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="⬇️ Clicca qui per scaricare il PDF",
            data=pdf_file,
            file_name=f"cicli_allenamento_{mese_cicli}_{anno_cicli}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_pdf_file_sincro"
        )
    st.success("PDF generato con successo! Clicca sopra per scaricarlo.")
