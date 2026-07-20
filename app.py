import streamlit as st
import pandas as pd

# 1. Configurazione della pagina
st.set_page_config(page_title="Diario Alimentare", page_icon="🍏", layout="centered")

# Stile CSS per rendere l'interfaccia elegante su iPhone e Mac
st.markdown("""
    <style>
    .main { background-color: #fafbfb; }
    .stButton>button { width: 100%; background-color: #3b5e4f; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #2e3b34; color: white; }
    .metric-box { background-color: #e8efea; padding: 15px; border-radius: 10px; text-align: center; border-left: 5px solid #3b5e4f; }
    </style>
""", unsafe_allow_html=True)

# 2. Inizializzazione della Banca Dati Alimenti nello Stato della Sessione
# Sostituisci la tua lista di alimenti predefinita con questa:
if 'banca_dati' not in st.session_state:
    st.session_state['banca_dati'] = {
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
if 'diario' not in st.session_state:
    st.session_state.diario = []

# 3. BARRA LATERALE: Calcolo Fabbisogno (Mifflin-St Jeor)
st.sidebar.header("⚙️ Impostazioni Fabbisogno")
genere = st.sidebar.radio("Genere", ["Uomo", "Donna"])
peso = st.sidebar.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
altezza = st.sidebar.number_input("Altezza (cm)", min_value=100, max_value=250, value=175)
eta = st.sidebar.number_input("Età (anni)", min_value=1, max_value=120, value=30)
laf = st.sidebar.selectbox("Attività Fisica (LAF)", 
                           options=[1.2, 1.375, 1.55, 1.725], 
                           format_func=lambda x: f"{x} (Sedentario)" if x==1.2 else f"{x} (Leggero)" if x==1.375 else f"{x} (Moderato)" if x==1.55 else f"{x} (Intenso)")

# Calcolo Mifflin-St Jeor
if genere == "Uomo":
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
else:
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161
tdee = int(bmr * laf)

# Target Macro
target_cho = int((tdee * 0.40) / 4)
target_pro = int((tdee * 0.30) / 4)
target_fat = int((tdee * 0.30) / 9)

# 4. SCHERMATA PRINCIPALE
st.title("🍏 Il Mio Diario Alimentare")

# Calcolo consumati
df_diario = pd.DataFrame(st.session_state.diario) if st.session_state.diario else pd.DataFrame(columns=["Pasto", "Alimento", "Grammi", "CHO", "PRO", "FAT", "Kcal"])

tot_cho = df_diario["CHO"].sum() if not df_diario.empty else 0.0
tot_pro = df_diario["PRO"].sum() if not df_diario.empty else 0.0
tot_fat = df_diario["FAT"].sum() if not df_diario.empty else 0.0
tot_kcal = df_diario["Kcal"].sum() if not df_diario.empty else 0

# Widget Riassuntivo (Calorie Rimanenti)
rem_kcal = tdee - tot_kcal
st.markdown(f"""
<div class="metric-box">
    <h3>Calorie Rimanenti Oggi</h3>
    <h1 style="color: {'#3b5e4f' if rem_kcal >= 0 else '#b02a37'};">{rem_kcal} / {tdee} kcal</h1>
    <p><b>Carboidrati:</b> {tot_cho:.1f}g / {target_cho}g | <b>Proteine:</b> {tot_pro:.1f}g / {target_pro}g | <b>Grassi:</b> {tot_fat:.1f}g / {target_fat}g</p>
</div>
""", unsafe_allow_html=True)

st.write("---")

# 5. AGGIUNGI ALIMENTO AL DIARIO
st.subheader("➕ Inserisci Alimento nel Diario")
col1, col2 = st.columns([2, 1])

with col1:
    pasto_sel = st.selectbox("Seleziona Pasto", ["Colazione", "Spuntino Mattutino", "Pranzo", "Merenda", "Cena", "Extra"])
    alimento_sel = st.selectbox("Seleziona Alimento", st.session_state.db_alimenti["Alimento"].tolist())

with col2:
    grammi_sel = st.number_input("Grammi (g)", min_value=1, max_value=2000, value=100, step=5)
    st.write(" ") # Spaziatore
    aggiungi = st.button("Aggiungi")

if aggiungi:
    row = st.session_state.db_alimenti[st.session_state.db_alimenti["Alimento"] == alimento_sel].iloc[0]
    st.session_state.diario.append({
        "Pasto": pasto_sel,
        "Alimento": alimento_sel,
        "Grammi": grammi_sel,
        "CHO": round((row["Carboidrati"] * grammi_sel) / 100, 1),
        "PRO": round((row["Proteine"] * grammi_sel) / 100, 1),
        "FAT": round((row["Grassi"] * grammi_sel) / 100, 1),
        "Kcal": int((row["Calorie"] * grammi_sel) / 100)
    })
    st.rerun()

# 6. VISUALIZZAZIONE DEI 6 PASTI
st.subheader("📑 I tuoi Pasti di Oggi")
pasti_lista = ["Colazione", "Spuntino Mattutino", "Pranzo", "Merenda", "Cena", "Extra"]

for p in pasti_lista:
    df_pasto = df_diario[df_diario["Pasto"] == p]
    with st.expander(f"➔ {p} (Totale Kcal: {int(df_pasto['Kcal'].sum()) if not df_pasto.empty else 0})", expanded=True):
        if not df_pasto.empty:
            st.dataframe(df_pasto[["Alimento", "Grammi", "CHO", "PRO", "FAT", "Kcal"]], use_container_width=True, hide_index=True)
        else:
            st.caption("Nessun alimento inserito per questo pasto.")

# Pulsante per resettare il diario giornaliero
if st.button("🗑️ Svuota Diario Giornaliero"):
    st.session_state.diario = []
    st.rerun()

# 7. GESTIONE BANCA DATI (Espandibile dall'utente)
st.write("---")
with st.expander("🗂️ Gestisci / Aggiungi Alimenti alla Banca Dati"):
    st.dataframe(st.session_state.db_alimenti, use_container_width=True, hide_index=True)
    
    st.write("**Nuovo Alimento (Valori per 100g):**")
    c1, c2, c3, c4, c5 = st.columns(5)
    n_nom = c1.text_input("Nome")
    n_cho = c2.number_input("Carb (g)", min_value=0.0, max_value=100.0, step=0.1)
    n_pro = c3.number_input("Prot (g)", min_value=0.0, max_value=100.0, step=0.1)
    n_fat = c4.number_input("Grass (g)", min_value=0.0, max_value=100.0, step=0.1)
    n_cal = c5.number_input("Kcal", min_value=0, max_value=900, step=1)
    
    if st.button("💾 Salva in Banca Dati"):
        if n_nom:
            nuovo_alimento = pd.DataFrame([{"Alimento": n_nom, "Carboidrati": n_cho, "Proteine": n_pro, "Grassi": n_fat, "Calorie": n_cal}])
            st.session_state.db_alimenti = pd.concat([st.session_state.db_alimenti, nuovo_alimento]).sort_values(by="Alimento").reset_index(drop=True)
            st.success(f"'{n_nom}' aggiunto correttamente!")
            st.rerun()
