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
        "Semi di chia": {"calorie": 486, "carboidrati": 42.0, "proteine": 17.0, "grassi": 31.0},
        "Semi di zucca": {"calorie": 559, "carboidrati": 10.0, "proteine": 30.0, "grassi": 49.0},
        "Tacchino": {"calorie": 135, "carboidrati": 0.0, "proteine": 30.0, "grassi": 1.0},
        "Tonno": {"calorie": 130, "carboidrati": 0.0, "proteine": 28.0, "grassi": 1.0},
        "Uova": {"calorie": 155, "carboidrati": 1.1, "proteine": 13.0, "grassi": 11.0},
        "Waxy maize Yamamoto": {"calorie": 360, "carboidrati": 90.0, "proteine": 0.0, "grassi": 0.0},
        "Yogurt greco": {"calorie": 59, "carboidrati": 4.0, "proteine": 10.3, "grassi": 0.0}
    }

# --- GESTIONE DEI DATI PERSISTENTI ---
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
# TAB 2: PROFILO & OBIETTIVI MACRO
# ==========================================
with tab_profilo:
    st.header("👤 Calcolo Fabbisogno & Target Macro")
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
    
    st.markdown("### 🎯 Imposta i tuoi Target Giornalieri")
    col_t1, col_t2 = st.columns(2)
    target_cal = col_t1.number_input("Target Calorico (kcal)", min_value=1000, max_value=6000, value=tdee)
    target_carbi = col_t2.number_input("Target Carboidrati (g)", min_value=0, max_value=1000, value=250)
    target_prot = col_t1.number_input("Target Proteine (g)", min_value=0, max_value=500, value=140)
    target_fat = col_t2.number_input("Target Grassi (g)", min_value=0, max_value=300, value=70)
    
    st.session_state.targets = {
        "calorie": target_cal, "carboidrati": target_carbi, "proteine": target_prot, "grassi": target_fat
    }

# Recupero target di sicurezza se non ancora configurati nel tab profilo
targets = st.session_state.get('targets', {"calorie": 2000, "carboidrati": 250, "proteine": 140, "grassi": 70})

