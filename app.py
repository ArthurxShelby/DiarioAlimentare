import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare & Allenamento",
    page_icon="🚴‍♂️",
    layout="wide"
)

# Banca dati precompilata con le 35 voci alimentari
@st.cache_data
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

banca_dati = get_banca_dati()

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

if "db_diario" not in st.session_state:
    st.session_state.db_diario = {}

st.title("🚴‍♂️ Pianificatore Alimentare & Allenamento (Mifflin)")

# Selezione della data tramite Calendario
st.sidebar.header("🗓️ Seleziona Giorno")
data_selezionata = st.sidebar.date_input("Data", value=date.today())
data_str = data_selezionata.strftime("%Y-%m-%d")

if data_str not in st.session_state.db_diario:
    st.session_state.db_diario[data_str] = {pasto: pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]) for pasto in PASTI}

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parametri Mifflin-St Jeor")
peso = st.sidebar.number_input("Peso (kg)", value=70.0)
altezza = st.sidebar.number_input("Altezza (cm)", value=175.0)
eta = st.sidebar.number_input("Età (anni)", value=56)
genere = st.sidebar.selectbox("Genere", ["Uomo", "Donna"])

# Calcolo BMR Mifflin-St Jeor
if genere == "Uomo":
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
else:
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

tdee = bmr * 1.55
obj_kcal = round(tdee, 0)
obj_carbo = 230.0
obj_prot = 165.0
obj_grassi = 70.0

st.sidebar.info(f"**BMR stimato:** {bmr:.0f} kcal\n\n**TDEE stimato:** {obj_kcal:.0f} kcal")

