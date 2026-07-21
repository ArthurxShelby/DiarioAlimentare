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
            "Settimana 2 (Carico Intermedio)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 3 x 6 min. Rec. 5 min Z1",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 6,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 1 x 30 min continui",
                    "Watt": 245,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 30,
                    "Recupero_m": 0,
                },
            },
            "Settimana 3 (Picco di Carico)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 4 x 6 min. Rec. 4 min Z1",
                    "Watt": 262,
                    "RPM": 90,
                    "Ripetizioni": 4,
                    "Lavoro_m": 6,
                    "Recupero_m": 4,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 1 x 40 min continui",
                    "Watt": 248,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 40,
                    "Recupero_m": 0,
                },
            },
            "Settimana 4 (Scarico)": {
                "Martedì": {
                    "Esercizio": "Soglia attiva: Solo 1 x 6 min in Z4",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 1,
                    "Lavoro_m": 6,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS",
                    "Watt": 150,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 15,
                    "Recupero_m": 0,
                },
            },
        },
        "Settembre": {
            "Settimana 1 (Carico Base)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 5 min Z1",
                    "Watt": 265,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 8,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 2 x 15 min. Rec. 5 min Z1",
                    "Watt": 250,
                    "RPM": 85,
                    "Ripetizioni": 2,
                    "Lavoro_m": 15,
                    "Recupero_m": 5,
                },
            },
            "Settimana 2 (Carico Intermedio)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 3 x 10 min. Rec. 5 min Z1",
                    "Watt": 265,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 10,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 5 min Z1",
                    "Watt": 250,
                    "RPM": 85,
                    "Ripetizioni": 2,
                    "Lavoro_m": 20,
                    "Recupero_m": 5,
                },
            },
            "Settimana 3 (Picco di Carico)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1",
                    "Watt": 268,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 12,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 1 x 45 min continui",
                    "Watt": 252,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 45,
                    "Recupero_m": 0,
                },
            },
            "Settimana 4 (Scarico)": {
                "Martedì": {
                    "Esercizio": "Mantenimento: 2 x 5 min Z4. Rec. 4 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 5,
                    "Recupero_m": 4,
                },
                "Giovedì": {
                    "Esercizio": "Scarico: Recupero Attivo Z1 ed agilità",
                    "Watt": 145,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
            },
        },
        "Ottobre": {
            "Settimana 1 (Carico Base)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 2 x 15 min. Rec. 6 min Z1",
                    "Watt": 270,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 15,
                    "Recupero_m": 6,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 2 x 25 min. Rec. 5 min Z1",
                    "Watt": 254,
                    "RPM": 85,
                    "Ripetizioni": 2,
                    "Lavoro_m": 25,
                    "Recupero_m": 5,
                },
            },
            "Settimana 2 (Carico Intermedio)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1",
                    "Watt": 272,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 12,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 1 x 50 min continui in salita",
                    "Watt": 254,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 50,
                    "Recupero_m": 0,
                },
            },
            "Settimana 3 (Picco di Carico)": {
                "Martedì": {
                    "Esercizio": "Soglia Z4: 2 x 20 min (Massima Densità)",
                    "Watt": 279,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 20,
                    "Recupero_m": 6,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: Salita costante di 55 min",
                    "Watt": 256,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 55,
                    "Recupero_m": 0,
                },
            },
            "Settimana 4 (Scarico)": {
                "Martedì": {
                    "Esercizio": "Scarico: 1 x 10 min Z4 rilassato",
                    "Watt": 265,
                    "RPM": 90,
                    "Ripetizioni": 1,
                    "Lavoro_m": 10,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Agilità di scarico senza spingere",
                    "Watt": 150,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
            },
        },
        "Novembre": {
            "Settimana 1 (Carico Base)": {
                "Martedì": {
                    "Esercizio": "Dinamica Over-Under: 3x (1' Over / 1' Under)",
                    "Watt": 275,
                    "RPM": 92,
                    "Ripetizioni": 3,
                    "Lavoro_m": 2,
                    "Recupero_m": 2,
                },
                "Giovedì": {
                    "Esercizio": "Mantenimento SS: 2 x 20 min",
                    "Watt": 252,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 20,
                    "Recupero_m": 5,
                },
            },
            "Settimana 2 (Carico Intermedio)": {
                "Martedì": {
                    "Esercizio": "Dinamica Over-Under: 4x (1' Over / 1' Under)",
                    "Watt": 275,
                    "RPM": 92,
                    "Ripetizioni": 4,
                    "Lavoro_m": 2,
                    "Recupero_m": 2,
                },
                "Giovedì": {
                    "Esercizio": "Mantenimento SS: 1 x 45 min costanti",
                    "Watt": 252,
                    "RPM": 90,
                    "Ripetizioni": 1,
                    "Lavoro_m": 45,
                    "Recupero_m": 0,
                },
            },
            "Settimana 3 (Picco di Carico)": {
                "Martedì": {
                    "Esercizio": "Dinamica Over-Under: Picco intensità variata",
                    "Watt": 280,
                    "RPM": 92,
                    "Ripetizioni": 5,
                    "Lavoro_m": 2,
                    "Recupero_m": 2,
                },
                "Giovedì": {
                    "Esercizio": "SS Esteso ad alta frequenza: 1 x 50 min",
                    "Watt": 255,
                    "RPM": 90,
                    "Ripetizioni": 1,
                    "Lavoro_m": 50,
                    "Recupero_m": 0,
                },
            },
            "Settimana 4 (Scarico)": {
                "Martedì": {
                    "Esercizio": "Assimilazione: Lavoro agile in Z2 lineare",
                    "Watt": 170,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Scarico Muscolare Totale",
                    "Watt": 140,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 15,
                    "Recupero_m": 0,
                },
            },
        },
        "Dicembre": {
            "Settimana 1 (Carico Base)": {
                "Martedì": {
                    "Esercizio": "Efficienza Soglia: 3 x 12 min. Rec. 4 min Z1",
                    "Watt": 278,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 12,
                    "Recupero_m": 4,
                },
                "Giovedì": {
                    "Esercizio": "Massimo Stimolo SS: 1 x 45 min",
                    "Watt": 255,
                    "RPM": 86,
                    "Ripetizioni": 1,
                    "Lavoro_m": 45,
                    "Recupero_m": 0,
                },
            },
            "Settimana 2 (Carico Intermedio)": {
                "Martedì": {
                    "Esercizio": "Efficienza Soglia: 3 x 15 min a 280W",
                    "Watt": 280,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 15,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Massimo Stimolo SS: 2 x 25 min",
                    "Watt": 256,
                    "RPM": 86,
                    "Ripetizioni": 2,
                    "Lavoro_m": 25,
                    "Recupero_m": 5,
                },
            },
            "Settimana 3 (Picco di Carico)": {
                "Martedì": {
                    "Esercizio": "Efficienza Soglia: 2 x 25 min Z4 massimali",
                    "Watt": 282,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 25,
                    "Recupero_m": 6,
                },
                "Giovedì": {
                    "Esercizio": "Efficienza SS Estrema: 1 x 60 min continui",
                    "Watt": 258,
                    "RPM": 86,
                    "Ripetizioni": 1,
                    "Lavoro_m": 60,
                    "Recupero_m": 0,
                },
            },
            "Settimana 4 (Scarico)": {
                "Martedì": {
                    "Esercizio": "Ripristino energetico e agilità controllata",
                    "Watt": 160,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Fine ciclo: Pedalata libera Z1",
                    "Watt": 140,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 15,
                    "Recupero_m": 0,
                },
            },
        },
    }
}

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

