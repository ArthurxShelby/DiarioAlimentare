from datetime import date, timedelta
from fpdf import FPDF
import os
import pandas as pd
import pickle
import re
import streamlit as st

# --- CONFIGURAZIONE PASSWORD AMMINISTRATORE ---
PASSWORD_ADMIN = "admin123"

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare & Allenamento - Isolamento Atleti",
    page_icon="",
    layout="wide",
)

# --- 0. GESTIONE PERSISTENZA DATI ISOLATA ---
FILE_PERSISTENZA = "diario_alimentare_isolato_db.pkl"


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
  """Salva lo stato isolato di ogni atleta e della banca dati globale."""
  try:
    dati = {
        "atleti": st.session_state.get("atleti", {}),
        "credenziali": st.session_state.get("credenziali", {}),
        "banca_dati_df": st.session_state.get("banca_dati_df"),
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
  return None


dati_salvati = carica_dati_disco()

DEFAULT_BANCA_DATI = [
    {
        "Alimento": "avena",
        "gr/n": 60,
        "carbo": 37.8,
        "proteine": 7.2,
        "grassi": 4.2,
        "kcal": 216.0,
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
        "Alimento": "olio evo",
        "gr/n": 1,
        "carbo": 0.0,
        "proteine": 0.0,
        "grassi": 10.0,
        "kcal": 90.0,
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

# Inizializzazione Atleti e Credenziali con isolamento rigoroso
if "atleti" not in st.session_state:
  if dati_salvati and "atleti" in dati_salvati:
    st.session_state.atleti = dati_salvati["atleti"]
  else:
    st.session_state.atleti = {
        "Atleta Principale": {
            "profilo": {
                "peso": 75.0,
                "altezza": 173.0,
                "eta": 56,
                "genere": "Uomo",
                "livello_allenamento": (
                    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)"
                ),
            },
            "db_diario": {},
            "dati_allenamento": {},
        }
    }

if "credenziali" not in st.session_state:
  if dati_salvati and "credenziali" in dati_salvati:
    st.session_state.credenziali = dati_salvati["credenziali"]
  else:
    st.session_state.credenziali = {"Atleta Principale": ""}

# Stato di autenticazione corrente
if "utente_autenticato" not in st.session_state:
  st.session_state["utente_autenticato"] = None

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

st.title("Pianificatore Alimentare & Allenamento - Accesso Isolato")

# --- SISTEMA DI LOGIN / SELEZIONE PROFILO PROTETTO ---
st.sidebar.header("🔐 Accesso al Sistema")

lista_atleti = list(st.session_state.atleti.keys())

modalita_accesso = st.sidebar.radio(
    "Accedi come:", ["Atleta", "Amministratore Master"]
)

if modalita_accesso == "Amministratore Master":
  pwd_admin_input = st.sidebar.text_input("Password Admin", type="password")
  if st.sidebar.button("Login Admin"):
    if pwd_admin_input == PASSWORD_ADMIN:
      st.session_state["utente_autenticato"] = "Admin"
      st.sidebar.success("Accesso Admin effettuato!")
      st.rerun()
    else:
      st.sidebar.error("Password Admin errata.")

  if st.session_state["utente_autenticato"] == "Admin":
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Sei loggato come **Admin Master**. Puoi creare nuovi atleti o"
        " visionare/gestire la banca dati."
    )
    if st.sidebar.button("Logout Admin"):
      st.session_state["utente_autenticato"] = None
      st.rerun()

else:
  atleta_scelto_login = st.sidebar.selectbox(
      "Seleziona il tuo Profilo", lista_atleti
  )
  pwd_atleta_input = st.sidebar.text_input(
      f"Password per '{atleta_scelto_login}'", type="password"
  )

  if st.sidebar.button("Accedi al Profilo"):
    password_registrata = st.session_state.credenziali.get(
        atleta_scelto_login, ""
    )
    if password_registrata == "" or pwd_atleta_input == password_registrata:
      st.session_state["utente_autenticato"] = atleta_scelto_login
      st.success(f"Benvenuto, {atleta_scelto_login}!")
      st.rerun()
    else:
      st.sidebar.error("Password non corretta per questo profilo.")

  if st.session_state["utente_autenticato"] and st.session_state[
      "utente_autenticato"
  ] not in ["Admin", None]:
    st.sidebar.success(
        f"Utente attivo: **{st.session_state['utente_autenticato']}**"
    )
    if st.sidebar.button("Disconnetti Profilo"):
      st.session_state["utente_autenticato"] = None
      st.rerun()

# --- BLOCCO DI SICUREZZA PRINCIPALE ---
if st.session_state["utente_autenticato"] is None:
  st.warning(
      "⚠️ Effettua il login dalla barra laterale (selezionando il tuo profilo"
      " con relativa password o accedendo come Admin) per visualizzare i tuoi"
      " dati personali e la tua sottopagina di allenamento."
  )
  st.stop()

# --- GESTIONE ADMIN: CREAZIONE NUOVI UTENTI ISOLATI ---
if st.session_state["utente_autenticato"] == "Admin":
  st.markdown("---")
  with st.expander(
      "🛠️ Pannello Admin: Gestione Atleti e Banca Dati", expanded=True
  ):
    st.subheader("Crea Nuovo Account Atleta Isolato")
    nuovo_nome = st.text_input("Nome Nuovo Atleta")
    nuova_pwd = st.text_input("Password di Accesso Atleta", type="password")

    if st.button("Crea Atleta"):
      nome_pulito = nuovo_nome.strip()
      if not nome_pulito:
        st.error("Inserisci un nome valido.")
      elif nome_pulito in st.session_state.atleti:
        st.warning("Esiste già un atleta con questo nome.")
      else:
        st.session_state.atleti[nome_pulito] = {
            "profilo": {
                "peso": 70.0,
                "altezza": 175.0,
                "eta": 40,
                "genere": "Uomo",
                "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
            },
            "db_diario": {},
            "dati_allenamento": {},
        }
        st.session_state.credenziali[nome_pulito] = nuova_pwd
        salva_dati_disco()
        st.success(
            f"Atleta '{nome_pulito}' creato con spazio dati e allenamento"
            " completamente isolato!"
        )
        st.rerun()

    st.markdown("---")
    st.subheader("Gestione Banca Dati Alimenti (Globale)")
    st.dataframe(st.session_state.banca_dati_df, use_container_width=True)

  st.stop()

# --- ACCESSO UTENTE STANDARD (ISOLATO AL 100%) ---
atleta_corrente = st.session_state["utente_autenticato"]
dati_atleta = st.session_state.atleti[atleta_corrente]

st.sidebar.markdown("---")
st.sidebar.header(f"⚙️ Parametri & Allenamento: {atleta_corrente}")

profilo = dati_atleta.setdefault("profilo", {})
peso = st.sidebar.number_input(
    "Peso (kg)", value=float(profilo.get("peso", 75.0))
)
altezza = st.sidebar.number_input(
    "Altezza (cm)", value=float(profilo.get("altezza", 173.0))
)
eta = st.sidebar.number_input("Età (anni)", value=int(profilo.get("eta", 56)))
genere = st.sidebar.selectbox(
    "Genere", ["Uomo", "Donna"], index=0 if profilo.get("genere", "Uomo") == "Uomo" else 1
)
livello_allenamento = st.sidebar.selectbox(
    "Intensità Allenamento / Attività",
    [
        "Riposo / Sedentario (PAL 1.2)",
        "Attività Leggera (PAL 1.375)",
        "Allenamento Moderato (PAL 1.55)",
        "Allenamento Intenso / Rouleur-Climber (PAL 1.725)",
        "Doppio Allenamento / Estremo (PAL 1.9)",
    ],
    index=3,
)

if (
    profilo.get("peso") != peso
    or profilo.get("altezza") != altezza
    or profilo.get("eta") != eta
    or profilo.get("genere") != genere
    or profilo.get("livello_allenamento") != livello_allenamento
):
  profilo.update({
      "peso": peso,
      "altezza": altezza,
      "eta": eta,
      "genere": genere,
      "livello_allenamento": livello_allenamento,
  })
  salva_dati_disco()

pal_dict = {
    "Riposo / Sedentario (PAL 1.2)": 1.2,
    "Attività Leggera (PAL 1.375)": 1.375,
    "Allenamento Moderato (PAL 1.55)": 1.55,
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)": 1.725,
    "Doppio Allenamento / Estremo (PAL 1.9)": 1.9,
}
pal_selezionato = pal_dict[livello_allenamento]