# Calcoli totali giornalieri
tot_carbo = sum([st.session_state.db_diario[data_str][p]["carbo"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])
tot_prot = sum([st.session_state.db_diario[data_str][p]["proteine"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])
tot_grassi = sum([st.session_state.db_diario[data_str][p]["grassi"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])
tot_kcal = sum([st.session_state.db_diario[data_str][p]["kcal"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])

# Dashboard principale con Progress Bar istantanee
st.subheader(f"📊 Riepilogo Giornaliero - {data_str}")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric("Calorie", f"{tot_kcal:.1f} / {obj_kcal} kcal", delta=f"{obj_kcal - tot_kcal:.1f} rimanenti")
    st.progress(min(tot_kcal / obj_kcal, 1.0) if obj_kcal > 0 else 0)

with col_m2:
    st.metric("Carboidrati", f"{tot_carbo:.1f} / {obj_carbo} g", delta=f"{obj_carbo - tot_carbo:.1f} g rimanenti")
    st.progress(min(tot_carbo / obj_carbo, 1.0) if obj_carbo > 0 else 0)

with col_m3:
    st.metric("Proteine", f"{tot_prot:.1f} / {obj_prot} g", delta=f"{obj_prot - tot_prot:.1f} g rimanenti")
    st.progress(min(tot_prot / obj_prot, 1.0) if obj_prot > 0 else 0)

with col_m4:
    st.metric("Grassi", f"{tot_grassi:.1f} / {obj_grassi} g", delta=f"{obj_grassi - tot_grassi:.1f} g rimanenti")
    st.progress(min(tot_grassi / obj_grassi, 1.0) if obj_grassi > 0 else 0)

st.markdown("---")

# Gestione dei 6 pasti giornalieri
st.subheader("🍽️ Gestione dei 6 Pasti Giornalieri")
pasto_selezionato = st.selectbox("Seleziona il pasto da modificare:", PASTI)

col_A, col_B = st.columns([1, 1])

with col_A:
    st.markdown(f"### Aggiungi a: {pasto_selezionato}")
    alimento_scelto = st.selectbox("Alimento", banca_dati["Alimento"].tolist(), key=f"sel_{pasto_selezionato}")
    
    item_row = banca_dati[banca_dati["Alimento"] == alimento_scelto].iloc[0]
    default_q = int(item_row["gr/n"])
    
    quantita = st.number_input("Quantità (g o porzione)", min_value=1, value=default_q, key=f"q_{pasto_selezionato}")
    
    fattore = quantita / default_q
    c_calc = round(item_row["carbo"] * fattore, 2)
    p_calc = round(item_row["proteine"] * fattore, 2)
    g_calc = round(item_row["grassi"] * fattore, 2)
    k_calc = round(item_row["kcal"] * fattore, 2)
    
    if st.button("Aggiungi Alimento", key=f"btn_{pasto_selezionato}"):
        nuova_riga = pd.DataFrame([{
            "Alimento": alimento_scelto,
            "gr/n": quantita,
            "carbo": c_calc,
            "proteine": p_calc,
            "grassi": g_calc,
            "kcal": k_calc
        }])
        st.session_state.db_diario[data_str][pasto_selezionato] = pd.concat(
            [st.session_state.db_diario[data_str][pasto_selezionato], nuova_riga], ignore_index=True
        )
        st.rerun()

with col_B:
    st.markdown(f"### Contenuto: {pasto_selezionato}")
    df_corrente = st.session_state.db_diario[data_str][pasto_selezionato]
    if not df_corrente.empty:
        st.dataframe(df_corrente, use_container_width=True)
        if st.button(f"Svuota {pasto_selezionato}", key=f"clear_{pasto_selezionato}"):
            st.session_state.db_diario[data_str][pasto_selezionato] = pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"])
            st.rerun()
    else:
        st.info(f"Nessun alimento inserito in {pasto_selezionato} per questa data.")

st.markdown("---")

# Sezione Esportazione PDF
st.subheader("📄 Esportazione Report in PDF")
if st.button("Genera e Scarica PDF Giornaliero"):
    try:
        pdf_output = FPDF()
        pdf_output.add_page()
        pdf_output.set_font("Arial", "B", 16)
        pdf_output.cell(0, 10, f"Report Nutrizionale - {data_str}", ln=True, align="C")
        pdf_output.ln(10)
        
        pdf_output.set_font("Arial", "B", 12)
        pdf_output.cell(0, 10, "Riepilogo Totale:", ln=True)
        pdf_output.set_font("Arial", "", 11)
        pdf_output.cell(0, 8, f"Calorie: {tot_kcal:.1f} / {obj_kcal} kcal", ln=True)
        pdf_output.cell(0, 8, f"Carboidrati: {tot_carbo:.1f} / {obj_carbo} g", ln=True)
        pdf_output.cell(0, 8, f"Proteine: {tot_prot:.1f} / {obj_prot} g", ln=True)
        pdf_output.cell(0, 8, f"Grassi: {tot_grassi:.1f} / {obj_grassi} g", ln=True)
        pdf_output.ln(10)
        
        for pasto in PASTI:
            pdf_output.set_font("Arial", "B", 12)
            pdf_output.cell(0, 8, f"Pasto: {pasto}", ln=True)
            pdf_output.set_font("Arial", "", 10)
            df_p = st.session_state.db_diario[data_str][pasto]
            if not df_p.empty:
                for _, row in df_p.iterrows():
                    testo_riga = f" - {row['Alimento']}: {row['gr/n']}g | Carbo: {row['carbo']}g | Prot: {row['proteine']}g | Grassi: {row['grassi']}g | {row['kcal']} kcal"
                    pdf_output.cell(0, 6, testo_riga, ln=True)
            else:
                pdf_output.cell(0, 6, " - Nessun alimento registrato", ln=True)
            pdf_output.ln(4)
            
        # Correzione fondamentale: conversione esplicita in bytes standard per Streamlit
        raw_output = pdf_output.output()
        pdf_bytes = bytes(raw_output) if isinstance(raw_output, (bytearray, bytes)) else raw_output.encode('latin1')
        
        st.download_button(
            label="📥 Clicca qui per scaricare il PDF",
            data=pdf_bytes,
            file_name=f"report_alimentare_{data_str}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Errore nella generazione del PDF: {e}")