# --- 3. SELEZIONE ANNO E MESE ---
col_anno, col_mese = st.columns(2)
with col_anno:
    anno_selezionato = st.selectbox(
        "Anno Solare:", list(database_allenamenti.keys())
    )
with col_mese:
    mesi_disponibili = list(database_allenamenti[anno_selezionato].keys())
    mese_selezionato = st.selectbox("Mese:", mesi_disponibili)

st.markdown("---")

# --- 4. GESTIONE STATO / CARICAMENTO CSV ---
# Inizializziamo lo stato della sessione per mantenere le modifiche o l'importazione CSV
key_stato_db = f"db_{anno_selezionato}_{mese_selezionato}"

# Creazione del DataFrame di partenza per il mese selezionato
righe_tabella = []
for settimana, giorni in database_allenamenti[anno_selezionato][
    mese_selezionato
].items():
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

df_base_mese = pd.DataFrame(righe_tabella)

# --- 5. SEZIONE IMPORTAZIONE CSV ---
with st.expander(
    "📂 Integra o carica piano di lavoro tramite file CSV", expanded=False
):
    st.write(
        "Carica un file CSV formattato con le stesse colonne della tabella sottostante per aggiornare o sostituire istantaneamente i 8 allenamenti del mese."
    )
    file_caricato = st.file_uploader(
        "Seleziona il file CSV", type=["csv"], key=f"uploader_{key_stato_db}"
    )

    if file_caricato is not None:
        try:
            # Modificato con sep=None e engine='python' per gestire automaticamente virgole o punti e virgola
            df_caricato = pd.read_csv(
                file_caricato, sep=None, engine="python"
            )

            # Pulizia preventiva degli spazi nei nomi delle colonne (es. eventuali spazi accidentali)
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
                    "File CSV caricato e integrato con successo nella tabella sottostante!"
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
    "Puoi modificare direttamente i valori in tabella o incollare i dati aggiornati."
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
