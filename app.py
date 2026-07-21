import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF
import re

# Configurazione della pagina (deve essere la prima istruzione Streamlit)
st.set_page_config(
    page_title="Diario Alimentare & Allenamento",
    page_icon="🚴‍♂️",
    layout="wide"
)

# Banca dati precompilata iniziale
DEFAULT_BANCA_DATI = [
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

if "banca_dati_df" not in st.session_state:
    st.session_state.banca_dati_df = pd.DataFrame(DEFAULT_BANCA_DATI)

# Pulizia preventiva della banca dati da eventuali valori NaN o stringhe vuote
st.session_state.banca_dati_df = st.session_state.banca_dati_df.dropna(subset=["Alimento"])
st.session_state.banca_dati_df = st.session_state.banca_dati_df[st.session_state.banca_dati_df["Alimento"].astype(str).str.strip() != ""]

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

if "db_diario" not in st.session_state:
    st.session_state.db_diario = {}

st.title("🚴‍♂️ Pianificatore Alimentare & Allenamento (Mifflin)")

st.sidebar.header("🗓️ Seleziona Giorno")
data_selezionata = st.sidebar.date_input("Data", value=date.today())
data_str = data_selezionata.strftime("%Y-%m-%d")

if data_str not in st.session_state.db_diario:
    st.session_state.db_diario[data_str] = {pasto: pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]) for pasto in PASTI}

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parametri Mifflin-St Jeor & Allenamento")
peso = st.sidebar.number_input("Peso (kg)", value=70.0)
altezza = st.sidebar.number_input("Altezza (cm)", value=175.0)
eta = st.sidebar.number_input("Età (anni)", value=56)
genere = st.sidebar.selectbox("Genere", ["Uomo", "Donna"])

livello_allenamento = st.sidebar.selectbox(
    "Intensità Allenamento / Attività Giornaliera",
    [
        "Riposo / Sedentario (PAL 1.2)", 
        "Attività Leggera (PAL 1.375)", 
        "Allenamento Moderato (PAL 1.55)", 
        "Allenamento Intenso / Rouleur-Climber (PAL 1.725)", 
        "Doppio Allenamento / Estremo (PAL 1.9)"
    ],
    index=2
)

pal_dict = {
    "Riposo / Sedentario (PAL 1.2)": 1.2,
    "Attività Leggera (PAL 1.375)": 1.375,
    "Allenamento Moderato (PAL 1.55)": 1.55,
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)": 1.725,
    "Doppio Allenamento / Estremo (PAL 1.9)": 1.9
}
pal_selezionato = pal_dict[livello_allenamento]

if genere == "Uomo":
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
else:
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

tdee = bmr * pal_selezionato
obj_kcal = round(tdee, 0)
obj_carbo = 230.0
obj_prot = 165.0
obj_grassi = 70.0

st.sidebar.info(f"**BMR stimato:** {bmr:.0f} kcal\n\n**TDEE dinamico:** {obj_kcal:.0f} kcal")

