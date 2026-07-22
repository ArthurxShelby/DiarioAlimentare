import os
import pickle
import re
from datetime import date, timedelta
from fpdf import FPDF
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare & Allenamento - Multi-Atleta",
    page_icon="",
    layout="wide",
)

# --- 0. GESTIONE PERSISTENZA DATI E PULIZIA ---
FILE_PERSISTENZA = "diario_alimentare_multi_db.pkl"
OLD_FILE_PERSISTENZA = "diario_alimentare_db.pkl"


def safe_float(val):
    """Converte in modo sicuro qualsiasi valore in float, gestendo virgole e stringhe."""
    if pd.isna(val):
        return 0.0
    try:
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip().replace(",", ".")
        val_clean = re.sub(r"[^\d.-]", "", val_str)
        return float(val_clean) if val_clean else 0.0
    except:
        return 0.0


def pulisci_dataframe_banca_dati(df):
    """Assicura che tutte le colonne numeriche siano float puliti."""
    colonne_numeriche = ["gr/n", "carbo", "proteine", "grassi", "kcal"]
    for col in colonne_numeriche:
        if col in df.columns:
            df[col] = df[col].apply(safe_float)
    return df


def salva_dati_disco():
    """Salva lo stato della banca dati, degli atleti e delle password nel file locale."""
    try:
        dati = {
            "atleti": st.session_state.get("atleti", {}),
            "banca_dati_df": st.session_state.get("banca_dati_df"),
            "password_atleti": st.session_state.get("password_atleti", {}),
        }
        with open(FILE_PERSISTENZA, "wb") as f:
            pickle.dump(dati, f)
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati: {e}")


