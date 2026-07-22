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
    """Salva lo stato della banca dati, degli atleti e delle credenziali nel file locale."""
    try:
        dati = {
            "atleti": st.session_state.get("atleti", {}),
            "banca_dati_df": st.session_state.get("banca_dati_df"),
            "credenziali": st.session_state.get("credenziali", {}),
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
                        "peso": old_dati.get("peso", 70.0),
                        "altezza": old_dati.get("altezza", 175.0),
                        "eta": old_dati.get("eta", 56),
                        "genere": old_dati.get("genere", "Uomo"),
                        "livello_allenamento": old_dati.get(
                            "livello_allenamento",
                            "Allenamento Moderato (PAL 1.55)",
                        ),
                        "db_diario": old_dati.get("db_diario", {}),
                    }
                },
                "banca_dati_df": old_dati.get("banca_dati_df", None),
                "credenziali": {"Admin": "admin123", "Atleta Principale": "atleta123"},
            }
            return migrated
        except Exception as e:
            st.error(f"Errore durante la migrazione dei vecchi dati: {e}")
    return None


dati_salvati = carica_dati_disco()

# Banca dati precompilata iniziale (condivisa)
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
        "Alimento": "carne gelatina",
        "gr/n": 212,
        "carbo": 1.272,
        "proteine": 23.32,
        "grassi": 3.18,
        "kcal": 129.32,
    },
    {
        "Alimento": "ciliege",
        "gr/n": 100,
        "carbo": 12.0,
        "proteine": 1.0,
        "grassi": 0.2,
        "kcal": 50.0,
    },
    {
        "Alimento": "crakers tre mulini",
        "gr/n": 40,
        "carbo": 30.0,
        "proteine": 3.6,
        "grassi": 3.8,
        "kcal": 97.2,
    },
    {
        "Alimento": "cuscus",
        "gr/n": 100,
        "carbo": 75.0,
        "proteine": 12.0,
        "grassi": 1.5,
        "kcal": 376.0,
    },
    {
        "Alimento": "digestive",
        "gr/n": 100,
        "carbo": 63.0,
        "proteine": 7.0,
        "grassi": 21.0,
        "kcal": 471.0,
    },
    {
        "Alimento": "fiocchi di latte",
        "gr/n": 100,
        "carbo": 3.4,
        "proteine": 13.0,
        "grassi": 4.2,
        "kcal": 98.0,
    },
    {
        "Alimento": "gallette di mais bio",
        "gr/n": 100,
        "carbo": 78.0,
        "proteine": 8.0,
        "grassi": 2.5,
        "kcal": 365.0,
    },
    {
        "Alimento": "gallette di riso bio",
        "gr/n": 2,
        "carbo": 9.6,
        "proteine": 1.0,
        "grassi": 0.16,
        "kcal": 44.0,
    },
    {
        "Alimento": "hamburgher bovino",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 19.0,
        "grassi": 10.0,
        "kcal": 165.0,
    },
    {
        "Alimento": "hamburgher vitello",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 20.0,
        "grassi": 6.0,
        "kcal": 134.0,
    },
    {
        "Alimento": "latte",
        "gr/n": 160,
        "carbo": 7.84,
        "proteine": 5.28,
        "grassi": 5.76,
        "kcal": 102.4,
    },
    {
        "Alimento": "merluzzo",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 17.0,
        "grassi": 0.8,
        "kcal": 75.0,
    },
    {
        "Alimento": "nocciolata",
        "gr/n": 1,
        "carbo": 8.3,
        "proteine": 0.9,
        "grassi": 4.7,
        "kcal": 81.0,
    },
    {
        "Alimento": "noci",
        "gr/n": 100,
        "carbo": 7.0,
        "proteine": 14.0,
        "grassi": 65.0,
        "kcal": 654.0,
    },
    {
        "Alimento": "olio evo",
        "gr/n": 1,
        "carbo": 0.0,
        "proteine": 0.0,
        "grassi": 10.0,
        "kcal": 90.0,
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
        "Alimento": "patate",
        "gr/n": 100,
        "carbo": 17.0,
        "proteine": 2.0,
        "grassi": 0.1,
        "kcal": 77.0,
    },
    {
        "Alimento": "patate congelate",
        "gr/n": 100,
        "carbo": 22.0,
        "proteine": 2.5,
        "grassi": 5.0,
        "kcal": 140.0,
    },
    {
        "Alimento": "pizza margherita",
        "gr/n": 100,
        "carbo": 28.0,
        "proteine": 11.0,
        "grassi": 10.0,
        "kcal": 240.0,
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
        "Alimento": "puccia",
        "gr/n": 100,
        "carbo": 55.0,
        "proteine": 8.0,
        "grassi": 2.0,
        "kcal": 270.0,
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
        "Alimento": "salmone",
        "gr/n": 100,
        "carbo": 1.0,
        "proteine": 23.5,
        "grassi": 3.0,
        "kcal": 107.0,
    },
    {
        "Alimento": "sciroppo d'acero",
        "gr/n": 1,
        "carbo": 12.0,
        "proteine": 0.0,
        "grassi": 0.0,
        "kcal": 52.0,
    },
    {
        "Alimento": "semi di chia",
        "gr/n": 13,
        "carbo": 5.473,
        "proteine": 2.145,
        "grassi": 2.34,
        "kcal": 63.18,
    },
    {
        "Alimento": "tacchino",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 24.0,
        "grassi": 1.0,
        "kcal": 106.0,
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
    {
        "Alimento": "yamamoto caseine",
        "gr/n": 25,
        "carbo": 1.425,
        "proteine": 19.5,
        "grassi": 0.375,
        "kcal": 92.5,
    },
    {
        "Alimento": "yogurt greco",
        "gr/n": 100,
        "carbo": 4.0,
        "proteine": 10.0,
        "grassi": 0.0,
        "kcal": 51.0,
    },
    {
        "Alimento": "zucca",
        "gr/n": 100,
        "carbo": 3.5,
        "proteine": 1.1,
        "grassi": 0.1,
        "kcal": 18.0,
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
st.session_state.banca_dati_df = st.session_state.banca_dati_df.dropna(
    subset=["Alimento"]
)
st.session_state.banca_dati_df = st.session_state.banca_dati_df[
    st.session_state.banca_dati_df["Alimento"].astype(str).str.strip() != ""
]

# Inizializzazione Atleti
if "atleti" not in st.session_state:
    if dati_salvati and "atleti" in dati_salvati:
        st.session_state.atleti = dati_salvati["atleti"]
    else:
        st.session_state.atleti = {
            "Atleta Principale": {
                "peso": 70.0,
                "altezza": 175.0,
                "eta": 56,
                "genere": "Uomo",
                "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
                "db_diario": {},
            }
        }

# Inizializzazione Credenziali (Admin user = "Admin", default pass = "admin123")
if "credenziali" not in st.session_state:
    if dati_salvati and "credenziali" in dati_salvati:
        st.session_state.credenziali = dati_salvati["credenziali"]
    else:
        st.session_state.credenziali = {
            "Admin": "admin123",
            "Atleta Principale": "atleta123",
        }

# --- SISTEMA DI AUTENTICAZIONE ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False
if "utente_loggato" not in st.session_state:
    st.session_state.utente_loggato = None

if not st.session_state.autenticato:
    st.title("Accesso - Pianificatore Alimentare & Allenamento")
    with st.form("form_login"):
        username_input = st.text_input("Nome Utente / Atleta")
        password_input = st.text_input("Password", type="password")
        btn_login = st.form_submit_button("Accedi")

        if btn_login:
            user_clean = username_input.strip()
            if (
                user_clean in st.session_state.credenziali
                and st.session_state.credenziali[user_clean] == password_input
            ):
                st.session_state.autenticato = True
                st.session_state.utente_loggato = user_clean
                if user_clean != "Admin":
                    st.session_state.atleta_corrente = user_clean
                else:
                    st.session_state.atleta_corrente = list(
                        st.session_state.atleti.keys()
                    )[0]
                st.success("Accesso eseguito con successo!")
                st.rerun()
            else:
                st.error("Nome utente o password errati.")
    st.stop()

# --- GESTIONE SESSIONE UTENTE LOGGATO ---
is_admin = st.session_state.utente_loggato == "Admin"

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

st.title("Pianificatore Alimentare & Allenamento - Multi-Atleta (Mifflin)")

# Pulsante di Logout nella sidebar
if st.sidebar.button("Disconnetti (Logout)", type="secondary"):
    st.session_state.autenticato = False
    st.session_state.utente_loggato = None
    st.rerun()

st.sidebar.markdown("---")

# --- SEZIONE GESTIONE ATLETI / UTENTI NELLA SIDEBAR ---
if is_admin:
    st.sidebar.header("Gestione Amministratore (Atleti & Password)")
    lista_atleti = list(st.session_state.atleti.keys())
    atleta_selezionato = st.sidebar.selectbox(
        "Seleziona Atleta da Visualizzare",
        lista_atleti,
        index=lista_atleti.index(st.session_state.atleta_corrente)
        if st.session_state.atleta_corrente in lista_atleti
        else 0,
        key="selectbox_atleta_admin",
    )

    if atleta_selezionato != st.session_state.atleta_corrente:
        st.session_state.atleta_corrente = atleta_selezionato
        salva_dati_disco()
        st.rerun()

    with st.sidebar.expander("Crea o Gestisci Utenti/Atleti"):
        nuovo_atleta_nome = st.text_input("Nome Nuovo Atleta")
        nuova_password = st.text_input("Password Iniziale", type="password")
        if st.button("Crea Nuovo Utente/Atleta"):
            nome_pulito = nuovo_atleta_nome.strip()
            pass_pulita = nuova_password.strip()
            if nome_pulito == "" or pass_pulita == "":
                st.error("Inserisci un nome e una password validi.")
            elif nome_pulito in st.session_state.atleti:
                st.warning("Esiste già un atleta con questo nome.")
            else:
                st.session_state.atleti[nome_pulito] = {
                    "peso": 70.0,
                    "altezza": 175.0,
                    "eta": 30,
                    "genere": "Uomo",
                    "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
                    "db_diario": {},
                }
                st.session_state.credenziali[nome_pulito] = pass_pulita
                st.session_state.atleta_corrente = nome_pulito
                salva_dati_disco()
                st.success(f"Utente '{nome_pulito}' creato con successo!")
                st.rerun()

        st.markdown("---")
        utente_sel_pw = st.selectbox(
            "Modifica Password Utente", list(st.session_state.credenziali.keys())
        )
        nuova_pw_mod = st.text_input("Nuova Password", type="password")
        if st.button("Aggiorna Password"):
            if nuova_pw_mod.strip():
                st.session_state.credenziali[utente_sel_pw] = nuova_pw_mod.strip()
                salva_dati_disco()
                st.success(
                    f"Password per '{utente_sel_pw}' aggiornata con successo!"
                )
                st.rerun()
            else:
                st.error("Inserisci una password non vuota.")

        if len(st.session_state.atleti) > 1:
            atleta_da_eliminare = st.selectbox(
                "Elimina Atleta",
                [a for a in lista_atleti if a != st.session_state.atleta_corrente],
            )
            if st.button("Conferma ed Elimina Atleta", type="primary"):
                if atleta_da_eliminare in st.session_state.atleti:
                    del st.session_state.atleti[atleta_da_eliminare]
                    if atleta_da_eliminare in st.session_state.credenziali:
                        del st.session_state.credenziali[atleta_da_eliminare]
                    st.session_state.atleta_corrente = list(
                        st.session_state.atleti.keys()
                    )[0]
                    salva_dati_disco()
                    st.success(f"Atleta '{atleta_da_eliminare}' eliminato.")
                    st.rerun()
else:
    # Utente standard vede solo se stesso
    st.sidebar.header(f"Profilo Utente: {st.session_state.utente_loggato}")
    st.session_state.atleta_corrente = st.session_state.utente_loggato

st.sidebar.markdown("---")
st.sidebar.header(
    f"Parametri Mifflin & Allenamento: {st.session_state.atleta_corrente}"
)

atleta_data = st.session_state.atleti[st.session_state.atleta_corrente]

saved_peso = atleta_data.get("peso", 70.0)
saved_altezza = atleta_data.get("altezza", 175.0)
saved_eta = atleta_data.get("eta", 56)
saved_genere = atleta_data.get("genere", "Uomo")
saved_allenamento = atleta_data.get(
    "livello_allenamento", "Allenamento Moderato (PAL 1.55)"
)

genere_opzioni = ["Uomo", "Donna"]
genere_index = (
    genere_opzioni.index(saved_genere) if saved_genere in genere_opzioni else 0
)

allenamento_opzioni = [
    "Riposo / Sedentario (PAL 1.2)",
    "Attività Leggera (PAL 1.375)",
    "Allenamento Moderato (PAL 1.55)",
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)",
    "Doppio Allenamento / Estremo (PAL 1.9)",
]
allenamento_index = (
    allenamento_opzioni.index(saved_allenamento)
    if saved_allenamento in allenamento_opzioni
    else 2
)

peso = st.sidebar.number_input(
    "Peso (kg)",
    value=float(saved_peso),
    key=f"peso_{st.session_state.atleta_corrente}",
)
altezza = st.sidebar.number_input(
    "Altezza (cm)",
    value=float(saved_altezza),
    key=f"altezza_{st.session_state.atleta_corrente}",
)
eta = st.sidebar.number_input(
    "Età (anni)",
    value=int(saved_eta),
    key=f"eta_{st.session_state.atleta_corrente}",
)
genere = st.sidebar.selectbox(
    "Genere",
    genere_opzioni,
    index=genere_index,
    key=f"genere_{st.session_state.atleta_corrente}",
)
livello_allenamento = st.sidebar.selectbox(
    "Intensità Allenamento / Attività",
    allenamento_opzioni,
    index=allenamento_index,
    key=f"allenamento_{st.session_state.atleta_corrente}",
)

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

pal_dict = {
    "Riposo / Sedentario (PAL 1.2)": 1.2,
    "Attività Leggera (PAL 1.375)": 1.375,
    "Allenamento Moderato (PAL 1.55)": 1.55,
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)": 1.725,
    "Doppio Allenamento / Estremo (PAL 1.9)": 1.9,
}
pal_selezionato = pal_dict[livello_allenamento]

