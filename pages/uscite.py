import streamlit as _st
from streamlit_folium import st_folium
import folium
import polyline  # Assicurati di avere la libreria 'polyline' installata per decodificare i tracciati GPS

# Esempio all'interno del ciclo che scorre le attività estratte:
for idx, attivita in enumerate(lista_attivita):
    key_bottoni = f"btn_mappa_{idx}"
    
    # Inizializza lo stato del singolo bottone se non esiste
    if key_bottoni not in _st.session_state:
        _st.session_state[key_bottoni] = False

    with _st.container():
        _st.markdown(f"### {attivita.get('name', 'Attività')} ({attivita.get('start_date', '')[:10]})")
        _st.write(f"Distanza: **{attivita.get('distance', 0):.2f} km** | D+: **{attivita.get('total_elevation_gain', 0):.0f} m** | Tempo: **{attivita.get('moving_time', '')}**")
        
        # Bottone per aprire/chiudere la mappa in-line
        testo_btn = "Nascondi Mappa" if _st.session_state[key_bottoni] else "🔍 Apri Mappa"
        if _st.button(testo_btn, key=key_bottoni):
            _st.session_state[key_bottoni] = not _st.session_state[key_bottoni]
            _st.rerun()

        # Se il bottone è attivo, genera e mostra la mappa direttamente sotto l'attività
        if _st.session_state[key_bottoni]:
            _st.markdown("---")
            _st.markdown("#### 🗺️ Anteprima Percorso GPS")
            
            # Recuperiamo i dati della polilinea (formato tipico di Intervals.icu / Strava)
            map_data = attivita.get('map', {})
            summary_polyline = map_data.get('summary_polyline') or map_data.get('polyline')
            
            if summary_polyline:
                try:
                    # Decodifichiamo la polyline in coordinate lat/lon
                    decoded_coordinates = polyline.decode(summary_polyline)
                    
                    if decoded_coordinates:
                        # Centriamo la mappa sul primo punto del percorso
                        m = folium.Map(location=decoded_coordinates[0], zoom_start=13, tiles="CartoDB positron")
                        
                        # Disegniamo la linea del tracciato
                        folium.PolyLine(
                            decoded_coordinates, 
                            color="#ff4b4b", 
                            weight=4, 
                            opacity=0.8
                        ).add_to(m)
                        
                        # Mostriamo la mappa all'interno dell'app Streamlit
                        st_folium(m, width=700, height=350, key=f"map_render_{idx}")
                    else:
                        _st.warning("Impossibile leggere le coordinate GPS per questa attività.")
                except Exception as e:
                    _st.error(్రిf"Errore durante il rendering della mappa: {e}")
            else:
                _st.warning("Nessun dato di tracciato (polyline) disponibile per questa attività.")
                
        _st.markdown("---")
        