bmr = (
    (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
    if genere == "Uomo"
    else (10 * peso) + (6.25 * altezza) - (5 * eta) - 161
)
tdee = bmr * pal_selezionato
obj_kcal = round(tdee, 0)
obj_carbo, obj_prot, obj_grassi = 230.0, 165.0, 70.0

st.sidebar.info(
    f"**Profilo Personale:** {atleta_corrente}\n\n**TDEE:** {obj_kcal:.0f} kcal"
)

menu_principale = st.radio(
    "Sezione:", ["Diario Alimentare", "Sottopagina Allenamento Personale"], horizontal=True
)

st.markdown("---")

if menu_principale == "Diario Alimentare":
  st.subheader(f"📅 Diario Alimentare di {atleta_corrente}")
  data_selezionata = st.date_input("Data", value=date.today())
  data_str = data_selezionata.strftime("%Y-%m-%d")

  db_diario = dati_atleta.setdefault("db_diario", {})
  if data_str not in db_diario:
    db_diario[data_str] = {
        pasto: pd.DataFrame(
            columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]
        )
        for pasto in PASTI
    }
    salva_dati_disco()

  st.info(
      "Stai visualizzando e modificando esclusivamente i tuoi dati alimentari"
      " protetti."
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

    if st.button("Aggiungi al pasto", key="btn_aggiungi_principale"):
      pasto_ins = st.selectbox("Scegli pasto", PASTI, key="sel_pasto_aggiunta")
      fattore = quantita / default_q if default_q > 0 else 1
      c_calc = round(safe_float(item_row["carbo"]) * fattore, 2)
      p_calc = round(safe_float(item_row["proteine"]) * fattore, 2)
      g_calc = round(safe_float(item_row["grassi"]) * fattore, 2)
      k_calc = round(safe_float(item_row["kcal"]) * fattore, 2)

      nuova_riga = pd.DataFrame([
          {
              "Alimento": alimento_scelto,
              "gr/n": quantita,
              "carbo": c_calc,
              "proteine": p_calc,
              "grassi": g_calc,
              "kcal": k_calc,
          }
      ])
      db_diario[data_str][pasto_ins] = pd.concat(
          [db_diario[data_str][pasto_ins], nuova_riga], ignore_index=True
      )
      salva_dati_disco()
      st.rerun()

else:
  st.subheader(f"🚴 Sottopagina Allenamento Privata - {atleta_corrente}")
  st.markdown(
      "Questa sottopagina contiene i tuoi dati di allenamento specifici,"
      " completamente separati e invisibili agli altri utenti."
  )

  dati_allenamento = dati_atleta.setdefault("dati_allenamento", {})

  note_allenamento = st.text_area(
      "Note di Allenamento / Programma Settimanale",
      value=dati_allenamento.get("note", ""),
  )
  ftp_personale = st.number_input(
      "FTP Personale (Watt)", value=int(dati_allenamento.get("ftp", 279))
  )

  if st.button("Salva Dati Allenamento Personali"):
    dati_allenamento["note"] = note_allenamento
    dati_allenamento["ftp"] = ftp_personale
    salva_dati_disco()
    st.success(
        "I tuoi dati di allenamento privati sono stati salvati con successo!"
    )
