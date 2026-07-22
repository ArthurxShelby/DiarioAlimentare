import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Diario Alimentare — KenToshi",
    page_icon="⚡",
    layout="wide"
)

# Stile CSS personalizzato per riprodurre il tema scuro e le card dell'interfaccia
st.markdown("""
<style>
    .stApp {
        background-color: #0e1110;
        color: #e8efe9;
        font-family: 'Inter', sans-serif;
    }
    .main-container {
        padding: 1rem 2rem;
    }
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #171d1a;
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        border: 1px solid #1a211c;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #171d1a;
        border: 1px solid #1a211c;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e8efe9;
    }
    .tag-badge {
        background-color: #1f2923;
        color: #4ade80;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Barra superiore
    st.markdown("""
    <div class="top-bar">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="background-color: #166534; color: #4ade80; padding: 0.4rem 0.8rem; border-radius: 8px; font-weight: bold;">K</span>
            <span style="font-size: 1.1rem; font-weight: 600;">Diario Alimentare — KenToshi</span>
            <span class="tag-badge">● dinamico • 22/07/2026</span>
        </div>
        <div style="display: flex; gap: 0.75rem;">
            <button style="background: #1f2923; color: #e8efe9; border: 1px solid #2d3732; padding: 0.4rem 0.8rem; border-radius: 8px; cursor: pointer;">📊 Banca Dati</button>
            <button style="background: #1f2923; color: #e8efe9; border: 1px solid #2d3732; padding: 0.4rem 0.8rem; border-radius: 8px; cursor: pointer;">⚙️ Profilo • 75kg</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout principale a colonne
    col_left, col_right = st.columns([2.2, 1])
    
    with col_left:
        # Sezione Principale: Oggi
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.4rem;">🔥 Oggi — 4230 / 2412 kcal</h2>
                    <p style="margin: 0; font-size: 0.85rem; color: #9ca3af;">P 177g • C 264g • F 299g • BMR 1556 • TDEE 2412</p>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button style="background: #ea580c; color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; cursor: pointer;">Carica Giorno Recupero</button>
                    <button style="background: #1f2923; color: #e8efe9; border: 1px solid #2d3732; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer;">Esporta</button>
                </div>
            </div>
            
            <!-- 4 Metric Cards in Grid -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1.5rem;">
                <div style="background: #0e1110; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid #ef4444;">
                    <div class="metric-title">KCAL</div>
                    <div class="metric-value">4230</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">/ 2412</div>
                    <div style="color: #ef4444; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">+1818 oltre</div>
                </div>
                <div style="background: #0e1110; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid #eab308;">
                    <div class="metric-title">CARBO</div>
                    <div class="metric-value">264</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">/ 301g</div>
                    <div style="color: #eab308; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">37 rimanenti</div>
                </div>
                <div style="background: #0e1110; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid #ef4444;">
                    <div class="metric-title">PROTEINE</div>
                    <div class="metric-value">177</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">/ 150g</div>
                    <div style="color: #ef4444; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">+27 oltre</div>
                </div>
                <div style="background: #0e1110; padding: 1rem; border-radius: 12px; text-align: center; border: 1px solid #ef4444;">
                    <div class="metric-title">GRASSI</div>
                    <div class="metric-value">299</div>
                    <div style="font-size: 0.8rem; color: #9ca3af;">/ 68g</div>
                    <div style="color: #ef4444; font-size: 0.8rem; margin-top: 0.5rem; font-weight: 600;">+231 oltre</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Split Macro & Rimanenze
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            st.markdown("""
            <div class="card">
                <h3>SPLIT MACRO</h3>
                <div style="display: flex; align-items: center; justify-content: space-around; margin-top: 1rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: #eab308; border: 4px solid #eab308; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;">100%</div>
                    <div>
                        <p style="margin: 0.2rem 0; font-size: 0.9rem;"><span style="color: #eab308;">■</span> Carbo 264g (36%)</p>
                        <p style="margin: 0.2rem 0; font-size: 0.9rem;"><span style="color: #4ade80;">■</span> Proteine 177g (24%)</p>
                        <p style="margin: 0.2rem 0; font-size: 0.9rem;"><span style="color: #d97706;">■</span> Grassi 299g (40%)</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_sub2:
            st.markdown("""
            <div class="card">
                <h3>RIMANENZE</h3>
                <div style="margin-top: 1rem;">
                    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #9ca3af;">Kcal rimanenti: <span style="color: #ef4444; font-weight: bold;">-1818</span></p>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #9ca3af;">Carbo rimanenti: <span style="color: #eab308; font-weight: bold;">37g</span></p>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #9ca3af;">Proteine rimanenti: <span style="color: #ef4444; font-weight: bold;">-27g</span></p>
                    <hr style="border-color: #2d3732; margin: 1rem 0;">
                    <p style="font-size: 0.75rem; color: #6b7280;">Verde = in target • Giallo = vicino (±15%) • Rosso = oltre</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Sezione Pasto: Colazione
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">🥣 Colazione <span style="font-size: 0.85rem; color: #9ca3af; font-weight: normal;">5 alimenti • 403 kcal</span></h3>
                <button style="background: #1f2923; color: #e8efe9; border: 1px solid #2d3732; padding: 0.3rem 0.8rem; border-radius: 8px; cursor: pointer;">+ Aggiungi</button>
            </div>
            <div style="background: #0e1110; padding: 1rem; border-radius: 10px; margin-top: 1rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>Avena</strong><br>
                    <span style="font-size: 0.85rem; color: #9ca3af;">30c • 6.25p • 3.5f • 180 kcal</span>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="background: #171d1a; padding: 0.3rem 0.8rem; border-radius: 6px; border: 1px solid #2d3732;">50 g</span>
                    <span style="color: #ef4444; cursor: pointer;">🗑️</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Profilo & Obiettivi
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; font-size: 1.1rem;">Profilo & Obiettivi</h3>
                <button style="background: #1f2923; color: #e8efe9; border: 1px solid #2d3732; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.8rem; cursor: pointer;">Modifica</button>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="background: #0e1110; padding: 0.75rem; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #9ca3af;">SESSO / ETÀ</div>
                    <div style="font-weight: 600;">M • 56 anni</div>
                </div>
                <div style="background: #0e1110; padding: 0.75rem; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #9ca3af;">PESO / ALTEZZA</div>
                    <div style="font-weight: 600;">75kg • 173cm</div>
                </div>
                <div style="background: #0e1110; padding: 0.75rem; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #9ca3af;">ATTIVITÀ</div>
                    <div style="font-weight: 600;">Moderato</div>
                </div>
                <div style="background: #0e1110; padding: 0.75rem; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #9ca3af;">OBIETTIVO</div>
                    <div style="font-weight: 600;">Mantenimento</div>
                </div>
            </div>
            <div style="font-size: 0.8rem; color: #9ca3af; background: #0e1110; padding: 0.75rem; border-radius: 8px;">
                <strong style="color: #e8efe9;">Formula Mifflin-St Jeor</strong><br>
                BMR = 10×75 + 6.25×173 −5×56 +5 = 1556<br>
                TDEE = BMR×1.55 = 2412<br><br>
                <span style="background: #1f2923; padding: 0.2rem 0.5rem; border-radius: 4px; color: #e8efe9;">BMR 1556</span>
                <span style="background: #1f2923; padding: 0.2rem 0.5rem; border-radius: 4px; color: #e8efe9;">TDEE 2412</span>
                <span style="background: #ea580c; padding: 0.2rem 0.5rem; border-radius: 4px; color: white; font-weight: bold;">Target 2412 kcal</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Riepilogo settimanale
        st.markdown("""
        <div class="card">
            <h3 style="margin-top: 0; font-size: 1.1rem;">📊 Riepilogo settimanale</h3>
            <p style="font-size: 0.8rem; color: #9ca3af;">KCAL GIORNALIERE • TARGET 2412</p>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; height: 120px; border-bottom: 1px solid #2d3732; padding-bottom: 0.5rem; margin-top: 1rem;">
                <div style="text-align: center;"><div style="font-size: 0.7rem; color: #9ca3af;">07-16</div><div style="font-size: 0.8rem;">0</div></div>
                <div style="text-align: center;"><div style="font-size: 0.7rem; color: #9ca3af;">07-17</div><div style="font-size: 0.8rem;">0</div></div>
                <div style="text-align: center;"><div style="font-size: 0.7rem; color: #9ca3af;">07-18</div><div style="font-size: 0.8rem;">0</div></div>
                <div style="text-align: center; background: #ef4444; width: 25px; height: 100px; border-radius: 4px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 5px;"><span style="font-size: 0.7rem; writing-mode: vertical-rl; transform: rotate(180deg);">4230</span></div>
                <div style="text-align: center;"><div style="font-size: 0.7rem; color: #9ca3af;">07-20</div><div style="font-size: 0.8rem;">0</div></div>
                <div style="text-align: center;"><div style="font-size: 0.7rem; color: #9ca3af;">07-21</div><div style="font-size: 0.8rem;">0</div></div>
                <div style="text-align: center; background: #ef4444; width: 25px; height: 100px; border-radius: 4px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 5px;"><span style="font-size: 0.7rem; writing-mode: vertical-rl; transform: rotate(180deg);">4230</span></div>
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.75rem; color: #9ca3af;">
                <span>➖ linea obiettivo</span>
                <span>• media 1209 kcal</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
