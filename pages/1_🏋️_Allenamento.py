import datetime
from requests.auth import HTTPBasicAuth
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide"
)

# --- 1. RIFERIMENTI FTP & SIDEBAR ---
ftp_atleta = 279

st.sidebar.markdown(f"## Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(
    f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W"
)
st.sidebar.markdown(
    f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W"
)
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM")
st.sidebar.markdown("**Cadenza SS:** ~85 RPM")

# --- 2. DATABASE STRUTTURATO PER ANNO SOLARE ---
database_allenamenti = {
    2026: {
        "Agosto": {
            "Settimana 1 (Carico Base)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 2 x 6 min. Rec. 5 min Z1",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 6,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 1 x 20 min continui",
                    "Watt": 245,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
            },
        }
    }
}

# Lista completa dei 12 mesi dell'anno per garantire la selezione universale
elenco_mesi_completo = [
    "Gennaio",
    "Febbraio",
    "Marzo",
    "Aprile",
    "Maggio",
    "Giugno",
    "Luglio",
    "Agosto",
    "Settembre",
    "Ottobre",
    "Novembre",
    "Dicembre",
]

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

# --- 3. SELEZIONE ANNO (LIBERO FINO AL 2100) E MESE ---
col_anno, col_mese = st.columns(2)

with col_anno:
    # Selezione dinamica e libera dell'anno da tastiera o frecce (da 2020 a 2100)
    anno_selezionato = st.number_input(
        "Anno Solare:", min_value=2020, max_value=2100, value=2026, step=1
    )

with col_mese:
    mese_selezionato = st.selectbox("Mese:", elenco_mesi_completo)

st.markdown("---")

# --- 4. GESTIONE STATO / CARICAMENTO CSV ---
key_stato_db = f"db_{anno_selezionato}_{mese_selezionato}"

# Assicura che l'anno e il mese selezionati esistano nel dizionario del database
if anno_selezionato not in database_allenamenti:
    database_allenamenti[anno_selezionato] = {}

if mese_selezionato not in database_allenamenti[anno_selezionato]:
    database_allenamenti[anno_selezionato][mese_selezionato] = {}

righe_tabella = []

# Controlla se ci sono allenamenti registrati per il periodo
try:
    dati_periodo = database_allenamenti[anno_selezionato][mese_selezionato]
    if dati_periodo:
        for settimana, giorni in dati_periodo.items():
            for giorno, dettagli in giorni.items():
                righe_tabella.append(
                    {
                        "Settimana": settimana,
                        "Giorno": giorno,
                        "Esercizio / Nome": dettagli["Esercizio"],
                        "Watt": int(dettagli["Watt"]),
                        "RPM": int(dettagli["RPM"]),
                        "Ripetizioni": int(dettagli["Ripetizioni"]),
                        "Lavoro (min)": int(dettagli["Lavoro_m"]),
                        "Recupero (min)": int(dettagli["Recupero_m"]),
                    }
                )
    else:
        raise KeyError
except (KeyError, TypeError):
    # Se il mese è vuoto, genera una riga di default pronta per la compilazione o l'upload CSV
    righe_tabella = [
        {
            "Settimana": "Settimana 1 (Carico Base)",
            "Giorno": "Martedì",
            "Esercizio / Nome": "Inserisci esercizio o carica CSV",
            "Watt": int(ftp_atleta * 0.9),
            "RPM": 90,
            "Ripetizioni": 1,
            "Lavoro (min)": 10,
            "Recupero (min)": 5,
        }
    ]

df_base_mese = pd.DataFrame(righe_tabella)

