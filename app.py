import streamlit as st
import pandas as pd
import json

# Configurazione della pagina ottimizzata per Mobile (iPhone) e Desktop (MacBook)
st.set_page_config(
    page_title="Il Mio Diario Alimentare Pro",
    page_icon="🍏",
    layout="centered"
)

# --- BANCA DATI ALIMENTI REALI (Valori per 100g) ---
if 'db_alimenti' not in st.session_state:
    st.session_state.db_alimenti = {
        "Anguria": {"calorie": 30, "carboidrati": 8.0, "proteine": 0.6, "grassi": 0.2},
        "Arista": {"calorie": 130, "carboidrati": 0.0, "proteine": 22.0, "grassi": 4.5},
        "Avena": {"calorie": 389, "carboidrati": 66.0, "proteine": 16.9, "grassi": 6.9},
        "Banana": {"calorie": 89, "carboidrati": 23.0, "proteine": 1.1, "grassi": 0.3},
        "Carne": {"calorie": 150, "carboidrati": 0.0, "proteine": 20.0, "grassi": 7.0},
        "Caseine": {"calorie": 360, "carboidrati": 1.0, "proteine": 85.0, "grassi": 1.5},
        "Ciliege": {"calorie": 50, "carboidrati": 12.0, "proteine": 1.0, "grassi": 0.3},
        "Crakers Tre Mulini": {"calorie": 440, "carboidrati": 70.0, "proteine": 10.0, "grassi": 12.0},
        "Cuscus": {"calorie": 360, "carboidrati": 73.0, "proteine": 12.0, "grassi": 1.0},
        "Digestive": {"calorie": 480, "carboidrati": 63.0, "proteine": 7.0, "grassi": 21.0},
        "Fiocchi di latte": {"calorie": 98, "carboidrati": 3.4, "proteine": 11.0, "grassi": 4.3},
        "Gallette di mais bio": {"calorie": 380, "carboidrati": 80.0, "proteine": 7.0, "grassi": 1.5},
        "Gallette di riso bio": {"calorie": 390, "carboidrati": 83.0, "proteine": 8.0, "grassi": 1.0},
        "Gelatina": {"calorie": 60, "carboidrati": 14.0, "proteine": 1.2, "grassi": 0.0},
        "Hamburgher bovino": {"calorie": 250, "carboidrati": 0.0, "proteine": 18.0, "grassi": 20.0},
        "Hamburgher vitello": {"calorie": 150, "carboidrati": 0.0, "proteine": 20.0, "grassi": 8.0},
        "Latte": {"calorie": 50, "carboidrati": 5.0, "proteine": 3.3, "grassi": 1.6},
        "Merluzzo": {"calorie": 82, "carboidrati": 0.0, "proteine": 18.0, "grassi": 0.7},
        "Nocciolata": {"calorie": 540, "carboidrati": 52.0, "proteine": 6.0, "grassi": 33.0},
        "Noci": {"calorie": 654, "carboidrati": 14.0, "proteine": 15.0, "grassi": 65.0},
        "Olio EVO": {"calorie": 884, "carboidrati": 0.0, "proteine": 0.0, "grassi": 100.0},
        "Pasta": {"calorie": 350, "carboidrati": 72.0, "proteine": 12.0, "grassi": 1.5},
        "Patate": {"calorie": 77, "carboidrati": 17.0, "proteine": 2.0, "grassi": 0.1},
        "Patate congelate": {"calorie": 130, "carboidrati": 22.0, "proteine": 2.0, "grassi": 3.5},
        "Pizza margherita": {"calorie": 270, "carboidrati": 36.0, "proteine": 10.0, "grassi": 9.5},
        "Pollo": {"calorie": 165, "carboidrati": 0.0, "proteine": 31.0, "grassi": 3.6},
        "Puccia": {"calorie": 270, "carboidrati": 52.0, "proteine": 8.0, "grassi": 2.5},
        "Riso basmati": {"calorie": 350, "carboidrati": 78.0, "proteine": 8.5, "grassi": 0.9},
        "Salmone": {"calorie": 208, "carboidrati": 0.0, "proteine": 20.0, "grassi": 13.0},
        "Sciroppo d'acero": {"calorie": 260, "carboidrati": 67.0, "proteine": 0.0, "grassi": 0.1},
        "Sciroppo d'agave": {"calorie": 310, "carboidrati": 76.0, "proteine": 0.0, "grassi": 0.5},
        "Semi di chia": {"calorie": 486, "carboidrati": 42.0, "proteine": 17.0, "grassi": 31.0},
        "Semi di zucca": {"calorie": 559, "carboidrati": 10.0, "proteine": 30.0, "grassi": 49.0},
        "Tacchino": {"calorie": 135, "carboidrati": 0.0, "proteine": 30.0, "grassi": 1.0},
        "Tonno": {"calorie": 130, "carboidrati": 0.0, "proteine": 28.0, "grassi": 1.0},
        "Uova": {"calorie": 155, "carboidrati": 1.1, "proteine": 13.0, "grassi": 11.0},
        "Waxy maize Yamamoto": {"calorie": 360, "carboidrati": 90.0, "proteine": 0.0, "grassi": 0.0},
        "Yogurt greco": {"calorie": 59, "carboidrati": 4.0, "proteine": 10.3, "grassi": 0.0}
    }

