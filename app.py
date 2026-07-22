import streamlit as dt

# Configurazione della pagina
dt.set_page_config(
    page_title="Dashboard Unica Allenamento & Nutrizione",
    page_icon="🚴‍♂️",
    layout="wide",
)

# Applicazione di stili CSS personalizzati per un layout pulito a pagina singola (senza sidebar)
dt.markdown(
    """
    <style>
    /* Stile generale dello sfondo e del font */
    .stApp {
        background-color: #0e1110;
        color: #e8efe9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Stile delle card / metric container */
    .metric-card {
        background-color: #171d1a;
        border: 1px solid #1a211c;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }
    
    /* Intestazioni personalizzate */
    h1, h2, h3 {
        color: #e8efe9 !important;
        font-weight: 600;
    }
    
    /* Rimozione degli elementi della sidebar qualora visibili */
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- INTESTAZIONE PRINCIPALE ---
dt.markdown(
    "<h1 style='font-size: 28px;'>Dashboard Unica: Attività & Diario Nutrizionale</h1>",
    unsafe_allow_html=True,
)
dt.markdown(
    "<p style='color: #8fa98c;'>Panoramica completa del carico di lavoro e monitoraggio calorico basato sull'equazione di Mifflin-St Jeor.</p>",
    unsafe_allow_html=True,
)

dt.markdown("<br>", unsafe_allow_html=True)

# --- PARAMETRI DI CALCOLO (Mifflin-St Jeor) ---
# Dati atleta: 56 anni, 173 cm, 75 kg (Uomo, inserendo un fattore di attività moderato/sportivo)
peso = 75.0
altezza = 173.0
eta = 56
# Formula BMR Mifflin-St Jeor per uomini: (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
tdee = bmr * 1.55  # Stima con allenamento regolare (passista-scalatore)

# Valori di esempio giornalieri consumati finora
calorie_assunte = 2100
proteine_assunte = 110
carboidrati_assunti = 250
grassi_assunti = 65

# Target giornalieri stimati sul TDEE
target_calorie = int(tdee)
target_proteine = 140  # g
target_carboidrati = 300  # g
target_grassi = 70  # g

# Calcolo rimanenze
rimanenza_calorie = target_calorie - calorie_assunte
rimanenza_proteine = target_proteine - proteine_assunte
rimanenza_carboidrati = target_carboidrati - carboidrati_assunti
rimanenza_grassi = target_grassi - grassi_assunti

# --- SEZIONE 1: METRICHE GENERALI (CARD) ---
col1, col2, col3, col4 = dt.columns(4)

with col1:
    dt.markdown(
        f"""
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Carico Settimanale</p>
            <h3 style="margin: 0; font-size: 24px;">450 TSS</h3>
            <p style="font-size: 11px; color: #10b981; margin-top: 8px;">FTP: 279 W</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    dt.markdown(
        f"""
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Dispendio Energetico (TDEE)</p>
            <h3 style="margin: 0; font-size: 24px;">{int(tdee)} kcal</h3>
            <p style="font-size: 11px; color: #8fa98c; margin-top: 8px;">Mifflin-St Jeor</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    dt.markdown(
        """
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Cadenza Media</p>
            <h3 style="margin: 0; font-size: 24px;">92 rpm</h3>
            <p style="font-size: 11px; color: #8fa98c; margin-top: 8px;">Target fluido</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    dt.markdown(
        f"""
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Bilancio Calorico</p>
            <h3 style="margin: 0; font-size: 24px;">{calorie_assunte} kcal</h3>
            <p style="font-size: 11px; color: #f59e0b; margin-top: 8px;">Mancano {rimanenza_calorie} kcal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- SEZIONE 2: DIARIO ALIMENTARE E PROGRESS BAR TARGET ---
dt.markdown("<br>", unsafe_allow_html=True)
dt.markdown("<h3>🥗 Diario Alimentare & Rimanenze al Target</h3>", unsafe_allow_html=True)
dt.markdown(
    "<p style='color: #8fa98c; font-size: 14px;'>Monitoraggio in tempo reale dei macronutrienti rispetto al fabbisogno giornaliero calcolato.</p>",
    unsafe_allow_html=True,
)

col_nutr1, col_nutr2 = dt.columns(2)

with col_nutr1:
    dt.markdown('<div class="metric-card">', unsafe_allow_html=True)
    dt.markdown("<h4>Calorie Giornaliere</h4>")
    dt.write(
        f"Assunte: **{calorie_assunte} kcal** / Target: **{target_calorie} kcal**"
    )
    prog_cal = min(max(calorie_assunte / target_calorie, 0.0), 1.0)
    dt.progress(prog_cal)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_calorie} kcal</b></p>",
        unsafe_allow_html=True,
    )

    dt.markdown("<h4>Proteine</h4>")
    dt.write(
        f"Assunte: **{proteine_assunte} g** / Target: **{target_proteine} g**"
    )
    prog_prot = min(max(proteine_assunte / target_proteine, 0.0), 1.0)
    dt.progress(prog_prot)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_proteine} g</b></p>",
        unsafe_allow_html=True,
    )
    dt.markdown("</div>", unsafe_allow_html=True)

with col_nutr2:
    dt.markdown('<div class="metric-card">', unsafe_allow_html=True)
    dt.markdown("<h4>Carboidrati</h4>")
    dt.write(
        f"Assunti: **{carboidrati_assunti} g** / Target: **{target_carboidrati} g**"
    )
    prog_carb = min(max(carboidrati_assunti / target_carboidrati, 0.0), 1.0)
    dt.progress(prog_carb)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_carboidrati} g</b></p>",
        unsafe_allow_html=True,
    )

    dt.markdown("<h4>Grassi</h4>")
    dt.write(f"Assunti: **{grassi_assunti} g** / Target: **{target_grassi} g**")
    prog_grassi = min(max(grassi_assunti / target_grassi, 0.0), 1.0)
    dt.progress(prog_grassi)
    dt.markdown(
        f"<p style='font-size: 12px; color: #8fa98c;'>Rimanenza al target: <b>{rimanenza_grassi} g</b></p>",
        unsafe_allow_html=True,
    )
    dt.markdown("</div>", unsafe_allow_html=True)

# --- SEZIONE 3: GRAFICO E DETTAGLIO ALLENAMENTO ---
dt.markdown("<br>", unsafe_allow_html=True)
col_sx, col_dx = dt.columns([7, 5])

with col_sx:
    dt.markdown(
        """
        <div class="metric-card">
            <h3>📈 Andamento Potenza & Sforzo</h3>
            <p style="color: #8fa98c; font-size: 14px;">Monitoraggio delle uscite settimanali.</p>
        """,
        unsafe_allow_html=True,
    )
    chart_data = {
        "Giorno": ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"],
        "Potenza (W)": [180, 210, 0, 195, 220, 250, 230],
    }
    dt.line_chart(
        chart_data,
        x="Giorno",
        y="Potenza (W)",
        color="#f97316",
        use_container_width=True,
    )
    dt.markdown("</div>", unsafe_allow_html=True)

with col_dx:
    dt.markdown(
        """
        <div class="metric-card">
            <h3>⚙️ Parametri Atleta</h3>
            <p style="color: #8fa98c; font-size: 14px;">Configurazione di riferimento per il calcolo metabolico:</p>
            <ul style="color: #e8efe9; font-size: 14px; line-height: 1.6;">
                <li><b>Profilo:</b> Passista-Scalatore</li>
                <li><b>Età / Altezza / Peso:</b> 56 anni, 173 cm, 75 kg</li>
                <li><b>BMR (Mifflin-St Jeor):</b> {0:.0f} kcal</li>
                <li><b>Sorgente Dati:</b> Database locale CSV</li>
            </ul>
        </div>
        """.format(
            bmr
        ),
        unsafe_allow_html=True,
    )
