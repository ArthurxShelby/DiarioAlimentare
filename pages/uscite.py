# --- 4. SEZIONE PARAMETRI DI INTERVALS ---
st.markdown("---")

# --- DEFINIZIONE MODALE (DIALOG) PER LA MAPPA ---
@st.dialog("🗺️ Percorso Attività e Tracciato GPX", width="large")
def apri_mappa_dialog(ag_id, ag_title):
    clean_id_s4 = ''.join(c for c in ag_id if c.isdigit())
    target_url_s4 = f"https://intervals.icu/api/v1/activity/{clean_id_s4}/streams"
    
    try:
        resp_s4_streams = requests.get(target_url_s4, auth=("API_KEY", API_KEY.strip()))
        if resp_s4_streams.status_code == 404 and ag_id != clean_id_s4:
            target_url_s4 = f"https://intervals.icu/api/v1/activity/{ag_id}/streams"
            resp_s4_streams = requests.get(target_url_s4, auth=("API_KEY", API_KEY.strip()))
            
        if resp_s4_streams.status_code == 200:
            data_s4 = resp_s4_streams.json()
            lats_s4, lons_s4 = [], []
            
            if isinstance(data_s4, list):
                for stream in data_s4:
                    if isinstance(stream, dict):
                        stype = stream.get("type")
                        if stype in ["latlng", "lating"]:
                            lat_data = stream.get("data", [])
                            lon_data = stream.get("data2", [])
                            
                            if isinstance(lat_data, list) and isinstance(lon_data, list) and len(lat_data) == len(lon_data) and len(lat_data) > 0:
                                for lat, lon in zip(lat_data, lon_data):
                                    if lat is not None and lon is not None:
                                        lats_s4.append(float(lat))
                                        lons_s4.append(float(lon))
                            elif isinstance(lat_data, list) and len(lat_data) > 0:
                                for pt in lat_data:
                                    if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                                        if pt[0] is not None and pt[1] is not None:
                                            lats_s4.append(float(pt[0]))
                                            lons_s4.append(float(pt[1]))
                                            
            if lats_s4 and lons_s4:
                # Selettore stile a sinistra e spazio vuoto a destra per lasciare posto alla barra nativa della mappa
                c_s4_style1, c_s4_space = st.columns([2, 3])
                with c_s4_style1:
                    stile_s4 = st.selectbox(
                        "Stile Mappa",
                        ["Stradale (OpenStreetMap)", "Satellite (ArcGIS)"],
                        key=f"style_s4_dialog_{ag_id}",
                        label_visibility="collapsed"
                    )

                altezza_mappa = 550
                
                if "Satellite" in stile_s4:
                    basemap_style_s4 = "white-bg"
                    tile_source_s4 = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    labels_source_s4 = "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                else:
                    basemap_style_s4 = "open-street-map"
                    tile_source_s4 = None
                    labels_source_s4 = None

                fig_s4 = go.Figure()
                fig_s4.add_trace(go.Scattermapbox(
                    lat=lats_s4, lon=lons_s4, mode='lines',
                    line=dict(width=4, color='dodgerblue'), name='Tracciato'
                ))
                fig_s4.add_trace(go.Scattermapbox(
                    lat=[lats_s4[0], lats_s4[-1]], lon=[lons_s4[0], lons_s4[-1]], mode='markers',
                    marker=dict(size=10, color=['green', 'red']), text=['Partenza', 'Arrivo'], name='Marker'
                ))
                
                mapbox_config_s4 = dict(
                    style=basemap_style_s4,
                    center=dict(lat=sum(lats_s4)/len(lats_s4), lon=sum(lons_s4)/len(lons_s4)),
                    zoom=11
                )

                layers_list_s4 = []
                if tile_source_s4:
                    layers_list_s4.append({
                        "sourcetype": "raster",
                        "source": [tile_source_s4],
                        "below": "traces"
                    })
                if labels_source_s4:
                    layers_list_s4.append({
                        "sourcetype": "raster",
                        "source": [labels_source_s4],
                        "below": "traces"
                    })
                    
                if layers_list_s4:
                    mapbox_config_s4["layers"] = layers_list_s4

                fig_s4.update_layout(
                    mapbox=mapbox_config_s4,
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=altezza_mappa,
                    autosize=False,
                    showlegend=False
                )
                
                config_mappa = {
                    'scrollZoom': True, 
                    'displaylogo': False,
                    'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
                }
                
                st.plotly_chart(fig_s4, use_container_width=True, key=f"plotly_map_sec4_dlg_{ag_id}", config=config_mappa)
                
                linee_s4 = [
                    '<?xml version="1.0" encoding="UTF-8"?>',
                    '<gpx version="1.1" creator="Streamlit App" xmlns="http://www.topografix.com/GPX/1/1">',
                    '  <trk>',
                    f'    <name>{ag_title}</name>',
                    '    <trkseg>'
                ]
                for lat, lon in zip(lats_s4, lons_s4):
                    linee_s4.append(f'      <trkpt lat="{lat}" lon="{lon}"></trkpt>')
                linee_s4.extend([
                    '    </trkseg>',
                    '  </trk>',
                    '</gpx>'
                ])
                contenuto_gpx_s4 = "\n".join(linee_s4)
                nome_file_s4 = "".join(c for c in ag_title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
                if not nome_file_s4:
                    nome_file_s4 = "tracciato"

                b64_s4 = base64.b64encode(contenuto_gpx_s4.encode()).decode()
                href_s4 = f'<a href="data:application/gpx+xml;base64,{b64_s4}" download="{nome_file_s4}.gpx" style="text-decoration: none;"><div style="background-color: #ff4b4b; color: white; padding: 0.6rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 600; margin-top: 1rem;">📥 Scarica Tracciato GPX</div></a>'
                st.markdown(href_s4, unsafe_allow_html=True)
            else:
                st.warning("Nessun punto di coordinate valido.")
        else:
            st.error(f"Errore recupero flussi (Status: {resp_s4_streams.status_code})")
    except Exception as e:
        st.error(f"Errore: {e}")

with st.expander("🎯 Dashboard Avanzata Parametri Intervals.icu", expanded=True):
    st.write("Estrazione dei parametri per il giorno selezionato.")
    
    oggi = date.today()
    
    c1, _ = st.columns([1, 3])
    with c1:
        giorno_scelto = st.date_input("Seleziona Giorno", value=oggi, key="sec4_giorno_singolo")
    
    start_sec4 = giorno_scelto
    end_sec4 = giorno_scelto

    url_sec4 = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/activities"
    params_sec4 = {
        "oldest": start_sec4.strftime("%Y-%m-%d"),
        "newest": end_sec4.strftime("%Y-%m-%d"),
        "iw": True
    }
    resp_sec4 = requests.get(url_sec4, auth=("API_KEY", API_KEY.strip()), params=params_sec4)

    if resp_sec4.status_code == 200:
        attivita_giorno = resp_sec4.json()
        if attivita_giorno:
            st.markdown("---")
            st.markdown(f"#### 🚴 Attività Trovata per il {giorno_scelto.strftime('%d/%m/%Y')}")
            for idx_sec4, act_g in enumerate(attivita_giorno):
                ag_id = str(act_g.get("id"))
                ag_title = act_g.get("name", "Uscita senza titolo")
                ag_dist = round(act_g.get("distance", 0) / 1000, 2)
                ag_time = timedelta_to_str(act_g.get("moving_time", 0))
                ag_elev = safe_int(act_g.get("total_elevation_gain")) or 0

                col_act_info, col_act_btn = st.columns([3, 1])
                with col_act_info:
                    st.write(f"**{ag_title}** — Distanza: **{ag_dist} km** | D+: **{ag_elev} m** | Tempo: **{ag_time}**")
                with col_act_btn:
                    if st.button("🗺️ Mostra Mappa", key=f"btn_sec4_map_{ag_id}_{idx_sec4}", use_container_width=True):
                        apri_mappa_dialog(ag_id, ag_title)
        else:
            st.info(f"Nessuna attività registrata per il {giorno_scelto.strftime('%d/%m/%Y')}.")

    # --- Resto del codice Wellness e Gauge ---
    url_well = f"https://intervals.icu/api/v1/athlete/{ATHLETE_ID}/wellness"
    params_well = {
        "oldest": start_sec4.strftime("%Y-%m-%d"),
        "newest": end_sec4.strftime("%Y-%m-%d")
    }
    resp_well = requests.get(url_well, auth=("API_KEY", API_KEY.strip()), params=params_well)

    val_load = 0.0
    val_if = 0.0
    val_vi = 1.0
    val_eftp = 279.0
    val_ef = 0.0
    val_ctl = 0.0
    val_atl = 0.0
    np_val = 0.0
    gp_val = 0.0
    avg_hr = 0.0
    m = {}

    if resp_well.status_code == 200:
        dati_well = resp_well.json()
        if dati_well:
            df_w = pd.DataFrame(dati_well)
            if not df_w.empty and 'id' in df_w.columns:
                df_w['data_well'] = pd.to_datetime(df_w['id']).dt.date
                df_w_filtrato = df_w[df_w['data_well'] == giorno_scelto]
                if not df_w_filtrato.empty:
                    ultimo_w = df_w_filtrato.sort_values('id', ascending=False).iloc[0]
                    val_ctl = float(ultimo_w.get('ctl', 0.0) or 0.0)
                    val_atl = float(ultimo_w.get('atl', 0.0) or 0.0)

    if resp_sec4.status_code == 200:
        dati_sec4 = resp_sec4.json()
        if dati_sec4:
            df_s4 = pd.DataFrame(dati_sec4)
            if not df_s4.empty and 'start_date_local' in df_s4.columns:
                df_s4['data_attivita'] = pd.to_datetime(df_s4['start_date_local']).dt.date
                df_s4_filtrato = df_s4[df_s4['data_attivita'] == giorno_scelto]
                
                if not df_s4_filtrato.empty:
                    ultima_act = df_s4_filtrato.sort_values('start_date_local', ascending=False).iloc[0]
                    m = ultima_act.to_dict()
                    
                    act_id = m.get('id')
                    if act_id:
                        url_detail = f"https://intervals.icu/api/v1/activity/{act_id}"
                        resp_detail = requests.get(url_detail, auth=("API_KEY", API_KEY.strip()))
                        if resp_detail.status_code == 200:
                            detail_json = resp_detail.json()
                            m.update(detail_json)

                        url_streams = f"https://intervals.icu/api/v1/activity/{act_id}/streams"
                        resp_streams = requests.get(url_streams, auth=("API_KEY", API_KEY.strip()))
                        watts_stream = []
                        if resp_streams.status_code == 200:
                            streams_data = resp_streams.json()
                            if isinstance(streams_data, list):
                                for stream in streams_data:
                                    if isinstance(stream, dict) and stream.get("type") == "watts":
                                        watts_stream = stream.get("data", [])
                                        break

                    val_load = float(m.get('icu_training_load') or m.get('load') or 0.0)
                    val_eftp = float(m.get('icu_ftp') or m.get('eftp') or 279.0)
                    
                    val_ctl = float(m.get('icu_ctl') or val_ctl or 0.0)
                    val_atl = float(m.get('icu_atl') or val_atl or 0.0)

                    np_val = float(m.get('normalized_watts') or m.get('icu_normalized_watts') or m.get('np') or m.get('weighted_average_watts') or 0.0)
                    gp_val = float(m.get('average_watts') or m.get('icu_average_watts') or m.get('watts') or 0.0)
                    avg_hr = float(m.get('average_heartrate') or m.get('icu_average_heartrate') or m.get('hr') or 0.0)

                    if np_val == 0.0 and watts_stream:
                        valid_watts = [w for w in watts_stream if w is not None and w >= 0]
                        if len(valid_watts) >= 30:
                            rolling_30s = [sum(valid_watts[i:i+30])/30 for i in range(len(valid_watts)-29)]
                            np_val = float((sum([w**4 for w in rolling_30s]) / len(rolling_30s)) ** 0.25)
                        elif valid_watts:
                            np_val = float(sum(valid_watts) / len(valid_watts))

                    if np_val == 0.0 and gp_val > 0:
                        np_val = gp_val

                    if np_val > 0 and val_eftp > 0:
                        val_if = np_val / val_eftp
                    else:
                        raw_if = float(m.get('intensity_factor') or m.get('icu_intensity') or 0.0)
                        val_if = raw_if / 100.0 if raw_if > 2.0 else raw_if

                    val_vi = float(m.get('variability_index') or m.get('vi') or m.get('icu_variability_index') or 0.0)
                    if val_vi == 0.0 and np_val > 0 and gp_val > 0:
                        val_vi = np_val / gp_val
                    if val_vi == 0.0: 
                        val_vi = 1.0

                    val_ef = float(m.get('efficiency_factor') or m.get('ef') or m.get('icu_efficiency_factor') or 0.0)
                    if val_ef == 0.0 and np_val > 0 and avg_hr > 0:
                        val_ef = np_val / avg_hr

    val_tsb = val_ctl - val_atl

    st.markdown("---")

    def apply_dark_theme(fig, height=220):
        fig.update_layout(
            height=height,
            autosize=False,
            margin=dict(l=20, r=20, t=50, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        return fig

    with st.container(border=True):
        st.markdown("### 1. Gestione del Carico e della Forma (Grafico 'Fitness')")
        st.caption("ℹ️ **Legenda:** Monitoraggio a lungo termine del carico di allenamento (CTL = Fitness, ATL = Fatica, TSB = Stato di Forma/Balance).")
        col_s1_1, col_s1_2, col_s1_3 = st.columns(3)
        
        with col_s1_1:
            fig_ctl = go.Figure(go.Indicator(
                mode="gauge+number", value=val_ctl, title={"text": "<b>Fitness (CTL)</b>"},
                gauge={'axis': {'range': [0, 150]}, 'bar': {'color': "royalblue"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_ctl), use_container_width=True, key="chart_gauge_ctl", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>CTL (Chronic Training Load):</b> Carico di allenamento cronico, ovvero la fitness aerobica di fondo sviluppata negli ultimi 42 giorni.</p>", unsafe_allow_html=True)
            
        with col_s1_2:
            fig_atl = go.Figure(go.Indicator(
                mode="gauge+number", value=val_atl, title={"text": "<b>Fatigue (ATL)</b>"},
                gauge={'axis': {'range': [0, 150]}, 'bar': {'color': "darkorange"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_atl), use_container_width=True, key="chart_gauge_atl", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>ATL (Acute Training Load):</b> Carico di fatica acuto e stress muscolare accumulato negli ultimi 7 giorni.</p>", unsafe_allow_html=True)
            
        with col_s1_3:
            fig_tsb = go.Figure(go.Indicator(
                mode="gauge+number", value=val_tsb, title={"text": "<b>Form (TSB)</b>"},
                gauge={'axis': {'range': [-50, 50]}, 'bar': {'color': "forestgreen" if -30 <= val_tsb <= -10 else "crimson"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_tsb), use_container_width=True, key="chart_gauge_tsb", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>TSB (Training Stress Balance):</b> Stato di freschezza o affaticamento (CTL meno ATL). Valori positivi indicano riposo, negativi indicano carico.</p>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 2. Intensità e Stress della Singola Sessione")
        st.caption("ℹ️ **Legenda:** Valutazione dello stress immediato dell'allenamento (TSS/Load), dell'Intensity Factor (IF) e della regolarità dello sforzo tramite il Variability Index (VI).")
        col_s2_1, col_s2_2, col_s2_3 = st.columns(3)
        
        with col_s2_1:
            fig_load = go.Figure(go.Indicator(
                mode="gauge+number", value=val_load, title={"text": "<b>Load / TSS Sessione</b>"},
                gauge={'axis': {'range': [0, 400]}, 'bar': {'color': "dodgerblue"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_load), use_container_width=True, key="chart_gauge_load", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>Training Stress Score (TSS):</b> Quantifica lo stress complessivo della singola sessione in base a durata e intensità rapportate alla tua FTP.</p>", unsafe_allow_html=True)

        with col_s2_2:
            fig_if = go.Figure(go.Indicator(
                mode="gauge+number", value=val_if, title={"text": "<b>Intensity Factor (IF)</b>"},
                number={'valueformat': ".2f"},
                gauge={'axis': {'range': [0, 1.3]}, 'bar': {'color': "purple"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_if), use_container_width=True, key="chart_gauge_if", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>Intensity Factor (IF):</b> Esprime quanto è stata dura l'uscita rapportando la Potenza Normalizzata (NP) alla tua soglia (FTP).</p>", unsafe_allow_html=True)

        with col_s2_3:
            fig_vi = go.Figure(go.Indicator(
                mode="gauge+number", value=val_vi, title={"text": "<b>Variability Index (VI)</b>"},
                number={'valueformat': ".2f"},
                gauge={'axis': {'range': [1.0, 1.5]}, 'bar': {'color': "teal"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_vi), use_container_width=True, key="chart_gauge_vi", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>Variability Index (VI):</b> Rapporto tra Potenza Normalizzata e Potenza Media; misura la regolarità dello sforzo (1.0 indica pedalata perfettamente rotonda).</p>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 3. Analisi della Performance e Capacità")
        st.caption("ℹ️ **Legenda:** Analisi della potenza funzionale stimata (eFTP) e dell'Efficiency Factor (EF).")
        col_s3_1, col_s3_2 = st.columns(2)
        
        with col_s3_1:
            fig_eftp = go.Figure(go.Indicator(
                mode="gauge+number", value=val_eftp, title={"text": "<b>eFTP (W)</b>"},
                gauge={'axis': {'range': [0, 400]}, 'bar': {'color': "crimson"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_eftp), use_container_width=True, key="chart_gauge_eftp", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>eFTP (Estimated Functional Threshold Power):</b> La stima dinamica della tua soglia di potenza funzionale calcolata sulle migliori prestazioni recenti.</p>", unsafe_allow_html=True)

        with col_s3_2:
            fig_ef = go.Figure(go.Indicator(
                mode="gauge+number", value=val_ef, title={"text": "<b>Efficiency Factor (EF)</b>"},
                number={'valueformat': ".2f"},
                gauge={'axis': {'range': [0.0, 2.5]}, 'bar': {'color': "goldenrod"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_ef), use_container_width=True, key="chart_gauge_ef", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>Efficiency Factor (EF):</b> Rapporto tra Potenza Normalizzata e frequenza cardiaca media; indica l'efficienza cardiocircolatoria e aerobica.</p>", unsafe_allow_html=True)

        st.markdown("---")

        col_s3_3, col_s3_4 = st.columns(2)
        with col_s3_3:
            valore_np_display = float(np_val) if np_val else 0.0
            
            fig_np_gauge = go.Figure(go.Indicator(
                mode="gauge+number", 
                value=valore_np_display, 
                title={"text": "<b>Potenza Normalizzata (NP)</b>"},
                gauge={'axis': {'range': [0, 400]}, 'bar': {'color': "mediumorchid"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_np_gauge), use_container_width=True, key="chart_gauge_np", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>Potenza Normalizzata (NP):</b> Stima della potenza equivalente che toglie i picchi, riflettendo il costo metabolico reale dell'uscita.</p>", unsafe_allow_html=True)

        with col_s3_4:
            valore_fc_display = float(avg_hr) if avg_hr else 0.0
            
            fig_fc_gauge = go.Figure(go.Indicator(
                mode="gauge+number", 
                value=valore_fc_display, 
                title={"text": "<b>FC Media (bpm)</b>"},
                gauge={'axis': {'range': [0, 200]}, 'bar': {'color': "orangered"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            st.plotly_chart(apply_dark_theme(fig_fc_gauge), use_container_width=True, key="chart_gauge_fc", config={'displaylogo': False})
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #aaa;'><b>Frequenza Cardiaca Media:</b> Battito cardiaco medio registrato durante tutta la sessione di allenamento.</p>", unsafe_allow_html=True)
