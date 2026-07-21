import streamlit as st
import pandas as pd
import json
from fpdf import FPDF
import io

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare & Allenamento",
    page_icon="🚴‍♂️",
    layout="wide"
)

# Banca dati precompilata degli alimenti (valori per 100g o porzione indicata)
@st.cache_data
ato
def get_banca_dati():
    data = [
        {"Alimento": "anguria", "gr/n": 300, "carbo": 111.0, "proteine": 1.2, "grassi": 0.6, "kcal": 48.0},
        {"Alimento": "arista", "gr/n": 100, "carbo": 0.0, "proteine": 24.0, "grassi": 5.0, "kcal": 145.0},
        {"Alimento": "avena", "gr/n": 60, "carbo": 37.8, "proteine": 7.2, "grassi": 4.2, "kcal": 216.0},
        {"Alimento": "banana", "gr/n": 100, "carbo": 23.0, "proteine": 1.2, "grassi": 0.3, "kcal": 89.0},
        {"Alimento": "carne", "gr/n": 100, "carbo": 0.0, "proteine": 20.0, "grassi": 5.0, "kcal": 125.0},
        {"Alimento": "carne gelatina", "gr/n": 212, "carbo": 1.272, "proteine": 23.32, "grassi": 3.18, "kcal": 129.32},
        {"Alimento": "ciliege", "gr/n": 100, "carbo": 12.0, "proteine": 1.0, "grassi": 0.2, "kcal": 50.0},
        {"Alimento": "crakers tre mulini", "gr/n": 40, "carbo": 30.0, "proteine": 3.6, "grassi": 3.8, "kcal": 97.2},
        {"Alimento": "cuscus", "gr/n": 100, "carbo": 75.0, "proteine": 12.0, "grassi": 1.5, "kcal": 376.0},
        {"Alimento": "digestive", "gr/n": 100, "carbo": 63.0, "proteine": 7.0, "grassi": 21.0, "kcal": 471.0},
        {"Alimento": "fiocchi di latte", "gr/n": 100, "carbo": 3.4, "proteine": 13.0, "grassi": 4.2, "kcal": 98.0},
        {"Alimento": "gallette di mais bio", "gr/n": 100, "carbo": 78.0, "proteine": 8.0, "grassi": 2.5, "kcal": 365.0},
        {"Alimento": "gallette di riso bio", "gr/n": 2, "carbo": 9.6, "proteine": 1.0, "grassi": 0.16, "kcal": 44.0},
        {"Alimento": "hamburgher bovino", "gr/n": 100, "carbo": 0.0, "proteine": 19.0, "grassi": 10.0, "kcal": 165.0},
        {"Alimento": "hamburgher vitello", "gr/n": 100, "carbo": 0.0, "proteine": 20.0, "grassi": 6.0, "kcal": 134.0},
        {"Alimento": "latte", "gr/n": 160, "carbo": 7.84, "proteine": 5.28, "grassi": 5.76, "kcal": 102.4},
        {"Alimento": "merluzzo", "gr/n": 100, "carbo": 0.0, "proteine": 17.0, "grassi": 0.8, "kcal": 75.0},
        {"Alimento": "nocciolata", "gr/n": 1, "carbo": 8.3, "proteine": 0.9, "grassi": 4.7, "kcal": 81.0},
        {"Alimento": "noci", "gr/n": 100, "carbo": 7.0, "proteine": 14.0, "grassi": 65.0, "kcal": 654.0},
        {"Alimento": "olio evo", "gr/n": 1, "carbo": 0.0, "proteine": 0.0, "grassi": 10.0, "kcal": 90.0},
        {"Alimento": "pasta", "gr/n": 100, "carbo": 75.0, "proteine": 12.0, "grassi": 1.5, "kcal": 360.0},
        {"Alimento": "patate", "gr/n": 100, "carbo": 17.0, "proteine": 2.0, "grassi": 0.1, "kcal": 77.0},
        {"Alimento": "patate congelate", "gr/n": 100, "carbo": 22.0, "proteine": 2.5, "grassi": 5.0, "kcal": 140.0},
        {"Alimento": "pizza margherita", "gr/n": 100, "carbo": 28.0, "proteine": 11.0, "grassi": 10.0, "kcal": 240.0},
        {"Alimento": "pollo", "gr/n": 100, "carbo": 0.0, "proteine": 23.0, "grassi": 1.5, "kcal": 105.0},
        {"Alimento": "puccia", "gr/n": 100, "carbo": 55.0, "proteine": 8.0, "grassi": 2.0, "kcal": 270.0},
        {"Alimento": "riso basmati", "gr/n": 100, "carbo": 83.0, "proteine": 9.0, "grassi": 1.9, "kcal": 367.0},
        {"Alimento": "salmone", "gr/n": 100, "carbo": 1.0, "proteine": 23.5, "grassi": 3.0, "kcal": 107.0},
        {"Alimento": "sciroppo d'acero", "gr/n": 1, "carbo": 12.0, "proteine": 0.0, "grassi": 0.0, "kcal": 52.0},
        {"Alimento": "semi di chia", "gr/n": 13, "carbo": 5.473, "proteine": 2.145, "grassi": 2.34, "kcal": 63.18},
        {"Alimento": "tacchino", "gr/n": 100, "carbo": 0.0, "proteine": 24.0, "grassi": 1.0, "kcal": 106.0},
        {"Alimento": "tonno", "gr/n": 100, "carbo": 0.0, "proteine": 25.0, "grassi": 1.0, "kcal": 110.0},
        {"Alimento": "uova", "gr/n": 3, "carbo": 0.9, "proteine": 19.5, "grassi": 15.0, "kcal": 210.0},
        {"Alimento": "yamamoto caseine", "gr/n": 25, "carbo": 1.425, "proteine": 19.5, "grassi": 0.375, "kcal": 92.5},
        {"Alimento": "yogurt greco", "gr/n": 100, "carbo": 4.0, "proteine": 10.0, "grassi": 0.0, "kcal": 51.0},
        {"Alimento": "zucca", "gr/n": 100, "carbo": 3.5, "proteine": 1.1, "grassi": 0.1, "kcal": 18.0}
    ]
    return pd.DataFrame(data)

