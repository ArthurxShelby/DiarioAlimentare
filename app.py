from datetime import date, timedelta
import os
import pickle
import re
from fpdf import FPDF
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare & Allenamento - Multi-Atleta",
    page_icon="🚴",
    layout="wide",
)

# --- 0. GESTIONE PERSISTENZA DATI E PULIZIA ---
FILE_PERSISTENZA = "diario_alimentare_multi_db.pkl"
OLD_FILE_PERSISTENZA = "diario_alimentare_db.pkl"


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
  try:
    dati = {
        "atleti": st.session_state.get("atleti", {}),
        "banca_dati_df": st.session_state.get("banca_dati_df"),
        "atleta_corrente": st.session_state.get("atleta_corrente"),
        "password_atleti": st.session_state.get("password_atleti", {}),
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
      st.error(f"Errore durante il caricamento dei dati: {e}")
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
                  "db_allenamenti": old_dati.get("db_allenamenti", {}),
              }
          },
          "banca_dati_df": old_dati.get("banca_dati_df", None),
          "atleta_corrente": "Atleta Principale",
          "password_atleti": {},
      }
      return migrated
    except Exception as e:
      st.error(f"Errore migrazione: {e}")
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
            "db_allenamenti": {},
        }
    }

if "password_atleti" not in st.session_state:
  if dati_salvati and "password_atleti" in dati_salvati:
    st.session_state.password_atleti = dati_salvati["password_atleti"]
  else:
    st.session_state.password_atleti = {}

if "utente_loggato" not in st.session_state:
  st.session_state.utente_loggato = None

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]
ADMIN_PASSWORD = "adminpassword123"

# --- GESTIONE LOGIN / PROFILI NELLA SIDEBAR ---
if st.session_state.utente_loggato is not None:
  atleta_corrente = st.session_state.utente_loggato
  st.session_state.atleta_corrente = atleta_corrente
  st.sidebar.warning(f"🔒 Accesso protetto come: **{atleta_corrente}**")
  if st.sidebar.button("🚪 Esci (Logout)"):
    st.session_state.utente_loggato = None
    st.rerun()
else:
  st.sidebar.header("Accesso Applicazione")
  modalita_accesso = st.sidebar.radio(
      "Seleziona modalità", ["Proprietario (Admin)", "Ospite / Utente"]
  )

  if modalita_accesso == "Ospite / Utente":
    atleti_disponibili = [
        a for a in st.session_state.atleti.keys() if a != "Atleta Principale"
    ]
    if not atleti_disponibili:
      st.sidebar.info(
          "Nessun profilo utente configurato. Crea prima un profilo dalla"
          " modalità Admin."
      )
      st.stop()

    atleta_scelto_login = st.sidebar.selectbox(
        "Seleziona il tuo profilo", atleti_disponibili
    )
    password_inserita = st.sidebar.text_input("Password Profilo", type="password")

    if st.sidebar.button("Accedi"):
      pwd_salvata = st.session_state.password_atleti.get(
          atleta_scelto_login, ""
      )
      if (pwd_salvata == "" and password_inserita == "") or (
          password_inserita == pwd_salvata and pwd_salvata != ""
      ):
        st.session_state.utente_loggato = atleta_scelto_login
        st.session_state.atleta_corrente = atleta_scelto_login
        st.rerun()
      else:
        st.sidebar.error("Password errata.")
    st.stop()
  else:
    password_admin = st.sidebar.text_input("Password Admin", type="password")
    if password_admin != "" and password_admin != ADMIN_PASSWORD:
      st.sidebar.error("Password Admin errata.")
      st.stop()
    st.session_state.atleta_corrente = "Atleta Principale"

