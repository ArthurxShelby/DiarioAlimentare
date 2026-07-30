import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import base64
from datetime import date, datetime

# --- CARICAMENTO CREDENZIALI DA SECRETS ---
try:
    ATHLETE_ID = st.secrets["ATHLETE_ID"]
    API_KEY = st.secrets["API_KEY"]
except Exception as e:
    st.error("⚠️ Credenziali non configurate correttamente nel file secrets.toml.")
    st.stop()

def timedelta_to_str(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# --- 3. CONTENITORE GRAFICI INTERATTIVI E DETTAGLIO USCITE (SOTTO MENU A DISCESA) ---
st.markdown("---")
with st.expander("📈 Analisi Grafica e Dettaglio Uscite per Metrica", expanded=False):
    st.write("Fissa il range temporale di ricerca, il livello di aggregazione (Settimane/Mesi) e seleziona il parametro da analizzare.")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns([2, 2, 2, 2])
    with col_r1:
        range_inizio_sec3 = st.date_input("Inizio Range Grafico", value=date(2026, 1, 1), key="grafico_start_indipendente")
    with col_r2:
        range_fine_sec3 = st.date_input("Fine Range Grafico", value=date.today(), key="grafico_end_indipendente")
    with col_r3:
        tipo_aggregazione = st.selectbox(
            "Raggruppa per",
            ["Giornaliero", "Settimanale", "Mensile"],
            key="selettore_aggregazione"
        )
    with col_r4:
        scelta_metrica = st.selectbox(
            "Seleziona Dato Grafico",
            ["Km", "D+", "Ore in sella"],
            key="selettore_metrica_grafico"
        )

    url_grafico = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
    params_grafico = {
        "oldest": range_inizio_sec3.strftime("%Y-%m-%d"),
        "newest": range_fine_sec3.strftime("%Y-%m-%d"),
        "iw": True
    }
    resp_grafico = requests.get(url_grafico, auth=("API_KEY", API_KEY.strip()), params=params_grafico)

    if resp_grafico.status_code == 200:
        dati_raw_grafico = resp_grafico.json()
        if dati_raw_grafico:
            df_g = pd.DataFrame(dati_raw_grafico)
            
            df_g['data_fmt'] = pd.to_datetime(df_g['start_date_local'])
            df_g['data_solo'] = df_g['data_fmt'].dt.date
            df_g['Km'] = df_g.get('distance', 0).fillna(0) / 1000.0
            df_g['D+'] = df_g.get('total_elevation_gain', 0).fillna(0)
            df_g['Ore in sella'] = df_g.get('moving_time', 0).fillna(0) / 3600.0
            df_g['titolo_uscita'] = df_g.get('name', 'Uscita senza nome')
            df_g['id_str'] = df_g.get('id').astype(str)

            if tipo_aggregazione == "Settimanale":
                df_g['periodo_chiave'] = df_g['data_fmt'].dt.to_period('W').dt.start_time.dt.date
                df_aggregato = df_g.groupby('periodo_chiave').agg({
                    'Km': 'sum',
                    'D+': 'sum',
                    'Ore in sella': 'sum',
                    'titolo_uscita': lambda x: f"Totale Settimanale ({len(x)} uscite)"
                }).reset_index().rename(columns={'periodo_chiave': 'asse_x'})
            elif tipo_aggregazione == "Mensile":
                df_g['periodo_chiave'] = df_g['data_fmt'].dt.to_period('M').dt.start_time.dt.date
                df_aggregato = df_g.groupby('periodo_chiave').agg({
                    'Km': 'sum',
                    'D+': 'sum',
                    'Ore in sella': 'sum',
                    'titolo_uscita': lambda x: f"Totale Mensile ({len(x)} uscite)"
                }).reset_index().rename(columns={'periodo_chiave': 'asse_x'})
            else:
                df_g['periodo_chiave'] = df_g['data_solo']
                df_aggregato = df_g.copy().rename(columns={'data_solo': 'asse_x'})

            fig_stat = go.Figure()
            fig_stat.add_trace(go.Bar(
                x=df_aggregato['asse_x'],
                y=df_aggregato[scelta_metrica],
                name=scelta_metrica,
                marker=dict(color='dodgerblue'),
                customdata=df_aggregato['asse_x'].astype(str).values
            ))

            fig_stat.update_layout(
                title=f"Andamento {tipo_aggregazione.lower()}: {scelta_metrica}",
                xaxis_title="Periodo",
                yaxis_title=scelta_metrica,
                margin=dict(l=20, r=20, t=40, b=20),
                height=350,
                clickmode='event+select'
            )

            event_selezionato = st.plotly_chart(fig_stat, use_container_width=True, on_select="rerun", key="chart_uscite_interattivo")

            periodo_selezionato = None
            if event_selezionato and "selection" in event_selezionato and event_selezionato["selection"]["points"]:
                punto = event_selezionato["selection"]["points"][0]
                if "customdata" in punto:
                    periodo_selezionato = punto["customdata"]

            if periodo_selezionato:
                p_date = datetime.strptime(periodo_selezionato, "%Y-%m-%d").date()
                df_filtrato_periodo = df_g[df_g['periodo_chiave'] == p_date]
            else:
                df_filtrato_periodo = df_g

            if df_filtrato_periodo.empty:
                df_filtrato_periodo = df_g

            tot_km_periodo = df_filtrato_periodo['Km'].sum()
            tot_d_periodo = df_filtrato_periodo['D+'].sum()
            tot_ore_periodo = df_filtrato_periodo['Ore in sella'].sum()

            st.markdown("---")
            
            if periodo_selezionato:
                p_date_str = datetime.strptime(periodo_selezionato, "%Y-%m-%d").strftime("%d/%m/%Y")
                if tipo_aggregazione == "Settimanale":
                    etichetta_periodo = f"Settimana dal {p_date_str}"
                elif tipo_aggregazione == "Mensile":
                    etichetta_periodo = f"Mese di {datetime.strptime(periodo_selezionato, '%Y-%m-%d').strftime('%B %Y')}"
                else:
                    etichetta_periodo = f"Giorno {p_date_str}"
                titolo_totali = f"Totale Selezionato ({etichetta_periodo})"
            else:
                titolo_totali = "Totale Intero Periodo"

            st.markdown(f"#### 📊 {titolo_totali}")
            
            col_tot1, col_tot2, col_tot3 = st.columns(3)
            col_tot1.metric("Km", f"{tot_km_periodo:,.2f} km")
            col_tot2.metric("D+", f"{tot_d_periodo:,.0f} m")
            col_tot3.metric("Ore in sella", f"{timedelta_to_str(tot_ore_periodo * 3600)}")

            st.markdown("---")
            
            opzioni_tendina = {
                f"{row['data_solo']} - {row['titolo_uscita']} ({row[scelta_metrica]:.1f} {scelta_metrica})": row['id_str'] 
                for _, row in df_filtrato_periodo.sort_values('data_fmt', ascending=False).iterrows()
            }
            
            if opzioni_tendina:
                scelta_utente_tendina = st.selectbox(
                    f"Seleziona Uscita dal Periodo ({len(opzioni_tendina)} disponibili)",
                    options=list(opzioni_tendina.keys()),
                    key="select_uscita_dettaglio_grafico"
                )
                id_attivita_scelta = opzioni_tendina[scelta_utente_tendina]
            else:
                st.warning("Nessuna uscita trovata per la selezione corrente.")
                id_attivita_scelta = None
            
            if id_attivita_scelta:
                dati_uscita_corrente = df_g[df_g['id_str'] == id_attivita_scelta].iloc[0]

                st.markdown(f"#### 🚴 Dettaglio: {dati_uscita_corrente['titolo_uscita']} ({dati_uscita_corrente['data_solo']})")
                
                clean_id_g = ''.join(c for c in id_attivita_scelta if c.isdigit())
                target_url_g = f"https://intervals.icu/api/v1/activity/{clean_id_g}/streams"
                
                with st.spinner("Caricamento traccia GPS in corso..."):
                    resp_str_g = requests.get(target_url_g, auth=("API_KEY", API_KEY.strip()))
                    if resp_str_g.status_code == 404 and id_attivita_scelta != clean_id_g:
                        target_url_g = f"https://intervals.icu/api/v1/activity/{id_attivita_scelta}/streams"
                        resp_str_g = requests.get(target_url_g, auth=("API_KEY", API_KEY.strip()))

                    if resp_str_g.status_code == 200:
                        stream_data_g = resp_str_g.json()
                        lats_g, lons_g = [], []
                        
                        if isinstance(stream_data_g, list):
                            for stream in stream_data_g:
                                if isinstance(stream, dict):
                                    stype = stream.get("type")
                                    if stype in ["latlng", "lating"]:
                                        lat_data = stream.get("data", [])
                                        lon_data = stream.get("data2", [])
                                        
                                        if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data) and len(lat_data) > 0:
                                            for lat, lon in zip(lat_data, lon_data):
                                                if lat is not None and lon is not None:
                                                    lats_g.append(float(lat))
                                                    lons_g.append(float(lon))
                                        break

                        if lats_g and lons_g and len(lats_g) > 0:
                            with st.expander("🗺️ Visualizza Mappa e Download GPX", expanded=False):
                                tipo_mappa = st.radio(
                                    "Stile Mappa",
                                    ["Satellite", "Standard"],
                                    horizontal=True,
                                    key=f"stile_mappa_{id_attivita_scelta}"
                                )

                                fig_map = go.Figure()
                                fig_map.add_trace(go.Scattermapbox(
                                    lat=lats_g, lon=lons_g, mode='lines',
                                    line=dict(width=4, color='dodgerblue'), name='Tracciato'
                                ))
                                fig_map.add_trace(go.Scattermapbox(
                                    lat=[lats_g[0], lats_g[-1]], lon=[lons_g[0], lons_g[-1]], mode='markers',
                                    marker=dict(size=10, color=['green', 'red']), text=['Partenza', 'Arrivo'], name='Marker'
                                ))
                                
                                if tipo_mappa == "Satellite":
                                    mapbox_config = dict(
                                        style="white-bg",
                                        layers=[
                                            {
                                                "below": 'traces',
                                                "sourcetype": "raster",
                                                "source": [
                                                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                                ]
                                            }
                                        ],
                                        center=dict(lat=sum(lats_g)/len(lats_g), lon=sum(lons_g)/len(lons_g)),
                                        zoom=11
                                    )
                                else:
                                    mapbox_config = dict(
                                        style="open-street-map",
                                        center=dict(lat=sum(lats_g)/len(lats_g), lon=sum(lons_g)/len(lons_g)),
                                        zoom=11
                                    )

                                fig_map.update_layout(
                                    mapbox=mapbox_config,
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    height=450,
                                    showlegend=False
                                )
                                
                                st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True, 'displaylogo': False})

                                linee_gpx = [
                                    '<?xml version="1.0" encoding="UTF-8"?>',
                                    '<gpx version="1.1" creator="Streamlit App" xmlns="http://www.topografix.com/GPX/1/1">',
                                    '  <trk>',
                                    f'    <name>{dati_uscita_corrente["titolo_uscita"]}</name>',
                                    '    <trkseg>'
                                ]
                                for lat, lon in zip(lats_g, lons_g):
                                    linee_gpx.append(f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>')
                                linee_gpx.extend([
                                    '    </trkseg>',
                                    '  </trk>',
                                    '</gpx>'
                                ])
                                contenuto_gpx_uscita = "\n".join(linee_gpx)
                                nome_file_gpx = "".join(c for c in dati_uscita_corrente["titolo_uscita"] if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                                if not nome_file_gpx:
                                    nome_file_gpx = "tracciato_uscita"

                                b64_gpx = base64.b64encode(contenuto_gpx_uscita.encode()).decode()
                                href_gpx = f'<a href="data:application/gpx+xml;base64,{b64_gpx}" download="{nome_file_gpx}.gpx" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 600; margin-top: 0.5rem; margin-bottom: 0.5rem;">📥 Scarica Tracciato GPX</div></a>'
                                st.markdown(href_gpx, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Nessuna coordinata GPS valida disponibile per questa specifica uscita su Intervals.icu.")
                    else:
                        st.error(f"Errore nel recupero flussi da Intervals (Status: {resp_str_g.status_code})")
        else:
            st.info("Nessuna attività trovata nel range temporale selezionato per il grafico.")
    else:
        st.error("Errore nel recupero dati per il grafico da Intervals.icu.")


# --- 4. ANALISI SCIENTIFICA E CARICO DI ALLENAMENTO (TSS, CTL, ATL, TSB) ---
st.markdown("---")
with st.expander("🧬 Analisi Scientifica: TSS, Carico e Forma Fisica (CTL/ATL/TSB)", expanded=False):
    st.write("Valutazione avanzata dello stress allenante, della potenza, della frequenza cardiaca e degli indici di condizione atletica.")

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        start_sci = st.date_input("Inizio Analisi Scientifica", value=date(2026, 1, 1), key="sci_start_indipendente")
    with col_a2:
        end_sci = st.date_input("Fine Analisi Scientifica", value=date.today(), key="sci_end_indipendente")

    url_sci = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
    params_sci = {
        "oldest": start_sci.strftime("%Y-%m-%d"),
        "newest": end_sci.strftime("%Y-%m-%d"),
        "iw": True
    }
    
    resp_sci = requests.get(url_sci, auth=("API_KEY", API_KEY.strip()), params=params_sci)

    if resp_sci.status_code == 200:
        dati_raw_sci = resp_sci.json()
        if dati_raw_sci:
            df_s = pd.DataFrame(dati_raw_sci)
            
            df_s['data_fmt'] = pd.to_datetime(df_s['start_date_local'])
            df_s['data_solo'] = df_s['data_fmt'].dt.date
            df_s['TSS'] = pd.to_numeric(df_s.get('icu_training_load', 0), errors='coerce').fillna(0)
            
            watts_col = 'average_watts' if 'average_watts' in df_s.columns else 'device_watts'
            df_s['Watt_Medi'] = pd.to_numeric(df_s.get(watts_col, 0), errors='coerce').fillna(0)
            df_s['BPM_Medi'] = pd.to_numeric(df_s.get('average_heartrate', 0), errors='coerce').fillna(0)
            df_s['Titolo'] = df_s.get('name', 'Uscita')

            df_s = df_s.sort_values('data_fmt').reset_index(drop=True)

            df_s['CTL'] = df_s['TSS'].ewm(span=42, adjust=False).mean()
            df_s['ATL'] = df_s['TSS'].ewm(span=7, adjust=False).mean()
            df_s['TSB'] = df_s['CTL'].shift(1) - df_s['ATL'].shift(1)
            df_s['TSB'] = df_s['TSB'].fillna(0)

            def calcola_ef(row):
                if row['BPM_Medi'] > 0 and row['Watt_Medi'] > 0:
                    return row['Watt_Medi'] / row['BPM_Medi']
                return 0

            df_s['EF'] = df_s.apply(calcola_ef, axis=1)

            tot_tss = df_s['TSS'].sum()
            media_watt = df_s[df_s['Watt_Medi'] > 0]['Watt_Medi'].mean()
            media_bpm = df_s[df_s['BPM_Medi'] > 0]['BPM_Medi'].mean()
            
            df_ef_validi = df_s[df_s['EF'] > 0]
            media_ef = df_ef_validi['EF'].mean() if not df_ef_validi.empty else 0

            st.markdown("#### 📊 Sintesi Indicatori Interni ed Esterni")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("TSS Totale", f"{tot_tss:,.0f}")
            col_m2.metric("Watt Medi (Sessione)", f"{media_watt:.1f} W" if not pd.isna(media_watt) else "N/D")
            col_m3.metric("BPM Medi", f"{media_bpm:.0f} bpm" if not pd.isna(media_bpm) else "N/D")
            col_m4.metric("Efficiency Factor (EF)", f"{media_ef:.2f}" if not pd.isna(media_ef) else "N/D")

            st.markdown("---")

            fig_pmc = go.Figure()

            fig_pmc.add_trace(go.Bar(
                x=df_s['data_solo'],
                y=df_s['TSS'],
                name='TSS (Carico)',
                marker=dict(color='rgba(31, 119, 180, 0.5)')
            ))

            fig_pmc.add_trace(go.Scatter(
                x=df_s['data_solo'],
                y=df_s['CTL'],
                name='CTL (Fitness)',
                mode='lines',
                line=dict(color='blue', width=2)
            ))

            fig_pmc.add_trace(go.Scatter(
                x=df_s['data_solo'],
                y=df_s['ATL'],
                name='ATL (Fatica)',
                mode='lines',
                line=dict(color='magenta', width=2)
            ))

            fig_pmc.add_trace(go.Scatter(
                x=df_s['data_solo'],
                y=df_s['TSB'],
                name='TSB (Forma)',
                mode='lines',
                line=dict(color='darkorange', width=2),
                yaxis='y2'
            ))

            fig_pmc.update_layout(
                title="Performance Management Chart (TSS, Fitness CTL, Fatica ATL & Forma TSB)",
                xaxis_title="Data",
                yaxis=dict(title="Carico / Fitness / Fatica"),
                yaxis2=dict(
                    title="Forma (TSB)",
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                margin=dict(l=20, r=40, t=40, b=20),
                height=420,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig_pmc, use_container_width=True, config={'displaylogo': False})

            st.markdown("---")
            st.markdown("#### 🧠 Resoconto e Valutazione Scientifica")

            ultimo_ctl = df_s['CTL'].iloc[-1] if not df_s.empty else 0
            ultimo_tsb = df_s['TSB'].iloc[-1] if not df_s.empty else 0

            if ultimo_tsb > 5:
                status_forma = "🟢 **Condizione di Freschezza / Supercompensazione**: Il corpo ha ampiamente smaltito i carichi passati. Ottimale per massimali o gare."
            elif -10 <= ultimo_tsb <= 5:
                status_forma = "🔵 **Stato di Assimilazione / equilibrio ottimale**: Il carico e il recupero sono perfettamente bilanciati per la crescita della forma."
            else:
                status_forma = "🟠 **Affaticamento / Sovraccarico funzionale**: Il bilancio energetico e di stress (TSB negativo) indica stanchezza accumulata; valutare riposo o scarico."

            st.markdown(f"""
            * **Fitness Attuale (CTL stimato):** `{ultimo_ctl:.1f}` punti.
            * **Bilancio di Forma (TSB corrente):** `{ultimo_tsb:.1f}`.
            * **Valutazione Clinico-Sportiva:** {status_forma}
            * **Analisi Efficienza Cardiometabolica:** Un Efficiency Factor medio di `{media_ef:.2f}` indica una solida coerenza tra spinta energetica espressa in Watt e risposta cardiaca nel periodo selezionato.
            """)
        else:
            st.info("Nessuna attività disponibile nel range selezionato per l'analisi scientifica.")
    else:
        st.error("Errore nel recupero dati per l'analisi scientifica da Intervals.icu.")