# ==========================================
# TAB 1: DIARIO ALIMENTARE
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
                "Grammi": int(grammi),
                "Calorie": round(info["calorie"] * moltiplicatore, 1),
                "Carboidrati": round(info["carboidrati"] * moltiplicatore, 1),
                "Proteine": round(info["proteine"] * moltiplicatore, 1),
                "Grassi": round(info["grassi"] * moltiplicatore, 1)
            })
            salva_dati(st.session_state.diario)
            st.success("Aggiunto!")
            st.rerun()

    st.divider()
    
    # Calcolo totali giornalieri obbligatori
    df_diario = pd.DataFrame(st.session_state.diario) if st.session_state.diario else pd.DataFrame(columns=["Pasto", "Alimento", "Grammi", "Calorie", "Carboidrati", "Proteine", "Grassi"])
    
    tot_cal = round(df_diario["Calorie"].sum(), 1) if not df_diario.empty else 0.0
    tot_carbi = round(df_diario["Carboidrati"].sum(), 1) if not df_diario.empty else 0.0
    tot_prot = round(df_diario["Proteine"].sum(), 1) if not df_diario.empty else 0.0
    tot_fat = round(df_diario["Grassi"].sum(), 1) if not df_diario.empty else 0.0
    
    rem_cal = targets["calorie"] - tot_cal
    rem_carbi = targets["carboidrati"] - tot_carbi
    rem_prot = targets["proteine"] - tot_prot
    rem_fat = targets["grassi"] - tot_fat
    
    # --- STATO GIORNALIERO CON RIMANENZE COMPLETE ---
    st.subheader("📊 Stato Giornaliero (Rimanenze)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calorie", f"{tot_cal} / {targets['calorie']} kcal", delta=f"{int(rem_cal)} rimanenti")
    col2.metric("Carboidrati", f"{tot_carbi} / {targets['carboidrati']} g", delta=f"{round(rem_carbi, 1)} g rim.")
    col3.metric("Proteine", f"{tot_prot} / {targets['proteine']} g", delta=f"{round(rem_prot, 1)} g rim.")
    col4.metric("Grassi", f"{tot_fat} / {targets['grassi']} g", delta=f"{round(rem_fat, 1)} g rim.")
    
    st.divider()
    
    # --- DETTAGLIO SEPARATO E EDITABILE PER SINGOLO PASTO ---
    st.subheader("🍴 Dettaglio Macro Diviso Per Pasto")
    st.caption("💡 Puoi modificare le quantità o eliminare le righe direttamente dalle tabelle qui sotto.")
    
    diario_aggiornato = []
    
    for pasto in pasti_categorie:
        df_pasto = df_diario[df_diario["Pasto"] == pasto] if not df_diario.empty else pd.DataFrame()
        
        # Calcolo macro parziali del pasto specifico
        pasto_cal = round(df_pasto["Calorie"].sum(), 1) if not df_pasto.empty else 0.0
        pasto_carbi = round(df_pasto["Carboidrati"].sum(), 1) if not df_pasto.empty else 0.0
        pasto_prot = round(df_pasto["Proteine"].sum(), 1) if not df_pasto.empty else 0.0
        pasto_fat = round(df_pasto["Grassi"].sum(), 1) if not df_pasto.empty else 0.0
        
        with st.expander(f"🔹 {pasto.upper()} — {int(pasto_cal)} kcal | C: {pasto_carbi}g | P: {pasto_prot}g | G: {pasto_fat}g", expanded=not df_pasto.empty):
            if not df_pasto.empty:
                # Tabella interattiva e indipendente solo per questo pasto
                df_pasto_mostrato = df_pasto[["Alimento", "Grammi", "Calorie", "Carboidrati", "Proteine", "Grassi"]].copy()
                df_edited_pasto = st.data_editor(
                    df_pasto_mostrato,
                    key=f"editor_{pasto}",
                    use_container_width=True,
                    num_rows="dynamic",
                    hide_index=True
                )
                
                # Se l'utente ha modificato i grammi, ricalcola i macro al volo prima di salvare
                for idx, row in df_edited_pasto.iterrows():
                    alimento = row["Alimento"]
                    if alimento in st.session_state.db_alimenti:
                        info = st.session_state.db_alimenti[alimento]
                        try:
                            gr = float(row["Grammi"])
                        except:
                            gr = 100.0
                        molt = gr / 100.0
                        diario_aggiornato.append({
                            "Pasto": pasto,
                            "Alimento": alimento,
                            "Grammi": int(gr),
                            "Calorie": round(info["calorie"] * molt, 1),
                            "Carboidrati": round(info["carboidrati"] * molt, 1),
                            "Proteine": round(info["proteine"] * molt, 1),
                            "Grassi": round(info["grassi"] * molt, 1)
                        })
            else:
                st.write("*Nessun alimento inserito in questo pasto oggi.*")
                
        # Ricostruiamo la lista globale mantenendo gli elementi dei pasti vuoti o non toccati
        if df_pasto.empty:
            pass 

    # Controllo se l'utente ha fatto modifiche strutturali nelle tabelle (es. eliminato righe o cambiato grammi)
    # Se il numero di elementi o i dati differiscono dal diario di sessione, sovrascrivi e salva
    if st.session_state.diario:
        # Generiamo una firma rapida per capire se è cambiato qualcosa
        sf_originale = df_diario[["Pasto", "Alimento", "Grammi"]].to_dict(orient="records")
        df_nuovo = pd.DataFrame(diario_aggiornato)
        sf_nuova = df_nuovo[["Pasto", "Alimento", "Grammi"]].to_dict(orient="records") if not df_nuovo.empty else []
        
        if sf_originale != sf_nuova:
            st.session_state.diario = diario_aggiornato
            salva_dati(st.session_state.diario)
            st.rerun()

    if st.button("🗑️ Svuota Intero Diario Odierno", use_container_width=True):
        st.session_state.diario = []
        salva_dati([])
        st.rerun()

# ==========================================
# TAB 3: BANCA DATI
# ==========================================
with tab_banca_dati:
    st.header("🗂️ Gestione Database Personale")
    df_db = pd.DataFrame.from_dict(st.session_state.db_alimenti, orient='index').reset_index()
    df_db.columns = ["Alimento", "Calorie (kcal)", "Carboidrati (g)", "Proteine (g)", "Grassi (g)"]
    st.dataframe(df_db.sort_values(by="Alimento"), hide_index=True, use_container_width=True)