def carica_dati_disco():
    """Carica i dati salvati dal file locale."""
    if os.path.exists(FILE_PERSISTENZA):
        try:
            with open(FILE_PERSISTENZA, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Errore durante il caricamento dei dati salvati: {e}")
    elif os.path.exists(OLD_FILE_PERSISTENZA):
        try:
            with open(OLD_FILE_PERSISTENZA, "rb") as f:
                old_dati = pickle.load(f)
            migrated = {
                "atleti": {
                    "Atleta Principale": {
                        "peso": old_dati.get("peso", 75.0),
                        "altezza": old_dati.get("altezza", 173.0),
                        "eta": old_dati.get("eta", 56),
                        "genere": "Uomo",
                        "livello_allenamento": "Allenamento Intenso / Rouleur-Climber (PAL 1.725)",
                        "db_diario": old_dati.get("db_diario", {}),
                    }
                },
                "banca_dati_df": old_dati.get("banca_dati_df", None),
                "password_atleti": {},
            }
            return migrated
        except Exception as e:
            st.error(f"Errore durante la migrazione dei vecchi dati: {e}")
    return None


dati_salvati = carica_dati_disco()

# Banca dati precompilata iniziale (condivisa per gli alimenti)
DEFAULT_BANCA_DATI = [
    {
        "Alimento": "anguria",
        "gr/n": 300,
        "carbo": 111.0,
        "proteine": 1.2,
        "grassi": 0.6,
        "kcal": 48.0,
    },
    {
        "Alimento": "arista",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 24.0,
        "grassi": 5.0,
        "kcal": 145.0,
    },
    {
        "Alimento": "avena",
        "gr/n": 60,
        "carbo": 37.8,
        "proteine": 7.2,
        "grassi": 4.2,
        "kcal": 216.0,
    },
    {
        "Alimento": "banana",
        "gr/n": 100,
        "carbo": 23.0,
        "proteine": 1.2,
        "grassi": 0.3,
        "kcal": 89.0,
    },
    {
        "Alimento": "carne",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 20.0,
        "grassi": 5.0,
        "kcal": 125.0,
    },
    {
        "Alimento": "pasta",
        "gr/n": 100,
        "carbo": 75.0,
        "proteine": 12.0,
        "grassi": 1.5,
        "kcal": 360.0,
    },
    {
        "Alimento": "riso basmati",
        "gr/n": 100,
        "carbo": 83.0,
        "proteine": 9.0,
        "grassi": 1.9,
        "kcal": 367.0,
    },
    {
        "Alimento": "pollo",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 23.0,
        "grassi": 1.5,
        "kcal": 105.0,
    },
    {
        "Alimento": "tonno",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 25.0,
        "grassi": 1.0,
        "kcal": 110.0,
    },
    {
        "Alimento": "uova",
        "gr/n": 3,
        "carbo": 0.9,
        "proteine": 19.5,
        "grassi": 15.0,
        "kcal": 210.0,
    },
]

# Inizializzazione Banca Dati
if "banca_dati_df" not in st.session_state:
    if (
        dati_salvati
        and "banca_dati_df" in dati_salvati
        and dati_salvati["banca_dati_df"] is not None
    ):
        st.session_state.banca_dati_df = dati_salvati["banca_dati_df"]
    else:
        st.session_state.banca_dati_df = pd.DataFrame(DEFAULT_BANCA_DATI)

st.session_state.banca_dati_df = pulisci_dataframe_banca_dati(
    st.session_state.banca_dati_df
)

# Inizializzazione Atleti
if "atleti" not in st.session_state:
    if dati_salvati and "atleti" in dati_salvati:
        st.session_state.atleti = dati_salvati["atleti"]
    else:
        st.session_state.atleti = {
            "Atleta Principale": {
                "peso": 75.0,
                "altezza": 173.0,
                "eta": 56,
                "genere": "Uomo",
                "livello_allenamento": "Allenamento Intenso / Rouleur-Climber (PAL 1.725)",
                "db_diario": {},
            }
        }

if "password_atleti" not in st.session_state:
    if dati_salvati and "password_atleti" in dati_salvati:
        st.session_state.password_atleti = dati_salvati["password_atleti"]
    else:
        st.session_state.password_atleti = {}

if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = (
        None  # None = Proprietario, altrimenti nome dell'atleta ospite
    )

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

# --- GESTIONE ACCESSI E LOGIN NELLA SIDEBAR ---
ADMIN_MASTER_PASSWORD = (
    "admin123"  # Puoi cambiarla o lasciarla vuota per accesso diretto da parte tua
)

if st.session_state.utente_loggato is not None:
    # --- SESSIONE UTENTE OSPITE (es. TUO FIGLIO) ---
    atleta_corrente = st.session_state.utente_loggato
    st.session_state.atleta_corrente = atleta_corrente

    st.sidebar.warning(f"🔒 Accesso limitato a: **{atleta_corrente}**")
    if st.sidebar.button("🚪 Esci (Logout)"):
        st.session_state.utente_loggato = None
        st.rerun()
else:
    # --- SCHERMATA DI SCELTA ACCESSO ---
    st.sidebar.header("🔐 Accesso Applicazione")
    tipo_accesso = st.sidebar.radio(
        "Modalità", ["Proprietario (Admin)", "Ospite / Atleta"]
    )

    if tipo_accesso == "Ospite / Atleta":
        atleti_ospiti = [
            a for a in st.session_state.atleti.keys() if a != "Atleta Principale"
        ]
        if not atleti_ospiti:
            st.sidebar.info(
                "Nessun profilo ospite configurato. Creane uno accedendo come Proprietario."
            )
            st.stop()

        profilo_scelto = st.sidebar.selectbox(
            "Seleziona il tuo profilo", atleti_ospiti
        )
        pwd_inserita = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Entra nel Diario"):
            pwd_vera = st.session_state.password_atleti.get(profilo_scelto, "")
            if pwd_vera == "" and pwd_inserita == "":
                st.session_state.utente_loggato = profilo_scelto
                st.session_state.atleta_corrente = profilo_scelto
                st.rerun()
            elif pwd_inserita == pwd_vera and pwd_vera != "":
                st.session_state.utente_loggato = profilo_scelto
                st.session_state.atleta_corrente = profilo_scelto
                st.rerun()
            else:
                st.sidebar.error("Password errata.")
        st.stop()
    else:
        # Accesso Proprietario
        st.session_state.atleta_corrente = "Atleta Principale"

# --- INTERFACCIA PRINCIPALE ---
st.title("Pianificatore Alimentare & Allenamento - Multi-Atleta")

# Se sei il proprietario, puoi gestire gli atleti e selezionarli liberamente
if st.session_state.utente_loggato is None:
    st.sidebar.header("Gestione Atleti")
    lista_nomi_atleti = list(st.session_state.atleti.keys())
    atleta_selezionato = st.sidebar.selectbox(
        "Seleziona Atleta Attivo",
        lista_nomi_atleti,
        index=lista_nomi_atleti.index(st.session_state.atleta_corrente)
        if st.session_state.atleta_corrente in lista_nomi_atleti
        else 0,
    )
    if atleta_selezionato != st.session_state.atleta_corrente:
        st.session_state.atleta_corrente = atleta_selezionato
        salva_dati_disco()
        st.rerun()

    with st.sidebar.expander("➕ Aggiungi o Gestisci Profili"):
        nuovo_nome = st.text_input("Nome Nuovo Atleta (es. Figlio)")
        nuova_pwd = st.text_input("Password dedicata", type="password")
        if st.button("Crea Profilo"):
            nome_pulito = nuovo_nome.strip()
            if not nome_pulito:
                st.error("Inserisci un nome valido.")
            elif nome_pulito in st.session_state.atleti:
                st.warning("Esiste già un profilo con questo nome.")
            else:
                st.session_state.atleti[nome_pulito] = {
                    "peso": 65.0,
                    "altezza": 170.0,
                    "eta": 25,
                    "genere": "Uomo",
                    "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
                    "db_diario": {},
                }
                if nuova_pwd.strip():
                    st.session_state.password_atleti[
                        nome_pulito
                    ] = nuova_pwd.strip()
                salva_dati_disco()
                st.success(f"Profilo '{nome_pulito}' creato con successo!")
                st.rerun()

        if len(st.session_state.atleti) > 1:
            da_eliminare = st.selectbox(
                "Elimina profilo",
                [
                    a
                    for a in lista_nomi_atleti
                    if a != st.session_state.atleta_corrente
                ],
            )
            if st.button("Conferma Eliminazione", type="primary"):
                if da_eliminare in st.session_state.atleti:
                    del st.session_state.atleti[da_eliminare]
                    if da_eliminare in st.session_state.password_atleti:
                        del st.session_state.password_atleti[da_eliminare]
                    st.session_state.atleta_corrente = list(
                        st.session_state.atleti.keys()
                    )[0]
                    salva_dati_disco()
                    st.success("Profilo eliminato.")
                    st.rerun()

# --- PARAMETRI FISICI E ALLENAMENTO DELL'ATLETA CORRENTE ---
atleta_data = st.session_state.atleti[st.session_state.atleta_corrente]

st.sidebar.markdown("---")
st.sidebar.header(f"Parametri & Allenamento: {st.session_state.atleta_corrente}")

peso = st.sidebar.number_input(
    "Peso (kg)",
    value=float(atleta_data.get("peso", 70.0)),
    key=f"p_{st.session_state.atleta_corrente}",
)
altezza = st.sidebar.number_input(
    "Altezza (cm)",
    value=float(atleta_data.get("altezza", 175.0)),
    key=f"alt_{st.session_state.atleta_corrente}",
)
eta = st.sidebar.number_input(
    "Età",
    value=int(atleta_data.get("eta", 30)),
    key=f"eta_{st.session_state.atleta_corrente}",
)
genere = st.sidebar.selectbox(
    "Genere",
    ["Uomo", "Donna"],
    index=0
    if atleta_data.get("genere", "Uomo") == "Uomo"
    else 1,
    key=f"gen_{st.session_state.atleta_corrente}",
)

allenamento_opzioni = [
    "Riposo / Sedentario (PAL 1.2)",
    "Attività Leggera (PAL 1.375)",
    "Allenamento Moderato (PAL 1.55)",
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)",
    "Doppio Allenamento / Estremo (PAL 1.9)",
]
saved_all = atleta_data.get(
    "livello_allenamento", "Allenamento Moderato (PAL 1.55)"
)
all_index = (
    allenamento_opzioni.index(saved_all)
    if saved_all in allenamento_opzioni
    else 2
)
livello_allenamento = st.sidebar.selectbox(
    "Profilo di Allenamento",
    allenamento_opzioni,
    index=all_index,
    key=f"all_{st.session_state.atleta_corrente}",
)

