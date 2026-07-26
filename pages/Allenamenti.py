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
# Verifica se l'utente ha effettuato il login come proprietario nella pagina principale
is_proprietario = (st.session_state.get("ruolo_corrente") == "Proprietario")

if not is_proprietario:
    st.error("🚨 Accesso Negato: questa sezione è riservata esclusivamente al proprietario.")
    st.info("Torna alla pagina principale del Diario Alimentare ed effettua il login con le credenziali da amministratore.")
    st.stop()  # Interrompe l'esecuzione del resto della pagina per i non autorizzati

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
            # Ricostruisce i DataFrame dai dizionari salvati
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

# Cadenze dinamiche orientate al ciclismo moderno (cadenza di passista/scalatore)
cadenza_soglia = "~90 RPM"
cadenza_ss = "~85 RPM"

st.sidebar.markdown(f"### Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {ss_min}-{ss_max}W")
st.sidebar.markdown(f"**Soglia Z4:** {soglia_min}-{soglia_max}W")
st.sidebar.markdown(f"**Cadenza Soglia:** {cadenza_soglia}")
st.sidebar.markdown(f"**Cadenza SS:** {cadenza_ss}")

# --- 2. DATABASE INIZIALE STRUTTURATO ---
database_iniziale = {
    "2026": {
        "Gennaio": {
            "Settimana 1 (Base Invernale)": {
                "Martedì": {
                    "Esercizio": "Fondo Medio Z3: 3 x 15 min",
                    "Watt": 230,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 15,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 2 x 15 min",
                    "Watt": 245,
                    "RPM": 85,
                    "Ripetizioni": 2,
                    "Lavoro_m": 15,
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

# Inizializzazione della memoria persistente via Supabase
if "database_allenamenti" not in st.session_state:
    st.session_state.database_allenamenti = carica_database(database_iniziale)
    if is_proprietario:
        salva_database()
if "version_editor" not in st.session_state:
    st.session_state.version_editor = 0

# Inizializzazione contatore di versione per forzare il refresh visivo del data_editor
if "version_editor" not in st.session_state:
    st.session_state.version_editor = 0

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

# --- FORZATURA LETTURA DATI AGGIORNATI ---
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

# Assicuriamo che la sessione rifletta esattamente il dataframe pronto
st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_base_mese

dati_correnti = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]

# Assicura che sia sempre un DataFrame pronto all'uso
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

# --- 4. & 5. SEZIONE IMPORTAZIONE CSV E TABELLA INTERATTIVA ---
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
                else:
                    st.error(f"Il file CSV non contiene le colonne corrette: {colonne_attese}")
            except Exception as e:
                st.error(f"Errore nella lettura del file CSV: {e}")

dati_aggiornati = st.session_state.database_allenamenti[anno_selezionato][mese_selezionato]

if isinstance(dati_aggiornati, pd.DataFrame):
    df_da_mostrare = dati_aggiornati
elif isinstance(dati_aggiornati, list):
    df_da_mostrare = pd.DataFrame(dati_aggiornati)
else:
    df_da_mostrare = pd.DataFrame(
        columns=[
            "Settimana", "Giorno", "Esercizio / Nome", "Watt",
            "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)",
        ]
    )

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

    # Confronto approfondito che intercetta qualsiasi modifica o riga aggiunta al primo colpo
    if not df_modificato.equals(df_da_mostrare):
        st.session_state.database_allenamenti[anno_selezionato][mese_selezionato] = df_modificato.copy()
        salva_database()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
        

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. PANNELLO DI CANCELLAZIONE AVANZATO (Riservato) ---
if is_proprietario:
    with st.expander("🗑️ Pannello di Pulizia / Cancellazione Periodo (Avanzato)"):
        st.write("Seleziona un intervallo esatto basato su date specifiche per svuotare i dati.")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inizio_del = st.date_input("Data Inizio Periodo", value=datetime.date(2026, 1, 1), key="data_ini_del")
        with col_d2:
            data_fine_del = st.date_input("Data Fine Periodo", value=datetime.date(2026, 12, 31), key="data_fin_del")

        if st.button("🚨 Svuota dati per il periodo selezionato"):
            if data_inizio_del > data_fine_del:
                st.error("La data di inizio non può essere successiva alla data di fine.")
            else:
                try:
                    anno_inizio_del = data_inizio_del.year
                    anno_fine_del = data_fine_del.year
                    idx_m_ini = data_inizio_del.month - 1
                    idx_m_fin = data_fine_del.month - 1

                    for anno_target_num in range(anno_inizio_del, anno_fine_del + 1):
                        anno_target = str(anno_target_num)
                        if anno_target not in st.session_state.database_allenamenti:
                            continue

                        start_idx = idx_m_ini if anno_target_num == anno_inizio_del else 0
                        end_idx = idx_m_fin if anno_target_num == anno_fine_del else 11

                        mesi_da_pulire = elenco_mesi_completo[start_idx : end_idx + 1]

                        for m in mesi_da_pulire:
                            if m in st.session_state.database_allenamenti[anno_target]:
                                st.session_state.database_allenamenti[anno_target][m] = pd.DataFrame(
                                    columns=[
                                        "Settimana", "Giorno", "Esercizio / Nome", "Watt",
                                        "RPM", "Ripetizioni", "Lavoro (min)", "Recupero (min)",
                                    ]
                                )

                    salva_database()
                    st.session_state.version_editor += 1
                    st.toast("Dati svuotati e sincronizzati con successo!", icon="🗑️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante la pulizia: {e}")

# --- NUOVA TABELLA: CICLI ALLENAMENTI ---
st.subheader("📋 Programmazione Cicli di Allenamento")
st.write("Modifica o compila i dati direttamente nelle celle sottostanti.")

# Selezione del Macrociclo (Mese a tendina, Anno con tasti +/-)
col_macro1, col_macro2 = st.columns(2)
with col_macro1:
    mese_riferimento = st.selectbox(
        "Mese di Riferimento", 
        ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
        key="macro_mese"
    )
with col_macro2:
    anno_riferimento = st.number_input(
        "Anno di Riferimento", 
        min_value=2020, 
        max_value=2050, 
        value=2026, 
        step=1,
        key="macro_anno"
    )

st.markdown(f"**Macrociclo Attuale:** {mese_riferimento} {anno_riferimento}")

# Inizializziamo lo stato con stringhe vuote anziché None per evitare la scritta "None" nelle celle
if "df_cicli_allenamento_v2" not in st.session_state:
    st.session_state.df_cicli_allenamento_v2 = pd.DataFrame([
        {"Cicli": "1°", "Allenamento": "Soglia", "Tipo": "Soglia Avanzata", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Rilancio Aerobico", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "II°", "Allenamento": "Soglia", "Tipo": "Blocco Solido di Soglia", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Estensione Moderata", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "III°", "Allenamento": "Soglia", "Tipo": "Intervalli Lineari VO2Max", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Blocco di tenuta", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "IV°", "Allenamento": "Richiami Soglia", "Tipo": "Scarico", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        {"Cicli": "", "Allenamento": "Richiami Mantenimento", "Tipo": "Scarico", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
    ])

# Editor interattivo pulito
df_cicli_modificato = st.data_editor(
    st.session_state.df_cicli_allenamento_v2,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_cicli_locali_v3",
    column_config={
        "Cicli": st.column_config.TextColumn("Cicli", required=False),
        "Allenamento": st.column_config.TextColumn("Allenamento", required=True),
        "Tipo": st.column_config.TextColumn("Tipo", required=True),
        "Serie": st.column_config.TextColumn("Serie", required=False),
        "Ripetizioni": st.column_config.TextColumn("Ripetizioni", required=False),
        "Watt": st.column_config.TextColumn("Watt", required=False),
        "Recupero": st.column_config.TextColumn("Recupero", required=False),
    },
)

# Sincronizzazione automatica dei dati inseriti/modificati
if not df_cicli_modificato.equals(st.session_state.df_cicli_allenamento_v2):
    st.session_state.df_cicli_allenamento_v2 = df_cicli_modificato.copy()
    st.rerun()

# --- BOTTONI DI AZIONE (ESPORTAZIONE PDF & CANCELLAZIONE) ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📥 Esporta Tabella in PDF", use_container_width=True):
        from fpdf import FPDF
        import tempfile

        # Creazione del PDF con fpdf2
        pdf = FPDF()
        pdf.add_page()
        
        # Titolo e Macrociclo nel PDF
        pdf.set_font("Helvetica", "B", 15)
        pdf.cell(0, 8, "Programmazione Cicli di Allenamento", ln=True, align="L")
        
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, f"Macrociclo: {mese_riferimento} {int(anno_riferimento)}", ln=True, align="L")
        pdf.ln(4)

        # Intestazioni tabella
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(43, 108, 176) # Blu coordinato
        pdf.set_text_color(255, 255, 255)
        
        headers = ["Cicli", "Allenamento", "Tipo", "Serie", "Rip", "Watt", "Recupero"]
        widths = [20, 35, 55, 15, 18, 18, 30]
        
        for i, h in enumerate(headers):
            pdf.cell(widths[i], 8, h, border=1, fill=True, align="C")
        pdf.ln()

        # Dati della tabella
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        
        df_export = st.session_state.df_cicli_allenamento_v2.fillna("")
        for _, row in df_export.iterrows():
            pdf.cell(widths[0], 7, str(row['Cicli']), border=1, align="C")
            pdf.cell(widths[1], 7, str(row['Allenamento']), border=1, align="L")
            pdf.cell(widths[2], 7, str(row['Tipo']), border=1, align="L")
            pdf.cell(widths[3], 7, str(row['Serie']), border=1, align="C")
            pdf.cell(widths[4], 7, str(row['Ripetizioni']), border=1, align="C")
            pdf.cell(widths[5], 7, str(row['Watt']), border=1, align="C")
            pdf.cell(widths[6], 7, str(row['Recupero']), border=1, align="C")
            pdf.ln()

        # Salvataggio in un file temporaneo e download diretto
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf_path = tmp_pdf.name
            pdf.output(pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Clicca qui per scaricare il PDF",
                data=pdf_file,
                file_name=f"cicli_allenamento_{mese_riferimento}_{int(anno_riferimento)}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        st.success("PDF generato con successo! Clicca sopra per scaricarlo.")

with col_btn2:
    if st.button("🗑️ Cancella Dati Inseriti", use_container_width=True):
        st.session_state.df_cicli_allenamento_v2 = pd.DataFrame([
            {"Cicli": "1°", "Allenamento": "Soglia", "Tipo": "Soglia Avanzata", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Rilancio Aerobico", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "II°", "Allenamento": "Soglia", "Tipo": "Blocco Solido di Soglia", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Estensione Moderata", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "III°", "Allenamento": "Soglia", "Tipo": "Intervalli Lineari VO2Max", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Blocco di tenuta", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "IV°", "Allenamento": "Richiami Soglia", "Tipo": "Scarico", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
            {"Cicli": "", "Allenamento": "Richiami Mantenimento", "Tipo": "Scarico", "Serie": "", "Ripetizioni": "", "Watt": "", "Recupero": ""},
        ])
        st.toast("Dati cancellati e ripristinati allo stato iniziale!", icon="🗑️")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