st.title("🚴‍♂️ Gestione Diario Alimentare e Allenamenti")

# Inizializzazione dello stato per il diario giornaliero
if "diario" not in st.session_state:
    st.session_state.diario = pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"])

banca_dati = get_banca_dati()

# Sidebar per navigazione
st.sidebar.header("Navigazione")
scelta = st.sidebar.radio("Vai a:", ["Diario Alimentare", "Banca Dati Alimenti"])

if scelta == "Banca Dati Alimenti":
    st.header("📋 Banca Dati Alimenti")
    st.dataframe(banca_dati, use_container_width=True)
    
    with st.expander("Aggiungi nuovo alimento alla banca dati"):
        nuovo_alimento = st.text_input("Nome Alimento")
        q_base = st.number_input("Quantità di riferimento (g)", min_value=1, value=100)
        c_base = st.number_input("Carboidrati (g)", min_value=0.0, value=0.0)
        p_base = st.number_input("Proteine (g)", min_value=0.0, value=0.0)
        g_base = st.number_input("Grassi (g)", min_value=0.0, value=0.0)
        k_base = st.number_input("Calorie (kcal)", min_value=0.0, value=0.0)
        
        if st.button("Salva in Banca Dati"):
            st.success(f"Alimento '{nuovo_alimento}' aggiunto con successo!")

elif scelta == "Diario Alimentare":
    st.header("🍽️ Diario Alimentare Giornaliero")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Aggiungi Alimento al Pasto")
        alimento_selezionato = st.selectbox("Seleziona dalla banca dati", banca_dati["Alimento"].tolist())
        
        # Recupera i valori di default basati sulla banca dati
        item_row = banca_dati[banca_dati["Alimento"] == alimento_selezionato].iloc[0]
        default_q = int(item_row["gr/n"])
        
        quantita = st.number_input("Quantità effettiva (g o porzioni)", min_value=1, value=default_q)
        
        # Calcolo proporzionale
 fattore = quantita / default_q
        c_calc = round(item_row["carbo"] * fattore, 2)
        p_calc = round(item_row["proteine"] * fattore, 2)
        g_calc = round(item_row["grassi"] * fattore, 2)
        k_calc = round(item_row["kcal"] * fattore, 2)
        
        if st.button("Aggiungi al Diario"):
            nuova_riga = pd.DataFrame([{
                "Alimento": alimento_selezionato,
                "gr/n": quantita,
                "carbo": c_calc,
                "proteine": p_calc,
                "grassi": g_calc,
                "kcal": k_calc
            }])
            st.session_state.diario = pd.concat([st.session_state.diario, nuova_riga], ignore_index=True)
            st.rerun()

    with col2:
        st.subheader("🎯 Obiettivi Giornalieri")
        obj_carbo = 230
        obj_prot = 165
        obj_grassi = 70
        obj_kcal = 2250
        
        st.metric("Carboidrati Obiettivo", f"{obj_carbo} g")
        st.metric("Proteine Obiettivo", f"{obj_prot} g")
        st.metric("Grassi Obiettivo", f"{obj_grassi} g")
        st.metric("Calorie Obiettivo", f"{obj_kcal} kcal")

    st.markdown("---")
    st.subheader("📝 RIEPILOGO GIORNATA")
    
    if not st.session_state.diario.empty:
        st.dataframe(st.session_state.diario, use_container_width=True)
        
        tot_carbo = st.session_state.diario["carbo"].sum()
        tot_prot = st.session_state.diario["proteine"].sum()
        tot_grassi = st.session_state.diario["grassi"].sum()
        tot_kcal = st.session_state.diario["kcal"].sum()
        
        st.markdown("### 📊 Totali vs Rimanenze")
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        
        with t_col1:
            st.metric("Carboidrati Totali", f"{tot_carbo:.2f} g", f"{tot_carbo - obj_carbo:.2f} g")
        with t_col2:
            st.metric("Proteine Totali", f"{tot_prot:.2f} g", f"{tot_prot - obj_prot:.2f} g")
        with t_col3:
            st.metric("Grassi Totali", f"{tot_grassi:.2f} g", f"{tot_grassi - obj_grassi:.2f} g")
        with t_col4:
            st.metric("Calorie Totali", f"{tot_kcal:.2f} kcal", f"{tot_kcal - obj_kcal:.2f} kcal")
            
        if st.button("Svuota Diario"):
            st.session_state.diario = pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"])
            st.rerun()
    else:
        st.info("Il diario di oggi è ancora vuoto. Aggiungi il primo alimento dal pannello sopra.")=True, use_container_width=True)
