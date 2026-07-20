import streamlit as st
import datetime
import requests
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide")

# --- 1. RIFERIMENTI FTP & SIDEBAR ---
ftp_atleta = 279  

st.sidebar.markdown(f"## Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM")
st.sidebar.markdown("**Cadenza SS:** ~85 RPM")

# --- 2. DIZIONARIO STRUTTURATO (MESE -> SETTIMANA -> GIORNO) ---
# Ripristinato esattamente con la struttura a cascata corretta
database_allenamenti = {
    "Agosto": {
        "Settimana 1 (Carico Base)": {
            "Martedì": {"Esercizio": "Soglia Z4: 2 x 6 min. Rec. 5 min Z1", "Watt": 260, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 6, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Sweet Spot: 1 x 20 min continui", "Watt": 245, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 0}
        },
        "Settimana 2 (Carico Intermedio)": {
            "Martedì": {"Esercizio": "Soglia Z4: 3 x 6 min. Rec. 5 min Z1", "Watt": 260, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 6, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Sweet Spot: 1 x 30 min continui", "Watt": 245, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 30, "Recupero_m": 0}
        },
        "Settimana 3 (Picco di Carico)": {
            "Martedì": {"Esercizio": "Soglia Z4: 4 x 6 min. Rec. 4 min Z1", "Watt": 262, "RPM": 90, "Ripetizioni": 4, "Lavoro_m": 6, "Recupero_m": 4},
            "Giovedì": {"Esercizio": "Sweet Spot: 1 x 40 min continui", "Watt": 248, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 40, "Recupero_m": 0}
        },
        "Settimana 4 (Scarico)": {
            "Martedì": {"Esercizio": "Soglia attiva: Solo 1 x 6 min in Z4", "Watt": 260, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 6, "Recupero_m": 0},
            "Giovedì": {"Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS", "Watt": 150, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 15, "Recupero_m": 0}
        }
    },
    "Settembre": {
        "Settimana 1 (Carico Base)": {
            "Martedì": {"Esercizio": "Soglia Z4: 3 x 8 min. Rec. 5 min Z1", "Watt": 265, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 8, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Sweet Spot: 2 x 15 min. Rec. 5 min Z1", "Watt": 250, "RPM": 85, "Ripetizioni": 2, "Lavoro_m": 15, "Recupero_m": 5}
        },
        "Settimana 2 (Carico Intermedio)": {
            "Martedì": {"Esercizio": "Soglia Z4: 3 x 10 min. Rec. 5 min Z1", "Watt": 265, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 10, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Sweet Spot: 2 x 20 min. Rec. 5 min Z1", "Watt": 250, "RPM": 85, "Ripetizioni": 2, "Lavoro_m": 20, "Recupero_m": 5}
        },
        "Settimana 3 (Picco di Carico)": {
            "Martedì": {"Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1", "Watt": 268, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 12, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Sweet Spot: 1 x 45 min continui", "Watt": 252, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 45, "Recupero_m": 0}
        },
        "Settimana 4 (Scarico)": {
            "Martedì": {"Esercizio": "Mantenimento: 2 x 5 min Z4. Rec. 4 min", "Watt": 260, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 5, "Recupero_m": 4},
            "Giovedì": {"Esercizio": "Scarico: Recupero Attivo Z1 ed agilità", "Watt": 145, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 0}
        }
    },
    "Ottobre": {
        "Settimana 1 (Carico Base)": {
            "Martedì": {"Esercizio": "Soglia Z4: 2 x 15 min. Rec. 6 min Z1", "Watt": 270, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 15, "Recupero_m": 6},
            "Giovedì": {"Esercizio": "Sweet Spot: 2 x 25 min. Rec. 5 min Z1", "Watt": 254, "RPM": 85, "Ripetizioni": 2, "Lavoro_m": 25, "Recupero_m": 5}
        },
        "Settimana 2 (Carico Intermedio)": {
            "Martedì": {"Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1", "Watt": 272, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 12, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Sweet Spot: 1 x 50 min continui in salita", "Watt": 254, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 50, "Recupero_m": 0}
        },
        "Settimana 3 (Picco di Carico)": {
            "Martedì": {"Esercizio": "Soglia Z4: 2 x 20 min (Massima Densità)", "Watt": 279, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 20, "Recupero_m": 6},
            "Giovedì": {"Esercizio": "Sweet Spot: Salita costante di 55 min", "Watt": 256, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 55, "Recupero_m": 0}
        },
        "Settimana 4 (Scarico)": {
            "Martedì": {"Esercizio": "Scarico: 1 x 10 min Z4 rilassato", "Watt": 265, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 10, "Recupero_m": 0},
            "Giovedì": {"Esercizio": "Agilità di scarico senza spingere", "Watt": 150, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 0}
        }
    },
    "Novembre": {
        "Settimana 1 (Carico Base)": {
            "Martedì": {"Esercizio": "Dinamica Over-Under: 3x (1' Over / 1' Under)", "Watt": 275, "RPM": 92, "Ripetizioni": 3, "Lavoro_m": 2, "Recupero_m": 2},
            "Giovedì": {"Esercizio": "Mantenimento SS: 2 x 20 min", "Watt": 252, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 20, "Recupero_m": 5}
        },
        "Settimana 2 (Carico Intermedio)": {
            "Martedì": {"Esercizio": "Dinamica Over-Under: 4x (1' Over / 1' Under)", "Watt": 275, "RPM": 92, "Ripetizioni": 4, "Lavoro_m": 2, "Recupero_m": 2},
            "Giovedì": {"Esercizio": "Mantenimento SS: 1 x 45 min costanti", "Watt": 252, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 45, "Recupero_m": 0}
        },
        "Settimana 3 (Picco di Carico)": {
            "Martedì": {"Esercizio": "Dinamica Over-Under: Picco intensità variata", "Watt": 280, "RPM": 92, "Ripetizioni": 5, "Lavoro_m": 2, "Recupero_m": 2},
            "Giovedì": {"Esercizio": "SS Esteso ad alta frequenza: 1 x 50 min", "Watt": 255, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 50, "Recupero_m": 0}
        },
        "Settimana 4 (Scarico)": {
            "Martedì": {"Esercizio": "Assimilazione: Lavoro agile in Z2 lineare", "Watt": 170, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 0},
            "Giovedì": {"Esercizio": "Scarico Muscolare Totale", "Watt": 140, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 15, "Recupero_m": 0}
        }
    },
    "Dicembre": {
        "Settimana 1 (Carico Base)": {
            "Martedì": {"Esercizio": "Efficienza Soglia: 3 x 12 min. Rec. 4 min Z1", "Watt": 278, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 12, "Recupero_m": 4},
            "Giovedì": {"Esercizio": "Massimo Stimolo SS: 1 x 45 min", "Watt": 255, "RPM": 86, "Ripetizioni": 1, "Lavoro_m": 45, "Recupero_m": 0}
        },
        "Settimana 2 (Carico Intermedio)": {
            "Martedì": {"Esercizio": "Efficienza Soglia: 3 x 15 min a 280W", "Watt": 280, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 15, "Recupero_m": 5},
            "Giovedì": {"Esercizio": "Massimo Stimolo SS: 2 x 25 min", "Watt": 256, "RPM": 86, "Ripetizioni": 2, "Lavoro_m": 25, "Recupero_m": 5}
        },
        "Settimana 3 (Picco di Carico)": {
            "Martedì": {"Esercizio": "Efficienza Soglia: 2 x 25 min Z4 massimali", "Watt": 282, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 25, "Recupero_m": 6},
            "Giovedì": {"Esercizio": "Efficienza SS Estrema: 1 x 60 min continui", "Watt": 258, "RPM": 86, "Ripetizioni": 1, "Lavoro_m": 60, "Recupero_m": 0}
        },
        "Settimana 4 (Scarico)": {
            "Martedì": {"Esercizio": "Ripristino energetico e agilità controllata", "Watt": 160, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 0},
            "Giovedì": {"Esercizio": "Fine ciclo: Pedalata libera Z1", "Watt": 140, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 15, "Recupero_m": 0}
        }
    }
}

st.title("🏋️ Pianificazione Allenamento")

# --- 3. MENÙ A TENDINA A CASCATA (SELEZIONE MESI ORIGINALE) ---
st.subheader("🚀 Invio Automatico a Intervals.icu")

col1, col2, col3 = st.columns(3)

with col1:
    mese_selezionato = st.selectbox("Seleziona Mese:", list(database_allenamenti.keys()))

with col2:
    settimane_disponibili = list(database_allenamenti[mese_selezionato].keys())
    settimana_selezionata = st.selectbox("Seleziona Settimana:", settimane_disponibili)

with col3:
    giorni_disponibili = list(database_allenamenti[mese_selezionato][settimana_selezionata].keys())
    giorno_selezionato = st.selectbox("Seleziona Giorno:", giorni_disponibili)

# Estrazione dei dati dell'allenamento scelto
dati_allenamento = database_allenamenti[mese_selezionato][settimana_selezionata][giorno_selezionato]

# Box riassuntivo per l'utente prima dell'invio
st.info(f"📋 **Dettaglio Sessione:** {dati_allenamento['Esercizio']} | Target: **{dati_allenamento['Watt']}W** | Cadenza: **{dati_allenamento['RPM']} RPM**")

# Selezione della data sul calendario Streamlit
data_pianificazione = st.date_input("Per quale giorno vuoi pianificarlo?", datetime.date.today())

# --- 4. LOGICA DI CARICAMENTO CORRETTA PER LE BARRE ---
if st.button("📤 Carica direttamente su Intervals.icu"):
    if "intervals" not in st.secrets:
        st.error("⚠️ Configura prima le credenziali nei Secrets di Streamlit!")
    else:
        try:
            with st.spinner("Generazione blocchi e calcolo minutaggio totale..."):
                atleta_id = st.secrets["intervals"]["athlete_id"]
                api_key = st.secrets["intervals"]["api_key"]
                auth = HTTPBasicAuth("API_KEY", api_key)
                
                pct_ftp = round((dati_allenamento['Watt'] / ftp_atleta) * 100, 1)
                
                # Risoluzione del bug delle barre: Generazione del testo e calcolo esatto dei minuti (duration)
                warmup_m = 10
                cooldown_m = 10
                ripetizioni = dati_allenamento["Ripetizioni"]
                lavoro_m = dati_allenamento["Lavoro_m"]
                recupero_m = dati_allenamento["Recupero_m"]
                
                if ripetizioni == 1:
                    testo_strutturato = f"- Warm Up 10m 55%\n- {lavoro_m}m {int(pct_ftp)}%\n- Cooldown 10m 50%"
                    durata_totale_secondi = (warmup_m + lavoro_m + cooldown_m) * 60
                else:
                    testo_strutturato = f"- Warm Up 10m 55%\n- {ripetizioni}x {lavoro_m}m {int(pct_ftp)}% {recupero_m}m 50%\n- Cooldown 10m 50%"
                    durata_totale_secondi = (warmup_m + (ripetizioni * (lavoro_m + recupero_m)) + cooldown_m) * 60
                
                # Payload corretto: 'moving_time' e 'total_time' permettono la cancellazione e sbloccano il grafico
                payload = {
                    "start_date_local": f"{data_pianificazione.isoformat()}T08:00:00",
                    "type": "Ride",
                    "category": "WORKOUT",
                    "name": f"🏋️ {giorno_selezionato} - {mese_selezionato} ({settimana_selezionata.split(' ')[0]})",
                    "description": f"🎯 Target: {int(dati_allenamento['Watt'])}W ({pct_ftp}% FTP)\n🔄 RPM: {dati_allenamento['RPM']}\n📋 {dati_allenamento['Esercizio']}",
                    "workout_text": testo_strutturato,
                    "moving_time": durata_totale_secondi,
                    "total_time": durata_totale_secondi,
                    "indoor": True
                }
                
                url = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events"
                response = requests.post(url, json=payload, auth=auth)
                
                if response.status_code in [200, 201]:
                    st.success("🎉 Successo! Allenamento caricato correttamente con grafico attivo e rimovibile.")
                else:
                    st.error(f"Errore da Intervals ({response.status_code}): {response.text}")
                    
        except Exception as e:
            st.error(f"Errore: {e}")
