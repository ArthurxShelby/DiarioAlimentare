import streamlit as st
import pandas as pd
import datetime
from garminconnect import Garmin
from fitfile import FitFile, Workout, Sport, Intensity, Step

# Configurazione pagina
st.set_page_config(page_title="Piano Allenamento Interattivo", page_icon="🏋️", layout="centered")

st.title("🏋️ Il Tuo Piano Allenamento Interattivo (Modello 3+1)")
st.markdown("---")

# Sezione Zone di Potenza statiche come riferimento nella barra laterale
ftp_atleta = 279
st.sidebar.markdown(f"### 📊 Riferimenti FTP ({ftp_atleta}W)")
st.sidebar.markdown(f"**Sweet Spot (SS):** {int(ftp_atleta*0.88)}-{int(ftp_atleta*0.93)}W")
st.sidebar.markdown(f"**Soglia Z4:** {int(ftp_atleta*0.91)}-{int(ftp_atleta*1.05)}W")
st.sidebar.markdown("**Cadenza Soglia:** ~90 RPM\n\n**Cadenza SS:** ~85 RPM")

# --- DATABASE INIZIALE COMPLETO ---
if "df_programma" not in st.session_state:
    data = [
        # --- AGOSTO ---
        {"Mese": "Agosto", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 6 min. Rec. 5 min Z1", "Watt": 260, "RPM": 90, "Note Spalla": "Agilità pura, zero rilanci"},
        {"Mese": "Agosto", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 20 min continuo", "Watt": 245, "RPM": 85, "Note Spalla": "Solo seduto, massima fluidità"},
        {"Mese": "Agosto", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 6 min. Rec. 4 min Z1", "Watt": 265, "RPM": 90, "Note Spalla": "Focus respirazione, busto fermo"},
        {"Mese": "Agosto", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 15 min. Rec. 5 min Z2", "Watt": 248, "RPM": 85, "Note Spalla": "Mantenere ritmo costante"},
        {"Mese": "Agosto", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 5 min Z1", "Watt": 270, "RPM": 92, "Note Spalla": "Massimo sforzo controllato del mese"},
        {"Mese": "Agosto", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 6 min Z2", "Watt": 250, "RPM": 85, "Note Spalla": "Spinta fluida ed estesa"},
        {"Mese": "Agosto", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: Solo 1 x 6 min in Z4", "Watt": 255, "RPM": 90, "Note Spalla": "Volume dimezzato, mantenimento motore"},
        {"Mese": "Agosto", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS", "Watt": 150, "RPM": 95, "Note Spalla": "Volume dimezzato, rigenerazione totale"},
        
        # --- SETTEMBRE ---
        {"Mese": "Settembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 10 min. Rec. 5 min Z1", "Watt": 270, "RPM": 90, "Note Spalla": "Estensione blocco soglia"},
        {"Mese": "Settembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 30 min continuo", "Watt": 250, "RPM": 85, "Note Spalla": "Passo costante da scalatore"},
        {"Mese": "Settembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 8 min. Rec. 4 min Z1", "Watt": 272, "RPM": 90, "Note Spalla": "Busto stabile sul manubrio"},
        {"Mese": "Settembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 5 min Z2", "Watt": 252, "RPM": 85, "Note Spalla": "Ottimizzazione ricircolo lattato"},
        {"Mese": "Settembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 15 min. Rec. 6 min Z1", "Watt": 275, "RPM": 90, "Note Spalla": "Frazione lunga simulazione crono"},
        {"Mese": "Settembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 45 min continuo", "Watt": 255, "RPM": 85, "Note Spalla": "Lunga ascesa simulata senza sosta"},
        {"Mese": "Settembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: Solo 1 x 8 min in Z4", "Watt": 265, "RPM": 90, "Note Spalla": "Volume dimezzato, gamba sciolta"},
        {"Mese": "Settembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Agilità in Z1/Z2. No SS", "Watt": 150, "RPM": 95, "Note Spalla": "Volume dimezzato, recupero spalla"},
        
        # --- OTTOBRE ---
        {"Mese": "Ottobre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 10 min. Rec. 5 min Z1", "Watt": 275, "RPM": 90, "Note Spalla": "Focus densità ad alti watt"},
        {"Mese": "Ottobre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 4 min Z2", "Watt": 255, "RPM": 85, "Note Spalla": "Consolidamento base solida"},
        {"Mese": "Ottobre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 4 x 8 min. Rec. 3 min stretto", "Watt": 277, "RPM": 90, "Note Spalla": "Tolleranza lattacida elevata"},
        {"Mese": "Ottobre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 25 min. Rec. 5 min", "Watt": 258, "RPM": 85, "Note Spalla": "Estensione del blocco"},
        {"Mese": "Ottobre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 2 x 20 min. Rec. 8 min Z1", "Watt": 279, "RPM": 90, "Note Spalla": "Piena FTP espressa sul lungo"},
        {"Mese": "Ottobre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 55 min continuo", "Watt": 260, "RPM": 85, "Note Spalla": "Resistenza specifica avanzata"},
        {"Mese": "Ottobre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: 2 x 5 min in Z4", "Watt": 270, "RPM": 90, "Note Spalla": "Volume dimezzato"},
        {"Mese": "Ottobre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Giro agile Z1", "Watt": 145, "RPM": 95, "Note Spalla": "Volume dimezzato, riposo totale"},

        # --- NOVEMBRE ---
        {"Mese": "Novembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Over-Under: 3 x 8 min (1' Over 290W / 1' Under 255W)", "Watt": 272, "RPM": 92, "Note Spalla": "Cambi di ritmo cardiaci dinamici"},
        {"Mese": "Novembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 20 min. Rec. 5 min", "Watt": 255, "RPM": 90, "Note Spalla": "Alta cadenza per scaricare muscoli"},
        {"Mese": "Novembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Over-Under: 3 x 10 min (1' Over 290W / 1' Under 255W)", "Watt": 272, "RPM": 92, "Note Spalla": "Gestione accumulo acido lattico"},
        {"Mese": "Novembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 3 x 15 min. Rec. 4 min", "Watt": 260, "RPM": 85, "Note Spalla": "Focus tenuta muscolare"},
        {"Mese": "Novembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Over-Under: 4 x 10 min (1' Over 295W / 1' Under 255W)", "Watt": 275, "RPM": 92, "Note Spalla": "Picco stress cardiaco simulazione gara"},
        {"Mese": "Novembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 30 min. Rec. 5 min", "Watt": 260, "RPM": 85, "Note Spalla": "Massimo volume di Sweet Spot"},
        {"Mese": "Novembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Soglia attiva: 1 x 8 min lineare (No scatti)", "Watt": 270, "RPM": 90, "Note Spalla": "Volume dimezzato, mantenimento"},
        {"Mese": "Novembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Totale: Pedalata agile Z1", "Watt": 150, "RPM": 95, "Note Spalla": "Volume dimezzato, relax nervoso"},

        # --- DICEMBRE ---
        {"Mese": "Dicembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 12 min. Rec. 5 min Z1", "Watt": 279, "RPM": 92, "Note Spalla": "Consolidamento FTP sul medio-lungo"},
        {"Mese": "Dicembre", "Settimana": "Settimana 1 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 45 min continuo", "Watt": 260, "RPM": 85, "Note Spalla": "Forza resistente pura in salita"},
        {"Mese": "Dicembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 4 x 10 min. Rec. 4 min Z1", "Watt": 282, "RPM": 92, "Note Spalla": "Lavoro leggermente sopra FTP"},
        {"Mese": "Dicembre", "Settimana": "Settimana 2 (Carico)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 2 x 25 min. Rec. 5 min", "Watt": 262, "RPM": 85, "Note Spalla": "Ottima spinta costante"},
        {"Mese": "Dicembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Martedì", "Esercizio": "Soglia Z4: 3 x 15 min. Rec. 6 min Z1", "Watt": 280, "RPM": 90, "Note Spalla": "Massimo volume espresso a FTP totale"},
        {"Mese": "Dicembre", "Settimana": "Settimana 3 (Picco)", "Giorno": "Giovedì", "Esercizio": "Sweet Spot: 1 x 60 min continuo", "Watt": 260, "RPM": 85, "Note Spalla": "Test finale di tenuta passista/scalatore"},
        {"Mese": "Dicembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Scarico Rigenerante: Solo Z1/Z2 agile", "Watt": 140, "RPM": 95, "Note Spalla": "Volume dimezzato, stop intensità"},
        {"Mese": "Dicembre", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Rigenerante: Sgambatella agile", "Watt": 140, "RPM": 95, "Note Spalla": "Preparazione muscolare per la palestra"},

        # --- GENNAIO ---
        {"Mese": "Gennaio", "Settimana": "Settimana 1 (Adattamento)", "Giorno": "Martedì", "Esercizio": "Bici Mantenimento: Z2 + 2 x 5 min SS", "Watt": 245, "RPM": 90, "Note Spalla": "Palestra: Introduzione pesi al 50% dei carichi"},
        {"Mese": "Gennaio", "Settimana": "Settimana 1 (Adattamento)", "Giorno": "Giovedì", "Esercizio": "Bici Mantenimento: 60 min Fondo Lento Z2", "Watt": 180, "RPM": 92, "Note Spalla": "Palestra: Focus esecuzione panca/trazioni lente"},
        {"Mese": "Gennaio", "Settimana": "Settimana 2 (Adattamento)", "Giorno": "Martedì", "Esercizio": "Bici Mantenimento: Z2 + 3 x 5 min SS", "Watt": 245, "RPM": 90, "Note Spalla": "Palestra: Mantenere carichi protettivi (50%)"},
        {"Mese": "Gennaio", "Settimana": "Settimana 2 (Adattamento)", "Giorno": "Giovedì", "Esercizio": "Bici Mantenimento: 75 min Fondo Lento Z2", "Watt": 185, "RPM": 90, "Note Spalla": "Palestra: Controllo stabilità dip e military press"},
        {"Mese": "Gennaio", "Settimana": "Settimana 3 (Progressione)", "Giorno": "Martedì", "Esercizio": "Bici Specifico: 2 x 10 min Sweet Spot", "Watt": 250, "RPM": 88, "Note Spalla": "Palestra: Incremento leggero pesi (+10% se stabile)"},
        {"Mese": "Gennaio", "Settimana": "Settimana 3 (Progressione)", "Giorno": "Giovedì", "Esercizio": "Bici Specifico: 1 x 20 min Soglia Z4", "Watt": 270, "RPM": 90, "Note Spalla": "Palestra: Monitorare sensazioni clavicola post-sforzo"},
        {"Mese": "Gennaio", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Martedì", "Esercizio": "Scarico Bici: 45 min agilità Z1", "Watt": 140, "RPM": 95, "Note Spalla": "Palestra: Settimana di scarico pesi (solo corpo libero)"},
        {"Mese": "Gennaio", "Settimana": "Settimana 4 (Scarico)", "Giorno": "Giovedì", "Esercizio": "Scarico Bici: 45 min agilità Z1", "Watt": 140, "RPM": 95, "Note Spalla": "Palestra: Fine ciclo di rientro biologico"}
    ]
    st.session_state.df_programma = pd.DataFrame(data)

# --- MENU INTERATTIVO ---
st.subheader("📅 Tabella Programmazione Modificabile")
mese_selezionato = st.selectbox("Seleziona il mese da visualizzare:", ["Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre", "Gennaio"])
df_filtrato = st.session_state.df_programma[st.session_state.df_programma["Mese"] == mese_selezionato]

df_editato = st.data_editor(
    df_filtrato, 
    hide_index=True, 
    use_container_width=True,
    column_config={
        "Mese": st.column_config.TextColumn("Mese", disabled=True),
        "Settimana": st.column_config.TextColumn("Microciclo", disabled=True),
        "Giorno": st.column_config.TextColumn("Giorno", disabled=True),
        "Esercizio": st.column_config.TextColumn("Descrizione Allenamento", width="large"),
        "Watt": st.column_config.NumberColumn("Watt Target"),
        "RPM": st.column_config.NumberColumn("RPM"),
        "Note Spalla": st.column_config.TextColumn("Note Cliniche")
    }
)

if st.button("💾 Salva modifiche nel piano globale"):
    st.session_state.df_programma.loc[st.session_state.df_programma["Mese"] == mese_selezionato, :] = df_editato.values
    st.success("Piano aggiornato!")

st.markdown("---")

# --- SEZIONE AUTOMAZIONE GARMIN ---
st.subheader("🚀 Invio Automatico a Garmin Connect")
st.markdown("Scegli quale sessione programmare direttamente sul calendario del tuo **Garmin Edge 540**:")

sessioni_disponibili = df_filtrato.apply(lambda row: f"{row['Settimana']} - {row['Giorno']}: {row['Esercizio'][:40]}...", axis=1).tolist()
sessione_scelta = st.selectbox("Seleziona sessione:", sessioni_disponibili)

index_scelta = sessioni_disponibili.index(sessione_scelta)
riga_target = df_filtrato.iloc[index_scelta]

# Selezione della data reale in cui si vuole eseguire l'allenamento
data_allenamento = st.date_input("Per quale giorno vuoi pianificarlo?", datetime.date.today())

if st.button("📤 Carica direttamente su Garmin Connect"):
    # Verifica che i segreti siano configurati
    if "garmin" not in st.secrets:
        st.error("⚠️ Configura prima le credenziali Garmin nei Secrets di Streamlit Cloud!")
    else:
        try:
            with st.spinner("Connessione ai server Garmin in corso..."):
                # 1. Creazione del file .FIT strutturato in memoria
                fit_workout = Workout(
                    name=f"{riga_target['Giorno']}_{riga_target['Mese']}"[:15],
                    sport=Sport.CYCLING
                )
                
                # Definiamo gli step dell'allenamento (Riscaldamento, Blocco, Defaticamento)
                fit_workout.steps = [
                    Step(intensity=Intensity.WARMUP, duration="10:00", target_watts=int(ftp_atleta * 0.5)),
                    Step(intensity=Intensity.ACTIVE, duration="30:00", target_watts=int(riga_target['Watt'])),
                    Step(intensity=Intensity.COOLDOWN, duration="10:00", target_watts=int(ftp_atleta * 0.5))
                ]
                
                # Salviamo il file temporaneamente
                file_path = "/tmp/temp_workout.fit"
                fit_workout.write(file_path)
                
                # 2. Accesso API Garmin e Upload
                garmin_client = Garmin(st.secrets["garmin"]["email"], st.secrets["garmin"]["password"])
                garmin_client.login()
                
                # Carica l'allenamento nella libreria personale di Garmin
                risultato_upload = garmin_client.upload_workout(file_path)
                workout_id = risultato_upload.get("workoutId")
                
                # Pianifica l'allenamento sul calendario alla data scelta
                garmin_client.schedule_workout(workout_id, data_allenamento.isoformat())
                
                st.success(f"🎉 Successo! Allenamento inviato al tuo calendario Garmin Connect per il giorno {data_allenamento}.")
                st.info("Accendi il tuo Edge 540 o apri l'app Garmin Connect sul tuo iPhone 13 per avviare la sincronizzazione Bluetooth.")
        except Exception as e:
            st.error(se := f"Errore durante la sincronizzazione: {e}")
            st.warning("Verifica che le credenziali nei Secrets siano corrette o riprova tra poco.")