tot_carbo = sum([st.session_state.db_diario[data_str][p]["carbo"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])
tot_prot = sum([st.session_state.db_diario[data_str][p]["proteine"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])
tot_grassi = sum([st.session_state.db_diario[data_str][p]["grassi"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])
tot_kcal = sum([st.session_state.db_diario[data_str][p]["kcal"].sum() for p in PASTI if not st.session_state.db_diario[data_str][p].empty])

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

with st.expander("📚 Gestione Avanzata Banca Dati Alimenti", expanded=False):
    st.markdown("### Accesso e Visualizzazione")
    banca_dati = st.session_state.banca_dati_df
    st.dataframe(banca_dati, use_container_width=True)
    
    st.markdown("---")
    
    # Sezione per l'inserimento manuale di un alimento alla volta
    st.markdown("### ✍️ Inserimento Manuale Singolo Alimento")
    with st.form("form_inserimento_manuale"):
        col_man1, col_man2, col_man3 = st.columns(3)
        with col_man1:
            nuovo_nome = st.text_input("Nome Alimento")
        with col_man2:
            nuovo_grn = st.number_input("Quantità di Riferimento (g o p)", min_value=1.0, value=100.0)
        with col_man3:
            nuovo_kcal = st.number_input("Calorie (kcal)", min_value=0.0, value=0.0, step=0.1)
            
        col_man4, col_man5, col_man6 = st.columns(3)
        with col_man4:
            nuovo_carbo = st.number_input("Carboidrati (g)", min_value=0.0, value=0.0, step=0.1)
        with col_man5:
            nuovo_prot = st.number_input("Proteine (g)", min_value=0.0, value=0.0, step=0.1)
        with col_man6:
            nuovo_grassi = st.number_input("Grassi (g)", min_value=0.0, value=0.0, step=0.1)
            
        btn_submit_manuale = st.form_submit_button("Aggiungi Alimento alla Banca Dati")
        if btn_submit_manuale:
            if nuovo_nome.strip() == "":
                st.error("Inserisci un nome valido per l'alimento.")
            else:
                nuova_riga_df = pd.DataFrame([{
                    "Alimento": nuovo_nome.strip().lower(),
                    "gr/n": nuovo_grn,
                    "carbo": nuovo_carbo,
                    "proteine": nuovo_prot,
                    "grassi": nuovo_grassi,
                    "kcal": nuovo_kcal
                }])
                # Se l'alimento esiste già, lo aggiorna/sostituisce
                st.session_state.banca_dati_df = pd.concat(
                    [st.session_state.banca_dati_df[st.session_state.banca_dati_df["Alimento"].astype(str).str.lower() != nuovo_nome.strip().lower()], nuova_riga_df],
                    ignore_index=True
                ).sort_values("Alimento").reset_index(drop=True)
                st.success(f"Alimento '{nuovo_nome}' aggiunto/aggiornato con successo nella banca dati!")
                st.rerun()

    st.markdown("---")
    
    col_bd1, col_bd2 = st.columns(2)
    
    with col_bd1:
        st.markdown("### 🗑️ Cancellazione Parziale o Totale")
        alimenti_disponibili = banca_dati["Alimento"].dropna().tolist()
        alimenti_da_eliminare = st.multiselect("Seleziona alimenti da rimuovere dalla banca dati:", alimenti_disponibili, key="multi_del_alimenti")
        
        col_del_a, col_del_b = st.columns(2)
        with col_del_a:
            if st.button("Elimina Selezionati"):
                if alimenti_da_eliminare:
                    st.session_state.banca_dati_df = banca_dati[~banca_dati["Alimento"].isin(alimenti_da_eliminare)].reset_index(drop=True)
                    st.success("Alimenti selezionati rimossi con successo!")
                    st.rerun()
                else:
                    st.warning("Nessun alimento selezionato.")
        with col_del_b:
            if st.button("Svuota Intera Banca Dati", type="primary"):
                st.session_state.banca_dati_df = pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"])
                st.warning("Banca dati svuotata completamente.")
                st.rerun()
                
   with col_bd2:
        st.markdown("### 📂 Integrazione File CSV")
        st.info(
            "Carica un file CSV. L'ordine atteso per colonna è: Alimento, gr/n, carbo, proteine, grassi, kcal."
        )
        file_caricato = st.file_uploader(
            "Carica file CSV", type=["csv"], key="uploader_banca_dati"
        )

        if file_caricato is not None:
            try:
                df_nuovo = None
                try:
                    df_nuovo = pd.read_csv(
                        file_caricato, encoding="utf-8", sep=None, engine="python"
                    )
                except UnicodeDecodeError:
                    file_caricato.seek(0)
                    df_nuovo = pd.read_csv(
                        file_caricato,
                        encoding="latin-1",
                        sep=None,
                        engine="python",
                    )
                except Exception:
                    file_caricato.seek(0)
                    df_nuovo = pd.read_csv(
                        file_caricato, encoding="utf-8", sep=";", engine="python"
                    )

                if df_nuovo is not None and not df_nuovo.empty:
                    st.write("Anteprima dati letti dal file:", df_nuovo.head())
                    if st.button("Conferma e Aggiungi alla Banca Dati"):
                        colonne_attese = [
                            "Alimento",
                            "gr/n",
                            "carbo",
                            "proteine",
                            "grassi",
                            "kcal",
                        ]

                        # Pulizia e standardizzazione nomi colonne
                        cols_orig = [str(c).strip().lower() for c in df_nuovo.columns]
                        df_nuovo.columns = cols_orig

                        mapping_colonne = {}
                        for c in cols_orig:
                            if "alimento" in c or "nome" in c:
                                mapping_colonne[c] = "Alimento"
                            elif "gr" in c or "quant" in c or "peso" in c or "numero" in c:
                                mapping_colonne[c] = "gr/n"
                            elif "carb" in c:
                                mapping_colonne[c] = "carbo"
                            elif "prot" in c:
                                mapping_colonne[c] = "proteine"
                            elif "grass" in c or "fat" in c:
                                mapping_colonne[c] = "grassi"
                            elif "kcal" in c or "calorie" in c:
                                mapping_colonne[c] = "kcal"

                        df_nuovo = df_nuovo.rename(columns=mapping_colonne)
                        # Elimina eventuali colonne duplicate dopo il mapping
                        df_nuovo = df_nuovo.loc[:, ~df_nuovo.columns.duplicated()]

                        presenti = [
                            col for col in colonne_attese if col in df_nuovo.columns
                        ]
                        if len(presenti) < 4 and len(df_nuovo.columns) >= 4:
                            col_mapping_pos = {}
                            for idx, col_name in enumerate(df_nuovo.columns):
                                if idx < len(colonne_attese):
                                    col_mapping_pos[col_name] = colonne_attese[idx]
                            df_nuovo = df_nuovo.rename(columns=col_mapping_pos)
                            df_nuovo = df_nuovo.loc[:, ~df_nuovo.columns.duplicated()]

                        # Costruzione sicura del DataFrame tramite dizionario
                        data_dict = {}
                        for col in colonne_attese:
                            if col in df_nuovo.columns:
                                data_dict[col] = df_nuovo[col].values
                            else:
                                data_dict[col] = (
                                    0 if col != "Alimento" else "Sconosciuto"
                                )

                        df_finale = pd.DataFrame(data_dict)

                        # Pulizia righe vuote o non valide
                        df_finale = df_finale.dropna(subset=["Alimento"])
                        df_finale = df_finale[
                            df_finale["Alimento"].astype(str).str.strip() != ""
                        ]

                        # Aggiornamento dello stato e salvataggio su disco
                        st.session_state.banca_dati_df = (
                            pd.concat(
                                [st.session_state.banca_dati_df, df_finale],
                                ignore_index=True,
                            )
                            .drop_duplicates(subset=["Alimento"])
                            .reset_index(drop=True)
                        )
                        salva_dati_disco()
                        st.success(
                            "Banca dati aggiornata con successo dal file CSV!"
                        )
                        st.rerun()
            except Exception as e:
                st.error(f"Errore durante la lettura del file CSV: {e}")

st.markdown("---")

st.subheader("🍽️ Inserimento Alimenti nei Pasti")
pasto_selezionato = st.selectbox("Seleziona il pasto a cui aggiungere l'alimento:", PASTI)

banca_dati_corrente = st.session_state.banca_dati_df
alimenti_validi = banca_dati_corrente["Alimento"].dropna().tolist()
alimenti_validati = [str(a) for a in alimenti_validi if str(a).strip() != "" and str(a).lower() != "nan"]

if alimenti_validati:
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        alimento_scelto = st.selectbox("Alimento", alimenti_validati, key="sel_alimento_principale")
        item_row = banca_dati_corrente[banca_dati_corrente["Alimento"].astype(str) == str(alimento_scelto)].iloc[0]
        
        val_gr_n = item_row["gr/n"]
        if pd.notna(val_gr_n):
            if isinstance(val_gr_n, (int, float)):
                default_q = int(val_gr_n)
            else:
                numeri_estratti = re.findall(r'\d+', str(val_gr_n))
                default_q = int(numeri_estratti[0]) if numeri_estratti else 100
        else:
            default_q = 100

    with col_ins2:
        quantita = st.number_input("Quantità (g o porzione)", min_value=1, value=default_q, key="num_quantita_principale")

    if st.button("Aggiungi al pasto selezionato", key="btn_aggiungi_principale"):
        fattore = quantita / default_q if default_q > 0 else 1
        c_calc = round(float(item_row["carbo"]) * fattore, 2) if pd.notna(item_row["carbo"]) else 0.0
        p_calc = round(float(item_row["proteine"]) * fattore, 2) if pd.notna(item_row["proteine"]) else 0.0
        g_calc = round(float(item_row["grassi"]) * fattore, 2) if pd.notna(item_row["grassi"]) else 0.0
        k_calc = round(float(item_row["kcal"]) * fattore, 2) if pd.notna(item_row["kcal"]) else 0.0
        
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
else:
    st.warning("La banca dati è vuota o contiene solo elementi non validi.")

st.markdown("---")

st.subheader("📋 Panoramica dei 6 Pasti Giornalieri")

cols_pasti = st.columns(3)
for i, pasto in enumerate(PASTI):
    col_target = cols_pasti[i % 3]
    with col_target:
        with st.container(border=True):
            st.markdown(f"### 🥣 {pasto}")
            df_p = st.session_state.db_diario[data_str][pasto]
            
            if not df_p.empty:
                p_kcal = df_p["kcal"].sum()
                p_carb = df_p["carbo"].sum()
                p_prot = df_p["proteine"].sum()
                p_gras = df_p["grassi"].sum()
                st.caption(f"Totale: {p_kcal:.1f} kcal | C: {p_carb:.1f}g | P: {p_prot:.1f}g | G: {p_gras:.1f}g")
                
                st.dataframe(df_p, use_container_width=True)
                
                indices_disponibili = df_p.index.tolist()
                opzioni_rimozione = {f"Riga {idx}: {df_p.loc[idx, 'Alimento']} ({df_p.loc[idx, 'gr/n']}g)": idx for idx in indices_disponibili}
                
                voce_da_rimuovere = st.selectbox("Elimina voce:", list(opzioni_rimozione.keys()), key=f"del_box_{pasto}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Elimina", key=f"btn_del_{pasto}"):
                        idx_to_drop = opzioni_rimozione[voce_da_rimuovere]
                        st.session_state.db_diario[data_str][pasto] = df_p.drop(idx_to_drop).reset_index(drop=True)
                        st.rerun()
                with col_btn2:
                    if st.button("Svuota", key=f"clear_{pasto}"):
                        st.session_state.db_diario[data_str][pasto] = pd.DataFrame(columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"])
                        st.rerun()
            else:
                st.info("Nessun alimento registrato.")

st.markdown("---")

st.subheader("📄 Esportazione Report in PDF")

col_pdf1, col_pdf2 = st.columns(2)

with col_pdf1:
    st.markdown("### Report Giornaliero")
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
            pdf_output.cell(0, 8, f"Calorie: {tot_kcal:.1f} / {obj_kcal} kcal ({livello_allenamento})", ln=True)
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
                
            raw_output = pdf_output.output()
            pdf_bytes = bytes(raw_output) if isinstance(raw_output, (bytearray, bytes)) else raw_output.encode('latin1')
            
            st.download_button(
                label="📥 Scarica PDF Giornaliero",
                data=pdf_bytes,
                file_name=f"report_giornaliero_{data_str}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Errore nella generazione del PDF giornaliero: {e}")

with col_pdf2:
    st.markdown("### Report Personalizzato per Intervallo di Date")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_inizio = st.date_input("Data Inizio", value=date.today() - timedelta(days=6), key="pdf_data_inizio")
    with col_d2:
        data_fine = st.date_input("Data Fine", value=date.today(), key="pdf_data_fine")
    
    if st.button("Genera e Scarica PDF Intervallo (Traccia Totale)"):
        try:
            if data_inizio > data_fine:
                st.error("La data di inizio non può essere successiva alla data di fine.")
            else:
                delta_giorni = (data_fine - data_inizio).days + 1
                tot_p_kcal, tot_p_carbo, tot_p_prot, tot_p_grassi = 0.0, 0.0, 0.0, 0.0
                dettaglio_periodo = []
                
                for i in range(delta_giorni):
                    d_corrente = data_inizio + timedelta(days=i)
                    d_str = d_corrente.strftime("%Y-%m-%d")
                    if d_str in st.session_state.db_diario:
                        d_kcal = sum([st.session_state.db_diario[d_str][p]["kcal"].sum() for p in PASTI if not st.session_state.db_diario[d_str][p].empty])
                        d_carbo = sum([st.session_state.db_diario[d_str][p]["carbo"].sum() for p in PASTI if not st.session_state.db_diario[d_str][p].empty])
                        d_prot = sum([st.session_state.db_diario[d_str][p]["proteine"].sum() for p in PASTI if not st.session_state.db_diario[d_str][p].empty])
                        d_grassi = sum([st.session_state.db_diario[d_str][p]["grassi"].sum() for p in PASTI if not st.session_state.db_diario[d_str][p].empty])
                        
                        tot_p_kcal += d_kcal
                        tot_p_carbo += d_carbo
                        tot_p_prot += d_prot
                        tot_p_grassi += d_grassi
                        
                        if d_kcal > 0 or d_carbo > 0:
                            dettaglio_periodo.append((d_str, d_kcal, d_carbo, d_prot, d_grassi))

                pdf_output = FPDF()
                pdf_output.add_page()
                pdf_output.set_font("Arial", "B", 16)
                pdf_output.cell(0, 10, f"Report Nutrizionale ({data_inizio.strftime('%d/%m/%Y')} - {data_fine.strftime('%d/%m/%Y')})", ln=True, align="C")
                pdf_output.ln(10)
                
                pdf_output.set_font("Arial", "B", 12)
                pdf_output.cell(0, 10, "Riepilogo Totale del Periodo:", ln=True)
                pdf_output.set_font("Arial", "", 11)
                pdf_output.cell(0, 8, f"Calorie Totali: {tot_p_kcal:.1f} kcal (Media giornaliera: {tot_p_kcal / delta_giorni:.1f} kcal)", ln=True)
                pdf_output.cell(0, 8, f"Carboidrati Totali: {tot_p_carbo:.1f} g (Media: {tot_p_carbo / delta_giorni:.1f} g)", ln=True)
                pdf_output.cell(0, 8, f"Proteine Totali: {tot_p_prot:.1f} g (Media: {tot_p_prot / delta_giorni:.1f} g)", ln=True)
                pdf_output.cell(0, 8, f"Grassi Totali: {tot_p_grassi:.1f} g (Media: {tot_p_grassi / delta_giorni:.1f} g)", ln=True)
                pdf_output.ln(10)
                
                pdf_output.set_font("Arial", "B", 12)
                pdf_output.cell(0, 10, "Traccia Giornaliera dei Macronutrienti:", ln=True)
                pdf_output.set_font("Arial", "", 10)
                
                if dettaglio_periodo:
                    for d_str, dk, dc, dp, dg in dettaglio_periodo:
                        riga_traccia = f" - {d_str}: {dk:.1f} kcal | Carbo: {dc:.1f}g | Prot: {dp:.1f}g | Grassi: {dg:.1f}g"
                        pdf_output.cell(0, 6, riga_traccia, ln=True)
                else:
                    pdf_output.cell(0, 6, " - Nessun dato registrato nel periodo selezionato", ln=True)
                    
                raw_output = pdf_output.output()
                pdf_bytes = bytes(raw_output) if isinstance(raw_output, (bytearray, bytes)) else raw_output.encode('latin1')
                
                st.download_button(
                    label="📥 Scarica PDF Periodo Personalizzato",
                    data=pdf_bytes,
                    file_name=f"report_periodo_{data_inizio}_al_{data_fine}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Errore nella generazione del PDF personalizzato: {e}")

