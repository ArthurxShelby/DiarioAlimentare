import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(page_title="Piano Allenamento Ciclismo", page_icon="🏋️", layout="centered")

st.title("🏋️ Centro Allenamento & Riatletizzazione")
st.markdown("---")

# --- SEZIONE 1: DATI ATLETA & CALCOLO ZONE ---
st.subheader("📊 Profilo Atleta & Zone di Potenza (Coggan)")

ftp_atleta = 279
eta_atleta = 56

zone_data = {
    "Zona": ["Z1 - Recupero Attivo", "Z2 - Fondo Lento", "Z3 - Fondo Medio", "Sweet Spot (SS)", "Z4 - Soglia Funzionale", "Z5 - Vo2Max"],
    "Percentuale FTP": ["< 55%", "55% - 75%", "76% - 90%", "88% - 93%", "91% - 105%", "106% - 120%"],
    "Watt Target": [
        f"< {int(ftp_atleta * 0.55)} W",
        f"{int(ftp_atleta * 0.55)} - {int(ftp_atleta * 0.75)} W",
        f"{int(ftp_atleta * 0.76)} - {int(ftp_atleta * 0.90)} W",
        f"{int(ftp_atleta * 0.88)} - {int(ftp_atleta * 0.93)} W",
        f"{int(ftp_atleta * 0.91)} - {int(ftp_atleta * 1.05)} W",
        f"{int(ftp_atleta * 1.06)} - {int(ftp_atleta * 1.20)} W"
    ],
    "Cadenza Consigliata": ["85-90 RPM", "85-95 RPM", "85-95 RPM", "80-90 RPM", "85-95 RPM", "> 95 RPM"],
    "Note sulla Spalla": ["Nessuna tensione", "Nessuna tensione", "Posizione fissa, no rilanci", "Massima fluidità seduto", "Seduto, focus spinta gambe", "DA EVITARE IN FASE 1"]
}

df_zone = pd.DataFrame(zone_data)
st.write(f"**Età:** {eta_atleta} anni | **Ultima FTP Rilevata:** {ftp_atleta} W")
st.dataframe(df_zone, hide_index=True, use_container_width=True)

st.markdown("---")

# --- SEZIONE 2: DIARIO DEI MACROCICLI (STRUTTURA COMPLETAMENTE DETTAGLIATA) ---
st.subheader("📅 Pianificazione Macro e Microcicli (Modello 3+1)")
st.write("Seleziona il mese per visualizzare la progressione dei carichi e la settimana di scarico a volumi dimezzati.")