# --- 5. SEZIONE IMPORTAZIONE CSV ---
with st.expander(
    "📂 Integra o carica piano di lavoro tramite file CSV", expanded=False
):
    st.write(
        f"Stai caricando i dati per: **{mese_selezionato} {anno_selezionato}**. Carica il file CSV formattato con le colonne corrette."
    )
    file_caricato = st.file_uploader(
        "Seleziona il file CSV", type=["csv"], key=f"uploader_{key_stato_db}"
    )

    if file_caricato is not None:
        try:
            df_caricato = pd.read_csv(file_caricato, sep=None, engine="python")
            df_caricato.columns = df_caricato.columns.str.strip()

            colonne_attese = [
                "Settimana",
                "Giorno",
                "Esercizio / Nome",
                "Watt",
                "RPM",
                "Ripetizioni",
                "Lavoro (min)",
                "Recupero (min)",
            ]

            if all(col in df_caricato.columns for col in colonne_attese):
                df_base_mese = df_caricato[colonne_attese]
                st.success(
                    f"File CSV caricato e integrato con successo per {mese_selezionato} {anno_selezionato}!"
                )
            else:
                st.error(
                    f"Il file CSV non contiene le colonne corrette. Assicurati che siano presenti: {colonne_attese}"
                )
        except Exception as e:
            st.error(f"Errore nella lettura del file CSV: {e}")

# --- 6. TABELLA INTERATTIVA DI MODIFICA ---
st.subheader(
    f"✍️ Gestione e Modifica Allenamenti: **{mese_selezionato} {anno_selezionato}**"
)
st.write(
    "Puoi modificare direttamente i valori in tabella o caricarli tramite il file CSV sopra."
)

df_modificato = st.data_editor(
    df_base_mese,
    num_rows="fixed",
    use_container_width=True,
    key=f"editor_{key_stato_db}",
    column_config={
        "Settimana": st.column_config.TextColumn(disabled=True),
        "Giorno": st.column_config.TextColumn(disabled=True),
        "Watt": st.column_config.NumberColumn(min_value=50, max_value=500, step=1),
        "RPM": st.column_config.NumberColumn(min_value=60, max_value=120, step=1),
        "Ripetizioni": st.column_config.NumberColumn(
            min_value=1, max_value=20, step=1
        ),
        "Lavoro (min)": st.column_config.NumberColumn(
            min_value=1, max_value=180, step=1
        ),
        "Recupero (min)": st.column_config.NumberColumn(
            min_value=0, max_value=60, step=1
        ),
    },
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. STRUMENTO DI PULIZIA DI EMERGENZA ---
with st.expander("🛠️ Pannello di Emergenza: Cancella file dal calendario"):
    st.write(
        "Se qualche allenamento risulta bloccato o vuoi ripulire i test, seleziona il periodo e premi il pulsante."
    )

    col_start, col_end = st.columns(2)
    with col_start:
        data_inizio_pulizia = st.date_input(
            "Data Inizio:", datetime.date.today() - datetime.timedelta(days=7)
        )
    with col_end:
        data_fine_pulizia = st.date_input(
            "Data Fine:", datetime.date.today() + datetime.timedelta(days=30)
        )

    if st.button(
        "🗑️ Elimina tutti gli allenamenti (🏋️) nel periodo selezionato"
    ):
        if "intervals" not in st.secrets:
            st.error("⚠️ Configura prima le credenziali!")
        else:
            try:
                atleta_id = st.secrets["intervals"]["athlete_id"]
                api_key = st.secrets["intervals"]["api_key"]
                auth = HTTPBasicAuth("API_KEY", api_key)

                url_get = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events?oldest={data_inizio_pulizia.isoformat()}&newest={data_fine_pulizia.isoformat()}"
                response = requests.get(url_get, auth=auth)

                if response.status_code == 200:
                    eventi = response.json()
                    count = 0
                    for evento in eventi:
                        if "🏋️" in evento.get("name", ""):
                            event_id = evento["id"]
                            url_del = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events/{event_id}"
                            requests.delete(url_del, auth=auth)
                            count += 1
                    st.success(
                        f"Pulizia completata! Eliminati {count} eventi di prova dal calendario."
                    )
                    st.rerun()
                else:
                    st.error(
                        f"Errore nel recupero eventi: {response.text}"
                    )
            except Exception as e:
                st.error(f"Errore: {e}")
