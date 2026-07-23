import os
import pickle
import re
from datetime import date, timedelta
from fpdf import FPDF
import pandas as pd
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare & Allenamento - Multi-Atleta",
    page_icon="",
    layout="wide",
)

# --- 0. GESTIONE AUTENTICAZIONE E RUOLI (BLINDATURA) ---
st.sidebar.markdown("### 🔐 Accesso e Sicurezza")
ruolo_utente = st.sidebar.radio(
    "Modalità Utente",
    ["Ospite (Sola Lettura)", "Proprietario / Autorizzato"],
    key="auth_diario",
)

is_proprietario = False
if ruolo_utente == "Proprietario / Autorizzato":
    password_inserita = st.sidebar.text_input(
        "Inserisci Password di Controllo", type="password", key="pass_diario"
    )
    password_corretta = st.secrets.get("auth", {}).get(
        "proprietario_password", "admin123"
    )
    if password_inserita == password_corretta:
        is_proprietario = True
        st.sidebar.success(
            "Accesso Proprietario Autorizzato (Controllo Completo)"
        )
    else:
        st.sidebar.error("Password errata. Modalità limitata a Ospite.")

# --- 0. GESTIONE PERSISTENZA DATI E PULIZIA ---
FILE_PERSISTENZA = "diario_alimentare_multi_db.pkl"
OLD_FILE_PERSISTENZA = "diario_alimentare_db.pkl"


def safe_float(val):
    """Converte in modo sicuro qualsiasi valore in float, gestendo virgole e stringhe."""
    if pd.isna(val):
        return 0.0
    try:
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).strip().replace(",", ".")
        val_clean = re.sub(r"[^\d.-]", "", val_str)
        return float(val_clean) if val_clean else 0.0
    except:
        return 0.0


def pulisci_e_ordina_banca_dati(df):
    """Pulisce le colonne numeriche, rimuove righe vuote e ordina alfabeticamente per Alimento."""
    colonne_numeriche = ["gr/n", "carbo", "proteine", "grassi", "kcal"]
    for col in colonne_numeriche:
        if col in df.columns:
            df[col] = df[col].apply(safe_float)
    
    if "Alimento" in df.columns:
        df = df.dropna(subset=["Alimento"])
        df = df[df["Alimento"].astype(str).str.strip() != ""]
        # Uniforma la formattazione del testo dell'alimento
        df["Alimento"] = df["Alimento"].astype(str).str.strip().str.lower()
        df = df.sort_values("Alimento").drop_duplicates(subset=["Alimento"]).reset_index(drop=True)
    return df


def salva_dati_disco():
    """Salva lo stato della banca dati, degli atleti e dell'atleta corrente nel file locale (solo se proprietario)."""
    if not is_proprietario:
        return
    try:
        dati = {
            "atleti": st.session_state.get("atleti", {}),
            "banca_dati_df": st.session_state.get("banca_dati_df"),
            "atleta_corrente": st.session_state.get("atleta_corrente"),
        }
        with open(FILE_PERSISTENZA, "wb") as f:
            pickle.dump(dati, f)
    except Exception as e:
        st.error(f"Errore durante il salvataggio dei dati: {e}")