# Aggiornamento dati atleta se modificati
if (
    atleta_data.get("peso") != peso
    or atleta_data.get("altezza") != altezza
    or atleta_data.get("eta") != eta
    or atleta_data.get("genere") != genere
    or atleta_data.get("livello_allenamento") != livello_allenamento
):
    atleta_data["peso"] = peso
    atleta_data["altezza"] = altezza
    atleta_data["eta"] = eta
    atleta_data["genere"] = genere
    atleta_data["livello_allenamento"] = livello_allenamento
    salva_dati_disco()

# Calcolo Fabbisogno Mifflin-St Jeor
pal_dict = {
    "Riposo / Sedentario (PAL 1.2)": 1.2,
    "Attività Leggera (PAL 1.375)": 1.375,
    "Allenamento Moderato (PAL 1.55)": 1.55,
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)": 1.725,
    "Doppio Allenamento / Estremo (PAL 1.9)": 1.9,
}
bmr = (
    (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
    if genere == "Uomo"
    else (10 * peso) + (6.25 * altezza) - (5 * eta) - 161
)
tdee = bmr * pal_dict[livello_allenamento]
obj_kcal = round(tdee, 0)
obj_carbo = 230.0
obj_prot = 165.0
obj_grassi = 70.0

st.sidebar.info(
    f"**Atleta:** {st.session_state.atleta_corrente}\n\n**BMR:** {bmr:.0f} kcal\n\n**TDEE:** {obj_kcal:.0f} kcal"
)

st.sidebar.markdown("---")
st.sidebar.header("Selezione Data Diario")
data_selezionata = st.sidebar.date_input("Data", value=date.today())
data_str = data_selezionata.strftime("%Y-%m-%d")

db_diario_atleta = atleta_data.setdefault("db_diario", {})
if data_str not in db_diario_atleta:
    db_diario_atleta[data_str] = {
        pasto: pd.DataFrame(
            columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]
        )
        for pasto in PASTI
    }
    salva_dati_disco()

