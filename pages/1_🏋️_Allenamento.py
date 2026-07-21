import pandas as pd
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

# --- 2. DATABASE STRUTTURATO PER ANNO SOLARE (2026 COMPLETO) ---
database_allenamenti = {
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
        "Febbraio": {
            "Settimana 1 (Forza e Incremento)": {
                "Martedì": {
                    "Esercizio": "Forza Frullata RPM Bassa: 4 x 4 min",
                    "Watt": 250,
                    "RPM": 65,
                    "Ripetizioni": 4,
                    "Lavoro_m": 4,
                    "Recupero_m": 3,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 2 x 10 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 10,
                    "Recupero_m": 5,
                },
            }
        },
        "Marzo": {
            "Settimana 1 (Sviluppo Potenza)": {
                "Martedì": {
                    "Esercizio": "VO2Max: 5 x 3 min",
                    "Watt": 290,
                    "RPM": 100,
                    "Ripetizioni": 5,
                    "Lavoro_m": 3,
                    "Recupero_m": 3,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 4 x 6 min",
                    "Watt": 265,
                    "RPM": 90,
                    "Ripetizioni": 4,
                    "Lavoro_m": 6,
                    "Recupero_m": 4,
                },
            }
        },
        "Aprile": {
            "Settimana 1 (Fase Agonistica Base)": {
                "Martedì": {
                    "Esercizio": "Over-Under: 3 x (2m @ 280W + 2m @ 230W)",
                    "Watt": 255,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 12,
                    "Recupero_m": 4,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 2 x 20 min",
                    "Watt": 245,
                    "RPM": 88,
                    "Ripetizioni": 2,
                    "Lavoro_m": 20,
                    "Recupero_m": 5,
                },
            }
        },
        "Maggio": {
            "Settimana 1 (Intensità)": {
                "Martedì": {
                    "Esercizio": "VO2Max Breve: 6 x 2 min",
                    "Watt": 300,
                    "RPM": 105,
                    "Ripetizioni": 6,
                    "Lavoro_m": 2,
                    "Recupero_m": 2,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 3 x 10 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 10,
                    "Recupero_m": 4,
                },
            }
        },
        "Giugno": {
            "Settimana 1 (Picco Estivo)": {
                "Martedì": {
                    "Esercizio": "Test FTP 20 min",
                    "Watt": 275,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Fartlek Collinare: 4 x 3 min",
                    "Watt": 270,
                    "RPM": 95,
                    "Ripetizioni": 4,
                    "Lavoro_m": 3,
                    "Recupero_m": 3,
                },
            }
        },
        "Luglio": {
            "Settimana 1 (Mantenimento)": {
                "Martedì": {
                    "Esercizio": "Sweet Spot: 1 x 30 min continui",
                    "Watt": 245,
                    "RPM": 85,
                    "Ripetizioni": 1,
                    "Lavoro_m": 30,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 2 x 12 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 12,
                    "Recupero_m": 5,
                },
            }
        },
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
                "Sabato": {
                    "Esercizio": "Fartlek Collinare: 4 x 3 min",
                    "Watt": 270,
                    "RPM": 95,
                    "Ripetizioni": 4,
                    "Lavoro_m": 3,
                    "Recupero_m": 3,
                },
            },
            "Settimana 2 (Sviluppo)": {
                "Martedì": {
                    "Esercizio": "VO2Max: 4 x 3 min. Rec. 3 min",
                    "Watt": 290,
                    "RPM": 100,
                    "Ripetizioni": 4,
                    "Lavoro_m": 3,
                    "Recupero_m": 3,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 4 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 8,
                    "Recupero_m": 4,
                },
            },
        },
        "Settembre": {
            "Settimana 1 (Ripresa)": {
                "Martedì": {
                    "Esercizio": "Test FTP 20 min",
                    "Watt": 275,
                    "RPM": 95,
                    "Ripetizioni": 1,
                    "Lavoro_m": 20,
                    "Recupero_m": 0,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 2 x 15 min",
                    "Watt": 245,
                    "RPM": 88,
                    "Ripetizioni": 2,
                    "Lavoro_m": 15,
                    "Recupero_m": 5,
                },
            }
        },
        "Ottobre": {
            "Settimana 1 (Transizione)": {
                "Martedì": {
                    "Esercizio": "Forza Frullata RPM Bassa: 5 x 3 min",
                    "Watt": 250,
                    "RPM": 65,
                    "Ripetizioni": 5,
                    "Lavoro_m": 3,
                    "Recupero_m": 3,
                },
                "Giovedì": {
                    "Esercizio": "Sweet Spot: 3 x 12 min",
                    "Watt": 245,
                    "RPM": 88,
                    "Ripetizioni": 3,
                    "Lavoro_m": 12,
                    "Recupero_m": 4,
                },
            }
        },
        "Novembre": {
            "Settimana 1 (Base Invernale)": {
                "Martedì": {
                    "Esercizio": "Cadenza Variazioni: 4 x 5 min",
                    "Watt": 250,
                    "RPM": 100,
                    "Ripetizioni": 4,
                    "Lavoro_m": 5,
                    "Recupero_m": 3,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 2 x 12 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 2,
                    "Lavoro_m": 12,
                    "Recupero_m": 5,
                },
            }
        },
        "Dicembre": {
            "Settimana 1 (Rifinitura Anno)": {
                "Martedì": {
                    "Esercizio": "Sweet Spot: 3 x 15 min",
                    "Watt": 245,
                    "RPM": 88,
                    "Ripetizioni": 3,
                    "Lavoro_m": 15,
                    "Recupero_m": 5,
                },
                "Giovedì": {
                    "Esercizio": "Soglia Z4: 3 x 10 min",
                    "Watt": 260,
                    "RPM": 90,
                    "Ripetizioni": 3,
                    "Lavoro_m": 10,
                    "Recupero_m": 4,
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

st.title("🏋️ Pianificazione Allenamento per Anno Solare")

# --- 3. SELEZIONE ANNO E MESE ---
col_anno, col_mese = st.columns(2)

with col_anno:
    anno_selezionato = st.number_input(
        "Anno Solare:", min_value=2020, max_value=2100, value=2026, step=1
    )

with col_mese:
    mese_selezionato = st.selectbox("Mese:", elenco_mesi_completo)

st.markdown("---")

# --- 4. GESTIONE STATO / CARICAMENTO CSV ---
key_stato_db = f"db_{anno_selezionato}_{mese_selezionato}"

if anno_selezionato not in database_allenamenti:
    database_allenamenti[anno_selezionato] = {}

if mese_selezionato not in database_allenamenti[anno_selezionato]:
    database_allenamenti[anno_selezionato][mese_selezionato] = {}

righe_tabella = []

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
        f"Stai caricando i dati per: **{mese_selezionato} {anno_selezionato}**."
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
                    f"File CSV caricato con successo per {mese_selezionato} {anno_selezionato}!"
                )
            else:
                st.error(
                    f"Il file CSV non contiene le colonne corrette: {colonne_attese}"
                )
        except Exception as e:
            st.error(f"Errore nella lettura del file CSV: {e}")

# --- 6. TABELLA INTERATTIVA DI MODIFICA ---
st.subheader(
    f"✍️ Gestione e Modifica Allenamenti: **{mese_selezionato} {anno_selezionato}**"
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