def carica_dati_disco():
    """Carica i dati salvati dal file locale (con supporto alla migrazione dal vecchio formato singolo)."""
    if os.path.exists(FILE_PERSISTENZA):
        try:
            with open(FILE_PERSISTENZA, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Errore durante il caricamento dei dati salvati: {e}")
    elif os.path.exists(OLD_FILE_PERSISTENZA):
        try:
            with open(OLD_FILE_PERSISTENZA, "rb") as f:
                old_dati = pickle.load(f)
            migrated = {
                "atleti": {
                    "Atleta Principale": {
                        "peso": old_dati.get("peso", 70.0),
                        "altezza": old_dati.get("altezza", 175.0),
                        "eta": old_dati.get("eta", 56),
                        "genere": old_dati.get("genere", "Uomo"),
                        "livello_allenamento": old_dati.get(
                            "livello_allenamento",
                            "Allenamento Moderato (PAL 1.55)",
                        ),
                        "db_diario": old_dati.get("db_diario", {}),
                    }
                },
                "banca_dati_df": old_dati.get("banca_dati_df", None),
                "atleta_corrente": "Atleta Principale",
            }
            return migrated
        except Exception as e:
            st.error(f"Errore durante la migrazione dei vecchi dati: {e}")
    return None


dati_salvati = carica_dati_disco()

# Banca dati precompilata iniziale (condivisa tra gli atleti)
DEFAULT_BANCA_DATI = [
    {
        "Alimento": "anguria",
        "gr/n": 300,
        "carbo": 111.0,
        "proteine": 1.2,
        "grassi": 0.6,
        "kcal": 48.0,
    },
    {
        "Alimento": "arista",
        "gr/n": 100,
        "carbo": 0.0,
        "proteine": 24.0,
        "grassi": 5.0,
        "kcal": 145.0,
    },
    {
        "Alimento": "avena",
        "gr/n": 60,
        "carbo": 37.8,
        "proteine": 7.2,
        "grassi": 4.2,
        "kcal": 216.0,
    },
    {
        "Alimento": "banana",
        "gr/n": 100,
        "carbo": 23.0,
        "proteine": 1.2,
        "grassi": 0.3,
        "kcal": 89.0,
    },
]

# Inizializzazione della Banca Dati
if "banca_dati_df" not in st.session_state:
    if (
        dati_salvati
        and "banca_dati_df" in dati_salvati
        and dati_salvati["banca_dati_df"] is not None
    ):
        st.session_state.banca_dati_df = dati_salvati["banca_dati_df"]
    else:
        st.session_state.banca_dati_df = pd.DataFrame(DEFAULT_BANCA_DATI)

st.session_state.banca_dati_df = pulisci_e_ordina_banca_dati(
    st.session_state.banca_dati_df
)

# Inizializzazione Atleti
if "atleti" not in st.session_state:
    if dati_salvati and "atleti" in dati_salvati:
        st.session_state.atleti = dati_salvati["atleti"]
    else:
        st.session_state.atleti = {
            "Atleta Principale": {
                "peso": 70.0,
                "altezza": 175.0,
                "eta": 56,
                "genere": "Uomo",
                "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
                "db_diario": {},
            }
        }

if "atleta_corrente" not in st.session_state:
    if (
        dati_salvati
        and "atleta_corrente" in dati_salvati
        and dati_salvati["atleta_corrente"] in st.session_state.atleti
    ):
        st.session_state.atleta_corrente = dati_salvati["atleta_corrente"]
    else:
        st.session_state.atleta_corrente = list(st.session_state.atleti.keys())[
            0
        ]

PASTI = ["Colazione", "Spuntino", "Pranzo", "Merenda", "Cena", "Extra"]

st.title("Pianificatore Alimentare & Allenamento - Multi-Atleta (Mifflin)")

# --- SEZIONE GESTIONE ATLETI NELLA SIDEBAR ---
st.sidebar.header("Gestione Atleti")
lista_atleti = list(st.session_state.atleti.keys())
atleta_selezionato = st.sidebar.selectbox(
    "Seleziona Atleta",
    lista_atleti,
    index=lista_atleti.index(st.session_state.atleta_corrente)
    if st.session_state.atleta_corrente in lista_atleti
    else 0,
    key="selectbox_atleta",
)

if atleta_selezionato != st.session_state.atleta_corrente:
    st.session_state.atleta_corrente = atleta_selezionato
    if is_proprietario:
        salva_dati_disco()
    st.rerun()

if is_proprietario:
    with st.sidebar.expander("Aggiungi o Gestisci Atleti"):
        nuovo_atleta_nome = st.text_input("Nome Nuovo Atleta")
        if st.button("Crea Nuovo Atleta"):
            nome_pulito = nuovo_atleta_nome.strip()
            if nome_pulito == "":
                st.error("Inserisci un nome valido.")
            elif nome_pulito in st.session_state.atleti:
                st.warning("Esiste già un atleta con questo nome.")
            else:
                st.session_state.atleti[nome_pulito] = {
                    "peso": 70.0,
                    "altezza": 175.0,
                    "eta": 30,
                    "genere": "Uomo",
                    "livello_allenamento": "Allenamento Moderato (PAL 1.55)",
                    "db_diario": {},
                }
                st.session_state.atleta_corrente = nome_pulito
                salva_dati_disco()
                st.success(f"Atleta '{nome_pulito}' aggiunto con successo!")
                st.rerun()

        if len(st.session_state.atleti) > 1:
            atleta_da_eliminare = st.selectbox(
                "Elimina Atleta",
                [a for a in lista_atleti if a != st.session_state.atleta_corrente],
            )
            if st.button("Conferma ed Elimina Atleta", type="primary"):
                if atleta_da_eliminare in st.session_state.atleti:
                    del st.session_state.atleti[atleta_da_eliminare]
                    st.session_state.atleta_corrente = list(
                        st.session_state.atleti.keys()
                    )[0]
                    salva_dati_disco()
                    st.success(f"Atleta '{atleta_da_eliminare}' eliminato.")
                    st.rerun()
else:
    st.sidebar.info("🔒 Gestione atleti bloccata per gli ospiti (Sola Lettura).")

st.sidebar.markdown("---")
st.sidebar.header(
    f"Parametri Mifflin & Allenamento: {st.session_state.atleta_corrente}"
)

atleta_data = st.session_state.atleti[st.session_state.atleta_corrente]

saved_peso = atleta_data.get("peso", 70.0)
saved_altezza = atleta_data.get("altezza", 175.0)
saved_eta = atleta_data.get("eta", 56)
saved_genere = atleta_data.get("genere", "Uomo")
saved_allenamento = atleta_data.get(
    "livello_allenamento", "Allenamento Moderato (PAL 1.55)"
)

genere_opzioni = ["Uomo", "Donna"]
genere_index = (
    genere_opzioni.index(saved_genere) if saved_genere in genere_opzioni else 0
)

allenamento_opzioni = [
    "Riposo / Sedentario (PAL 1.2)",
    "Attività Leggera (PAL 1.375)",
    "Allenamento Moderato (PAL 1.55)",
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)",
    "Doppio Allenamento / Estremo (PAL 1.9)",
]
allenamento_index = (
    allenamento_opzioni.index(saved_allenamento)
    if saved_allenamento in allenamento_opzioni
    else 2
)

