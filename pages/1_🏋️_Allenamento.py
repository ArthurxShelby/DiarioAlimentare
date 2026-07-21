import datetime
from requests.auth import HTTPBasicAuth
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Pianificazione Allenamento Perpetua",
    page_icon="🏋️",
    layout="wide",
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

st.sidebar.markdown("---")
st.sidebar.header("🗓️ Selettore Periodo")

# Selezione della data di riferimento per il calendario perpetuo
data_riferimento = st.sidebar.date_input(
    "Data di riferimento:", datetime.date.today()
)

# Calcola il lunedì della settimana selezionata per allineare il microciclo
inizio_settimana = data_riferimento - datetime.timedelta(
    days=data_riferimento.weekday()
)

# Calcolo perpetuo basato sul modello 3+1 rispetto a una data di inizio (es. 1 agosto 2026)
data_inizio_prep = datetime.date(2026, 8, 1)
differenza_giorni = (inizio_settimana - data_inizio_prep).days
numero_settimana_totale = max(0, differenza_giorni // 7) + 1
ciclo_4_settimane = ((numero_settimana_totale - 1) % 4) + 1

if ciclo_4_settimane == 4:
  fase_corrente = "Settimana 4: Scarico ed Assimilazione (Volumi dimezzati)"
  st.sidebar.warning(f"Fase: {fase_corrente}")
else:
  fase_corrente = f"Settimana {ciclociclo_str if 'ciclociclo_str' in locals() else ciclo_4_settimane} di Carico"
  st.sidebar.success(f"Fase: Settimana {ciclo_4_settimane} (Carico)")

st.title("🏋️ Pianificazione Allenamento Perpetua & Intervals.icu")
st.write(
    "Gestione dei microcicli con modello **3+1** (3 settimane di carico e 1 di"
    " scarico) e sincronizzazione diretta con il calendario."
)

# --- 2. GENERAZIONE TABELLA SETTIMANALE PERPETUA ---
giorni_settimana = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
]

righe_tabella = []
for i, nome_giorno in enumerate(giorni_settimana):
  data_corrente = inizio_settimana + datetime.timedelta(days=i)

  # Assegnazione automatica del workout in base al giorno e alla fase 3+1
  if i == 1:  # Martedì (Focus Soglia Z4)
    esercizio = (
        "Scarico Soglia Z4 (Agilità 90 RPM)"
        if ciclo_4_settimane == 4
        else "Soglia Z4: 3 x 8 min. Rec. 5 min Z1"
    )
    watt = int(260 if ciclo_4_settimane == 4 else 265)
    rpm = 90
    rip = 3
    lav = 8
    rec = 5
  elif i == 3:  # Giovedì (Focus Sweet Spot)
    esercizio = (
        "Scarico Sweet Spot (85 RPM)"
        if ciclo_4_settimane == 4
        else "Sweet Spot: 2 x 20 min. Rec. 5 min Z1"
    )
    watt = int(240 if ciclo_4_settimane == 4 else 250)
    rpm = 85
    rip = 2
    lav = 20
    rec = 5
  elif i in [5, 6]:  # Weekend
    esercizio = "Uscita lunga / Fondo Z2"
    watt = 170
    rpm = 90
    rip = 1
    lav = 120
    rec = 0
  else:
    esercizio = "Riposo / Recupero attivo"
    watt = 130
    rpm = 95
    rip = 1
    lav = 20
    rec = 0

  righe_tabella.append({
      "Data": data_corrente.strftime("%d/%m/%Y"),
      "Giorno": nome_giorno,
      "Esercizio / Nome": esercizio,
      "Watt": watt,
      "RPM": rpm,
      "Ripetizioni": rip,
      "Lavoro (min)": lav,
      "Recupero (min)": rec,
  })

df_base_settimana = pd.DataFrame(righe_tabella)

# --- 3. SEZIONE IMPORTAZIONE / CARICAMENTO CSV ---
with st.expander(
    "📂 Integra o carica piano di lavoro tramite file CSV", expanded=False
):
  st.write(
      "Carica un file CSV formattato con le stesse colonne della tabella"
      " sottostante per personalizzare la settimana."
  )
  file_caricato = st.file_uploader(
      "Seleziona il file CSV", type=["csv"], key="uploader_perpetuo"
  )

  if file_caricato is not None:
    try:
      df_caricato = pd.read_csv(file_caricato, sep=None, engine="python")
      df_caricato.columns = df_caricato.columns.str.strip()

      colonne_attese = [
          "Data",
          "Giorno",
          "Esercizio / Nome",
          "Watt",
          "RPM",
          "Ripetizioni",
          "Lavoro (min)",
          "Recupero (min)",
      ]

      if all(col in df_caricato.columns for col in colonne_attese):
        df_base_settimana = df_caricato[colonne_attese]
        st.success("File CSV caricato e integrato con successo nella tabella!")
      else:
        st.error(
            "Il file CSV non contiene le colonne corrette. Assicurati che siano"
            f" presenti: {colonne_attese}"
        )
    except Exception as e:
      st.error(f"Errore nella lettura del file CSV: {e}")

