import streamlit as st
import pandas as pd

# Configurazione della pagina ottimizzata per Mobile (iPhone) e Desktop (MacBook)
st.set_page_config(
    page_title="Il Mio Diario Alimentare",
    page_icon="🍏",
    layout="centered"
)

# --- BANCA DATI ALIMENTI REALI (Valori indicativi per 100g) ---
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

# --- INIZIALIZZAZIONE DIARIO ---
if 'diario' not in st.session_state:
    st.session_state.diario = []

# Categorie di pasti
pasti_categorie = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

st.title("🍏 Diario Alimentare")

# --- SEZIONE 1: INSERIMENTO ALIMENTI ---
st.subheader("➕ Inserisci Alimento nel Diario")

pasto_sel = st.selectbox("Seleziona Pasto", pasti_categorie)

# Generazione pulita della lista delle chiavi per evitare KeyError
alimenti_disponibili = sorted(list(st.session_state.db_alimenti.keys()))
alimento_sel = st.selectbox("Seleziona Alimento", options=alimenti_disponibili)

grammi = st.number_input("Grammi (g)", min_value=1, value=100, step=10)

if st.button("Aggiungi al Diario", use_container_width=True):
    info = st.session_state.db_alimenti[alimento_sel]
    moltiplicatore = grammi / 100.0
    
    nuovo_inserimento = {
        "Pasto": pasto_sel,
        "Alimento": alimento_sel,
        "Grammi": grammi,
        "Calorie": round(info["calorie"] * moltiplicatore, 1),
        "Carboidrati": round(info["carboidrati"] * moltiplicatore, 1),
        "Proteine": round(info["proteine"] * moltiplicatore, 1),
        "Grassi": round(info["grassi"] * moltiplicatore, 1)
    }
    
    st.session_state.diario.append(nuovo_inserimento)
    st.success(f"Aggiunto {grammi}g di {alimento_sel} a {pasto_sel}!")

st.divider()

# --- SEZIONE 2: DIARIO DEL GIORNO E CALCOLI ---
st.subheader("📅 I tuoi Pasti di Oggi")

if st.session_state.diario:
    df_diario = pd.DataFrame(st.session_state.diario)
    
    tot_cal = round(df_diario["Calorie"].sum(), 1)
    tot_carbi = round(df_diario["Carboidrati"].sum(), 1)
    tot_prot = round(df_diario["Proteine"].sum(), 1)
    tot_fat = round(df_diario["Grassi"].sum(), 1)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calorie Totali", f"{tot_cal} kcal")
    col2.metric("Carboidrati", f"{tot_carbi} g")
    col3.metric("Proteine", f"{tot_prot} g")
    col4.metric("Grassi", f"{tot_fat} g")
    
    st.divider()
    
    for pasto in pasti_categorie:
        df_pasto = df_diario[df_diario["Pasto"] == pasto]
        if not df_pasto.empty:
            st.markdown(f"#### 🍴 {pasto}")
            st.dataframe(
                df_pasto[["Alimento", "Grammi", "Calorie", "Carboidrati", "Proteine", "Grassi"]],
                hide_index=True,
                use_container_width=True
            )
            
    if st.button("🗑️ Svuota Diario", use_container_width=True):
        st.session_state.diario = []
        st.rerun()
else:
    st.info("Il diario è vuoto. Inizia ad aggiungere gli alimenti dal menu sopra!")