fasi_allenamento = {
    "Agosto 2026: Riatletizzazione Post-Infortunio": 
        "### 🏃‍♂️ Agosto: Rientro Progressivo in Agilità Pura\n"
        "*Focus: Ricostruire la base aerobica senza strattoni. Zero SFR, solo pedalata fluida seduto.*\n\n"
        "**🟢 SETTIMANA 1**\n"
        "*   **Martedì (Soglia):** 60 min totali. Riscaldamento + **2 x 6 min in Z4 (255-265W) a 90 RPM**. Rec. 5 min Z1. (Totale Z4: 12 min)\n"
        "*   **Giovedì (Consolidamento SS):** 60 min totali. **1 x 20 min in Sweet Spot (245W) a 85 RPM** inserito nel fondo lento. (Totale SS: 20 min)\n\n"
        "**📈 SETTIMANA 2 (Carico +)**\n"
        "*   **Martedì (Soglia):** 75 min totali. Riscaldamento + **3 x 6 min in Z4 (260-270W) a 90 RPM**. Rec. 4 min Z1. (Totale Z4: 18 min)\n"
        "*   **Giovedì (Consolidamento SS):** 75 min totali. **2 x 15 min in Sweet Spot (245-250W) a 85 RPM**. Rec. 5 min Z2. (Totale SS: 30 min)\n\n"
        "**🔥 SETTIMANA 3 (Picco Carico ++)**\n"
        "*   **Martedì (Soglia):** 90 min totali. Riscaldamento + **3 x 8 min in Z4 (270W) a 92 RPM**. Rec. 5 min Z1. (Totale Z4: 24 min)\n"
        "*   **Giovedì (Consolidamento SS):** 90 min totali. **2 x 20 min in Sweet Spot (250W) a 85 RPM**. Rec. 6 min Z2. (Totale SS: 40 min)\n\n"
        "**📉 SETTIMANA 4 (Scarico - Volumi ed Intensità Dimezzati)**\n"
        "*   **Martedì (Soglia attiva):** 30 min totali. Solo **1 x 6 min in Z4 (255W)** giusto per non addormentare il motore. Tutto il resto Z1 agile.\n"
        "*   **Giovedì (Scarico SS):** 35 min totali in Z2 agile (90 RPM). **Zero blocchi di Sweet Spot**, focus su capillarizzazione e recupero spalla.",

    "Settembre 2026: Costruzione Capace Muscolare": 
        "### 🧱 Settembre: Estensione del Tempo sotto Sforzo\n"
        "*Focus: Aumentare la durata dei blocchi di lavoro alla soglia e nel fondo veloce.*\n\n"
        "**🟢 SETTIMANA 5**\n"
        "*   **Martedì (Soglia):** 75 min totali. Riscaldamento + **2 x 10 min in Z4 (270W) a 90 RPM**. Rec. 5 min Z1. (Totale Z4: 20 min)\n"
        "*   **Giovedì (Consolidamento SS):** 75 min totali. **1 x 30 min in Sweet Spot (250W) a 85 RPM** continuo. (Totale SS: 30 min)\n\n"
        "**📈 SETTIMANA 6 (Carico +)**\n"
        "*   **Martedì (Soglia):** 85 min totali. Riscaldamento + **3 x 8 min in Z4 (270-275W) a 90 RPM**. Rec. 4 min Z1. (Totale Z4: 24 min)\n"
        "*   **Giovedì (Consolidamento SS):** 85 min totali. **2 x 20 min in Sweet Spot (250-255W) a 85 RPM**. Rec. 5 min Z2. (Totale SS: 40 min)\n\n"
        "**🔥 SETTIMANA 7 (Picco Carico ++)**\n"
        "*   **Martedì (Soglia):** 95 min totali. Riscaldamento + **2 x 15 min in Z4 (275W) a 90 RPM**. Rec. 6 min Z1. (Totale Z4: 30 min)\n"
        "*   **Giovedì (Consolidamento SS):** 95 min totali. **1 x 45 min in Sweet Spot (255W) a 85 RPM** continuo (simulazione passo scalatore). (Totale SS: 45 min)\n\n"
        "**📉 SETTIMANA 8 (Scarico - Volumi ed Intensità Dimezzati)**\n"
        "*   **Martedì (Soglia attiva):** 35 min totali. Solo **1 x 8 min in Z4 (265W)** agile. Resto della seduta in Z1.\n"
        "*   **Giovedì (Scarico SS):** 40 min totali di agilità a 95 RPM in Z1/Z2. **Nessun lavoro di forza o intensità**.",

    "Ottobre 2026: Densità e Tolleranza Lattacida": 
        "### ⛰️ Ottobre: Focus Specifico Passista / Scalatore\n"
        "*Focus: Incrementare i watt espressi in quota Z4 avvicinandosi alla FTP reale.*\n\n"
        "**🟢 SETTIMANA 9**\n"
        "*   **Martedì (Soglia):** 80 min totali. Riscaldamento + **3 x 10 min in Z4 (275W) a 90 RPM**. Rec. 5 min Z1. (Totale Z4: 30 min)\n"
        "*   **Giovedì (Consolidamento SS):** 80 min totali. **2 x 20 min in Sweet Spot (255W) a 85 RPM**. Rec. 4 min Z2. (Totale SS: 40 min)\n\n"
        "**📈 SETTIMANA 10 (Carico +)**\n"
        "*   **Martedì (Soglia):** 90 min totali. Riscaldamento + **4 x 8 min in Z4 (275-279W) a 90 RPM** con recupero stretto a 3 min. (Totale Z4: 32 min)\n"
        "*   **Giovedì (Consolidamento SS):** 90 min totali. **2 x 25 min in Sweet Spot (255-260W) a 85 RPM**. Rec. 5 min. (Totale SS: 50 min)\n\n"
        "**🔥 SETTIMANA 11 (Picco Carico ++)**\n"
        "*   **Martedì (Soglia):** 100 min totali. Riscaldamento + **2 x 20 min in Z4 (279W - Piena FTP)** a 90 RPM. Rec. 8 min Z1. (Totale Z4: 40 min)\n"
        "*   **Giovedì (Consolidamento SS):** 100 min totali. **1 x 55 min in Sweet Spot (260W)** continuo, simulando una lunga ascesa in progressione. (Totale SS: 55 min)\n\n"
        "**📉 SETTIMANA 12 (Scarico - Volumi ed Intensità Dimezzati)**\n"
        "*   **Martedì (Soglia attiva):** 40 min totali. Solo **2 x 5 min in Z4 (270W)** agile per mantenere brillantezza.\n"
        "*   **Giovedì (Scarico SS):** 45 min totali in Z1/Z2 in totale relax muscolare.",

    "Novembre 2026: Dinamica ed Over-Under": 
        "### ⚡ Novembre: Lavori Intervallati e Gestione Lattato\n"
        "*Focus: Introdurre variazioni di ritmo sopra/sotto soglia per simulare attacchi in salita.*\n\n"
        "**🟢 SETTIMANA 13**\n"
        "*   **Martedì (Soglia Over-Under):** 80 min totali. 3 serie da 8 min strutturate come (1 min a 290W [Over] + 1 min a 255W [Under]). Rec. 5 min tra le serie. (Totale Z4+: 24 min)\n"
        "*   **Giovedì (Consolidamento SS):** 80 min totali. **2 x 20 min in Sweet Spot (255W) a 90 RPM** ad alta cadenza per scaricare i muscoli. (Totale SS: 40 min)\n\n"
        "**📈 SETTIMANA 14 (Carico +)**\n"
        "*   **Martedì (Soglia Over-Under):** 90 min totali. 3 serie da 10 min strutturate come (1 min a 290W + 1 min a 255W). Rec. 5 min. (Totale Z4+: 30 min)\n"
        "*   **Giovedì (Consolidamento SS):** 90 min totali. **3 x 15 min in Sweet Spot (260W) a 85 RPM**. Rec. 4 min. (Totale SS: 45 min)\n\n"
        "**🔥 SETTIMANA 15 (Picco Carico ++)**\n"
        "*   **Martedì (Soglia Over-Under):** 100 min totali. 4 serie da 10 min strutturate come (1 min a 295W + 1 min a 255W). Rec. 5 min. (Totale Z4+: 40 min)\n"
        "*   **Giovedì (Consolidamento SS):** 100 min totali. **2 x 30 min in Sweet Spot (260W)** stabili a 85 RPM. (Totale SS: 60 min)\n\n"
        "**📉 SETTIMANA 16 (Scarico - Volumi ed Intensità Dimezzati)**\n"
        "*   **Martedì (Soglia attiva):** 40 min totali. Solo **1 x 8 min in Z4 lineare (270W)** senza scatti.\n"
        "*   **Giovedì (Scarico SS):** 45 min totali in Z1 agile.",

    "Dicembre 2026: Picco Massima Efficienza": 
        "### 🏆 Dicembre: Consolidamento Finale della FTP prima della Palestra\n"
        "*Focus: Massimizzare il tempo totale speso a ridosso o sopra i 279W di FTP.*\n\n"
        "**🟢 SETTIMANA 17**\n"
        "*   **Martedì (Soglia):** 85 min totali. Riscaldamento + **3 x 12 min in Z4 (279W) a 92 RPM**. Rec. 5 min. (Totale Z4: 36 min)\n"
        "*   **Giovedì (Consolidamento SS):** 85 min totali. **1 x 45 min in Sweet Spot (260W) a 85 RPM** continuo. (Totale SS: 45 min)\n\n"
        "**📈 SETTIMANA 18 (Carico +)**\n"
        "*   **Martedì (Soglia):** 95 min totali. Riscaldamento + **4 x 10 min in Z4 (279-282W) a 92 RPM**. Rec. 4 min. (Totale Z4: 40 min)\n"
        "*   **Giovedì (Consolidamento SS):** 95 min totali. **2 x 25 min in Sweet Spot (260-265W) a 85 RPM**. (Totale SS: 50 min)\n\n"
        "**🔥 SETTIMANA 19 (Picco Carico ++)**\n"
        "*   **Martedì (Soglia):** 110 min totali. Riscaldamento + **3 x 15 min in Z4 (280W) a 90 RPM**. Rec. 6 min Z1. (Totale Z4: 45 min)\n"
        "*   **Giovedì (Consolidamento SS):** 110 min totali. **1 x 60 min in Sweet Spot (260W) a 85 RPM** continuo. Il massimo stimolo di forza resistente specifica. (Totale SS: 60 min)\n\n"
        "**📉 SETTIMANA 20 (Scarico totale ed Assimilazione per Gennaio)**\n"
        "*   **Martedì (Scarico):** 45 min totali. Solo Z1/Z2 in agilità. **Zero lavori di soglia**.\n"
        "*   **Giovedì (Scarico):** 45 min totali. Sgambatella agile per scaricare completamente il tono muscolare delle gambe e preparare il corpo al rientro controllato in palestra di Gennaio 2027.",

    "Gennaio 2027: Transizione e Palestra": 
        "### 🏋️ Gennaio 2027: Introduzione Condizionamento Pesi\n"
        "*Focus: Mantenimento motore ciclistico e ripresa graduale della forza della parte superiore.*\n\n"
        "*   **In Bici:** Passaggio a sedute di puro mantenimento (Z2 + brevi richiami in SS il martedì).\n"
        "*   **In Palestra (3 volte a settimana):** Ripresa di Trazioni, Panca, Dip, Bilanciere Bicipiti, Corda Tricipiti e Military Press.\n"
        "*   **⚠️ Regola dei Pesi:** Utilizzare esclusivamente il **50% dei vecchi carichi** per le prime 2 settimane. Focus totale sull'esecuzione controllata per verificare la stabilità biologica al 100% della clavicola."
}

