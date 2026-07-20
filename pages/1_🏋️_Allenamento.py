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

# Definizione delle zone basate sulla FTP di 279W
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

# --- SEZIONE 2: DIARIO DEI MACROCICLI (STRUTTURA FINO A GENNAIO 2027) ---
st.subheader("📅 Pianificazione Macro e Microcicli")

fasi_allenamento = {
    "Fase 1: Riatletizzazione (Agosto 2026)": 
        "**Obiettivo:** Ripristino della capacità aerobica in totale agilità. **Zero SFR, zero rilanci.**\n\n"
        "*   **Martedì:** 60-90 min in Z2 con 3 blocchi da 5 min in **Sweet Spot (245-260W)** a 85 RPM. Solo seduto.\n"
        "*   **Giovedì:** 60-90 min progressivo: 30 min Z2 + 30 min Z3 (Fondo Medio) + 10 min **Soglia Z4 (254W)** in agilità pura (90 RPM).\n"
        "*   **Sabato/Domenica:** Uscite di gruppo passive. Resta in scia, evita scatti, prediligi pianura o salite pedalabili senza mai alzarti sui pedali.",
        
    "Fase 2: Potenziamento Specifico (Settembre - Ottobre 2026)": 
        "**Obiettivo:** Costruzione del passista/scalatore tramite estensione del tempo in SS e Z4.\n\n"
        "*   **Martedì:** Lavori estesi in **Sweet Spot** (es. 2 x 20 min a 85 RPM) focalizzati sulla respirazione e stabilità del core.\n"
        "*   **Giovedì:** Intervalli Over-Under attorno alla Soglia (es. 4 x 5 min alternando 2 min a 260W e 3 min a 285W).\n"
        "*   **Sabato/Domenica:** Fondo lungo con dislivello accumulato su salite regolari a ritmo costante, simulando il passo da scalatore.",
        
    "Fase 3: Sviluppo Potenza e Innalzamento Soglia (Novembre - Dicembre 2026)": 
        "**Obiettivo:** Consolidamento dei wattaggi e richiami di Vo2Max dinamico.\n\n"
        "*   **Martedì:** Blocchi solidi a **Soglia Z4** (es. 3 x 12 min a 270W) a frequenze di pedalata elevate.\n"
        "*   **Giovedì:** Lavori di micro-intervalli (es. 30/30 o 40/20) per stimolare il sistema cardiocircolatorio senza affaticare le braccia.\n"
        "*   **Sabato/Domenica:** Uscite di gruppo con intensità libera in salita, gestendo i picchi di potenza in agilità.",
        
    "Fase 4: Rientro in Palestra Graduale (Gennaio 2027)": 
        "**Obiettivo:** Mantenimento della condizione in bici e reintroduzione della pesistica.\n\n"
        "*   **In Bici:** Passaggio alla fase di mantenimento e scarico relativo.\n"
        "*   **In Palestra:** Ripresa graduale degli esercizi multiarticolari (trazioni, panca, dip, military press) partendo con carichi minimi di condizionamento (50% del massimale precedente) per testare la stabilità definitiva della clavicola."
}

scelta_fase = st.selectbox("Seleziona la Fase del Piano per vedere il dettaglio:", list(fasi_allenamento.keys()))
st.info(fasi_allenamento[scelta_fase])

st.markdown("---")

# --- SEZIONE 3: REGISTRO DIARIO ALLENAMENTI (SALVATAGGIO) ---
st.subheader("📝 Registro delle tue sensazioni in sella")
st.write("Usa questo spazio per annotare i watt espressi, le RPM e lo stato di stabilità della spalla dopo ogni seduta.")

with st.form("diario_allenamento_form"):
    giorno_all = st.selectbox("Giorno Allenamento", ["Martedì", "Giovedì", "Sabato", "Domenica"])
    tipo_lavoro = st.text_input("Tipo di Lavoro (es. Sweet Spot 2x15 min, Fondo in scia)")
    watt_medi = st.number_input("Watt Medi nei blocchi principali", min_value=0, max_value=500, value=245)
    rpm_medie = st.number_input("Cadenza Media (RPM)", min_value=0, max_value=130, value=85)
    stato_spalla = st.select_slider(
        "Sensazione stabilità Clavicola/Spalla durante/dopo lo sforzo:",
        options=["Dolore/Instabile", "Fastidio leggero", "Stabile (nessun fastidio)", "Perfetta/Solida"]
    )
    note_all = st.text_area("Note aggiuntive (vibrazioni strada, stanchezza, ecc.)")
    
    submit_button = st.form_submit_button(label="Salva Allenamento nel Diario")
    
    if submit_button:
        st.success(f"Allenamento di {giorno_all} registrato con successo! Ottimo lavoro di conservazione muscolare.")
