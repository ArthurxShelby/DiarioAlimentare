from datetime import date, timedelta
from fpdf import FPDF
import os
import pandas as pd
import pickle
import re
import streamlit as st

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Diario Alimentare & Pianificazione Allenamento",
    page_icon="🏋️",
    layout="wide",
)

# --- 0. GESTIONE PERSISTENZA DATI E PASSWORD ADMIN ---
FILE_PERSISTENZA = "diario_allenamento_completo_db.pkl"


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
  """Salva lo stato globale su file pickle."""
  try:
    dati = {
        "atleti": st.session_state.get("atleti", {}),
        "credenziali": st.session_state.get("credenziali", {}),
        "banca_dati_df": st.session_state.get("banca_dati_df"),
        "database_allenamenti": st.session_state.get("database_allenamenti", {}),
        "password_admin": st.session_state.get("password_admin", "admin123"),
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

# Inizializzazione Password Admin
if "password_admin" not in st.session_state:
  if dati_salvati and "password_admin" in dati_salvati:
    st.session_state.password_admin = dati_salvati["password_admin"]
  else:
    st.session_state.password_admin = "admin123"

# Inizializzazione Banca Dati Alimenti
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
            "profilo": {
                "peso": 75.0,
                "altezza": 173.0,
                "eta": 56,
                "genere": "Uomo",
                "livello_allenamento": (
                    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)"
                ),
                "target_carbo": 230.0,
                "target_proteine": 165.0,
                "target_grassi": 70.0,
            },
            "db_diario": {},
        }
    }

if "credenziali" not in st.session_state:
  if dati_salvati and "credenziali" in dati_salvati:
    st.session_state.credenziali = dati_salvati["credenziali"]
  else:
    st.session_state.credenziali = {"Atleta Principale": ""}

# Inizializzazione Database Allenamenti
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

if "database_allenamenti" not in st.session_state:
  if dati_salvati and "database_allenamenti" in dati_salvati:
    st.session_state.database_allenamenti = dati_salvati[
        "database_allenamenti"
    ]
  else:
    st.session_state.database_allenamenti = database_iniziale

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

# Stato di autenticazione corrente
if "utente_autenticato" not in st.session_state:
  st.session_state["utente_autenticato"] = None

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

st.title("🏋️ Pianificatore Alimentare & Allenamento - Piattaforma Unificata")

# --- BARRA LATERALE: LOGIN E GESTIONE ACCESSO ---
st.sidebar.header("🔐 Accesso al Sistema")

lista_atleti = list(st.session_state.atleti.keys())
modalita_accesso = st.sidebar.radio(
    "Accedi come:", ["Atleta", "Amministratore Master"]
)

if modalita_accesso == "Amministratore Master":
  pwd_admin_input = st.sidebar.text_input("Password Admin", type="password")
  if st.sidebar.button("Login Admin"):
    if pwd_admin_input == st.session_state.password_admin:
      st.session_state["utente_autenticato"] = "Admin"
      st.sidebar.success("Accesso Admin effettuato!")
      st.rerun()
    else:
      st.sidebar.error("Password Admin errata.")

  if st.session_state["utente_autenticato"] == "Admin":
    st.sidebar.markdown("---")
    st.sidebar.info("Sei loggato come **Admin Master**.")
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

# --- CONTROLLO ACCESSO BLOCCANTE ---
if st.session_state["utente_autenticato"] is None:
  st.warning(
      "⚠️ Effettua il login dalla barra laterale per visualizzare i contenuti e"
      " le sezioni dedicate."
  )
  st.stop()

# --- PANNELLO ADMIN MASTER ---
if st.session_state["utente_autenticato"] == "Admin":
  st.markdown("---")
  with st.expander(
      "🛠️ Pannello Admin: Gestione Credenziali, Atleti e Banca Dati",
      expanded=True,
  ):
    st.subheader("Modifica Password Amministratore")
    vecchia_pwd = st.text_input(
        "Password Amministratore Attuale", type="password", key="old_pwd_admin"
    )
    nuova_pwd_1 = st.text_input(
        "Nuova Password Amministratore", type="password", key="new_pwd_1"
    )
    nuova_pwd_2 = st.text_input(
        "Conferma Nuova Password", type="password", key="new_pwd_2"
    )

    if st.button("Aggiorna Password Admin"):
      if vecchia_pwd != st.session_state.password_admin:
        st.error("La password attuale inserita non è corretta.")
      elif not nuova_pwd_1:
        st.error("La nuova password non può essere vuota.")
      elif nuova_pwd_1 != nuova_pwd_2:
        st.error("Le nuove password inserite non coincidono.")
      else:
        st.session_state.password_admin = nuova_pwd_1
        salva_dati_disco()
        st.success("Password dell'amministratore aggiornata con successo!")

    st.markdown("---")
    st.subheader("Crea Nuovo Account Atleta")
    nuovo_nome = st.text_input("Nome Nuovo Atleta")
    nuova_pwd_atleta = st.text_input(
        "Password di Accesso Atleta", type="password"
    )

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
                "target_carbo": 230.0,
                "target_proteine": 165.0,
                "target_grassi": 70.0,
            },
            "db_diario": {},
        }
        st.session_state.credenziali[nome_pulito] = nuova_pwd_atleta
        salva_dati_disco()
        st.success(f"Atleta '{nome_pulito}' creato correttamente!")
        st.rerun()

    st.markdown("---")
    st.subheader("Banca Dati Alimenti (Globale)")
    st.dataframe(st.session_state.banca_dati_df, use_container_width=True)

  st.stop()