if is_proprietario:
    peso = st.sidebar.number_input(
        "Peso (kg)",
        value=float(saved_peso),
        key=f"peso_{st.session_state.atleta_corrente}",
    )
    altezza = st.sidebar.number_input(
        "Altezza (cm)",
        value=float(saved_altezza),
        key=f"altezza_{st.session_state.atleta_corrente}",
    )
    eta = st.sidebar.number_input(
        "Età (anni)",
        value=int(saved_eta),
        key=f"eta_{st.session_state.atleta_corrente}",
    )
    genere = st.sidebar.selectbox(
        "Genere",
        genere_opzioni,
        index=genere_index,
        key=f"genere_{st.session_state.atleta_corrente}",
    )
    livello_allenamento = st.sidebar.selectbox(
        "Intensità Allenamento / Attività",
        allenamento_opzioni,
        index=allenamento_index,
        key=f"allenamento_{st.session_state.atleta_corrente}",
    )

    if (
        atleta_data.get("peso") != peso
        or atleta_data.get("altezza") != altezza
        or atleta_data.get("eta") != eta
        or atleta_data.get("genere") != genere
        or atleta_data.get("livello_allenamento") != livello_allenamento
    ):
        atleta_data["peso"] = peso
        atleta_data["altezza"] = altezza
        atleta_data["eta"] = eta
        atleta_data["genere"] = genere
        atleta_data["livello_allenamento"] = livello_allenamento
        salva_dati_disco()
else:
    peso = saved_peso
    altezza = saved_altezza
    eta = saved_eta
    genere = saved_genere
    livello_allenamento = saved_allenamento
    st.sidebar.text(f"Peso: {peso} kg")
    st.sidebar.text(f"Altezza: {altezza} cm")
    st.sidebar.text(f"Età: {eta} anni")
    st.sidebar.text(f"Genere: {genere}")
    st.sidebar.text(f"Attività: {livello_allenamento}")

pal_dict = {
    "Riposo / Sedentario (PAL 1.2)": 1.2,
    "Attività Leggera (PAL 1.375)": 1.375,
    "Allenamento Moderato (PAL 1.55)": 1.55,
    "Allenamento Intenso / Rouleur-Climber (PAL 1.725)": 1.725,
    "Doppio Allenamento / Estremo (PAL 1.9)": 1.9,
}
pal_selezionato = pal_dict.get(livello_allenamento, 1.55)

if genere == "Uomo":
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) + 5
else:
    bmr = (10 * peso) + (6.25 * altezza) - (5 * eta) - 161

tdee = bmr * pal_selezionato
obj_kcal = round(tdee, 0)
obj_carbo = 230.0
obj_prot = 165.0
obj_grassi = 70.0

st.sidebar.info(
    f"**Atleta in uso:** {st.session_state.atleta_corrente}\n\n**BMR stimato:** {bmr:.0f} kcal\n\n**TDEE dinamico:** {obj_kcal:.0f} kcal"
)

st.sidebar.markdown("---")
st.sidebar.header("Seleziona Giorno")
data_selezionata = st.sidebar.date_input("Data", value=date.today())
data_str = data_selezionata.strftime("%Y-%m-%d")

