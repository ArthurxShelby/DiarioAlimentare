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

# Inizializziamo lo stato con i dati esatti presenti nel documento PDF
if "df_cicli_allenamento_v2" not in st.session_state:
    st.session_state.df_cicli_allenamento_v2 = pd.DataFrame([
        {"Cicli": "1°", "Allenamento": "Soglia", "Tipo": "Soglia Avanzata", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Rilancio Aerobico", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "II°", "Allenamento": "Soglia", "Tipo": "Blocco Solido di Soglia", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Estensione Moderata", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "III°", "Allenamento": "Soglia", "Tipo": "Intervalli Lineari VO2Max", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Blocco di tenuta", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "IV°", "Allenamento": "Richiami Soglia", "Tipo": "Scarico", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        {"Cicli": "", "Allenamento": "Richiami Mantenimento", "Tipo": "Scarico", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
    ])

# Editor interattivo per la tabella identica al PDF
df_cicli_modificato = st.data_editor(
    st.session_state.df_cicli_allenamento_v2,
    num_rows="dynamic",
    use_container_width=True,
    key="editor_cicli_locali_v2",
    column_config={
        "Cicli": st.column_config.TextColumn("Cicli", required=False),
        "Allenamento": st.column_config.TextColumn("Allenamento", required=True),
        "Tipo": st.column_config.TextColumn("Tipo", required=True),
        "Serie": st.column_config.NumberColumn("Serie", min_value=0, max_value=50, step=1, format="%d"),
        "Ripetizioni": st.column_config.NumberColumn("Ripetizioni", min_value=0, max_value=100, step=1, format="%d"),
        "Watt": st.column_config.NumberColumn("Watt", min_value=0, max_value=1000, step=1, format="%d"),
        "Recupero": st.column_config.TextColumn("Recupero", required=False),
    },
)

# Sincronizzazione automatica dei dati inseriti/modificati
if not df_cicli_modificato.equals(st.session_state.df_cicli_allenamento_v2):
    st.session_state.df_cicli_allenamento_v2 = df_cicli_modificato.copy()
    st.rerun()

# --- BOTTONI DI AZIONE (PDF & CANCELLAZIONE) ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📥 Esporta Tabella in PDF"):
        import weasyprint
        import tempfile

        # Generazione HTML pulito per il documento PDF
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            @page { size: A4; margin: 15mm; background-color: #faf8f5; }
            body { font-family: Helvetica, Arial, sans-serif; color: #2d3748; margin: 0; padding: 0; }
            h1 { color: #1a365d; font-size: 18pt; border-bottom: 2px solid #cbd5e0; padding-bottom: 6px; margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            th { background-color: #2b6cb0; color: white; padding: 10px; font-size: 9pt; text-align: left; text-transform: uppercase; }
            td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-size: 9pt; }
            tr:nth-child(even) { background-color: #f7fafc; }
        </style>
        </head>
        <body>
            <h1>Programmazione Cicli di Allenamento</h1>
            <table>
                <tr>
                    <th>Cicli</th>
                    <th>Allenamento</th>
                    <th>Tipo</th>
                    <th>Serie</th>
                    <th>Ripetizioni</th>
                    <th>Watt</th>
                    <th>Recupero</th>
                </tr>
        """
        
        df_to_export = st.session_state.df_cicli_allenamento_v2
        for _, row in df_to_export.iterrows():
            c = row['Cicli'] if pd.notna(row['Cicli']) else ""
            a = row['Allenamento'] if pd.notna(row['Allenamento']) else ""
            t = row['Tipo'] if pd.notna(row['Tipo']) else ""
            s = int(row['Serie']) if pd.notna(row['Serie']) else ""
            r = int(row['Ripetizioni']) if pd.notna(row['Ripetizioni']) else ""
            w = int(row['Watt']) if pd.notna(row['Watt']) else ""
            rec = row['Recupero'] if pd.notna(row['Recupero']) else ""

            html_content += f"""
                <tr>
                    <td>{c}</td>
                    <td>{a}</td>
                    <td>{t}</td>
                    <td>{s}</td>
                    <td>{r}</td>
                    <td>{w}</td>
                    <td>{rec}</td>
                </tr>
            """
            
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
            tmp_html.write(html_content.encode("utf-8"))
            tmp_html_path = tmp_html.name

        pdf_path = tmp_html_path.replace(".html", ".pdf")
        weasyprint.HTML(tmp_html_path).write_pdf(pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Clicca qui per scaricare il PDF",
                data=pdf_file,
                file_name="cicli_allenamento.pdf",
                mime="application/pdf"
            )
        st.success("PDF generato con successo! Clicca sul pulsante sopra per scaricarlo.")

with col_btn2:
    if st.button("🗑️ Cancella Dati Inseriti"):
        # Ripristiniamo la tabella pulita iniziale con i campi numerici azzerati/vuoti
        st.session_state.df_cicli_allenamento_v2 = pd.DataFrame([
            {"Cicli": "1°", "Allenamento": "Soglia", "Tipo": "Soglia Avanzata", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Rilancio Aerobico", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "II°", "Allenamento": "Soglia", "Tipo": "Blocco Solido di Soglia", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Estensione Moderata", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "III°", "Allenamento": "Soglia", "Tipo": "Intervalli Lineari VO2Max", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "", "Allenamento": "Mantenimento", "Tipo": "Blocco di tenuta", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "IV°", "Allenamento": "Richiami Soglia", "Tipo": "Scarico", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
            {"Cicli": "", "Allenamento": "Richiami Mantenimento", "Tipo": "Scarico", "Serie": None, "Ripetizioni": None, "Watt": None, "Recupero": ""},
        ])
        st.toast("Dati cancellati e ripristinati allo stato iniziale!", icon="🗑️")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