# --- FUNZIONI DI SALVATAGGIO LOCALE (Simulato tramite file o stato persistente lato server) ---
# Nota: Poiché Streamlit azzera la sessione, per salvare in modo permanente tra sessioni diverse 
# senza un database cloud complesso, usiamo un file di testo locale 'diario_salvato.json' sul server.
def carica_dati():
    try:
        with open("diario_salvato.json", "r") as f:
            return json.load(f)
    except:
        return []

def salva_dati(dati):
    with open("diario_salvato.json", "w") as f:
        json.dump(dati, f)

if 'diario' not in st.session_state:
    st.session_state.diario = carica_dati()

pasti_categorie = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

# --- TABS PRINCIPALI ---
tab_diario, tab_profilo, tab_banca_dati = st.tabs(["📅 Diario Alimentare", "👤 Profilo & Obiettivo", "🗂️ Gestione Alimenti"])

# ==========================================
# TAB 2: PROFILO
# ==========================================
with tab_profilo:
    st.header("👤 Calcolo Fabbisogno Energetico")
    sesso = st.radio("Sesso", ["Uomo", "Donna"], horizontal=True)
    
    col_dati1, col_dati2, col_dati3 = st.columns(3)
    peso = col_dati1.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.5)
    altezza = col_dati2.number_input("Altezza (cm)", min_value=100, max_value=250, value=175)
    eta = col_dati3.number_input("Età (anni)", min_value=10, max_value=100, value=25)
    
    laf_opzioni = {
        "Sedentario (Lavoro d'ufficio, poco movimento)": 1.2,
        "Leggermente Attivo (Attività leggera 1-3 volte/settimana)": 1.375,
        "Moderatamente Attivo (Allenamento moderato 3-5 volte/settimana)": 1.55,
        "Molto Attivo (Allenamento intenso 6-7 volte/settimana)": 1.725,
        "Estremamente Attivo (Lavoro pesante o atleta professionista)": 1.9
    }
    la = st.selectbox("Livello di Attività Fisica (LAF)", options=list(laf_opzioni.keys()), index=2)
    laf_scelto = laf_opzioni[la]

    if sesso == "Uomo":
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
    else:
        bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161
        
    tdee = int(bmr * laf_scelto)
    st.session_state.target_calorie = st.number_input("Target Calorico Personalizzato (kcal)", min_value=1000, max_value=6000, value=tdee)