# Sezione Admin per gestione atleti
if st.session_state.utente_loggato is None:
  st.sidebar.header("Gestione Atleti")
  lista_atleti = list(st.session_state.atleti.keys())
  atleta_selezionato = st.sidebar.selectbox(
      "Seleziona Atleta",
      lista_atleti,
      index=lista_atleti.index(st.session_state.atleta_corrente)
      if st.session_state.atleta_corrente in lista_atleti
      else 0,
  )
  if atleta_selezionato != st.session_state.atleta_corrente:
    st.session_state.atleta_corrente = atleta_selezionato
    salva_dati_disco()
    st.rerun()

  with st.sidebar.expander("Aggiungi o Gestisci Atleti"):
    nuovo_atleta_nome = st.text_input("Nome Nuovo Atleta")
    nuova_pwd_atleta = st.text_input("Password", type="password")
    if st.button("Crea Nuovo Atleta"):
      nome_pulito = nuovo_atleta_nome.strip()
      if nome_pulito and nome_pulito not in st.session_state.atleti:
        st.session_state.atleti[nome_pulito] = {
            "peso": 70.0,
            "altezza": 175.0,
            "eta": 30,
            "genere": "Uomo",
            "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
            "db_diario": {},
            "db_allenamenti": {},
        }
        if nuova_pwd_atleta.strip():
          st.session_state.password_atleti[nome_pulito] = (
              nuova_pwd_atleta.strip()
          )
        st.session_state.atleta_corrente = nome_pulito
        salva_dati_disco()
        st.success(f"Atleta '{nome_pulito}' aggiunto!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header(f"Parametri: {st.session_state.atleta_corrente}")
atleta_data = st.session_state.atleti[st.session_state.atleta_corrente]

peso = st.sidebar.number_input(
    "Peso (kg)",
    value=float(atleta_data.get("peso", 70.0)),
    key=f"peso_{st.session_state.atleta_corrente}",
)
altezza = st.sidebar.number_input(
    "Altezza (cm)",
    value=float(atleta_data.get("altezza", 175.0)),
    key=f"alt_{st.session_state.atleta_corrente}",
)
eta = st.sidebar.number_input(
    "Età",
    value=int(atleta_data.get("eta", 56)),
    key=f"eta_{st.session_state.atleta_corrente}",
)

atleta_data["peso"] = peso
atleta_data["altezza"] = altezza
atleta_data["eta"] = eta
salva_dati_disco()

st.sidebar.markdown("---")
data_selezionata = st.sidebar.date_input("Seleziona Giorno", value=date.today())
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

# --- CORPO PRINCIPALE DIARIO ---
st.title(
    f"Pianificatore Alimentare - {st.session_state.atleta_corrente}"
    f" ({data_str})"
)

banca_dati_corrente = st.session_state.banca_dati_df
alimenti_validi = banca_dati_corrente["Alimento"].dropna().tolist()

pasto_selezionato = st.selectbox("Seleziona il pasto", PASTI)

if alimenti_validi:
  col1, col2 = st.columns(2)
  with col1:
    alimento_scelto = st.selectbox("Alimento", alimenti_validi)
    item_row = banca_dati_corrente[
        banca_dati_corrente["Alimento"] == alimento_scelto
    ].iloc[0]
    default_q = safe_float(item_row["gr/n"]) or 100.0
  with col2:
    quantita = st.number_input(
        "Quantità (g o porzione)", min_value=1.0, value=float(default_q)
    )

  if st.button("Aggiungi al pasto"):
    fattore = quantita / default_q if default_q > 0 else 1
    nuova_riga = pd.DataFrame([
        {
            "Alimento": alimento_scelto,
            "gr/n": quantita,
            "carbo": round(safe_float(item_row["carbo"]) * fattore, 2),
            "proteine": round(safe_float(item_row["proteine"]) * fattore, 2),
            "grassi": round(safe_float(item_row["grassi"]) * fattore, 2),
            "kcal": round(safe_float(item_row["kcal"]) * fattore, 2),
        }
    ])
    db_diario_atleta[data_str][pasto_selezionato] = pd.concat(
        [db_diario_atleta[data_str][pasto_selezionato], nuova_riga],
        ignore_index=True,
    )
    salva_dati_disco()
    st.rerun()

st.markdown("### Riepilogo Pasti Giornalieri")
cols = st.columns(3)
for i, pasto in enumerate(PASTI):
  with cols[i % 3]:
    with st.container(border=True):
      st.markdown(f"**{pasto}**")
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