# --- 4. TABELLA INTERATTIVA DI MODIFICA ---
st.subheader(
    f"✍️ Modifica Allenamenti Settimana dal {inizio_settimana.strftime('%d/%m/%Y')}"
)
df_modificato = st.data_editor(
    df_base_settimana,
    num_rows="fixed",
    use_container_width=True,
    key="editor_settimana",
    column_config={
        "Data": st.column_config.TextColumn(disabled=True),
        "Giorno": st.column_config.TextColumn(disabled=True),
        "Watt": st.column_config.NumberColumn(min_value=50, max_value=500, step=1),
        "RPM": st.column_config.NumberColumn(min_value=60, max_value=120, step=1),
        "Ripetizioni": st.column_config.NumberColumn(
            min_value=1, max_value=20, step=1
        ),
        "Lavoro (min)": st.column_config.NumberColumn(
            min_value=1, max_value=300, step=1
        ),
        "Recupero (min)": st.column_config.NumberColumn(
            min_value=0, max_value=60, step=1
        ),
    },
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. SINCRONIZZAZIONE INTERVALS.ICU ---
if st.button("🚀 Invia Allenamenti a Intervals.icu", type="primary"):
  if "intervals" not in st.secrets:
    st.error(
        "⚠️ Credenziali di Intervals.icu non configurate nei secrets di"
        " Streamlit!"
    )
  else:
    try:
      atleta_id = st.secrets["intervals"]["athlete_id"]
      api_key = st.secrets["intervals"]["api_key"]
      auth = HTTPBasicAuth("API_KEY", api_key)

      successi = 0
      for index, row in df_modificato.iterrows():
        # Converte la stringa della data nel formato ISO per l'API
        data_obj = datetime.datetime.strptime(row["Data"], "%d/%m/%Y").date()

        # Crea la descrizione strutturata dell'allenamento
        descrizione_workout = (
            f"🏋️ {row['Esercizio / Nome']}\nTarget Watt: {row['Watt']}W\nRPM:"
            f" {row['RPM']}\nRipetizioni: {row['Ripetizioni']}\nLavoro:"
            f" {row['Lavoro (min)']} min\nRecupero: {row['Recupero (min)']} min"
        )

        payload = {
            "category": "WORKOUT",
            "start_date_local": data_obj.isoformat() + "T09:00:00",
            "name": f"🏋️ {row['Esercizio / Nome']}",
            "description": descrizione_workout,
            "type": "Ride",
            "color": "yellow",
        }

        url_post = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events"
        response = requests.post(url_post, json=payload, auth=auth)

        if response.status_code in [200, 201]:
          successi += 1

      st.success(
          f"Sincronizzazione completata! Inviati {successi} eventi a"
          " Intervals.icu con successo."
      )
    except Exception as e:
      st.error(f"Errore durante la connessione a Intervals.icu: {e}")

# --- 6. STRUMENTO DI PULIZIA DI EMERGENZA ---
with st.expander("🛠️ Pannello di Emergenza: Cancella file dal calendario"):
  st.write(
      "Se qualche allenamento risulta errato o vuoi ripulire il calendario nel"
      " periodo selezionato, usa questo pulsante."
  )

  col_start, col_end = st.columns(2)
  with col_start:
    data_inizio_pulizia = st.date_input(
        "Data Inizio:", inizio_settimana
    )
  with col_end:
    data_fine_pulizia = st.date_input(
        "Data Fine:", inizio_settimana + datetime.timedelta(days=6)
    )

  if st.button("🗑️ Elimina tutti gli allenamenti (🏋️) nel periodo selezionato"):
    if "intervals" not in st.secrets:
      st.error("⚠️ Configura prima le credenziali nei secrets!")
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
          st.success(f"Pulizia completata! Eliminati {count} eventi.")
          st.rerun()
        else:
          st.error(f"Errore nel recupero eventi: {response.text}")
      except Exception as e:
        st.error(f"Errore: {e}")
