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

# --- 2. DATABASE STRUTTURATO ---
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

# --- 3. SELEZIONE A CASCATA (MENU A TENDINA) ---
st.subheader("🚀 Selezione Sessione del Piano")
col_m, col_s, col_g = st.columns(3)

with col_m:
    mese_selezionato = st.selectbox("Mese:", list(database_allenamenti.keys()))
with col_s:
    settimane_disponibili = list(database_allenamenti[mese_selezionato].keys())
    settimana_selezionata = st.selectbox("Settimana:", settimane_disponibili)
with col_g:
    giorni_disponibili = list(database_allenamenti[mese_selezionato][settimana_selezionata].keys())
    giorno_selezionato = st.selectbox("Giorno:", giorni_disponibili)

# Estrazione dei dati template di partenza
allenamento_base = database_allenamenti[mese_selezionato][settimana_selezionata][giorno_selezionato]

st.markdown("---")

# --- 4. PANNELLO DI MODIFICA DEI DATI ---
st.subheader("✍️ Modifica o Verifica i dati prima dell'invio")
st.write("Puoi variare i parametri qui sotto, l'invio terrà conto dei valori che inserisci:")

col_w, col_r, col_l, col_rec = st.columns(4)

with col_w:
    watt_modificati = st.number_input("Target Watt:", min_value=50, max_value=500, value=int(allenamento_base["Watt"]))
with col_r:
    ripetizioni_modificate = st.number_input("Numero Serie/Ripetizioni:", min_value=1, max_value=20, value=int(allenamento_base["Ripetizioni"]))
with col_l:
    lavoro_modificato = st.number_input("Durata Lavoro (minuti ciascuno):", min_value=1, max_value=120, value=int(allenamento_base["Lavoro_m"]))
with col_rec:
    recupero_modificato = st.number_input("Durata Recupero (minuti):", min_value=0, max_value=30, value=int(allenamento_base["Recupero_m"]))

col_n, col_d = st.columns([2, 1])
with col_n:
    nome_allenamento = st.text_input("Nome Allenamento (visualizzato su Intervals):", value=f"{allenamento_base['Esercizio']}")
with col_d:
    data_pianificazione = st.date_input("Data nel Calendario:", datetime.date.today())

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. LOGICA DI SINCRO NATIVA INTERVALS (FIX COMPLETO BARRE) ---
# --- 5. LOGICA DI SINCRO NATIVA INTERVALS (FIX DEFINITIVO BARRE & CANCELLAZIONE) ---
if st.button("📤 Carica direttamente su Intervals.icu"):
    if "intervals" not in st.secrets:
        st.error("⚠️ Configura prima le credenziali nei Secrets di Streamlit!")
    else:
        try:
            with st.spinner("Invio in corso..."):
                atleta_id = st.secrets["intervals"]["athlete_id"]
                api_key = st.secrets["intervals"]["api_key"]
                auth = HTTPBasicAuth("API_KEY", api_key)
                
                # Calcolo percentuale sul target attuale modificato
                pct_ftp = round((watt_modificati / ftp_atleta) * 100, 1)
                
                warmup_m = 10
                cooldown_m = 10
                
                # Sintassi nativa a inizio riga senza spazi nascosti o rientri di tabulazione
                if ripetizioni_modificate == 1:
                    testo_strutturato = f"""Warm Up
- 10m 55%

Lavoro
- {lavoro_modificato}m {int(pct_ftp)}%

Cooldown
- 10m 50%"""
                    durata_totale_secondi = (warmup_m + lavoro_modificato + cooldown_m) * 60
                else:
                    testo_strutturato = f"""Warm Up
- 10m 55%

Main Set {ripetizioni_modificate}x
- {lavoro_modificato}m {int(pct_ftp)}%
- {recupero_modificato}m 50%

Cooldown
- 10m 50%"""
                    durata_totale_secondi = (warmup_m + (ripetizioni_modificate * (lavoro_modificato + recupero_modificato)) + cooldown_m) * 60
                
                # Payload pulito con 'workout_text' formattato correttamente
                payload = {
                    "start_date_local": f"{data_pianificazione.isoformat()}T08:00:00",
                    "type": "Ride",
                    "category": "WORKOUT",
                    "name": f"🏋️ {nome_allenamento}",
                    "description": f"🎯 Target impostato: {watt_modificati}W ({pct_ftp}% FTP)",
                    "workout_text": testo_strutturato,
                    "moving_time": durata_totale_secondi,
                    "total_time": durata_totale_secondi,
                    "indoor": True
                }
                
                url = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events"
                response = requests.post(url, json=payload, auth=auth)
                
                if response.status_code in [200, 201]:
                    st.success("🎉 Successo! Ora l'allenamento ha le barre grafiche attive ed è completamente modificabile e cancellabile dal calendario.")
                else:
                    st.error(f"Errore da Intervals ({response.status_code}): {response.text}")
                    
        except Exception as e:
            st.error(f"Errore: {e}")