if genere == "Uomo":
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
else:
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

tdee = bmr * pal_selezionato
obj_kcal = round(tdee, 0)
obj_carbo = 230.0
obj_prot = 165.0
obj_grassi = 70.0

st.sidebar.info(
    f"**Atleta in uso:** {st.session_state.atleta_corrente}\n\n**BMR stimato:** {bmr:.0f} kcal\n\n**TDEE dinamico:** {obj_kcal:.0f} kcal"
)

st.sidebar.markdown("---")
st.sidebar.header("Seleziona Giorno")
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
    progresso_grassi = (
        float(min(tot_grassi / obj_grassi, 1.0)) if obj_grassi > 0 else 0.0
    )
    st.progress(progresso_grassi)

st.markdown("---")

with st.expander("Gestione Avanzata Banca Dati Alimenti (Condivisa)", expanded=False):
    st.markdown("### Accesso e Visualizzazione")
    banca_dati = st.session_state.banca_dati_df
    st.dataframe(banca_dati, use_container_width=True)

    csv_backup_data = banca_dati.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Scarica Backup Banca Dati (CSV)",
        data=csv_backup_data,
        file_name=f"banca_dati_alimentare_backup_{date.today().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )

    st.markdown("---")

    st.markdown("### Inserimento Manuale Singolo Alimento")
    with st.form("form_inserimento_manuale"):
        col_man1, col_man2, col_man3 = st.columns(3)
        with col_man1:
            nuovo_nome = st.text_input("Nome Alimento")
        with col_man2:
            nuovo_grn = st.number_input(
                "Quantità di Riferimento (g o p)", min_value=1.0, value=100.0
            )
        with col_man3:
            nuovo_kcal = st.number_input(
                "Calorie (kcal)", min_value=0.0, value=0.0, step=0.1
            )

        col_man4, col_man5, col_man6 = st.columns(3)
        with col_man4:
            nuovo_carbo = st.number_input(
                "Carboidrati (g)", min_value=0.0, value=0.0, step=0.1
            )
        with col_man5:
            nuovo_prot = st.number_input(
                "Proteine (g)", min_value=0.0, value=0.0, step=0.1
            )
        with col_man6:
            nuovo_grassi = st.number_input(
                "Grassi (g)", min_value=0.0, value=0.0, step=0.1
            )

        btn_submit_manuale = st.form_submit_button(
            "Aggiungi Alimento alla Banca Dati"
        )
        if btn_submit_manuale:
            if nuovo_nome.strip() == "":
                st.error("Inserisci un nome valido per l'alimento.")
            else:
                nuova_riga_df = pd.DataFrame(
                    [
                        {
                            "Alimento": nuovo_nome.strip().lower(),
                            "gr/n": nuovo_grn,
                            "carbo": nuovo_carbo,
                            "proteine": nuovo_prot,
                            "grassi": nuovo_grassi,
                            "kcal": nuovo_kcal,
                        }
                    ]
                )
                nuova_riga_df = pulisci_dataframe_banca_dati(nuova_riga_df)
                st.session_state.banca_dati_df = (
                    pd.concat(
                        [
                            st.session_state.banca_dati_df[
                                st.session_state.banca_dati_df[
                                    "Alimento"
                                ].astype(str).str.lower()
                                != nuovo_nome.strip().lower()
                            ],
                            nuova_riga_df,
                        ],
                        ignore_index=True,
                    )
                    .sort_values("Alimento")
                    .reset_index(drop=True)
                )
                salva_dati_disco()
                st.success(
                    f"Alimento '{nuovo_nome}' aggiunto/aggiornato con successo nella banca dati!"
                )
                st.rerun()

    st.markdown("---")

    col_bd1, col_bd2 = st.columns(2)

    with col_bd1:
        st.markdown("### Cancellazione Parziale o Totale")
        alimenti_disponibili = banca_dati["Alimento"].dropna().tolist()
        alimenti_da_eliminare = st.multiselect(
            "Seleziona alimenti da rimuovere dalla banca dati:",
            alimenti_disponibili,
            key="multi_del_alimenti",
        )

        col_del_a, col_del_b = st.columns(2)
        with col_del_a:
            if st.button("Elimina Selezionati"):
                if alimenti_da_eliminare:
                    st.session_state.banca_dati_df = banca_dati[
                        ~banca_dati["Alimento"].isin(alimenti_da_eliminare)
                    ].reset_index(drop=True)
                    salva_dati_disco()
                    st.success("Alimenti selezionati rimossi con successo!")
                    st.rerun()
                else:
                    st.warning("Nessun alimento selezionato.")
        with col_del_b:
            if st.button("Svuota Intera Banca Dati", type="primary"):
                st.session_state.banca_dati_df = pd.DataFrame(
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
                st.warning("Banca dati svuotata completamente.")
                st.rerun()

    with col_bd2:
        st.markdown("### Integrazione File CSV")
        st.info(
            "Carica un file CSV. L'ordine atteso per colonna è: Alimento, gr/n, carbo, proteine, grassi, kcal."
        )
        file_caricato = st.file_uploader(
            "Carica file CSV", type=["csv"], key="uploader_banca_dati"
        )

        if file_caricato is not None:
            try:
                df_nuovo = None
                try:
                    df_nuovo = pd.read_csv(
                        file_caricato, encoding="utf-8", sep=None, engine="python"
                    )
                except UnicodeDecodeError:
                    file_caricato.seek(0)
                    df_nuovo = pd.read_csv(
                        file_caricato,
                        encoding="latin-1",
                        sep=None,
                        engine="python",
                    )
                except Exception:
                    file_caricato.seek(0)
                    df_nuovo = pd.read_csv(
                        file_caricato, encoding="utf-8", sep=";", engine="python"
                    )

                if df_nuovo is not None and not df_nuovo.empty:
                    st.write("Anteprima dati letti dal file:", df_nuovo.head())
                    if st.button("Conferma e Aggiungi alla Banca Dati"):
                        colonne_attese = [
                            "Alimento",
                            "gr/n",
                            "carbo",
                            "proteine",
                            "grassi",
                            "kcal",
                        ]
                        cols_orig = [
                            str(c).strip().lower() for c in df_nuovo.columns
                        ]
                        df_nuovo.columns = cols_orig

                        mapping_colonne = {}
                        for c in cols_orig:
                            if "alimento" in c or "nome" in c:
                                mapping_colonne[c] = "Alimento"
                            elif "grass" in c or c == "g":
                                mapping_colonne[c] = "grassi"
                            elif (
                                "gr" in c
                                or "quant" in c
                                or "peso" in c
                                or "numero" in c
                            ):
                                mapping_colonne[c] = "gr/n"
                            elif "carb" in c:
                                mapping_colonne[c] = "carbo"
                            elif "prot" in c:
                                mapping_colonne[c] = "proteine"
                            elif "kcal" in c or "calorie" in c or "kca" in c:
                                mapping_colonne[c] = "kcal"

                        df_nuovo = df_nuovo.rename(columns=mapping_colonne)
                        df_nuovo = df_nuovo.loc[
                            :, ~df_nuovo.columns.duplicated()
                        ]

                        presenti = [
                            col
                            for col in colonne_attese
                            if col in df_nuovo.columns
                        ]
                        if len(presenti) < 4 and len(df_nuovo.columns) >= 4:
                            col_mapping_pos = {}
                            for idx, col_name in enumerate(df_nuovo.columns):
                                if idx < len(colonne_attese):
                                    col_mapping_pos[col_name] = colonne_attese[
                                        idx
                                    ]
                            df_nuovo = df_nuovo.rename(columns=col_mapping_pos)
                            df_nuovo = df_nuovo.loc[
                                :, ~df_nuovo.columns.duplicated()
                            ]

                        data_dict = {}
                        for col in colonne_attese:
                            if col in df_nuovo.columns:
                                data_dict[col] = df_nuovo[col].values
                            else:
                                data_dict[col] = (
                                    0 if col != "Alimento" else "Sconosciuto"
                                )

                        df_finale = pd.DataFrame(data_dict)
                        df_finale = pulisci_dataframe_banca_dati(df_finale)
                        df_finale = df_finale.dropna(subset=["Alimento"])
                        df_finale = df_finale[
                            df_finale["Alimento"].astype(str).str.strip() != ""
                        ]

                        st.session_state.banca_dati_df = (
                            pd.concat(
                                [st.session_state.banca_dati_df, df_finale],
                                ignore_index=True,
                            )
                            .drop_duplicates(subset=["Alimento"])
                            .reset_index(drop=True)
                        )
                        salva_dati_disco()
                        st.success(
                            "Banca dati aggiornata con successo dal file CSV!"
                        )
                        st.rerun()
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {e}")

st.markdown("---")

st.subheader("Inserimento Alimenti nei Pasti")
pasto_selezionato = st.selectbox(
    "Seleziona il pasto a cui aggiungere l'alimento:", PASTI
)

banca_dati_corrente = st.session_state.banca_dati_df
alimenti_validi = banca_dati_corrente["Alimento"].dropna().tolist()
alimenti_validati = [
    str(a)
    for a in alimenti_validi
    if str(a).strip() != "" and str(a).lower() != "nan"
]

if alimenti_validati:
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        alimento_scelto = st.selectbox(
            "Alimento", alimenti_validati, key="sel_alimento_principale"
        )
        item_row = banca_dati_corrente[
            banca_dati_corrente["Alimento"].astype(str) == str(alimento_scelto)
        ].iloc[0]

        val_gr_n = safe_float(item_row["gr/n"])
        default_q = int(val_gr_n) if val_gr_n > 0 else 100

    with col_ins2:
        quantita = st.number_input(
            "Quantità (g o porzione)",
            min_value=1.0,
            value=float(default_q),
            key="num_quantita_principale",
        )

    if st.button("Aggiungi al pasto selezionato", key="btn_aggiungi_principale"):
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
else:
    st.warning("La banca dati è vuota o contiene solo elementi non validi.")

st.markdown("---")

st.subheader(
    f"Panoramica dei 6 Pasti Giornalieri - {st.session_state.atleta_corrente}"
)

cols_pasti = st.columns(3)
for i, pasto in enumerate(PASTI):
    col_target = cols_pasti[i % 3]
    with col_target:
        with st.container(border=True):
            st.markdown(f"### {pasto}")
            df_p = db_diario_atleta[data_str][pasto]

            if not df_p.empty:
                p_kcal = safe_float(df_p["kcal"].sum())
                p_carb = safe_float(df_p["carbo"].sum())
                p_prot = safe_float(df_p["proteine"].sum())
                p_gras = safe_float(df_p["grassi"].sum())
                st.caption(
                    f"Totale: {p_kcal:.1f} kcal | C: {p_carb:.1f}g | P: {p_prot:.1f}g | G: {p_gras:.1f}g"
                )

                st.dataframe(df_p, use_container_width=True)

                mostra_gestione_voci = st.toggle(
                    "Modifica voci pasto", key=f"toggle_mod_{pasto}"
                )

                if mostra_gestione_voci:
                    indices_disponibili = df_p.index.tolist()
                    opzioni_rimozione = {
                        f"Riga {idx}: {df_p.loc[idx, 'Alimento']} ({df_p.loc[idx, 'gr/n']}g)": idx
                        for idx in indices_disponibili
                    }

                    voce_da_rimuovere = st.selectbox(
                        "Elimina voce:",
                        list(opzioni_rimozione.keys()),
                        key=f"del_box_{pasto}",
                    )

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Elimina", key=f"btn_del_{pasto}"):
                            idx_to_drop = opzioni_rimozione[voce_da_rimuovere]
                            db_diario_atleta[data_str][pasto] = df_p.drop(
                                idx_to_drop
                            ).reset_index(drop=True)
                            salva_dati_disco()
                            st.rerun()
                    with col_btn2:
                        if st.button("Svuota", key=f"clear_{pasto}"):
                            db_diario_atleta[data_str][
                                pasto
                            ] = pd.DataFrame(
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
                st.info("Nessun alimento registrato.")

st.markdown("---")

st.subheader(
    f"Esportazione Report in PDF - {st.session_state.atleta_corrente}"
)

col_pdf1, col_pdf2 = st.columns(2)

with col_pdf1:
    st.markdown("### Report Giornaliero")
    if st.button("Genera e Scarica PDF Giornaliero"):
        try:
            pdf_output = FPDF()
            pdf_output.add_page()
            pdf_output.set_font("Arial", "B", 16)
            pdf_output.cell(
                0,
                10,
                f"Report Nutrizionale - {st.session_state.atleta_corrente} ({data_str})",
                ln=True,
                align="C",
            )
            pdf_output.ln(10)

            pdf_output.set_font("Arial", "B", 12)
            pdf_output.cell(0, 10, "Riepilogo Totale:", ln=True)
            pdf_output.set_font("Arial", "", 11)

            pdf_output.set_text_color(0, 0, 0)
            pdf_output.write(8, "Calorie: ")
            if tot_kcal > obj_kcal:
                pdf_output.set_text_color(220, 20, 60)
            pdf_output.write(8, f"{tot_kcal:.1f}")
            pdf_output.set_text_color(0, 0, 0)
            pdf_output.write(
                8, f" / {obj_kcal} kcal ({livello_allenamento})\n"
            )
            pdf_output.ln(2)

            pdf_output.write(8, "Carboidrati: ")
            if tot_carbo > obj_carbo:
                pdf_output.set_text_color(220, 20, 60)
            pdf_output.write(8, f"{tot_carbo:.1f}")
            pdf_output.set_text_color(0, 0, 0)
            pdf_output.write(8, f" / {obj_carbo} g\n")
            pdf_output.ln(2)

            pdf_output.write(8, "Proteine: ")
            if tot_prot > obj_prot:
                pdf_output.set_text_color(220, 20, 60)
            pdf_output.write(8, f"{tot_prot:.1f}")
            pdf_output.set_text_color(0, 0, 0)
            pdf_output.write(8, f" / {obj_prot} g\n")
            pdf_output.ln(2)

            pdf_output.write(8, "Grassi: ")
            if tot_grassi > obj_grassi:
                pdf_output.set_text_color(220, 20, 60)
            pdf_output.write(8, f"{tot_grassi:.1f}")
            pdf_output.set_text_color(0, 0, 0)
            pdf_output.write(8, f" / {obj_grassi} g\n")
            pdf_output.ln(10)

            for pasto in PASTI:
                pdf_output.set_font("Arial", "B", 12)
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.cell(0, 8, f"Pasto: {pasto}", ln=True)
                pdf_output.set_font("Arial", "", 10)
                df_p = db_diario_atleta[data_str][pasto]
                if not df_p.empty:
                    for _, row in df_p.iterrows():
                        testo_riga = f" - {row['Alimento']}: {row['gr/n']}g | Carbo: {row['carbo']}g | Prot: {row['proteine']}g | Grassi: {row['grassi']}g | {row['kcal']} kcal"
                        pdf_output.cell(0, 6, testo_riga, ln=True)
                else:
                    pdf_output.cell(
                        0, 6, " - Nessun alimento registrato", ln=True
                    )
                pdf_output.ln(4)

            raw_output = pdf_output.output()
            pdf_bytes = (
                bytes(raw_output)
                if isinstance(raw_output, (bytearray, bytes))
                else raw_output.encode("latin1")
            )

            st.download_button(
                label="Scarica PDF Giornaliero",
                data=pdf_bytes,
                file_name=f"report_{st.session_state.atleta_corrente}_{data_str}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"Errore nella generazione del PDF giornaliero: {e}")

with col_pdf2:
    st.markdown("### Report Personalizzato per Intervallo di Date")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_inizio = st.date_input(
            "Data Inizio",
            value=date.today() - timedelta(days=6),
            key="pdf_data_inizio",
        )
    with col_d2:
        data_fine = st.date_input(
            "Data Fine", value=date.today(), key="pdf_data_fine"
        )

    if st.button("Genera e Scarica PDF Intervallo (Traccia Totale)"):
        try:
            if data_inizio > data_fine:
                st.error(
                    "La data di inizio non può essere successiva alla data di fine."
                )
            else:
                delta_giorni = (data_fine - data_inizio).days + 1
                (
                    tot_p_kcal,
                    tot_p_carbo,
                    tot_p_prot,
                    tot_p_grassi,
                ) = 0.0, 0.0, 0.0, 0.0
                dettaglio_periodo = []

                for i in range(delta_giorni):
                    d_corrente = data_inizio + timedelta(days=i)
                    d_str = d_corrente.strftime("%Y-%m-%d")
                    if d_str in db_diario_atleta:
                        d_kcal = sum(
                            [
                                safe_float(
                                    db_diario_atleta[d_str][p]["kcal"].sum()
                                )
                                for p in PASTI
                                if not db_diario_atleta[d_str][p].empty
                            ]
                        )
                        d_carbo = sum(
                            [
                                safe_float(
                                    db_diario_atleta[d_str][p]["carbo"].sum()
                                )
                                for p in PASTI
                                if not db_diario_atleta[d_str][p].empty
                            ]
                        )
                        d_prot = sum(
                            [
                                safe_float(
                                    db_diario_atleta[d_str][p][
                                        "proteine"
                                    ].sum()
                                )
                                for p in PASTI
                                if not db_diario_atleta[d_str][p].empty
                            ]
                        )
                        d_grassi = sum(
                            [
                                safe_float(
                                    db_diario_atleta[d_str][p]["grassi"].sum()
                                )
                                for p in PASTI
                                if not db_diario_atleta[d_str][p].empty
                            ]
                        )

                        tot_p_kcal += d_kcal
                        tot_p_carbo += d_carbo
                        tot_p_prot += d_prot
                        tot_p_grassi += d_grassi

                        if d_kcal > 0 or d_carbo > 0:
                            dettaglio_periodo.append(
                                (d_str, d_kcal, d_carbo, d_prot, d_grassi)
                            )

                pdf_output = FPDF()
                pdf_output.add_page()
                pdf_output.set_font("Arial", "B", 16)
                pdf_output.cell(
                    0,
                    10,
                    f"Report Nutrizionale - {st.session_state.atleta_corrente} ({data_inizio.strftime('%d/%m/%Y')} - {data_fine.strftime('%d/%m/%Y')})",
                    ln=True,
                    align="C",
                )
                pdf_output.ln(10)

                pdf_output.set_font("Arial", "B", 12)
                pdf_output.cell(0, 10, "Riepilogo Totale del Periodo:", ln=True)
                pdf_output.set_font("Arial", "", 11)

                media_kcal = tot_p_kcal / delta_giorni
                media_carbo = tot_p_carbo / delta_giorni
                media_prot = tot_p_prot / delta_giorni
                media_grassi = tot_p_grassi / delta_giorni

                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, "Calorie Totali: ")
                if media_kcal > obj_kcal:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_p_kcal:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" kcal (Media giornaliera: ")
                if media_kcal > obj_kcal:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{media_kcal:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, " kcal)\n")
                pdf_output.ln(2)

                pdf_output.write(8, "Carboidrati Totali: ")
                if media_carbo > obj_carbo:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_p_carbo:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" g (Media: ")
                if media_carbo > obj_carbo:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{media_carbo:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, " g)\n")
                pdf_output.ln(2)

                pdf_output.write(8, "Proteine Totali: ")
                if media_prot > obj_prot:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_p_prot:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" g (Media: ")
                if media_prot > obj_prot:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{media_prot:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, " g)\n")
                pdf_output.ln(2)

                pdf_output.write(8, "Grassi Totali: ")
                if media_grassi > obj_grassi:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_p_grassi:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" g (Media: ")
                if media_grassi > obj_grassi:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{media_grassi:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, " g)\n")
                pdf_output.ln(10)

                pdf_output.set_font("Arial", "B", 12)
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.cell(
                    0, 10, "Traccia Giornaliera dei Macronutrienti:", ln=True
                )
                pdf_output.set_font("Arial", "", 10)

                if dettaglio_periodo:
                    for d_str, dk, dc, dp, dg in dettaglio_periodo:
                        pdf_output.set_text_color(0, 0, 0)
                        pdf_output.write(6, f" - {d_str}: ")
                        if dk > obj_kcal:
                            pdf_output.set_text_color(220, 20, 60)
                        pdf_output.write(6, f"{dk:.1f} kcal")
                        pdf_output.set_text_color(0, 0, 0)
                        pdf_output.write(6, " | Carbo: ")
                        if dc > obj_carbo:
                            pdf_output.set_text_color(220, 20, 60)
                        pdf_output.write(6, f"{dc:.1f}g")
                        pdf_output.set_text_color(0, 0, 1)
                        pdf_output.write(
                            6, f" | Prot: {dp:.1f}g | Grassi: {dg:.1f}g\n"
                        )
                else:
                    pdf_output.cell(
                        0,
                        6,
                        " - Nessun dato registrato nel periodo selezionato",
                        ln=True,
                    )

                raw_output = pdf_output.output()
                pdf_bytes = (
                    bytes(raw_output)
                    if isinstance(raw_output, (bytearray, bytes))
                    else raw_output.encode("latin1")
                )

                st.download_button(
                    label="Scarica PDF Periodo Personalizzato",
                    data=pdf_bytes,
                    file_name=f"report_periodo_{st.session_state.atleta_corrente}_{data_inizio}_al_{data_fine}.pdf",
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(f"Errore nella generazione del PDF personalizzato: {e}")