scelta_fase = st.selectbox("Seleziona la Fase del Piano per vedere il dettaglio:", list(fasi_allenamento.keys()))
st.markdown(fasi_allenamento[scelta_fase])

st.markdown("---")

# --- SEZIONE 3: REGISTRO DIARIO ALLENAMENTI ---
st.subheader("📝 Registro delle tue sensazioni in sella")
with st.form("diario_allenamento_form"):
    giorno_all = st.selectbox("Giorno Allenamento", ["Martedì", "Giovedì", "Sabato", "Domenica"])
    tipo_lavoro = st.text_input("Tipo di Lavoro (es. 3x8 min Soglia, 2x15 min SS)")
    watt_medi = st.number_input("Watt Medi nei blocchi principali", min_value=0, max_value=500, value=250)
    rpm_medie = st.number_input("Cadenza Media (RPM)", min_value=0, max_value=130, value=90)
    stato_spalla = st.select_slider(
        "Sensazione stabilità Clavicola/Spalla:",
        options=["Dolore/Instabile", "Fastidio leggero", "Stabile (nessun fastidio)", "Perfetta/Solida"]
    )
    note_all = st.text_area("Note aggiuntive")
    
    submit_button = st.form_submit_button(label="Salva Allenamento nel Diario")
    if submit_button:
        st.success(f"Allenamento di {giorno_all} registrato con successo!")
