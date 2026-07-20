import streamlit as st
import datetime
import requests
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Pianificazione Allenamento", page_icon="🏋️")

st.title("🏋️ Pianificazione Allenamento")

# --- 1. DATI ATLETA & RIFERIMENTI FTP ---
# Sostituisci o dinamizza questo valore con il tuo FTP reale se necessario
ftp_atleta = 279  

st.sidebar.markdown(f"### Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM")
st.sidebar.markdown("**Cadenza SS:** ~85 RPM")

# --- 2. DATABASE ALLENAMENTI DI ESEMPIO ---
# (Usa la struttura reale del tuo dataframe/database)
lista_allenamenti = [
    {
        "Mese": "Agosto",
        "Settimana": "Settimana 1 (Carico)",
        "Giorno": "Martedì",
        "Esercizio": "Soglia Z4: 2 x 6 min. Rec. 5 min Z1",
        "Watt": 260,
        "RPM": 90
    },
    {
        "Mese": "Agosto",
        "Settimana": "Settimana 4 (Scarico)",
        "Giorno": "Martedì",
        "Esercizio": "Soglia attiva: Solo 1 x 6 min in Z4",
        "Watt": 260,
        "RPM": 90
    },
    {
        "Mese": "Agosto",
        "Settimana": "Settimana 4 (Scarico)",
        "Giorno": "Giovedì",
        "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS",
        "Watt": 150,
        "RPM": 95
    }
]

# --- 3. INTERFACCIA DI SELEZIONE ---
st.subheader("🚀 Invio Automatico a Intervals.icu")
st.write("Scegli quale sessione programmare direttamente sul tuo calendario:")

# Creiamo le opzioni leggibili per la selectbox
opzioni_sessioni = [
    f"{a['Settimana']} - {a['Giorno']}: {a['Esercizio']}..." 
    for a in lista_allenamenti
]

sessione_selezionata = st.selectbox("Seleziona sessione:", opzioni_sessioni)
indice_selezionato = opzioni_sessioni.index(sessione_selezionata)
riga_target = lista_allenamenti[indice_selezionato]

# Selezione della data di pianificazione
data_allenamento = st.date_input(
    "Per quale giorno vuoi pianificarlo?", 
    datetime.date.today()
)

st.markdown("---")

# --- 4. PULSANTE DI COLLEGAMENTO E INVIO A INTERVALS.ICU ---
if st.button("📤 Carica direttamente su Intervals.icu"):
    if "intervals" not in st.secrets:
        st.error("⚠️ Configura prima le credenziali Intervals nei Secrets di Streamlit Cloud!")
    else:
        try:
            with st.spinner("Invio dell'allenamento strutturato a Intervals.icu..."):
                
                # Recupero credenziali corrette dai Secrets
                atleta_id = st.secrets["intervals"]["athlete_id"]
                api_key = st.secrets["intervals"]["api_key"]
                auth = HTTPBasicAuth("API_KEY", api_key)
                
                # Calcolo percentuale FTP in base ai Watt target della sessione
              

                pct_ftp = round((riga_target['Watt'] / ftp_atleta) * 100, 1)
                
                # Scomponiamo l'esercizio per estrarre la ripetizione. 
                # Se è un classico "2 x 6 min. Rec. 5 min", generiamo la stringa nativa per i blocchi di Intervals:
                # Esempio di sintassi digerita da Intervals:
                # - Warm Up 10m 50%
                # - 2x 6m 93% 5m 50%
                # - Cooldown 10m 50%
                
                testo_strutturato = f"""- Warm Up 10m 55%
- 2x 6m {int(pct_ftp)}% 5m 50%
- Cooldown 10m 50%
"""
                
                # Payload per le API ufficiali di Intervals.icu
                payload = {
                    "start_date_local": f"{data_allenamento.isoformat()}T08:00:00",
                    "type": "Ride",
                    "category": "WORKOUT",
                    "name": f"🏋️ {riga_target['Giorno']} - {riga_target['Mese']}",
                    "description": f"🎯 Target: {int(riga_target['Watt'])}W ({pct_ftp}% FTP)\n🔄 Cadenza: {riga_target['RPM']} RPM\n📋 Dettaglio: {riga_target['Esercizio']}",
                    "workout_text": testo_strutturato,
                    "indoor": False
                }
                
                # Chiamata API ufficiale con autenticazione Basic
                url = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events"
                response = requests.post(
                    url, 
                    json=payload, 
                    auth=HTTPBasicAuth("API_KEY", api_key)
                )
                
                if response.status_code in [200, 201]:
                    st.success("🎉 Successo! Allenamento strutturato caricato su Intervals.icu.")
                    st.info("Apri la scheda di Intervals: ora vedrai le barre colorate del grafico e la sessione verrà inviata istantaneamente al tuo Garmin!")
                else:
                    st.error(f"Errore da Intervals ({response.status_code}): {response.text}")
                    
        except Exception as e:
            st.error(f"Errore durante la sincronizzazione: {e}")
