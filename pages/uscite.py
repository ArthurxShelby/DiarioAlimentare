# --- 4. SEZIONE INDICATORI CIRCOLARI (GAUGE CHART A 360°) ---
st.markdown("---")
st.subheader("🎯 Indicatori di Performance (Gauge a 360°)")
st.write("Visualizzazione circolare delle metriche chiave dell'uscita rapportate al valore massimo di riferimento.")

# Se abbiamo un'uscita selezionata nel contesto o prendiamo l'ultima disponibile
# Creiamo un contenitore con i valori di esempio o presi dall'ultima attività attiva
try:
    # Verifichiamo se abbiamo dati attivi dal dataframe del grafico o dell'archivio
    if 'df_g' in locals() and not df_g.empty:
        # Prendiamo l'ultima uscita in ordine di data come default
        ultima_uscita = df_g.sort_values('data_fmt', ascending=False).iloc[0]
        val_carico = float(ultima_uscita.get('load', 243)) # fallback sul valore noto se manca la colonna specifica
        val_dplus = float(ultima_uscita.get('D+', 1664))
        val_km = float(ultima_uscita.get('Km', 112.38))
        val_np = float(ultima_uscita.get('np', 214)) # se disponibile o stimata
    else:
        # Valori di fallback basati sull'ultima schermata analizzata
        val_carico = 243.0
        val_dplus = 1664.0
        val_km = 112.38
        val_np = 214.0
except Exception:
    val_carico = 243.0
    val_dplus = 1664.0
    val_km = 112.38
    val_np = 214.0

# Definizione delle metriche, dei valori attuali e dei rispettivi massimi di scala (360°)
metriche_gauge = [
    {
        "titolo": "Carico (Load)", 
        "valore": val_carico, 
        "max": 350.0, 
        "unita": ""
    },
    {
        "titolo": "Dislivello (D+)", 
        "valore": val_dplus, 
        "max": 3000.0, 
        "unita": " m"
    },
    {
        "titolo": "Distanza", 
        "valore": val_km, 
        "max": 200.0, 
        "unita": " km"
    },
    {
        "titolo": "Potenza Norm.", 
        "valore": val_np, 
        "max": 300.0, 
        "unita": " W"
    }
]

# Disposizione in griglia su colonne in Streamlit
cols_gauge = st.columns(len(metriche_gauge))

for i, m in enumerate(metriche_gauge):
    with cols_gauge[i]:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = m["valore"],
            title = {"text": f"<b>{m['titolo']}</b>", "font": {"size": 16}},
            number = {'suffix': m["unita"], 'font': {'size': 20}},
            gauge = {
                'axis': {'range': [0, m["max"]], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "dodgerblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, m["max"] * 0.6], 'color': "#f0f2f6"},
                    {'range': [m["max"] * 0.6, m["max"] * 0.85], 'color': "#d1e7dd"},
                    {'range': [m["max"] * 0.85, m["max"]], 'color': "#f8d7da"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': m["max"] * 0.9
                }
            }
        ))
        
        # Ottimizzazione del layout per adattarsi ai blocchi della pagina
        fig_gauge.update_layout(
            height=220, 
            margin=dict(l=20, r=20, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displaylogo': False})
