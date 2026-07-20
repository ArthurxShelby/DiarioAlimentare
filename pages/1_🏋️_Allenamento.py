import streamlit as st
import datetime
import requests
from requests.auth import HTTPBasicAuth

# Configurazione della pagina (assicurati che sia la prima istruzione Streamlit)
st.set_page_config(page_title="Allenamento", page_icon="🏋️", layout="wide")

# --- 1. RIPRISTINO SIDEBAR ORIGINALE ---
# Inserisci qui il tuo valore di FTP reale (es. 279)
ftp_atleta = 279  

st.sidebar.markdown(f"## Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM")
st.sidebar.markdown("**Cadenza SS:** ~85 RPM")

# --- 2. IL TUO DATABASE DI ALLENAMENTI ---
# Questa è la tabella che avevi originariamente nella pagina principale
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

# Mostra la tabella degli allenamenti all'utente (come nel tuo primissimo screen)
st.title("🏋️ Pianificazione Allenamento")
st.table(lista_allenamenti)

st.markdown("---")

# --- 3. BLOCCO DI INVIO AUTOMATICO A INTERVALS.ICU ---
st.subheader("🚀 Invio Automatico a Intervals.icu")
st.write("Scegli quale sessione programmare direttamente sul tuo calendario:")

# Creazione delle opzioni testuali per la selectbox
opzioni_sessioni = [
    f"{a['Settimana']} - {a['Giorno']}: {a['Esercizio']}" 
    for a in lista_allenamenti
]

sessione_selezionata = st.selectbox("Seleziona sessione:", opzioni_sessioni)
indice_selezionato = opzioni_sessioni.index(sessione_selezionata)
riga_target = lista_allenamenti[indice_selezionato]

# Input della data (Default: oggi)
data_allenamento = st.date_input(
    "Per quale giorno vuoi pianificarlo?", 
    datetime.date.today()
)

# Pulsante per il caricamento
if st.button("📥 Carica direttamente su Intervals.icu"):
    if "intervals" not in st.secrets:
        st.error("⚠️ Configura prima le credenziali Intervals nei Secrets di Streamlit Cloud!")
    else:
        try:
            with st.spinner("Generazione blocchi e invio a Intervals.icu..."):
                
                atleta_id = st.secrets["intervals"]["athlete_id"]
                api_key = st.secrets["intervals"]["api_key"]
                auth = HTTPBasicAuth("API_KEY", api_key)
                
                # Calcolo dinamico della percentuale di FTP basata sui Watt della riga selezionata
                pct_ftp = round((riga_target['Watt'] / ftp_atleta) * 100, 1)
                
                # Sintassi nativa a blocchi per Intervals.icu (genera le barre del grafico)
                testo_strutturato = f"""- Warm Up 10m 55%
- 2x 6m {int(pct_ftp)}% 5m 50%
- Cooldown 10m 50%
"""
                
                payload = {
                    "start_date_local": f"{data_allenamento.isoformat()}T08:00:00",
                    "type": "Ride",
                    "category": "WORKOUT",
                    "name": f"🏋️ {riga_target['Giorno']} - {riga_target['Mese']}",
                    "description": f"🎯 Target: {int(riga_target['Watt'])}W ({pct_ftp}% FTP)\n🔄 Cadenza: {riga_target['RPM']} RPM\n📋 Dettaglio: {riga_target['Esercizio']}",
                    "workout_text": testo_strutturato,
                    "indoor": False
                }
                
                url = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events"
                response = requests.post(url, json=payload, auth=auth)
                
                if response.status_code in [200, 201]:
                    st.success("🎉 Successo! Allenamento strutturato caricato su Intervals.icu.")
                    st.info("Aggiorna Intervals: ora vedrai il grafico a blocchi completo ed esteso!")
                else:
                    st.error(f"Errore da Intervals ({response.status_code}): {response.text}")
                    
        except Exception as e:
            st.error(f"Errore durante la sincronizzazione: {e}")
