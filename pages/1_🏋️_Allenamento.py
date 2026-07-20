import streamlit as st
import datetime
import requests
from requests.auth import HTTPBasicAuth

# Configurazione iniziale della pagina
st.set_page_config(page_title="Pianificazione Allenamento", page_icon="🏋️", layout="wide")

# --- 1. RIFERIMENTI FTP & SIDEBAR ORIGINALE ---
ftp_atleta = 279  

st.sidebar.markdown(f"## Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta * 0.88)}-{int(ftp_atleta * 0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta * 0.91)}-{int(ftp_atleta * 1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM")
st.sidebar.markdown("**Cadenza SS:** ~85 RPM")

# --- 2. DATABASE COMPLETO DELLE PROGRESSIONI (AGOSTO - DICEMBRE) ---
lista_allenamenti = [
    # --- AGOSTO: RIATLETIZZAZIONE ---
    {"Mese": "Agosto", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 6 min. Rec. 5 min Z1", "Watt": 260, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 6, "Recupero_m": 5},
    {"Mese": "Agosto", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 20 min continui", "Watt": 245, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 5},
    {"Mese": "Agosto", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 6 min. Rec. 5 min Z1", "Watt": 260, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 6, "Recupero_m": 5},
    {"Mese": "Agosto", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 30 min continui", "Watt": 245, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 30, "Recupero_m": 5},
    {"Mese": "Agosto", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 4 x 6 min. Rec. 4 min Z1", "Watt": 262, "RPM": 90, "Ripetizioni": 4, "Lavoro_m": 6, "Recupero_m": 4},
    {"Mese": "Agosto", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 40 min continui", "Watt": 248, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 40, "Recupero_m": 5},
    {"Mese": "Agosto", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: Solo 1 x 6 min in Z4", "Watt": 260, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 6, "Recupero_m": 5},
    {"Mese": "Agosto", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS", "Watt": 150, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 15, "Recupero_m": 5},

    # --- SETTEMBRE: COSTRUZIONE ---
    {"Mese": "Settembre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 5 min Z1", "Watt": 265, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 8, "Recupero_m": 5},
    {"Mese": "Settembre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 15 min. Rec. 5 min Z1", "Watt": 250, "RPM": 85, "Ripetizioni": 2, "Lavoro_m": 15, "Recupero_m": 5},
    {"Mese": "Settembre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 10 min. Rec. 5 min Z1", "Watt": 265, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 10, "Recupero_m": 5},
    {"Mese": "Settembre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 5 min Z1", "Watt": 250, "RPM": 85, "Ripetizioni": 2, "Lavoro_m": 20, "Recupero_m": 5},
    {"Mese": "Settembre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1", "Watt": 268, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 12, "Recupero_m": 5},
    {"Mese": "Settembre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 45 min continui", "Watt": 252, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 45, "Recupero_m": 5},
    {"Mese": "Settembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Mantenimento: 2 x 5 min Z4. Rec. 4 min", "Watt": 260, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 5, "Recupero_m": 4},
    {"Mese": "Settembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico: Recupero Attivo Z1 ed agilità", "Watt": 145, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 5},

    # --- OTTOBRE: DENSITÀ ---
    {"Mese": "Ottobre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 15 min. Rec. 6 min Z1", "Watt": 270, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 15, "Recupero_m": 6},
    {"Mese": "Ottobre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 25 min. Rec. 5 min Z1", "Watt": 254, "RPM": 85, "Ripetizioni": 2, "Lavoro_m": 25, "Recupero_m": 5},
    {"Mese": "Ottobre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1", "Watt": 272, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 12, "Recupero_m": 5},
    {"Mese": "Ottobre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 50 min continui in salita", "Watt": 254, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 50, "Recupero_m": 5},
    {"Mese": "Ottobre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 20 min (Massima Densità a 279W)", "Watt": 279, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 20, "Recupero_m": 6},
    {"Mese": "Ottobre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: Salita costante di 55 min", "Watt": 256, "RPM": 85, "Ripetizioni": 1, "Lavoro_m": 55, "Recupero_m": 5},
    {"Mese": "Ottobre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Scarico: 1 x 10 min Z4 rilassato", "Watt": 265, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 10, "Recupero_m": 5},
    {"Mese": "Ottobre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Agilità di scarico senza spingere", "Watt": 150, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 5},

    # --- NOVEMBRE: DINAMICA ---
    {"Mese": "Novembre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Martedì", "Esercizio": "Dinamica Over-Under: 3 x (1' Over / 1' Under) per 4 serie", "Watt": 275, "RPM": 92, "Ripetizioni": 4, "Lavoro_m": 6, "Recupero_m": 4},
    {"Mese": "Novembre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Giovedì", "Esercizio": "Mantenimento SS ad alta cadenza: 2 x 20 min", "Watt": 252, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 20, "Recupero_m": 5},
    {"Mese": "Novembre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Martedì", "Esercizio": "Dinamica Over-Under: 4 x (1' Over / 1' Under) per 4 serie", "Watt": 275, "RPM": 92, "Ripetizioni": 4, "Lavoro_m": 8, "Recupero_m": 4},
    {"Mese": "Novembre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Giovedì", "Esercizio": "Mantenimento SS: 1 x 45 min costanti", "Watt": 252, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 45, "Recupero_m": 5},
    {"Mese": "Novembre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Martedì", "Esercizio": "Dinamica Over-Under: Picco intensità variata", "Watt": 280, "RPM": 92, "Ripetizioni": 5, "Lavoro_m": 8, "Recupero_m": 4},
    {"Mese": "Novembre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Giovedì", "Esercizio": "SS Esteso ad alta frequenza: 1 x 50 min", "Watt": 255, "RPM": 90, "Ripetizioni": 1, "Lavoro_m": 50, "Recupero_m": 5},
    {"Mese": "Novembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Assimilazione: Lavoro agile in Z2 lineare", "Watt": 170, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 5},
    {"Mese": "Novembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Muscolare Totale", "Watt": 140, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 15, "Recupero_m": 5},

    # --- DICEMBRE: EFFICIENZA ---
    {"Mese": "Dicembre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Martedì", "Esercizio": "Efficienza Soglia: 3 x 12 min. Rec. 4 min Z1", "Watt": 278, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 12, "Recupero_m": 4},
    {"Mese": "Dicembre", "Settimana": "Settimana 1 (Carico Base)", "Giorno": "Giovedì", "Esercizio": "Massimo Stimolo SS: 1 x 45 min", "Watt": 255, "RPM": 86, "Ripetizioni": 1, "Lavoro_m": 45, "Recupero_m": 5},
    {"Mese": "Dicembre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Martedì", "Esercizio": "Efficienza Soglia: 3 x 15 min a 280W", "Watt": 280, "RPM": 90, "Ripetizioni": 3, "Lavoro_m": 15, "Recupero_m": 5},
    {"Mese": "Dicembre", "Settimana": "Settimana 2 (Carico Intermedio)", "Giorno": "Giovedì", "Esercizio": "Massimo Stimolo SS: 2 x 25 min", "Watt": 256, "RPM": 86, "Ripetizioni": 2, "Lavoro_m": 25, "Recupero_m": 5},
    {"Mese": "Dicembre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Martedì", "Esercizio": "Efficienza Soglia: 2 x 25 min Z4 massimali", "Watt": 282, "RPM": 90, "Ripetizioni": 2, "Lavoro_m": 25, "Recupero_m": 6},
    {"Mese": "Dicembre", "Settimana": "Settimana 3 (Picco di Carico)", "Giorno": "Giovedì", "Esercizio": "Efficienza SS Estrema: 1 x 60 min continui", "Watt": 258, "RPM": 86, "Ripetizioni": 1, "Lavoro_m": 60, "Recupero_m": 5},
    {"Mese": "Dicembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Ripristino energetico e agilità controllata", "Watt": 160, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 20, "Recupero_m": 5},
    {"Mese": "Dicembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Fine ciclo: Pedalata libera Z1", "Watt": 140, "RPM": 95, "Ripetizioni": 1, "Lavoro_m": 15, "Recupero_m": 5}
]

st.title("🏋️ Pianificazione Allenamento")

# Mostra il database completo come tabella pivot visiva pulita
st.subheader("📋 Tabella dei Macro e Microcicli Programmati")
st.dataframe(lista_allenamenti, use_container_width=True, height=400)

st.markdown("---")

# --- 3. SELEZIONE E INTERFACCIA D'INVIO ---
st.subheader("🚀 Invio Automatico a Intervals.icu")
st.write("Sfoglia l'intero piano da agosto a dicembre e invialo istantaneamente sul calendario:")

# Filtro preliminare del mese per rendere la scelta più ordinata
mese_scelto = st.selectbox("1. Scegli il Mese del blocco:", ["Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"])

#Filtriamo la lista solo per il mese scelto
allenamenti_filtrati = [a for a in lista_allenamenti if a["Mese"] == mese_scelto]

# Creiamo le stringhe descrittive per la selectbox
opzioni_sessioni = [
    f"{a['Settimana']} - {a['Giorno']}: {a['Esercizio']} ({a['Watt']}W)" 
    for a in allenamenti_filtrati
]

sessione_selezionata = st.selectbox("2. Seleziona la sessione specifica:", opzioni_sessioni)
indice_selezionato = opzioni_sessioni.index(sessione_selezionata)
riga_target = allenamenti_filtrati[indice_selezionato]

# Selezione calendario
data_allenamento = st.date_input("3. Per quale data vuoi programmarlo?", datetime.date.today())

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. LOGICA ATTIVAZIONE PULSANTE E PARSER INTERVALLI ---
if st.button("📤 Carica direttamente su Intervals.icu"):
    if "intervals" not in st.secrets:
        st.error("⚠️ Inserisci le tue chiavi Intervals nei Secrets di Streamlit Cloud per abilitare la trasmissione!")
    else:
        try:
            with st.spinner("Compilazione blocchi ed esportazione in corso..."):
                atleta_id = st.secrets["intervals"]["athlete_id"]
                api_key = st.secrets["intervals"]["api_key"]
                auth = HTTPBasicAuth("API_KEY", api_key)
                
                # Calcolo percentuale rispetto all'FTP di riferimento (279W)
                pct_ftp = round((riga_target['Watt'] / ftp_atleta) * 100, 1)
                
                # Generazione dinamica e rigorosa del testo a blocchi in base alla riga scelta
                ripetizioni = riga_target["Ripetizioni"]
                minuti_lavoro = riga_target["Lavoro_m"]
                minuti_recupero = riga_target["Recupero_m"]
                
                # Se l'esercizio prevede ripetizioni singole (es. blocchi SS continui)
                if ripetizioni == 1:
                    testo_strutturato = f"""- Warm Up 10m 55%
- {minuti_lavoro}m {int(pct_ftp)}%
- Cooldown 10m 50%
"""
                # Se l'esercizio è strutturato a intervalli ripetuti (es. le serie Z4)
                else:
                    testo_strutturato = f"""- Warm Up 10m 55%
- {ripetizioni}x {minuti_lavoro}m {int(pct_ftp)}% {minuti_recupero}m 50%
- Cooldown 10m 50%
"""
                
                # Preparazione payload per l'endpoint API degli eventi di Intervals
                payload = {
                    "start_date_local": f"{data_allenamento.isoformat()}T08:00:00",
                    "type": "Ride",
                    "category": "WORKOUT",
                    "name": f"🏋️ {riga_target['Giorno']} ({riga_target['Mese']}) - {riga_target['Settimana'].split(' ')[0]}",
                    "description": f"🎯 Intensità Target: {int(riga_target['Watt'])}W ({pct_ftp}% FTP)\n🔄 Frequenza di pedalata: {riga_target['RPM']} RPM\n📋 Esercizio: {riga_target['Esercizio']}",
                    "workout_text": testo_strutturato,
                    "indoor": False
                }
                
                url = f"https://intervals.icu/api/v1/athlete/{atleta_id}/events"
                response = requests.post(url, json=payload, auth=auth)
                
                if response.status_code in [200, 201]:
                    st.success("🎉 Successo! L'allenamento progressivo strutturato è stato inviato ad Intervals.icu.")
                    st.info("Aggiorna la pagina di Intervals: adesso il blocco grafico risulterà disegnato correttamente e pronto per Garmin!")
                else:
                    st.error(f"Errore di comunicazione API ({response.status_code}): {response.text}")
                    
        except Exception as e:
            st.error(f"Errore durante l'elaborazione o l'invio: {e}")
