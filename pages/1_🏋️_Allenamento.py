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

# --- SEZIONE 2: DIARIO DEI MACROCICLI (STRUTTURA FINO A GENNAIO 2027) ---
st.subheader("📅 Pianificazione Macro e Microcicli")

fasi_allenamento = {
    "Fase 1: Riatletizzazione (Agosto 2026)": 
        "**Obiettivo:** Ripartenza aerobica e stimoli mirati in agilità. **Zero SFR, zero rilanci.**\n\n"
        "*   **Martedì (Il giorno più duro):** Lavoro specifico di **Soglia (Z4)**. 60-90 min totali con blocchi in agilità pura (90 RPM) attorno ai 254-270W per stimolare la massima efficienza cardiocircolatoria senza appesantire il busto.\n"
        "*   **Giovedì (Consolidamento):** Lavoro di **Sweet Spot (SS)**. Seduta focalizzata sul mantenere un ritmo solido ma gestibile (245-260W) a 85 RPM, ideale per consolidare il volume e la resistenza muscolare specifica.\n"
        "*   **Sabato/Domenica:** Uscite di gruppo passive. Resta coperto in scia, evita scatti improvvisi e affronta le salite con passo regolare e agile, unicamente seduto.",
        
    "Fase 2: Potenziamento Specifico (Settembre - Ottobre 2026)": 
        "**Obiettivo:** Incremento dell'estensione temporale nei wattaggi chiave da passista/scalatore.\n\n"
        "*   **Martedì (Il giorno più duro):** Intervalli estesi o frazionati alla **Soglia (Z4)** (es. 3 x 10 min a ritmo FTP 270-279W) curando la massima fluidità di pedalata.\n"
        "*   **Giovedì (Consolidamento):** Lunghi blocchi di **Sweet Spot (SS)** (es. 2 x 20 min o 1 x 40 min a 250W) per abituare il corpo a riciclare lattato a intensità medio-alta.\n"
        "*   **Sabato/Domenica:** Fondo lungo con dislivello accumulato su salite costanti, mantenendo una frequenza di pedalata sempre superiore alle 75-80 RPM.",
        
    "Fase 3: Sviluppo Potenza (Novembre - Dicembre 2026)": 
        "**Obiettivo:** Ottimizzazione dei 279W di FTP in vista della ripresa invernale.\n\n"
        "*   **Martedì (Il giorno più duro):** Blocchi solidi a **Soglia (Z4)** (es. 2 x 20 min a 275W) oppure variazioni Over-Under (sopra/sotto soglia) per simulare i cambi di ritmo in salita.\n"
        "*   **Giovedì (Consolidamento):** Richiami di **Sweet Spot (SS)** ad alta cadenza accoppiati a tratti di fondo medio (Z3) per stabilizzare la potenza aerobica.\n"
        "*   **Sabato/Domenica:** Uscite di gruppo con sezioni a ritmo controllato in salita, gestendo le accelerazioni solo con il cambio.",
        
    "Fase 4: Rientro in Palestra Graduale (Gennaio 2027)": 
        "**Obiettivo:** Transizione e reintroduzione della pesistica per la parte superiore.\n\n"
        "*   **In Bici:** Mantenimento della base aerobica e agilità generale.\n"
        "*   **In Palestra:** Ripresa graduale dei pesi (trazioni, panca, dip, military press) partendo con carichi minimi di ricondizionamento articolare per valutare la totale stabilità della clavicola."
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
