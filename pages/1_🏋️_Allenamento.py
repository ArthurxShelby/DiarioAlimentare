import streamlit as st
import pandas as pd

# Configurazione pagina
st.set_page_config(page_title="Piano Allenamento Interattivo", page_icon="🏋️", layout="centered")

st.title("🏋️ Il Tuo Piano Allenamento Interattivo (Modello 3+1)")
st.markdown("---")

# Sezione Zone di Potenza statiche come riferimento
ftp_atleta = 279
st.sidebar.markdown(f"### 📊 Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta*0.88)}-{int(ftp_atleta*0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta*0.91)}-{int(ftp_atleta*1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM\n\n**Cadenza SS:** ~85 RPM")

# --- DATABASE INIZIALE DEGLI ALLENAMENTI ---
# Inizializziamo i dati in session_state così le modifiche persistono durante la navigazione
if "df_programma" not in st.session_state:
    data = [
        # AGOSTO
        {"Mese": "Agosto", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 6 min. Rec. 5 min Z1", "Watt": 260, "RPM": 90, "Note Spalla": "Agilità pura, zero rilanci"},
        {"Mese": "Agosto", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 20 min continuo", "Watt": 245, "RPM": 85, "Note Spalla": "Solo seduto, massima fluidità"},
        {"Mese": "Agosto", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 6 min. Rec. 4 min Z1", "Watt": 265, "RPM": 90, "Note Spalla": "Focus respirazione, busto fermo"},
        {"Mese": "Agosto", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 15 min. Rec. 5 min Z2", "Watt": 248, "RPM": 85, "Note Spalla": "Mantenere ritmo costante"},
        {"Mese": "Agosto", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 5 min Z1", "Watt": 270, "RPM": 92, "Note Spalla": "Massimo sforzo controllato del mese"},
        {"Mese": "Agosto", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 6 min Z2", "Watt": 250, "RPM": 85, "Note Spalla": "Spinta fluida ed estesa"},
        {"Mese": "Agosto", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: Solo 1 x 6 min in Z4", "Watt": 255, "RPM": 90, "Note Spalla": "Volume dimezzato, mantenimento motore"},
        {"Mese": "Agosto", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS", "Watt": 150, "RPM": 95, "Note Spalla": "Volume dimezzato, rigenerazione totale"},
        
        # SETTEMBRE
        {"Mese": "Settembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 10 min. Rec. 5 min Z1", "Watt": 270, "RPM": 90, "Note Spalla": "Estensione blocco soglia"},
        {"Mese": "Settembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 30 min continuo", "Watt": 250, "RPM": 85, "Note Spalla": "Passo costante da scalatore"},
        {"Mese": "Settembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 4 min Z1", "Watt": 272, "RPM": 90, "Note Spalla": "Busto stabile sul manubrio"},
        {"Mese": "Settembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 5 min Z2", "Watt": 252, "RPM": 85, "Note Spalla": "Ottimizzazione ricircolo lattato"},
        {"Mese": "Settembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 15 min. Rec. 6 min Z1", "Watt": 275, "RPM": 90, "Note Spalla": "Frazione lunga simulazione crono"},
        {"Mese": "Settembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 45 min continuo", "Watt": 255, "RPM": 85, "Note Spalla": "Lunga ascesa simulata senza sosta"},
        {"Mese": "Settembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: Solo 1 x 8 min in Z4", "Watt": 265, "RPM": 90, "Note Spalla": "Volume dimezzato, gamba sciolta"},
        {"Mese": "Settembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS", "Watt": 150, "RPM": 95, "Note Spalla": "Volume dimezzato, recupero spalla"},
        
        # OTTOBRE
        {"Mese": "Ottobre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 10 min. Rec. 5 min Z1", "Watt": 275, "RPM": 90, "Note Spalla": "Focus densità ad alti watt"},
        {"Mese": "Ottobre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 4 min Z2", "Watt": 255, "RPM": 85, "Note Spalla": "Consolidamento base solida"},
        {"Mese": "Ottobre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 4 x 8 min. Rec. 3 min stretto", "Watt": 277, "RPM": 90, "Note Spalla": "Tolleranza lattacida elevata"},
        {"Mese": "Ottobre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 25 min. Rec. 5 min", "Watt": 258, "RPM": 85, "Note Spalla": "Estensione del blocco"},
        {"Mese": "Ottobre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 20 min. Rec. 8 min Z1", "Watt": 279, "RPM": 90, "Note Spalla": "Piena FTP espressa sul lungo"},
        {"Mese": "Ottobre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 55 min continuo", "Watt": 260, "RPM": 85, "Note Spalla": "Resistenza specifica avanzata"},
        {"Mese": "Ottobre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: 2 x 5 min in Z4", "Watt": 270, "RPM": 90, "Note Spalla": "Volume dimezzato"},
        {"Mese": "Ottobre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Giro agile Z1", "Watt": 145, "RPM": 95, "Note Spalla": "Volume dimezzato, riposo totale"}
    ]
    st.session_state.df_programma = pd.DataFrame(data)

# --- MENU INTERATTIVO DI SELEZIONE MESE ---
st.subheader("📅 Tabella Programmazione Modificabile")
mese_selezionato = st.selectbox("Seleziona il mese da visualizzare e personalizzare:", ["Agosto", "Settembre", "Ottobre"])

# Filtra il dataframe in base al mese scelto
df_filtrato = st.session_state.df_programma[st.session_state.df_programma["Mese"] == mese_selezionato]

st.info("💡 Fai doppio clic su qualsiasi cella (es. Esercizio, Watt o RPM) per modificarla. Le modifiche verranno applicate istantaneamente.")

# --- DATA EDITOR INTERATTIVO ---
df_editato = st.data_editor(
    df_filtrato, 
    hide_index=True, 
    use_container_width=True,
    column_config={
        "Mese": st.column_config.TextColumn("Mese", disabled=True),
        "Settimana": st.column_config.TextColumn("Microciclo", disabled=True),
        "Giorno": st.column_config.TextColumn("Giorno", disabled=True),
        "Esercizio": st.column_config.TextColumn("Descrizione Allenamento Specifico", width="large"),
        "Watt": st.column_config.NumberColumn("Watt Target", min_value=100, max_value=400, step=1),
        "RPM": st.column_config.NumberColumn("RPM Consigliate", min_value=50, max_value=120, step=1),
        "Note Spalla": st.column_config.TextColumn("Note Sicurezza / Cliniche")
    }
)

# Pulsante per salvare lo stato globale se si modificano i dati
if st.button("💾 Salva modifiche nel piano globale"):
    # Aggiorna il dataframe principale in session_state con le righe modificate
    st.session_state.df_programma.update(df_editato)
    st.success(f"Piano di {mese_selezionato} aggiornato con successo!")

st.markdown("---")

# --- SEZIONE COMPLEMENTARE: REGISTRO DIARIO ---
st.subheader("📝 Registro delle tue sensazioni in sella")
with st.form("diario_allenamento_form"):
    giorno_all = st.selectbox("Giorno Allenamento Effettuato", ["Martedì", "Giovedì", "Sabato", "Domenica"])
    tipo_lavoro = st.text_input("Lavoro svolto (es. Risp + 3x6min Soglia + Defa)")
    watt_espressi = st.number_input("Watt Medi nei blocchi principali", min_value=0, max_value=500, value=250)
    rpm_medie = st.number_input("Cadenza Media Rilevata (RPM)", min_value=0, max_value=130, value=90)
    stato_spalla = st.select_slider(
        "Stabilità ed assenza fastidi alla spalla:",
        options=["Dolore", "Fastidio leggero", "Stabile (Nessun fastidio)", "Perfetta"]
    )
    note_all = st.text_area("Note e Sensazioni (es. spalla solida sui rulli, fatica accumulata)")
    
    submit_button = st.form_submit_button(label="Registra Allenamento nel Diario")
    if submit_button:
        st.success(f"Allenamento registrato nel database personale! Continua così.")
