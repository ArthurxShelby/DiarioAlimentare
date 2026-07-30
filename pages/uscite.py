import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import base64
from datetime import date, datetime

# --- VERIFICA / INIZIALIZZAZIONE CREDENZIALI ---
# Assicurati che ATHLETE_ID e API_KEY siano presenti in st.session_state 
# (oppure inseriscili qui se li definisci direttamente)
if "ATHLETE_ID" not in st.session_state or "API_KEY" not in st.session_state:
    st.error("⚠️ Credenziali mancanti. Assicurati di aver inserito ATHLETE_ID e API_KEY nella pagina principale o nelle impostazioni.")
    st.stop()

ATHLETE_ID = st.session_state["ATHLETE_ID"]
API_KEY = st.session_state["API_KEY"]

# Se invece usi st.secrets, puoi mapparli così:
# ATHLETE_ID = st.secrets.get("ATHLETE_ID", "tuo_id_default")
# API_KEY = st.secrets.get("API_KEY", "tua_chiave_default")