# --- AREA UTENTE STANDARD ---
atleta_corrente = st.session_state["utente_autenticato"]
dati_atleta = st.session_state.atleti[atleta_corrente]

st.sidebar.markdown("---")
st.sidebar.header(f"⚙️ Parametri Atleta: {atleta_corrente} (Mifflin-St Jeor)")

profilo = dati_atleta.setdefault("profilo", {})
peso = st.sidebar.number_input(
    "Peso (kg)", value=float(profilo.get("peso", 75.0))
)
altezza = st.sidebar.number_input(
    "Altezza (cm)", value=float(profilo.get("altezza", 173.0))
)
eta = st.sidebar.number_input("Età (anni)", value=int(profilo.get("eta", 56)))
genere = st.sidebar.selectbox(
    "Genere", ["Uomo", "Donna"], index=0 if profilo.get("genere") == "Uomo" else 1
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

st.sidebar.markdown("### Target Macronutrienti (Mifflin)")
target_carbo = st.sidebar.number_input(
    "Target Carboidrati (g)", value=float(profilo.get("target_carbo", 230.0))
)
target_proteine = st.sidebar.number_input(
    "Target Proteine (g)", value=float(profilo.get("target_proteine", 165.0))
)
target_grassi = st.sidebar.number_input(
    "Target Grassi (g)", value=float(profilo.get("target_grassi", 70.0))
)

if (
    profilo.get("peso") != peso
    or profilo.get("altezza") != altezza
    or profilo.get("eta") != eta
    or profilo.get("genere") != genere
    or profilo.get("livello_allenamento") != livello_allenamento
    or profilo.get("target_carbo") != target_carbo
    or profilo.get("target_proteine") != target_proteine
    or profilo.get("target_grassi") != target_grassi
):
  profilo.update({
      "peso": peso,
      "altezza": altezza,
      "eta": eta,
      "genere": genere,
      "livello_allenamento": livello_allenamento,
      "target_carbo": target_carbo,
      "target_proteine": target_proteine,
      "target_grassi": target_grassi,
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

st.sidebar.info(f"**BMR Mifflin:** {bmr:.0f} kcal | **TDEE:** {obj_kcal:.0f} kcal")

# Navigazione Sezioni
sezione_scelta = st.radio(
    "Seleziona Sezione:",
    ["Diario Alimentare", "Pianificazione Allenamenti"],
    horizontal=True,
)

st.markdown("---")

if sezione_scelta == "Diario Alimentare":
  st.subheader(f"📅 Diario Alimentare di {atleta_corrente}")
  data_selezionata = st.date_input("Data Diario", value=date.today())
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
      alimento_scelto = st.selectbox("Alimento", alimenti_validati)
      item_row = banca_dati_corrente[
          banca_dati_corrente["Alimento"].astype(str) == str(alimento_scelto)
      ].iloc[0]
      val_gr_n = safe_float(item_row["gr/n"])
      default_q = int(val_gr_n) if val_gr_n > 0 else 100

    with col_ins2:
      quantita = st.number_input(
          "Quantità (g o porzione)", min_value=1.0, value=float(default_q)
      )

    if st.button("Aggiungi al pasto"):
      pasto_ins = st.selectbox("Scegli pasto", PASTI, key="pasto_ins_selezionato")
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

  # Calcolo totali giornalieri consumati
  tot_carbo = 0.0
  tot_proteine = 0.0
  tot_grassi = 0.0
  tot_kcal = 0.0

  for pasto in PASTI:
    df_p = db_diario[data_str][pasto]
    if not df_p.empty:
      tot_carbo += safe_float(df_p["carbo"].sum())
      tot_proteine += safe_float(df_p["proteine"].sum())
      tot_grassi += safe_float(df_p["grassi"].sum())
      tot_kcal += safe_float(df_p["kcal"].sum())

  st.markdown("### 📊 Bilancio Giornaliero & Mancanze (Profilo Mifflin)")
  col_m1, col_m2, col_m3, col_m4 = st.columns(4)

  def delta_str(consumato, target):
    diff = target - consumato
    if diff > 0:
      return f"Mancano: {diff:.1f}g", "normal"
    else:
      return f"In eccesso: {abs(diff):.1f}g", "inverse"

  with col_m1:
    mancanza_c, _ = delta_str(tot_carbo, target_carbo)
    st.metric(
        "Carboidrati",
        f"{tot_carbo:.1f}g",
        delta=mancanza_c,
        delta_color="off" if "Mancano" in mancanza_c else "inverse",
    )
    st.caption(f"Target Mifflin: {target_carbo}g")

  with col_m2:
    mancanza_p, _ = delta_str(tot_proteine, target_proteine)
    st.metric(
        "Proteine",
        f"{tot_proteine:.1f}g",
        delta=mancanza_p,
        delta_color="off" if "Mancano" in mancanza_p else "inverse",
    )
    st.caption(f"Target Mifflin: {target_proteine}g")

  with col_m3:
    mancanza_g, _ = delta_str(tot_grassi, target_grassi)
    st.metric(
        "Grassi",
        f"{tot_grassi:.1f}g",
        delta=mancanza_g,
        delta_color="off" if "Mancano" in mancanza_g else "inverse",
    )
    st.caption(f"Target Mifflin: {target_grassi}g")

  with col_m4:
    mancanza_k, _ = delta_str(tot_kcal, obj_kcal)
    st.metric(
        "Calorie Totali",
        f"{tot_kcal:.0f} kcal",
        delta=mancanza_k,
        delta_color="off" if "Mancano" in mancanza_k else "inverse",
    )
    st.caption(f"Target TDEE: {obj_kcal:.0f} kcal")

  st.markdown("---")
  st.markdown("### Riepilogo Pasti Giornalieri")
  cols_pasti = st.columns(3)
  for i, pasto in enumerate(PASTI):
    with cols_pasti[i % 3]:
      with st.container(border=True):
        st.markdown(f"**{pasto}**")
        df_p = db_diario[data_str][pasto]
        if not df_p.empty:
          st.dataframe(df_p, use_container_width=True)
          if st.button(f"Svuota {pasto}", key=f"clear_{pasto}"):
            db_diario[data_str][pasto] = pd.DataFrame(
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

else:
  st.subheader("🚴 Pianificazione Allenamento per Anno Solare")

  ftp_atleta = 279
  st.sidebar.markdown(f"## Riferimenti FTP ({ftp_atleta}W)")
  st.sidebar.markdown(
      f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W"
  )
  st.sidebar.markdown(
      f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W"
  )

  col_anno, col_mese = st.columns(2)
  with col_anno:
    anno_selezionato = st.number_input(
        "Anno Solare Corrente:", min_value=2020, max_value=2100, value=2026, step=1
    )
  with col_mese:
    mese_selezionato = st.selectbox("Mese Corrente:", elenco_mesi_completo)

  st.markdown("---")

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

  dati_correnti = st.session_state.database_allenamenti[anno_selezionato][
      mese_selezionato
  ]

  if isinstance(dati_correnti, dict):
    righe_tabella = []
    for settimana, giorni in dati_correnti.items():
      for giorno, dettagli in giorni.items():
        righe_tabella.append({
            "Settimana": settimana,
            "Giorno": giorno,
            "Esercizio / Nome": dettagli.get("Esercizio", ""),
            "Watt": int(dettagli.get("Watt", 0)),
            "RPM": int(dettagli.get("RPM", 0)),
            "Ripetizioni": int(dettagli.get("Ripetizioni", 0)),
            "Lavoro (min)": int(dettagli.get("Lavoro_m", 0)),
            "Recupero (min)": int(dettagli.get("Recupero_m", 0)),
        })
    df_base_mese = pd.DataFrame(righe_tabella)
    st.session_state.database_allenamenti[anno_selezionato][
        mese_selezionato
    ] = df_base_mese
    salva_dati_disco()
  else:
    df_base_mese = dati_correnti

  with st.expander("📂 Carica piano di lavoro tramite file CSV"):
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
          salva_dates = salva_dati_disco()
          st.success("File CSV caricato e salvato correttamente!")
          st.rerun()
        else:
          st.error(
              f"Il file CSV deve contenere le colonne: {colonne_attese}"
          )
      except Exception as e:
        st.error(f"Errore nella lettura del file: {e}")

  st.subheader(
      f"✍️ Gestione Allenamenti: **{mese_selezionato} {anno_selezionato}**"
  )
  df_modificato = st.data_editor(
      df_base_mese,
      num_rows="dynamic",
      use_container_width=True,
      key=f"editor_{anno_selezionato}_{mese_selezionato}",
  )

  if not df_modificato.equals(df_base_mese):
    st.session_state.database_allenamenti[anno_selezionato][
        mese_selezionato
    ] = df_modificato
    salva_dati_disco()
