import datetime
import os
import pickle
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide"
)

# --- 0. GESTIONE PERSISTENZA DATI SU DISCO ---
DB_FILE = "database_allenamenti.pkl"


def salva_database():
    """Salva lo stato attuale degli allenamenti nel file locale."""
    try:
        with open(DB_FILE, "wb") as f:
            pickle.dump(st.session_state.database_allenamenti, f)
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati: {e}")


def carica_database(db_iniziale):
    """Carica il database dal file locale se esiste, altrimenti carica quello iniziale."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Errore nel caricamento dei dati salvati: {e}")
            return db_iniziale
    return db_iniziale


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

# --- 2. DATABASE INIZIALE STRUTTURATO ---
database_iniziale = {
    2026: {
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
                "Sabato": {
                    "Esercizio": "Fondo Lungo Z2",
                    "Watt": 210,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 120,
                    "Recupero_m": 0,
                },
            }
        },
    }
}

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

# Inizializzazione della memoria persistente
if "database_allenamenti" not in st.session_state:
    st.session_state.database_allenamenti = carica_database(database_iniziale)

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

# --- 3. SELEZIONE ANNO E MESE ---
col_anno, col_mese = st.columns(2)

with col_anno:
    anno_selezionato = st.number_input(
        "Anno Solare Corrente:", min_value=2020, max_value=2100, value=2026, step=1
    )

with col_mese:
    mese_selezionato = st.selectbox("Mese Corrente:", elenco_mesi_completo)

st.markdown("---")

# Assicuriamoci che l'anno e il mese esistano nello state
if anno_selezionato not in st.session_state.database_allenamenti:
    st.session_state.database_allenamenti[anno_selezionato] = {}

if (
    mese_selezionato
    not in st.session_state.database_allenamenti[anno_selezionato]
):
    st.session_state.database_allenamenti[anno_selezionato][
        mese_selezionato
    ] = pd.DataFrame(
        columns=[
            "Settimana",
            "Giorno",
            "Esercizio / Nome",
            "Watt",
            "RPM",
            "Ripetizioni",
            "Lavoro (min)",
            "Recupero (min)",
        ]
    )

# Recupera i dati correnti del mese/anno in memoria
dati_correnti = st.session_state.database_allenamenti[anno_selezionato][
    mese_selezionato
]

if isinstance(dati_correnti, dict):
    righe_tabella = []
    for settimana, giorni in dati_correnti.items():
        for giorno, dettagli in giorni.items():
            righe_tabella.append(
                {
                    "Settimana": settimana,
                    "Giorno": giorno,
                    "Esercizio / Nome": dettagli.get("Esercizio", ""),
                    "Watt": int(dettagli.get("Watt", 0)),
                    "RPM": int(dettagli.get("RPM", 0)),
                    "Ripetizioni": int(dettagli.get("Ripetizioni", 0)),
                    "Lavoro (min)": int(dettagli.get("Lavoro_m", 0)),
                    "Recupero (min)": int(dettagli.get("Recupero_m", 0)),
                }
            )
    df_base_mese = pd.DataFrame(righe_tabella)
    st.session_state.database_allenamenti[anno_selezionato][
        mese_selezionato
    ] = df_base_mese
    salva_database()
else:
    df_base_mese = dati_correnti

# --- 4. SEZIONE IMPORTAZIONE CSV ---
with st.expander(
    "📂 Integra o carica piano di lavoro tramite file CSV", expanded=False
):
    st.write(
        f"Stai caricando i dati per: **{mese_selezionato} {anno_selezionato}**."
    )
    file_caricato = st.file_uploader(
        "Seleziona il file CSV",
        type=["csv"],
        key=f"uploader_{anno_selezionato}_{mese_selezionato}",
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
                st.session_state.database_allenamenti[anno_selezionato][
                    mese_selezionato
                ] = df_caricato[colonne_attese]
                salva_database()  # Salvataggio immediato su file
                st.success(
                    f"File CSV caricato e salvato permanentemente per {mese_selezionato} {anno_selezionato}!"
                )
                st.rerun()
            else:
                st.error(
                    f"Il file CSV non contiene le colonne corrette: {colonne_attese}"
                )
        except Exception as e:
            st.error(f"Errore nella lettura del file CSV: {e}")

# --- 5. TABELLA INTERATTIVA DI MODIFICA ---
st.subheader(
    f"✍️ Gestione e Modifica Allenamenti: **{mese_selezionato} {anno_selezionato}**"
)

df_modificato = st.data_editor(
    df_base_mese,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_{anno_selezionato}_{mese_selezionato}",
    column_config={
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

# Salva lo stato modificato e aggiorna il file locale se ci sono variazioni
if not df_modificato.equals(df_base_mese):
    st.session_state.database_allenamenti[anno_selezionato][
        mese_selezionato
    ] = df_modificato
    salva_database()

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. PANNELLO DI CANCELLAZIONE AVANZATO ---
with st.expander("🗑️ Pannello di Pulizia / Cancellazione Periodo (Avanzato)"):
    st.write(
        "Seleziona un intervallo esatto (Mese e Anno) per svuotare i dati in quel periodo specifico."
    )

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        mese_inizio_del = st.selectbox(
            "Mese Inizio:", elenco_mesi_completo, key="m_ini"
        )
    with col_p2:
        anno_inizio_del = st.number_input(
            "Anno Inizio:",
            min_value=2020,
            max_value=2100,
            value=2026,
            step=1,
            key="a_ini",
        )
    with col_p3:
        mese_fine_del = st.selectbox(
            "Mese Fine:", elenco_mesi_completo, index=11, key="m_fin"
        )
    with col_p4:
        anno_fine_del = st.number_input(
            "Anno Fine:",
            min_value=2020,
            max_value=2100,
            value=2026,
            step=1,
            key="a_fin",
        )

    if st.button("🚨 Svuota dati per il periodo selezionato"):
        idx_m_ini = elenco_mesi_completo.index(mese_inizio_del)
        idx_m_fin = elenco_mesi_completo.index(mese_fine_del)

        if anno_inizio_del > anno_fine_del or (
            anno_inizio_del == anno_fine_del and idx_m_ini > idx_m_fin
        ):
            st.error(
                "Il periodo di inizio deve precedere o coincidere con il periodo di fine."
            )
        else:
            try:
                for anno_target in range(anno_inizio_del, anno_fine_del + 1):
                    if anno_target not in st.session_state.database_allenamenti:
                        continue

                    start_idx = (
                        idx_m_ini if anno_target == anno_inizio_del else 0
                    )
                    end_idx = idx_m_fin if anno_target == anno_fine_del else 11

                    mesi_da_pulire = elenco_mesi_completo[
                        start_idx : end_idx + 1
                    ]

                    for m in mesi_da_pulire:
                        if (
                            m
                            in st.session_state.database_allenamenti[
                                anno_target
                            ]
                        ):
                            st.session_state.database_allenamenti[anno_target][
                                m
                            ] = pd.DataFrame(
                                columns=[
                                    "Settimana",
                                    "Giorno",
                                    "Esercizio / Nome",
                                    "Watt",
                                    "RPM",
                                    "Ripetizioni",
                                    "Lavoro (min)",
                                    "Recupero (min)",
                                ]
                            )

                salva_database()  # Salvataggio delle modifiche di cancellazione
                st.success(
                    f"Dati svuotati e salvati con successo da {mese_inizio_del} {anno_inizio_del} a {mese_fine_del} {anno_fine_del}!"
                )
                st.rerun()
            except Exception as e:
                st.error(f"Errore durante la pulizia: {e}")
