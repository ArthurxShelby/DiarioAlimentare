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
""", unsafe_allow_index=True)

# 2. Inizializzazione della Banca Dati Alimenti nello Stato della Sessione
if 'db_alimenti' not in st.session_state:
    st.session_state.db_alimenti = pd.DataFrame([
        {"Alimento": "Albume d'uovo", "Carboidrati": 0.7, "Proteine": 11.0, "Grassi": 0.2, "Calorie": 52},
        {"Alimento": "Petto di Pollo", "Carboidrati": 0.0, "Proteine": 23.0, "Grassi": 1.2, "Calorie": 114},
        {"Alimento": "Avocado", "Carboidrati": 8.5, "Proteine": 2.0, "Grassi": 15.0, "Calorie": 160},
        {"Alimento": "Banana", "Carboidrati": 22.8, "Proteine": 1.1, "Grassi": 0.3, "Calorie": 89},
        {"Alimento": "Bresaola", "Carboidrati": 0.0, "Proteine": 32.0, "Grassi": 2.0, "Calorie": 151},
        {"Alimento": "Broccoli", "Carboidrati": 7.0, "Proteine": 2.8, "Grassi": 0.4, "Calorie": 34},
        {"Alimento": "Fiocchi d'avena", "Carboidrati": 66.0, "Proteine": 16.9, "Grassi": 6.9, "Calorie": 389},
        {"Alimento": "Olio extravergine", "Carboidrati": 0.0, "Proteine": 0.0, "Grassi": 100.0, "Calorie": 884},
        {"Alimento": "Riso Basmati", "Carboidrati": 77.0, "Proteine": 8.0, "Grassi": 1.0, "Calorie": 350},
        {"Alimento": "Salmone fresco", "Carboidrati": 0.0, "Proteine": 20.0, "Grassi": 13.0, "Calorie": 208},
        {"Alimento": "Skyr Bianco", "Carboidrati": 4.0, "Proteine": 11.0, "Grassi": 0.2, "Calorie": 62},
        {"Alimento": "Yogurt greco 0%", "Carboidrati": 4.0, "Proteine": 10.3, "Grassi": 0.0, "Calorie": 57}
    ]).sort_values(by="Alimento").reset_index(drop=True)

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
""", unsafe_allow_index=True)

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