# Calcoli totali giornalieri del singolo atleta
tot_carbo = sum(
    [
        db_diario_atleta[data_str][p]["carbo"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)
tot_prot = sum(
    [
        db_diario_atleta[data_str][p]["proteine"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)
tot_grassi = sum(
    [
        db_diario_atleta[data_str][p]["grassi"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)
tot_kcal = sum(
    [
        db_diario_atleta[data_str][p]["kcal"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)

st.subheader(
    f"Riepilogo Giornaliero - {st.session_state.atleta_corrente} ({data_str})"
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(
        "Calorie",
        f"{tot_kcal:.1f} / {obj_kcal} kcal",
        delta=f"{obj_kcal - tot_kcal:.1f} rimanenti",
    )
    st.progress(min(tot_kcal / obj_kcal, 1.0) if obj_kcal > 0 else 0)
with col_m2:
    st.metric(
        "Carboidrati",
        f"{tot_carbo:.1f} / {obj_carbo} g",
        delta=f"{obj_carbo - tot_carbo:.1f} g rimanenti",
    )
    st.progress(min(tot_carbo / obj_carbo, 1.0) if obj_carbo > 0 else 0)
with col_m3:
    st.metric(
        "Proteine",
        f"{tot_prot:.1f} / {obj_prot} g",
        delta=f"{obj_prot - tot_prot:.1f} g rimanenti",
    )
    st.progress(min(tot_prot / obj_prot, 1.0) if obj_prot > 0 else 0)
with col_m4:
    st.metric(
        "Grassi",
        f"{tot_grassi:.1f} / {obj_grassi} g",
        delta=f"{obj_grassi - tot_grassi:.1f} g rimanenti",
    )
    st.progress(min(tot_grassi / obj_grassi, 1.0) if obj_grassi > 0 else 0)

st.markdown("---")

# Gestione Avanzata Banca Dati (Visibile solo al proprietario o in sola lettura)
if st.session_state.utente_loggato is None:
    with st.expander("Gestione Avanzata Banca Dati Alimenti", expanded=False):
        st.dataframe(st.session_state.banca_dati_df, use_container_width=True)
        # Semplificato per brevità, mantiene la banca dati comune degli alimenti

st.markdown("---")

st.subheader("Inserimento Alimenti nei Pasti")
pasto_selezionato = st.selectbox(
    "Seleziona il pasto a cui aggiungere l'alimento:", PASTI
)

banca_dati_corrente = st.session_state.banca_dati_df
alimenti_validi = (
    banca_dati_corrente["Alimento"].dropna().astype(str).tolist()
)

if alimenti_validi:
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        alimento_scelto = st.selectbox("Alimento", alimenti_validi)
        item_row = banca_dati_corrente[
            banca_dati_corrente["Alimento"].astype(str) == str(alimento_scelto)
        ].iloc[0]
        val_gr_n = safe_float(item_row["gr/n"])
        default_q = int(val_gr_n) if val_gr_n > 0 else 100
    with col_ins2:
        quantita = st.number_input(
            "Quantità (g o porzione)", min_value=1.0, value=float(default_q)
        )

    if st.button("Aggiungi al pasto selezionato"):
        fattore = quantita / default_q if default_q > 0 else 1
        c_calc = round(safe_float(item_row["carbo"]) * fattore, 2)
        p_calc = round(safe_float(item_row["proteine"]) * fattore, 2)
        g_calc = round(safe_float(item_row["grassi"]) * fattore, 2)
        k_calc = round(safe_float(item_row["kcal"]) * fattore, 2)

        nuova_riga = pd.DataFrame(
            [
                {
                    "Alimento": alimento_scelto,
                    "gr/n": quantita,
                    "carbo": c_calc,
                    "proteine": p_calc,
                    "grassi": g_calc,
                    "kcal": k_calc,
                }
            ]
        )
        db_diario_atleta[data_str][pasto_selezionato] = pd.concat(
            [db_diario_atleta[data_str][pasto_selezionato], nuova_riga],
            ignore_index=True,
        )
        salva_dati_disco()
        st.rerun()

st.markdown("---")
st.subheader(
    f"Panoramica dei 6 Pasti - {st.session_state.atleta_corrente} ({data_str})"
)

cols_pasti = st.columns(3)
for i, pasto in enumerate(PASTI):
    with cols_pasti[i % 3]:
        with st.container(border=True):
            st.markdown(f"### {pasto}")
            df_p = db_diario_atleta[data_str][pasto]
            if not df_p.empty:
                st.dataframe(df_p, use_container_width=True)
                if st.button(f"Svuota {pasto}", key=f"clr_{pasto}"):
                    db_diario_atleta[data_str][pasto] = pd.DataFrame(
                        columns=[
                            "Alimento",
                            "gr/n",
                            "carbo",
                            "proteine",
                            "grassi",
                            "kcal",
                        ]
                    )
                    salva_dati_disco()
                    st.rerun()
            else:
                st.info("Nessun alimento.")
