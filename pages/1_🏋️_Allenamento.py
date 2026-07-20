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
