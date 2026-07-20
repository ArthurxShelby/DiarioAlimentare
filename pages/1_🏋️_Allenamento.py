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
st.subheader("📅 Pianificazione Macro e Microcicli (Struttura 3+1)")

fasi_allenamento = {
    "Fase 1: Riatletizzazione (Agosto 2026)": 
        "**Struttura del Macrociclo:** 3 Settimane di Carico Progressivo + 1 Settimana di Scarico.\n"
        "**Focus:** Stimolo progressivo a frequenze fluide. *Zero SFR, zero carichi spalla.*\n\n"
        "---"
        "\n\n**📊 MICROCICLO 1 (Settimana 1) - Ripristino Aerobico**\n"
        "*   **Martedì (Soglia):** 60 min totali. Inserire 2 x 6 min in Z4 (254-265W) a 90 RPM. Recupero 5 min in Z1.\n"
        "*   **Giovedì (Consolidamento SS):** 60 min in Z2 con 1 blocco solido da 20 min in Sweet Spot (245W) a 85 RPM.\n"
        "*   **Sabato/Domenica:** 90-120 min di fondo lento (Z2) in gruppo. Coperto in scia, massimo controllo.\n\n"
        "**📈 MICROCICLO 2 (Settimana 2) - Incremento Volume**\n"
        "*   **Martedì (Soglia):** 75 min totali. Inserire 3 x 8 min in Z4 (260-270W) a 90 RPM. Recupero 4 min.\n"
        "*   **Giovedì (Consolidamento SS):** 75 min. Inserire 2 x 15 min in Sweet Spot (250W) a 85 RPM. Recupero 5 min in Z2.\n"
        "*   **Sabato/Domenica:** 120-150 min in gruppo. Passo regolare in salita, rigorosamente seduto.\n\n"
        "**🔥 MICROCICLO 3 (Settimana 3) - Picco di Carico**\n"
        "*   **Martedì (Soglia):** 90 min totali. Lavoro principale: 3 x 10 min in Z4 (270W) a 90 RPM. Recupero 5 min.\n"
        "*   **Giovedì (Consolidamento SS):** 90 min. Lavoro principale: 2 x 20 min in Sweet Spot (255W) a 85 RPM.\n"
        "*   **Sabato/Domenica:** 150-180 min in gruppo. Maggiore volume, focus sulla resistenza generale senza scatti.\n\n"
        "**📉 MICROCICLO 4 (Settimana 4) - Scarico ed Assimilazione**\n"
        "*   **Martedì (Soglia ridotta):** 60 min totali. Solo 2 x 5 min in Z4 (254W) giusto per mantenere attivo il motore. Agile.\n"
        "*   **Giovedì (Scarico SS):** 50 min in Z2 agile (90 RPM). Nessun blocco di Sweet Spot, massima capillarizzazione.\n"
        "*   **Sabato/Domenica:** 60-90 min da solo o in gruppo molto tranquillo, solo Z1/Z2 per rigenerare i tessuti della spalla.",
        
    "Fase 2: Potenziamento Specifico (Settembre - Ottobre 2026)": 
        "**Struttura:** Blocchi 3+1 focalizzati sull'estensione del minutaggio nelle zone chiave.\n\n"
        "*   **Martedì (Soglia):** Progressioni fino a blocchi solidi da 2 x 20 min a ritmo FTP (270-279W) a 90 RPM.\n"
        "*   **Giovedì (Consolidamento SS):** Lavori estesi in Sweet Spot (fino a 1 x 50 min continui a 255W) per simulare il passo del passista in salita.\n"
        "*   **Sabato/Domenica:** Fondo lungo con dislivello in progressione nelle settimane 1-3, riduzione del 40% del volume nella settimana 4.",
        
    "Fase 3: Sviluppo Potenza (Novembre - Dicembre 2026)": 
        "**Struttura:** Blocchi 3+1 ad alta densità per rifinire l'efficienza aerobica.\n\n"
        "*   **Martedì (Soglia):** Lavori Over-Under (es. 4 x 5 min alternando 1 min a 290W e 1 min a 255W) nelle settimane di carico.\n"
        "*   **Giovedì (Consolidamento SS):** Mantenimento dello Sweet Spot alternato a richiami di Fondo Medio (Z3) in agilità.\n"
        "*   **Settimana di Scarico (Ogni 4a):** Taglio del 50% delle intensità per scaricare il sistema nervoso prima del rientro in palestra.",
        
    "Fase 4: Rientro in Palestra Graduale (Gennaio 2027)": 
        "**Obiettivo:** Transizione e inserimento della pesistica per la parte superiore della spalla.\n\n"
        "*   **In Bici:** Mantenimento della base e agilità generale, scarico relativo delle intensità su strada.\n"
        "*   **In Palestra:** Ripresa graduale (trazioni, panca, dip, military press) con carichi di condizionamento minimi (50% del potenziale precedente) per monitorare la stabilità articolare definitiva."
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
