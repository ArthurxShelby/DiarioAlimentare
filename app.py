import os
import pickle
import re
from datetime import date, timedelta
from fpdf import FPDF
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Diario Alimentare & Allenamento - Multi-Atleta",
    page_icon="",
    layout="wide",
)

# --- 0. GESTIONE AUTENTICAZIONE E RUOLI (BLINDATURA) ---
st.sidebar.markdown("### 🔐 Accesso e Sicurezza")
ruolo_utente = st.sidebar.radio(
    "Modalità Utente",
    ["Ospite (Sola Lettura)", "Proprietario / Autorizzato"],
    key="auth_diario",
)

is_proprietario = False
if ruolo_utente == "Proprietario / Autorizzato":
    password_inserita = st.sidebar.text_input(
        "Inserisci Password di Controllo", type="password", key="pass_diario"
    )
    password_corretta = st.secrets.get("auth", {}).get(
        "proprietario_password", "admin123"
    )
    if password_inserita == password_corretta:
        is_proprietario = True
        st.sidebar.success(
            "Accesso Proprietario Autorizzato (Controllo Completo)"
        )
    else:
        st.sidebar.error("Password errata. Modalità limitata a Ospite.")

# --- 0. GESTIONE PERSISTENZA DATI E PULIZIA ---
FILE_PERSISTENZA = "diario_alimentare_multi_db.pkl"


def safe_float(val):
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
    colonne_numeriche = ["gr/n", "carbo", "proteine", "grassi", "kcal"]
    for col in colonne_numeriche:
        if col in df.columns:
            df[col] = df[col].apply(safe_float)
    return df


def salva_dati_disco():
    if not is_proprietario:
        return
    try:
        dati = {
            "atleti": st.session_state.get("atleti", {}),
            "banca_dati_df": st.session_state.get("banca_dati_df"),
            "atleta_corrente": st.session_state.get("atleta_corrente"),
        }
        with open(FILE_PERSISTENZA, "wb") as f:
            pickle.dump(dati, f)
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati: {e}")


def carica_dati_disco():
    if os.path.exists(FILE_PERSISTENZA):
        try:
            with open(FILE_PERSISTENZA, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Errore durante il caricamento dei dati salvati: {e}")
    return None


dati_salvati = carica_dati_disco()

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
        "Alimento": "pollo",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 23.0,
        "grassi": 1.5,
        "kcal": 105.0,
    },
]

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

if "atleta_corrente" not in st.session_state:
    if (
        dati_salvati
        and "atleta_corrente" in dati_salvati
        and dati_salvati["atleta_corrente"] in st.session_state.atleti
    ):
        st.session_state.atleta_corrente = dati_salvati["atleta_corrente"]
    else:
        st.session_state.atleta_corrente = list(st.session_state.atleti.keys())[
            0
        ]

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

st.title("Pianificatore Alimentare & Allenamento - Multi-Atleta (Mifflin)")

st.sidebar.header("Gestione Atleti")
lista_atleti = list(st.session_state.atleti.keys())
atleta_selezionato = st.sidebar.selectbox(
    "Seleziona Atleta",
    lista_atleti,
    index=lista_atleti.index(st.session_state.atleta_corrente)
    if st.session_state.atleta_corrente in lista_atleti
    else 0,
    key="selectbox_atleta",
)

if atleta_selezionato != st.session_state.atleta_corrente:
    st.session_state.atleta_corrente = atleta_selezionato
    if is_proprietario:
        salva_dati_disco()
    st.rerun()

if is_proprietario:
    with st.sidebar.expander("Aggiungi o Gestisci Atleti"):
        nuovo_atleta_nome = st.text_input("Nome Nuovo Atleta")
        if st.button("Crea Nuovo Atleta"):
            nome_pulito = nuovo_atleta_nome.strip()
            if nome_pulito == "":
                st.error("Inserisci un nome valido.")
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
                st.session_state.atleta_corrente = nome_pulito
                salva_dati_disco()
                st.success(f"Atleta '{nome_pulito}' aggiunto!")
                st.rerun()
else:
    st.sidebar.info("🔒 Gestione atleti bloccata per gli ospiti.")

st.sidebar.markdown("---")
st.sidebar.header(f"Parametri Mifflin: {st.session_state.atleta_corrente}")

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

