import streamlit as dt

# Configurazione della pagina
dt.set_page_config(
    page_title="Diario Sportivo & Alimentare",
    page_icon="🚴‍♂️",
    layout="wide",
)

# Applicazione di stili CSS personalizzati per un layout pulito a pagina singola senza sidebar
dt.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1110;
        color: #e8efe9;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background-color: #171d1a;
        border: 1px solid #1a211c;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }
    h1, h2, h3, h4 {
        color: #e8efe9 !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- INTESTAZIONE PRINCIPALE E MENU A SCOMPARSA IN ALTO A DESTRA ---
col_title, col_menu = dt.columns([7, 5])

with col_title:
    dt.markdown(
        "<h1 style='font-size: 28px; margin-top: 10px;'>Diario Sportivo / Alimentare</h1>",
        unsafe_allow_html=True,
    )

with col_menu:
    with dt.expander("⚙️ Parametri & Profilo Mifflin-St Jeor"):
        dt.markdown(
            "**Dati Antropometrici di Riferimento:**\n\n"
            "- **Età:** 56 anni\n"
            "- **Altezza:** 173 cm\n"
            "- **Peso:** 75 kg\n"
            "- **Profilo:** Passista-Scalatore"
        )

# --- PARAMETRI DI CALCOLO (Mifflin-St Jeor) ---
peso = 75.0
altezza = 173.0
eta = 56

# Formula BMR Mifflin-St Jeor per uomini: (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
tdee = bmr * 1.55  # Stima con allenamento regolare

target_calorie = int(tdee)
target_proteine = 140  # g
target_carboidrati = 300  # g
target_grassi = 70  # g

# --- GESTIONE DEI 6 PASTI ---
pasti = {
    "Colazione": {"calorie": 450, "proteine": 25, "carboidrati": 60, "grassi": 12},
    "Merenda Mattutina": {
        "calorie": 200,
        "proteine": 10,
        "carboidrati": 30,
        "grassi": 4,
    },
    "Pranzo": {"calorie": 700, "proteine": 45, "carboidrati": 90, "grassi": 20},
    "Merenda Pomeridiana": {
        "calorie": 250,
        "proteine": 15,
        "carboidrati": 35,
        "grassi": 6,
    },
    "Cena": {"calorie": 650, "proteine": 40, "carboidrati": 70, "grassi": 22},
    "Extra": {"calorie": 150, "proteine": 5, "carboidrati": 20, "grassi": 6},
}

tot_calorie = sum(p["calorie"] for p in pasti.values())
tot_proteine = sum(p["proteine"] for p in pasti.values())
tot_carboidrati = sum(p["carboidrati"] for p in pasti.values())
tot_grassi = sum(p["grassi"] for p in pasti.values())

rimanenza_calorie = target_calorie - tot_calorie
rimanenza_proteine = target_proteine - tot_proteine
rimanenza_carboidrati = target_carboidrati - tot_carboidrati
rimanenza_grassi = target_grassi - tot_grassi

# --- SEZIONE 1: PROGRESS BAR MACRONUTRIENTI E TARGET ---
dt.markdown(
    "<h3>🥗 Diario Alimentare: 6 Pasti & Rimanenze al Target</h3>",
    unsafe_allow_html=True,
)
dt.markdown(
    f"<p style='color: #8fa98c; font-size: 14px;'>Dispendio energetico calcolato con Mifflin-St Jeor (BMR: {bmr:.0f} kcal | TDEE: {tdee:.0f} kcal).</p>",
    unsafe_allow_html=True,
)

col_met1, col_met2 = dt.columns(2)

with col_met1:
    dt.markdown('<div class="metric-card">', unsafe_allow_html=True)
    dt.markdown(
        f"<h4>Calorie Totali: {tot_calorie} / {target_calorie} kcal</h4>"
    )
    prog_cal = min(max(tot_calorie / target_calorie, 0.0), 1.0)
    dt.progress(prog_cal)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_calorie} kcal</b></p>",
        unsafe_allow_html=True,
    )

    dt.markdown(
        f"<h4>Proteine: {tot_proteine}g / {target_proteine}g</h4>",
        unsafe_allow_html=True,
    )
    prog_prot = min(max(tot_proteine / target_proteine, 0.0), 1.0)
    dt.progress(prog_prot)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_proteine} g</b></p>",
        unsafe_allow_html=True,
    )
    dt.markdown("</div>", unsafe_allow_html=True)

with col_met2:
    dt.markdown('<div class="metric-card">', unsafe_allow_html=True)
    dt.markdown(
        f"<h4>Carboidrati: {tot_carboidrati}g / {target_carboidrati}g</h4>",
        unsafe_allow_html=True,
    )
    prog_carb = min(max(tot_carboidrati / target_carboidrati, 0.0), 1.0)
    dt.progress(prog_carb)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_carboidrati} g</b></p>",
        unsafe_allow_html=True,
    )

    dt.markdown(
        f"<h4>Grassi: {tot_grassi}g / {target_grassi}g</h4>",
        unsafe_allow_html=True,
    )
    prog_grassi = min(max(tot_grassi / target_grassi, 0.0), 1.0)
    dt.progress(prog_grassi)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_grassi} g</b></p>",
        unsafe_allow_html=True,
    )
    dt.markdown("</div>", unsafe_allow_html=True)

# --- SEZIONE 2: DETTAGLIO DEI 6 PASTI ---
dt.markdown("<br>", unsafe_allow_html=True)
dt.markdown("<h3>🍽️ Ripartizione dei 6 Pasti Giornalieri</h3>", unsafe_allow_html=True)

cols = dt.columns(3)
pasti_lista = list(pasti.items())

for i, (nome_pasto, valori) in enumerate(pasti_lista):
    with cols[i % 3]:
        dt.markdown(
            f"""
            <div class="metric-card">
                <h4>{nome_pasto}</h4>
                <p style="font-size: 14px; color: #e8efe9; margin: 4px 0;"><b>{valori['calorie']} kcal</b></p>
                <hr style="border-color: #1a211c; margin: 8px 0;">
                <p style="font-size: 12px; color: #8fa98c; margin: 2px 0;">P: {valori['proteine']}g | C: {valori['carboidrati']}g | G: {valori['grassi']}g</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
