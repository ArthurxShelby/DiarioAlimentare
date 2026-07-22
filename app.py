import streamlit as dt

# Configurazione della pagina
dt.set_page_config(
    page_title="Dashboard Allenamento & Nutrizione",
    page_icon="🚴‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Applicazione di stili CSS personalizzati per replicare il look scuro e moderno dell'artifact
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
    }
    
    /* Intestazioni personalizzate */
    h1, h2, h3 {
        color: #e8efe9 !important;
        font-weight: 600;
    }
    
    /* Bottoni personalizzati */
    .stButton>button {
        background-color: #f97316;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #ea6a0f;
        color: white;
    }
    
    /* Sidebar personalizzata */
    [data-testid="stSidebar"] {
        background-color: #121412;
        border-right: 1px solid #1a211c;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR ---
with dt.sidebar:
    dt.markdown(
        "### 🚴‍♂️ Navigazione",
        help="Seleziona la sezione della dashboard",
    )
    menu = dt.radio(
        "",
        [
            "Panoramica",
            "Sessioni di Allenamento",
            "Diario Nutrizionale",
            "Impostazioni",
        ],
    )

    dt.markdown("---")
    dt.markdown("### Profilo Atleta")
    dt.info(
        "**Stile:** Passista-Scalatore\n\n"
        "**FTP:** 279 W\n\n"
        "**Altezza/Peso:** 173 cm / 75 kg"
    )

# --- CONTENUTO PRINCIPALE ---
dt.markdown(
    "<h1 style='font-size: 28px;'>Dashboard Attività</h1>",
    unsafe_allow_html=True,
)
dt.markdown(
    "<p style='color: #8fa98c;'>Benvenuto nel pannello di controllo per la gestione di carico e nutrizione.</p>",
    unsafe_allow_html=True,
)

dt.markdown("<br>", unsafe_allow_html=True)

# Layout a griglia con colonne per le metriche principali (stile card)
col1, col2, col3, col4 = dt.columns(4)

with col1:
    dt.markdown(
        """
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Carico Settimanale</p>
            <h3 style="margin: 0; font-size: 24px;">450 TSS</h3>
            <p style="font-size: 11px; color: #10b981; margin-top: 8px;">↑ 12% rispetto a ieri</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
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

with col3:
    dt.markdown(
        """
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Dislivello</p>
            <h3 style="margin: 0; font-size: 24px;">3.240 m</h3>
            <p style="font-size: 11px; color: #f59e0b; margin-top: 8px;">Obiettivo mensile</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    dt.markdown(
        """
        <div class="metric-card">
            <p style="font-size: 12px; color: #8fa98c; text-transform: uppercase; margin-bottom: 4px;">Bilancio Calorico</p>
            <h3 style="margin: 0; font-size: 24px;">2.450 kcal</h3>
            <p style="font-size: 11px; color: #10b981; margin-top: 8px;">In linea col piano</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

dt.markdown("<br>", unsafe_allow_html=True)

# Sezione centrale con grafici o tabelle di dettaglio
col_sx, col_dx = dt.columns([7, 5])

with col_sx:
    dt.markdown(
        """
        <div class="metric-card">
            <h3>📈 Andamento Potenza & Sforzo</h3>
            <p style="color: #8fa98c; font-size: 14px;">Monitoraggio delle uscite su base mensile e riscontro dei watt medi registrati.</p>
        """,
        unsafe_allow_html=True,
    )
    # Esempio di grafico nativo Streamlit
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
            <h3>🥗 Ripartizione Macronutrienti</h3>
            <p style="color: #8fa98c; font-size: 14px;">Riepporto giornaliero stimato per sostenere i blocchi di carico.</p>
        """,
        unsafe_allow_html=True,
    )

    # Indicatori di progresso personalizzati
    dt.text("Carboidrati (60%)")
    dt.progress(0.60)

    dt.text("Proteine (25%)")
    dt.progress(0.25)

    dt.text("Grassi (15%)")
    dt.progress(0.15)

    dt.markdown(
        "<br><p style='font-size: 12px; color: #8fa98c;'>Dati sincronizzati con il database locale CSV.</p>",
        unsafe_allow_html=True,
    )
    dt.markdown("</div>", unsafe_allow_html=True)