if is_proprietario:
    peso = st.sidebar.number_input("Peso (kg)", value=float(saved_peso))
    altezza = st.sidebar.number_input("Altezza (cm)", value=float(saved_altezza))
    eta = st.sidebar.number_input("Età (anni)", value=int(saved_eta))
    genere = st.sidebar.selectbox("Genere", genere_opzioni, index=genere_index)
    livello_allenamento = st.sidebar.selectbox(
        "Attività", allenamento_opzioni, index=allenamento_index
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
else:
    peso = saved_peso
    altezza = saved_altezza
    eta = saved_eta
    genere = saved_genere
    livello_allenamento = saved_allenamento
    st.sidebar.text(f"Peso: {peso} kg")

pal_dict = {
    "Riposo / Sedentario (PAL 1.2)": 1.2,
    "Attività Leggera (PAL 1.375)": 1.375,
    "Allenamento Moderato (PAL 1.55)": 1.55,
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)": 1.725,
    "Doppio Allenamento / Estremo (PAL 1.9)": 1.9,
}
pal_selezionato = pal_dict.get(livello_allenamento, 1.55)

if genere == "Uomo":
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
else:
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

tdee = bmr * pal_selezionato
obj_kcal = round(tdee, 0)
obj_carbo = 230.0
obj_prot = 165.0
obj_grassi = 70.0

st.sidebar.info(f"**TDEE dinamico:** {obj_kcal:.0f} kcal")

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
    if is_proprietario:
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
    st.metric("Calorie", f"{tot_kcal:.1f} / {obj_kcal} kcal")
with col_m2:
    st.metric("Carboidrati", f"{tot_carbo:.1f} / {obj_carbo} g")
with col_m3:
    st.metric("Proteine", f"{tot_prot:.1f} / {obj_prot} g")
with col_m4:
    st.metric("Grassi", f"{tot_grassi:.1f} / {obj_grassi} g")

st.markdown("---")

# Selezione alimenti e gestione pasti
st.subheader("Inserimento Alimenti nei Pasti")
pasto_selezionato = st.selectbox(
    "Seleziona il pasto:", PASTI
)

banca_dati_corrente = st.session_state.banca_dati_df
alimenti_validi = banca_dati_corrente["Alimento"].dropna().tolist()

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
        quantita = st.number_input("Quantità (g)", min_value=1.0, value=float(default_q))

    if is_proprietario:
        if st.button("Aggiungi al pasto"):
            fattore = quantita / default_q if default_q > 0 else 1
            nuova_riga = pd.DataFrame(
                [
                    {
                        "Alimento": alimento_scelto,
                        "gr/n": quantita,
                        "carbo": round(safe_float(item_row["carbo"]) * fattore, 2),
                        "proteine": round(safe_float(item_row["proteine"]) * fattore, 2),
                        "grassi": round(safe_float(item_row["grassi"]) * fattore, 2),
                        "kcal": round(safe_float(item_row["kcal"]) * fattore, 2),
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
        st.button("Aggiungi al pasto", disabled=True)

st.markdown("---")

# Visualizzazione Pasti
cols_pasti = st.columns(3)
for i, pasto in enumerate(PASTI):
    with cols_pasti[i % 3]:
        with st.container(border=True):
            st.markdown(f"### {pasto}")
            df_p = db_diario_atleta[data_str][pasto]
            if not df_p.empty:
                st.dataframe(df_p, use_container_width=True)
                if is_proprietario:
                    if st.button(f"Svuota {pasto}", key=f"clear_{pasto}"):
                        db_diario_atleta[data_str][pasto] = pd.DataFrame(
                            columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]
                        )
                        salva_dati_disco()
                        st.rerun()
            else:
                st.info("Nessun alimento.")

# --- GESTIONE MANUALE DEL FILE .PKL DEL DIARIO (RISERVATO AL PROPRIETARIO) ---
st.markdown("---")
if is_proprietario:
    st.subheader("📦 Gestione Avanzata File di Database Diario (.pkl)")
    st.write("Scarica o carica il file `.pkl` del diario e della banca dati per sincronizzarlo manualmente con GitHub.")

    col_pkl1, col_pkl2 = st.columns(2)

    with col_pkl1:
        st.markdown("#### 📥 Scarica Database Diario (.pkl)")
        if os.path.exists(FILE_PERSISTENZA):
            with open(FILE_PERSISTENZA, "rb") as f:
                pkl_bytes = f.read()
            st.download_button(
                label="Scarica diario_alimentare_multi_db.pkl",
                data=pkl_bytes,
                file_name=FILE_PERSISTENZA,
                mime="application/octet-stream",
                key="btn_download_pkl_diario"
            )
        else:
            st.info("Nessun file .pkl del diario trovato.")

    with col_pkl2:
        st.markdown("#### 📤 Carica Database Diario (.pkl)")
        pkl_caricato = st.file_uploader("Carica file .pkl del diario", type=["pkl"], key="uploader_pkl_diario")
        if pkl_caricato is not None:
            if st.button("Conferma e Sostituisci .pkl del Diario"):
                try:
                    with open(FILE_PERSISTENZA, "wb") as f:
                        f.write(pkl_caricato.getbuffer())
                    st.success("File .pkl del diario ricaricato con successo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante il caricamento: {e}")
else:
    st.info("🔒 Area di gestione file .pkl del diario riservata al proprietario.")