db_diario_atleta = atleta_data.setdefault("db_diario", {})
if data_str not in db_diario_atleta:
    db_diario_atleta[data_str] = {
        pasto: pd.DataFrame(
            columns=["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]
        )
        for pasto in PASTI
    }
    if is_proprietario:
        salva_dati_disco()

tot_carbo = sum(
    [
        db_diario_atleta[data_str][p]["carbo"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)
tot_prot = sum(
    [
        db_diario_atleta[data_str][p]["proteine"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)
tot_grassi = sum(
    [
        db_diario_atleta[data_str][p]["grassi"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)
tot_kcal = sum(
    [
        db_diario_atleta[data_str][p]["kcal"].sum()
        for p in PASTI
        if not db_diario_atleta[data_str][p].empty
    ]
)

st.subheader(
    f"Riepilogo Giornaliero - {st.session_state.atleta_corrente} ({data_str})"
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(
        "Calorie",
        f"{tot_kcal:.1f} / {obj_kcal} kcal",
        delta=f"{obj_kcal - tot_kcal:.1f} rimanenti",
    )
    st.progress(min(tot_kcal / obj_kcal, 1.0) if obj_kcal > 0 else 0)

with col_m2:
    st.metric(
        "Carboidrati",
        f"{tot_carbo:.1f} / {obj_carbo} g",
        delta=f"{obj_carbo - tot_carbo:.1f} g rimanenti",
    )
    st.progress(min(tot_carbo / obj_carbo, 1.0) if obj_carbo > 0 else 0)

with col_m3:
    st.metric(
        "Proteine",
        f"{tot_prot:.1f} / {obj_prot} g",
        delta=f"{obj_prot - tot_prot:.1f} g rimanenti",
    )
    st.progress(min(tot_prot / obj_prot, 1.0) if obj_prot > 0 else 0)

with col_m4:
    st.metric(
        "Grassi",
        f"{tot_grassi:.1f} / {obj_grassi} g",
        delta=f"{obj_grassi - tot_grassi:.1f} g rimanenti",
    )
    progresso_grassi = (
        float(min(tot_grassi / obj_grassi, 1.0)) if obj_grassi > 0 else 0.0
    )
    st.progress(progresso_grassi)

st.markdown("---")

with st.expander("Gestione Avanzata Banca Dati Alimenti (Condivisa)", expanded=False):
    st.markdown("### Accesso e Visualizzazione")
    banca_dati = st.session_state.banca_dati_df
    st.dataframe(banca_dati, use_container_width=True)

    csv_backup_data = banca_dati.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Scarica Backup Banca Dati (CSV)",
        data=csv_backup_data,
        file_name=f"banca_dati_alimentare_backup_{date.today().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )

    if is_proprietario:
        st.markdown("---")
        st.markdown("### Inserimento Manuale Singolo Alimento")
        with st.form("form_inserimento_manuale"):
            col_man1, col_man2, col_man3 = st.columns(3)
            with col_man1:
                nuovo_nome = st.text_input("Nome Alimento")
            with col_man2:
                nuovo_grn = st.number_input(
                    "Quantità di Riferimento (g o p)", min_value=1.0, value=100.0
                )
            with col_man3:
                nuovo_kcal = st.number_input(
                    "Calorie (kcal)", min_value=0.0, value=0.0, step=0.1
                )

            col_man4, col_man5, col_man6 = st.columns(3)
            with col_man4:
                nuovo_carbo = st.number_input(
                    "Carboidrati (g)", min_value=0.0, value=0.0, step=0.1
                )
            with col_man5:
                nuovo_prot = st.number_input(
                    "Proteine (g)", min_value=0.0, value=0.0, step=0.1
                )
            with col_man6:
                nuovo_grassi = st.number_input(
                    "Grassi (g)", min_value=0.0, value=0.0, step=0.1
                )

            btn_submit_manuale = st.form_submit_button(
                "Aggiungi Alimento alla Banca Dati"
            )
            if btn_submit_manuale:
                if nuovo_nome.strip() == "":
                    st.error("Inserisci un nome valido per l'alimento.")
                else:
                    nuova_riga_df = pd.DataFrame(
                        [
                            {
                                "Alimento": nuovo_nome.strip().lower(),
                                "gr/n": nuovo_grn,
                                "carbo": nuovo_carbo,
                                "proteine": nuovo_prot,
                                "grassi": nuovo_grassi,
                                "kcal": nuovo_kcal,
                            }
                        ]
                    )
                    st.session_state.banca_dati_df = pulisci_e_ordina_banca_dati(
                        pd.concat(
                            [st.session_state.banca_dati_df, nuova_riga_df],
                            ignore_index=True,
                        )
                    )
                    salva_dati_disco()
                    st.success(
                        f"✅ Alimento '{nuovo_nome.strip().lower()}' aggiunto e banca dati ordinata con successo!"
                    )
                    st.rerun()

        st.markdown("---")
        col_bd1, col_bd2 = st.columns(2)

        with col_bd1:
            st.markdown("### Cancellazione Parziale o Totale")
            alimenti_disponibili = banca_dati["Alimento"].dropna().tolist()
            alimenti_da_eliminare = st.multiselect(
                "Seleziona alimenti da rimuovere dalla banca dati:",
                alimenti_disponibili,
                key="multi_del_alimenti",
            )

            col_del_a, col_del_b = st.columns(2)
            with col_del_a:
                if st.button("Elimina Selezionati"):
                    if alimenti_da_eliminare:
                        st.session_state.banca_dati_df = pulisci_e_ordina_banca_dati(
                            banca_dati[~banca_dati["Alimento"].isin(alimenti_da_eliminare)]
                        )
                        salva_dati_disco()
                        st.success("✅ Alimenti selezionati rimossi con successo!")
                        st.rerun()
                    else:
                        st.warning("Nessun alimento selezionato.")
            with col_del_b:
                if st.button("Svuota Intera Banca Dati", type="primary"):
                    st.session_state.banca_dati_df = pd.DataFrame(
                        columns=[
                            "Alimento",
                            "gr/n",
                            "carbo",
                            "proteine",
                            "grassi",
                            "kcal",
                        ]
                    )
                    salva_dati_disco()
                    st.warning("⚠️ Banca dati svuotata completamente.")
                    st.rerun()

        with col_bd2:
            st.markdown("### Integrazione File CSV")
            st.info(
                "Carica un file CSV. Colonne attese: Alimento, gr/n, carbo, proteine, grassi, kcal."
            )
            file_caricato = st.file_uploader(
                "Carica file CSV", type=["csv"], key="uploader_banca_dati"
            )

            if file_caricato is not None:
                try:
                    df_nuovo = None
                    for enc in ["utf-8", "latin-1", "cp1252"]:
                        try:
                            file_caricato.seek(0)
                            df_nuovo = pd.read_csv(
                                file_caricato, encoding=enc, sep=None, engine="python"
                            )
                            if df_nuovo is not None and not df_nuovo.empty:
                                break
                        except Exception:
                            continue

                    if df_nuovo is not None and not df_nuovo.empty:
                        st.write("Anteprima dati letti dal file:", df_nuovo.head())
                        
                        # Normalizzazione automatica colonne
                        cols_orig = [str(c).strip().lower() for c in df_nuovo.columns]
                        df_nuovo.columns = cols_orig
                        mapping_colonne = {}
                        for c in cols_orig:
                            if "alimento" in c or "nome" in c:
                                mapping_colonne[c] = "Alimento"
                            elif "grass" in c or c == "g":
                                mapping_colonne[c] = "grassi"
                            elif "gr" in c or "quant" in c or "peso" in c or "numero" in c:
                                mapping_colonne[c] = "gr/n"
                            elif "carb" in c:
                                mapping_colonne[c] = "carbo"
                            elif "prot" in c:
                                mapping_colonne[c] = "proteine"
                            elif "kcal" in c or "calorie" in c or "kca" in c:
                                mapping_colonne[c] = "kcal"

                        df_nuovo = df_nuovo.rename(columns=mapping_colonne)
                        
                        colonne_attese = ["Alimento", "gr/n", "carbo", "proteine", "grassi", "kcal"]
                        data_dict = {}
                        for col in colonne_attese:
                            if col in df_nuovo.columns:
                                data_dict[col] = df_nuovo[col].values
                            else:
                                data_dict[col] = 0 if col != "Alimento" else "sconosciuto"

                        df_finale = pd.DataFrame(data_dict)
                        df_finale = pulisci_e_ordina_banca_dati(df_finale)

                        # Fusione automatica ed ordinamento immediato
                        st.session_state.banca_dati_df = pulisci_e_ordina_banca_dati(
                            pd.concat(
                                [st.session_state.banca_dati_df, df_finale],
                                ignore_index=True
                            )
                        )
                        salva_dati_disco()
                        st.success(
                            f"✅ Upload completato! Aggiunti/Aggiornati {len(df_finale)} alimenti. Banca dati ordinata alfabeticamente."
                        )
                        st.rerun()
                    else:
                        st.error("Il file CSV risulta vuoto o non leggibile.")
                except Exception as e:
                    st.error(f"Errore durante la lettura del file CSV: {e}")
    else:
        st.info("🔒 Funzionalità di modifica della banca dati riservate al proprietario.")

st.markdown("---")

st.subheader("Inserimento Alimenti nei Pasti")
pasto_selezionato = st.selectbox(
    "Seleziona il pasto a cui aggiungere l'alimento:", PASTI
)

banca_dati_corrente = st.session_state.banca_dati_df
alimenti_validi = banca_dati_corrente["Alimento"].dropna().tolist()
alimenti_validati = [
    str(a)
    for a in alimenti_validi
    if str(a).strip() != "" and str(a).lower() != "nan"
]

if alimenti_validati:
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        alimento_scelto = st.selectbox(
            "Alimento", alimenti_validati, key="sel_alimento_principale"
        )
        item_row = banca_dati_corrente[
            banca_dati_corrente["Alimento"].astype(str) == str(alimento_scelto)
        ].iloc[0]

        val_gr_n = safe_float(item_row["gr/n"])
        default_q = int(val_gr_n) if val_gr_n > 0 else 100

    with col_ins2:
        quantita = st.number_input(
            "Quantità (g o porzione)",
            min_value=1.0,
            value=float(default_q),
            key="num_quantita_principale",
        )

    if is_proprietario:
        if st.button("Aggiungi al pasto selezionato", key="btn_aggiungi_principale"):
            fattore = quantita / default_q if default_q > 0 else 1

            c_calc = round(safe_float(item_row["carbo"]) * fattore, 2)
            p_calc = round(safe_float(item_row["proteine"]) * fattore, 2)
            g_calc = round(safe_float(item_row["grassi"]) * fattore, 2)
            k_calc = round(safe_float(item_row["kcal"]) * fattore, 2)

            nuova_riga = pd.DataFrame(
                [
                    {
                        "Alimento": alimento_scelto,
                        "gr/n": quantita,
                        "carbo": c_calc,
                        "proteine": p_calc,
                        "grassi": g_calc,
                        "kcal": k_calc,
                    }
                ]
            )
            db_diario_atleta[data_str][pasto_selezionato] = pd.concat(
                [db_diario_atleta[data_str][pasto_selezionato], nuova_riga],
                ignore_index=True,
            )
            salva_dati_disco()
            st.success(f"✅ Aggiunto {alimento_scelto} ({quantita}g) a {pasto_selezionato}!")
            st.rerun()
    else:
        st.button("Aggiungi al pasto selezionato", key="btn_aggiungi_principale", disabled=True)
        st.caption("🔒 Azione non consentita in modalità ospite (sola lettura).")
else:
    st.warning("La banca dati è vuota o contiene solo elementi non validi.")

st.markdown("---")

st.subheader(
    f"Panoramica dei 6 Pasti Giornalieri - {st.session_state.atleta_corrente}"
)

cols_pasti = st.columns(3)
for i, pasto in enumerate(PASTI):
    col_target = cols_pasti[i % 3]
    with col_target:
        with st.container(border=True):
            st.markdown(f"### {pasto}")
            df_p = db_diario_atleta[data_str][pasto]

            if not df_p.empty:
                p_kcal = safe_float(df_p["kcal"].sum())
                p_carb = safe_float(df_p["carbo"].sum())
                p_prot = safe_float(df_p["proteine"].sum())
                p_gras = safe_float(df_p["grassi"].sum())
                st.caption(
                    f"Totale: {p_kcal:.1f} kcal | C: {p_carb:.1f}g | P: {p_prot:.1f}g | G: {p_gras:.1f}g"
                )

                st.dataframe(df_p, use_container_width=True)

                if is_proprietario:
                    mostra_gestione_voci = st.toggle(
                        "Modifica voci pasto", key=f"toggle_mod_{pasto}"
                    )

                    if mostra_gestione_voci:
                        indices_disponibili = df_p.index.tolist()
                        opzioni_rimozione = {
                            f"Riga {idx}: {df_p.loc[idx, 'Alimento']} ({df_p.loc[idx, 'gr/n']}g)": idx
                            for idx in indices_disponibili
                        }

                        voce_da_rimuovere = st.selectbox(
                            "Elimina voce:",
                            list(opzioni_rimozione.keys()),
                            key=f"del_box_{pasto}",
                        )

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("Elimina", key=f"btn_del_{pasto}"):
                                idx_to_drop = opzioni_rimozione[voce_da_rimuovere]
                                db_diario_atleta[data_str][pasto] = df_p.drop(
                                    idx_to_drop
                                ).reset_index(drop=True)
                                salva_dati_disco()
                                st.rerun()
                        with col_btn2:
                            if st.button("Svuota", key=f"clear_{pasto}"):
                                db_diario_atleta[data_str][
                                    pasto
                                ] = pd.DataFrame(
                                    columns=[
                                        "Alimento",
                                        "gr/n",
                                        "carbo",
                                        "proteine",
                                        "grassi",
                                        "kcal",
                                    ]
                                )
                                salva_dati_disco()
                                st.rerun()
                else:
                    st.caption("🔒 Modifica voci disattivata per gli ospiti.")
            else:
                st.info("Nessun alimento registrato.")

st.markdown("---")

st.subheader(
    f"Esportazione Report in PDF - {st.session_state.atleta_corrente}"
)

with st.expander("📥 Opzioni di Esportazione Report PDF (Giornaliero e Intervallo)", expanded=False):
    col_pdf1, col_pdf2 = st.columns(2)

    with col_pdf1:
        st.markdown("### Report Giornaliero")
        if st.button("Genera e Scarica PDF Giornaliero"):
            try:
                pdf_output = FPDF()
                pdf_output.add_page()
                pdf_output.set_font("Arial", "B", 16)
                pdf_output.cell(
                    0,
                    10,
                    f"Report Nutrizionale - {st.session_state.atleta_corrente} ({data_str})",
                    ln=True,
                    align="C",
                )
                pdf_output.ln(10)

                pdf_output.set_font("Arial", "B", 12)
                pdf_output.cell(0, 10, "Riepilogo Totale:", ln=True)
                pdf_output.set_font("Arial", "", 11)

                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, "Calorie: ")
                if tot_kcal > obj_kcal:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_kcal:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(
                    8, f" / {obj_kcal} kcal ({livello_allenamento})\n"
                )
                pdf_output.ln(2)

                pdf_output.write(8, "Carboidrati: ")
                if tot_carbo > obj_carbo:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_carbo:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" / {obj_carbo} g\n")
                pdf_output.ln(2)

                pdf_output.write(8, "Proteine: ")
                if tot_prot > obj_prot:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_prot:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" / {obj_prot} g\n")
                pdf_output.ln(2)

                pdf_output.write(8, "Grassi: ")
                if tot_grassi > obj_grassi:
                    pdf_output.set_text_color(220, 20, 60)
                pdf_output.write(8, f"{tot_grassi:.1f}")
                pdf_output.set_text_color(0, 0, 0)
                pdf_output.write(8, f" / {obj_grassi} g\n")
                pdf_output.ln(10)

                for pasto in PASTI:
                    pdf_output.set_font("Arial", "B", 12)
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.cell(0, 8, f"Pasto: {pasto}", ln=True)
                    pdf_output.set_font("Arial", "", 10)
                    df_p = db_diario_atleta[data_str][pasto]
                    if not df_p.empty:
                        for _, row in df_p.iterrows():
                            testo_riga = f" - {row['Alimento']}: {row['gr/n']}g | Carbo: {row['carbo']}g | Prot: {row['proteine']}g | Grassi: {row['grassi']}g | {row['kcal']} kcal"
                            pdf_output.cell(0, 6, testo_riga, ln=True)
                    else:
                        pdf_output.cell(
                            0, 6, " - Nessun alimento registrato", ln=True
                        )
                    pdf_output.ln(4)

                raw_output = pdf_output.output()
                pdf_bytes = (
                    bytes(raw_output)
                    if isinstance(raw_output, (bytearray, bytes))
                    else raw_output.encode("latin1")
                )

                st.download_button(
                    label="Scarica PDF Giornaliero",
                    data=pdf_bytes,
                    file_name=f"report_{st.session_state.atleta_corrente}_{data_str}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Errore nella generazione del PDF giornaliero: {e}")

    with col_pdf2:
        st.markdown("### Report Personalizzato per Intervallo di Date")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inizio = st.date_input(
                "Data Inizio",
                value=date.today() - timedelta(days=6),
                key="pdf_data_inizio",
            )
        with col_d2:
            data_fine = st.date_input(
                "Data Fine", value=date.today(), key="pdf_data_fine"
            )

        if st.button("Genera e Scarica PDF Intervallo (Traccia Totale)"):
            try:
                if data_inizio > data_fine:
                    st.error(
                        "La data di inizio non può essere successiva alla data di fine."
                    )
                else:
                    delta_giorni = (data_fine - data_inizio).days + 1
                    (
                        tot_p_kcal,
                        tot_p_carbo,
                        tot_p_prot,
                        tot_p_grassi,
                    ) = 0.0, 0.0, 0.0, 0.0

                    for i in range(delta_giorni):
                        d_corrente = data_inizio + timedelta(days=i)
                        d_str = d_corrente.strftime("%Y-%m-%d")
                        if d_str in db_diario_atleta:
                            d_kcal = sum(
                                [
                                    safe_float(
                                        db_diario_atleta[d_str][p]["kcal"].sum()
                                    )
                                    for p in PASTI
                                    if not db_diario_atleta[d_str][p].empty
                                ]
                            )
                            d_carbo = sum(
                                [
                                    safe_float(
                                        db_diario_atleta[d_str][p]["carbo"].sum()
                                    )
                                    for p in PASTI
                                    if not db_diario_atleta[d_str][p].empty
                                ]
                            )
                            d_prot = sum(
                                [
                                    safe_float(
                                        db_diario_atleta[d_str][p][
                                            "proteine"
                                        ].sum()
                                    )
                                    for p in PASTI
                                    if not db_diario_atleta[d_str][p].empty
                                ]
                            )
                            d_grassi = sum(
                                [
                                    safe_float(
                                        db_diario_atleta[d_str][p]["grassi"].sum()
                                    )
                                    for p in PASTI
                                    if not db_diario_atleta[d_str][p].empty
                                ]
                            )

                            tot_p_kcal += d_kcal
                            tot_p_carbo += d_carbo
                            tot_p_prot += d_prot
                            tot_p_grassi += d_grassi

                    pdf_output = FPDF()
                    pdf_output.add_page()
                    pdf_output.set_font("Arial", "B", 16)
                    pdf_output.cell(
                        0,
                        10,
                        f"Report Nutrizionale - {st.session_state.atleta_corrente} ({data_inizio.strftime('%d/%m/%Y')} - {data_fine.strftime('%d/%m/%Y')})",
                        ln=True,
                        align="C",
                    )
                    pdf_output.ln(10)

                    pdf_output.set_font("Arial", "B", 12)
                    pdf_output.cell(0, 10, "Riepilogo Totale del Periodo:", ln=True)
                    pdf_output.set_font("Arial", "", 11)

                    media_kcal = tot_p_kcal / delta_giorni
                    media_carbo = tot_p_carbo / delta_giorni
                    media_prot = tot_p_prot / delta_giorni
                    media_grassi = tot_p_grassi / delta_giorni

                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, "Calorie Totali: ")
                    if media_kcal > obj_kcal:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{tot_p_kcal:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, f" kcal (Media giornaliera: ")
                    if media_kcal > obj_kcal:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{media_kcal:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, " kcal)\n")
                    pdf_output.ln(2)

                    pdf_output.write(8, "Carboidrati Totali: ")
                    if media_carbo > obj_carbo:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{tot_p_carbo:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, f" g (Media: ")
                    if media_carbo > obj_carbo:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{media_carbo:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, " g)\n")
                    pdf_output.ln(2)

                    pdf_output.write(8, "Proteine Totali: ")
                    if media_prot > obj_prot:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{tot_p_prot:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, f" g (Media: ")
                    if media_prot > obj_prot:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{media_prot:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, " g)\n")
                    pdf_output.ln(2)

                    pdf_output.write(8, "Grassi Totali: ")
                    if media_grassi > obj_grassi:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{tot_p_grassi:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, f" g (Media: ")
                    if media_grassi > obj_grassi:
                        pdf_output.set_text_color(220, 20, 60)
                    pdf_output.write(8, f"{media_grassi:.1f}")
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.write(8, " g)\n")
                    pdf_output.ln(10)

                    pdf_output.set_font("Arial", "B", 12)
                    pdf_output.set_text_color(0, 0, 0)
                    pdf_output.cell(
                        0, 10, "Traccia Giornaliera dei Macronutrienti:", ln=True
                    )
                    pdf_output.set_font("Arial", "", 10)

                    for i in range(delta_giorni):
                        d_corrente = data_inizio + timedelta(days=i)
                        d_str = d_corrente.strftime("%Y-%m-%d")
                        
                        dk, dc, dp, dg = 0.0, 0.0, 0.0, 0.0
                        if d_str in db_diario_atleta:
                            dk = sum([safe_float(db_diario_atleta[d_str][p]["kcal"].sum()) for p in PASTI if not db_diario_atleta[d_str][p].empty])
                            dc = sum([safe_float(db_diario_atleta[d_str][p]["carbo"].sum()) for p in PASTI if not db_diario_atleta[d_str][p].empty])
                            dp = sum([safe_float(db_diario_atleta[d_str][p]["proteine"].sum()) for p in PASTI if not db_diario_atleta[d_str][p].empty])
                            dg = sum([safe_float(db_diario_atleta[d_str][p]["grassi"].sum()) for p in PASTI if not db_diario_atleta[d_str][p].empty])

                        pdf_output.set_text_color(0, 0, 0)
                        pdf_output.write(6, f" - {d_str} -> Kcal: {dk:.1f} | Carbo: {dc:.1f}g | Prot: {dp:.1f}g | Grassi: {dg:.1f}g\n")

                    raw_output = pdf_output.output()
                    pdf_bytes = (
                        bytes(raw_output)
                        if isinstance(raw_output, (bytearray, bytes))
                        else raw_output.encode("latin1")
                    )

                    st.download_button(
                        label="Scarica PDF Periodo Personalizzato",
                        data=pdf_bytes,
                        file_name=f"report_periodo_{st.session_state.atleta_corrente}_{data_inizio}_al_{data_fine}.pdf",
                        mime="application/pdf",
                    )
            except Exception as e:
                st.error(f"Errore nella generazione del PDF personalizzato: {e}")

# --- BACKUP E RIPRISTINO PKL INTERO ---
st.markdown("---")
st.subheader("💾 Backup e Ripristino Dati (File .pkl)")
st.info(
    "Puoi scaricare l'intero database dell'applicazione (inclusi tutti gli atleti, i diari e la banca dati) "
    "oppure caricare un file .pkl precedentemente salvato per ripristinare lo stato."
)

col_pkl1, col_pkl2 = st.columns(2)

with col_pkl1:
    try:
        dati_completi_per_salvataggio = {
            "atleti": st.session_state.get("atleti", {}),
            "banca_dati_df": st.session_state.get("banca_dati_df"),
            "atleta_corrente": st.session_state.get("atleta_corrente"),
        }
        pkl_bytes = pickle.dumps(dati_completi_per_salvataggio)
        st.download_button(
            label="📥 Scarica Intero Database (.pkl)",
            data=pkl_bytes,
            file_name=f"diario_alimentare_multi_db_completo_{date.today().strftime('%Y-%m-%d')}.pkl",
            mime="application/octet-stream",
        )
    except Exception as e:
        st.error(f"Errore nella preparazione del download .pkl: {e}")

with col_pkl2:
    if is_proprietario:
        file_pkl_caricato = st.file_uploader(
            "Carica file .pkl di Backup", type=["pkl"], key="uploader_backup_pkl"
        )
        if file_pkl_caricato is not None:
            if st.button("Conferma e Ripristina Database da .pkl"):
                try:
                    dati_ripristinati = pickle.load(file_pkl_caricato)
                    if isinstance(dati_ripristinati, dict) and "atleti" in dati_ripristinati:
                        st.session_state.atleti = dati_ripristinati.get("atleti", {})
                        if "banca_dati_df" in dati_ripristinati and dati_ripristinati["banca_dati_df"] is not None:
                            st.session_state.banca_dati_df = pulisci_e_ordina_banca_dati(
                                dati_ripristinati["banca_dati_df"]
                            )
                        if "atleta_corrente" in dati_ripristinati and dati_ripristinati["atleta_corrente"] in st.session_state.atleti:
                            st.session_state.atleta_corrente = dati_ripristinati["atleta_corrente"]
                        else:
                            st.session_state.atleta_corrente = list(st.session_state.atleti.keys())[0]
                        
                        salva_dati_disco()
                        st.success("✅ Database ripristinato con successo dal file .pkl!")
                        st.rerun()
                    else:
                        st.error("Il file .pkl caricato non ha una struttura valida.")
                except Exception as e:
                    st.error(f"Errore durante il ripristino del file .pkl: {e}")
    else:
        st.info("🔒 Il ripristino da file .pkl è riservato al proprietario.")
