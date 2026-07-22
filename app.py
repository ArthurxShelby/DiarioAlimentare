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
    page_icon="",
    layout="wide",
)

# --- 0. GESTIONE PERSISTENZA DATI E PULIZIA ---
FILE_PERSISTENZA = "diario_alimentare_multi_db.pkl"


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
        "atleta_corrente": st.session_state.get("atleta_corrente"),
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
]

DATABASE_ALLENAMENTI_INIZIALE = {
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
            }
        }
    }
}

ELENCO_MESI_COMPLETO = [
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
            "db_allenamenti_anni": DATABASE_ALLENAMENTI_INIZIALE.copy(),
        }
    }

for a_nome, a_dati in st.session_state.atleti.items():
  if "db_allenamenti_anni" not in a_dati:
    a_dati["db_allenamenti_anni"] = DATABASE_ALLENAMENTI_INIZIALE.copy()

if "password_atleti" not in st.session_state:
  if dati_salvati and "password_atleti" in dati_salvati:
    st.session_state.password_atleti = dati_salvati["password_atleti"]
  else:
    st.session_state.password_atleti = {}

if "utente_loggato" not in st.session_state:
  st.session_state.utente_loggato = None

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

ADMIN_PASSWORD = "adminpassword123"

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

    if st.sidebar.button("Accedi al Diario & Allenamenti"):
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
        st.sidebar.error("Password errata o non impostata.")
    st.stop()
  else:
    password_admin = st.sidebar.text_input(
        "Password Admin (opzionale)", type="password"
    )
    if password_admin != "" and password_admin != ADMIN_PASSWORD:
      st.sidebar.error("Password Admin errata.")
      st.stop()
    st.session_state.atleta_corrente = "Atleta Principale"

st.title(
    f"Pianificatore & Allenamento -"
    f" {st.session_state.get('atleta_corrente', 'Atleta')}"
)

if st.session_state.utente_loggato is None:
  st.sidebar.header("Gestione Atleti")
  lista_atleti = list(st.session_state.atleti.keys())
  atleta_selezionato = st.sidebar.selectbox(
      "Seleziona Atleta",
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

  with st.sidebar.expander("Aggiungi o Gestisci Atleti"):
    nuovo_atleta_nome = st.text_input("Nome Nuovo Atleta")
    nuova_pwd_atleta = st.text_input(
        "Password per il nuovo atleta", type="password"
    )
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
            "db_allenamenti": {},
            "db_allenamenti_anni": DATABASE_ALLENAMENTI_INIZIALE.copy(),
        }
        if nuova_pwd_atleta.strip() != "":
          st.session_state.password_atleti[nome_pulito] = (
              nuova_pwd_atleta.strip()
          )
        st.session_state.atleta_corrente = nome_pulito
        salva_dati_disco()
        st.success(
            f"Atleta '{nome_pulito}' aggiunto con database allenamenti isolato!"
        )
        st.rerun()

st.sidebar.markdown("---")
atleta_data = st.session_state.atleti[st.session_state.atleta_corrente]

peso = st.sidebar.number_input(
    "Peso (kg)",
    value=float(atleta_data.get("peso", 70.0)),
    key=f"peso_{st.session_state.atleta_corrente}",
)
altezza = st.sidebar.number_input(
    "Altezza (cm)",
    value=float(atleta_data.get("altezza", 175.0)),
    key=f"altezza_{st.session_state.atleta_corrente}",
)
eta = st.sidebar.number_input(
    "Età (anni)",
    value=int(atleta_data.get("eta", 56)),
    key=f"eta_{st.session_state.atleta_corrente}",
)

atleta_data["peso"] = peso
atleta_data["altezza"] = altezza
atleta_data["eta"] = eta
salva_dati_disco()

st.sidebar.markdown("---")
st.sidebar.header("Seleziona Giorno Diario")
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

st.markdown("---")
st.header(
    f"🏋️ Pianificazione Allenamento per Anno Solare -"
    f" {st.session_state.atleta_corrente}"
)

db_allenamenti_anni = atleta_data.setdefault(
    "db_allenamenti_anni", DATABASE_ALLENAMENTI_INIZIALE.copy()
)

col_anno, col_mese = st.columns(2)
with col_anno:
  anno_selezionato = st.number_input(
      "Anno Solare Corrente:",
      min_value=2020,
      max_value=2100,
      value=2026,
      step=1,
      key=f"anno_{st.session_state.atleta_corrente}",
  )
with col_mese:
  mese_selezionato = st.selectbox(
      "Mese Corrente:",
      ELENCO_MESI_COMPLETO,
      key=f"mese_{st.session_state.atleta_corrente}",
  )

if anno_selezionato not in db_allenamenti_anni:
  db_allenamenti_anni[anno_selezionato] = {}

if mese_selezionato not in db_allenamenti_anni[anno_selezionato]:
  db_allenamenti_anni[anno_selezionato][mese_selezionato] = pd.DataFrame(
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

dati_correnti_all = db_allenamenti_anni[anno_selezionato][mese_selezionato]

if isinstance(dati_correnti_all, dict):
  righe_tabella = []
  for settimana, giorni in dati_correnti_all.items():
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
  db_allenamenti_anni[anno_selezionato][mese_selezionato] = df_base_mese
  salva_dati_disco()
else:
  df_base_mese = dati_correnti_all

df_modificato_all = st.data_editor(
    df_base_mese,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_all_{st.session_state.atleta_corrente}_{anno_selezionato}_{mese_selezionato}",
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

if not df_modificato_all.equals(df_base_mese):
  db_allenamenti_anni[anno_selezionato][mese_selezionato] = df_modificato_all
  salva_dati_disco()

st.success(
    f"Dati di allenamento sincronizzati e protetti per:"
    f" **{st.session_state.atleta_corrente}**"
)

# Eventuale riferimento esterno in formato markdown corretto all'interno di st.markdown
st.markdown(
    "[Tutorial on Multi-User Streamlit"
    " Apps](https://www.youtube.com/watch?v=eCbH2nPL9sU)"
)
