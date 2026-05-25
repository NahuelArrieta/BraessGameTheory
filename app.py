import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import ticker
import random
import pandas as pd
import numpy as np
import globals
from controller import run_simulation
import graphics


st.set_page_config(page_title="Paradoja de Braess", layout="wide")
st.title("Simulación: Paradoja de Braess")

## Form
with st.sidebar.form("config_simulacion"):
    st.header("Configuración")

    ##  Agent Configuration
    col1, col2 = st.columns(2)

    with col1:
        n_adverse_agents = st.number_input("N° de Agentes Aversos", value=50)

    with col2:
        n_neutral_agents = st.number_input("N° de Agentes Neutrales", value=50)

    total_agents = n_adverse_agents + n_neutral_agents

    ## Cost Configuration
    st.write("")
    col1, col2 = st.columns(2)

    with col1:
        safe_road_costs = st.number_input("Costo Ruta Segura", value=45)

    with col2:
        free_shortcut_cost = st.number_input("Costo Atajo Libre", value=10)
    
    congestion_factor = st.slider("Factor de Congestión", 0.1, 5.0, 1.2)

    shortcut_capacity = st.slider("Capacidad Atajo (K)", 5, total_agents, 25)

    
    ## Submit Button
    submitted = st.form_submit_button("Correr Experimento")

if submitted:
    globals.AGENT_COUNT_MAP[globals.ADVERSE_AGENT_KEY] = n_adverse_agents
    globals.AGENT_COUNT_MAP[globals.NEUTRAL_AGENT_KEY] = n_neutral_agents
    globals.SAFE_ROAD_COST = safe_road_costs
    globals.FREE_SHORTCUT_COST = free_shortcut_cost
    globals.CONGESTION_FACTOR = congestion_factor
    globals.SHORTCUT_THRESHOLD = shortcut_capacity

    results = run_simulation()

    graphics.draw_graphics(results)
else:
    st.info("Ajustá los parámetros en el panel izquierdo y hacé clic en 'Correr Experimento' para ver los resultados.")