# ==========================================
# TAB 1: DIARIO ALIMENTARE (Principale)
# ==========================================
with tab_diario:
    st.header("🍏 Registro dei Pasti")
    
    with st.expander("➕ Inserisci un nuovo alimento nel diario", expanded=True):
        col_ins1, col_ins2 = st.columns(2)
        pasto_sel = col_ins1.selectbox("Seleziona Pasto", pasti_categorie)
        alimenti_disponibili = sorted(list(st.session_state.db_alimenti.keys()))
        alimento_sel = col_ins2.selectbox("Seleziona Alimento", options=alimenti_disponibili)
        grammi = st.number_input("Grammi consumati (g)", min_value=1, value=100, step=5)
        
        if st.button("Aggiungi al Pasto", use_container_width=True):
            info = st.session_state.db_alimenti[alimento_sel]
            moltiplicatore = grammi / 100.0
            
            st.session_state.diario.append({
                "Pasto": pasto_sel,
                "Alimento": alimento_sel,
                "Grammi": grammi,
                "Calorie": round(info["calorie"] * moltiplicatore, 1),
                "Carboidrati": round(info["carboidrati"] * moltiplicatore, 1),
                "Proteine": round(info["proteine"] * moltiplicatore, 1),
                "Grassi": round(info["grassi"] * moltiplicatore, 1)
            })
            salva_dati(st.session_state.diario)
            st.success("Aggiunto e Salvato!")
            st.rerun()

    st.divider()
    
    if st.session_state.diario:
        df_diario = pd.DataFrame(st.session_state.diario)
        
        tot_cal = round(df_diario["Calorie"].sum(), 1)
        tot_carbi = round(df_diario["Carboidrati"].sum(), 1)
        tot_prot = round(df_diario["Proteine"].sum(), 1)
        tot_fat = round(df_diario["Grassi"].sum(), 1)
        
        target = st.session_state.get('target_calorie', 2000)
        bilancio = target - tot_cal
        
        st.subheader("📊 Stato Giornaliero")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Calorie Totali", f"{tot_cal} / {target} kcal", delta=f"{int(bilancio)} rim.")
        col2.metric("Carboidrati", f"{tot_carbi} g")
        col3.metric("Proteine", f"{tot_prot} g")
        col4.metric("Grassi", f"{tot_fat} g")
        
        st.divider()
        
        st.subheader("🍴 I tuoi Pasti (Puoi modificare o eliminare righe)")
        st.info("💡 **Per eliminare un alimento:** Seleziona la riga cliccando sul quadratino a sinistra nella tabella e premi il tasto **Canc (o Delete)** sulla tastiera del Mac, oppure usa il pulsante elimina integrato.")
        
        # Rendiamo la tabella modificabile ed eliminabile in tempo reale!
        df_editabile = st.data_editor(
            df_diario,
            use_container_width=True,
            num_rows="dynamic", # Permette la cancellazione dinamica
            hide_index=True
        )
        
        # Se l'utente cancella o modifica qualcosa nella tabella, aggiorna il database e salva
        if not df_editabile.equals(df_diario):
            st.session_state.diario = df_editabile.to_dict(orient="records")
            salva_dati(st.session_state.diario)
            st.rerun()
        
        if st.button("🗑️ Svuota Tutto", use_container_width=True):
            st.session_state.diario = []
            salva_dati([])
            st.rerun()
    else:
        st.info("Il diario è vuoto. Registra gli alimenti per iniziare.")

# ==========================================
# TAB 3: BANCA DATI
# ==========================================
with tab_banca_dati:
    st.header("🗂️ Gestione Database Personale")
    # ... Resto del codice database invariato ...
    df_db = pd.DataFrame.from_dict(st.session_state.db_alimenti, orient='index').reset_index()
    df_db.columns = ["Alimento", "Calorie (kcal)", "Carboidrati (g)", "Proteine (g)", "Grassi (g)"]
    st.dataframe(df_db.sort_values(by="Alimento"), hide_index=True, use_container_width=True)
