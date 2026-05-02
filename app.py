import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import ticker
import random
import pandas as pd
import numpy as np
import globals
from controller import run_simulation


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

    ## Simulation Configuration
    st.write("")

    number_of_rounds = st.number_input("Cantidad de Rondas", value=100)

    ## Submit Button
    submitted = st.form_submit_button("Correr Experimento")

if submitted:
    globals.AGENT_COUNT_MAP[globals.ADVERSE_AGENT_KEY] = n_adverse_agents
    globals.AGENT_COUNT_MAP[globals.NEUTRAL_AGENT_KEY] = n_neutral_agents
    globals.SAFE_ROAD_COST = safe_road_costs
    globals.FREE_SHORTCUT_COST = free_shortcut_cost
    globals.CONGESTION_FACTOR = congestion_factor
    globals.SHORTCUT_THRESHOLD = shortcut_capacity
    globals.NUMBER_OF_ROUNDS = number_of_rounds

    results = run_simulation()

    
    ## Post processing for visualization
    history = pd.DataFrame(results["history"])
    agents = results["agents"]
    

    all_snapshots = []
    for a in agents:
        for s in a.snapshots:
            s['agent_type'] = a.type
            all_snapshots.append(s)
    df_snap = pd.DataFrame(all_snapshots)

    safe_cost = globals.SAFE_ROAD_COST

    round_by_type = df_snap.groupby(['round', 'agent_type'])

    shortcut_counts = round_by_type['decision'].apply(lambda x: (x == globals.SHORTCUT_KEY).sum()).unstack(fill_value=0)

    mean_beliefs = round_by_type['belief'].mean().unstack()
    mean_expected_cost = round_by_type['expected_cost_shortcut'].mean().unstack()

    ## Visualización
    st.header("Resultados de la Simulación")

    col1, col2 = st.columns(2)

    with col1:
        # Plot 1: Shortcut Occupation by Agent Type
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        shortcut_counts.plot(kind='bar', stacked=True, ax=ax1, alpha=0.8)
        ax1.axhline(y=shortcut_capacity, color='green', label=f'Capacidad ({shortcut_capacity})')
        ax1.axhline(y=globals.OPTIMAL_AGENTS_IN_SHORTCUT, color='red', label=f'Óptimo ({int(globals.OPTIMAL_AGENTS_IN_SHORTCUT)})')
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
        plt.xticks(rotation=0)
        ax1.set_title("Autos en el Atajo por Tipo de Agente")
        ax1.set_ylabel("Cantidad de Autos")
        ax1.set_xlabel("Ronda")
        ax1.legend()
        st.pyplot(fig1)

        # Plot 2: Expected Costs vs Real Costs
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        for col in mean_expected_cost.columns:
            ax2.plot(mean_expected_cost.index, mean_expected_cost[col], label=f"Costo atajo según {col}", linestyle='-')
        ax2.plot(history['round'], history['real_shortcut_cost'], label="Costo Real Atajo", color='#707070', linewidth=2)
        ax2.axhline(y=safe_cost, color='green', linestyle='-', label="Costo Camino Seguro")
        ax2.set_title("Variación de Costos")
        ax2.set_xlabel("Ronda")
        ax2.set_ylabel("Costo")
        ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
        ax2.legend()
        st.pyplot(fig2)

    with col2:
        ## Plot 3: Mean System Cost
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        total_agents = len(agents)
        history['mean_system_cost'] = (
            (history['cars_in_shortcut'] * history['real_shortcut_cost']) + 
            ((total_agents - history['cars_in_shortcut']) * safe_cost)
        ) / total_agents
        
        ax3.bar(history['round'], history['mean_system_cost'], color='skyblue')
        ax3.set_title("Costo Medio del Viaje")
        ax3.axhline(y=safe_cost, color='green', label=f'Costo Camino Seguro ({safe_cost})')
        ax3.axhline(y=globals.OPTIMAL_COST, color='red', label=f'Costo Óptimo ({globals.OPTIMAL_COST:.2f})')
        ax3.set_ylabel("Minutos")
        ax3.set_xlabel("Ronda")
        ax3.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
        ax3.legend()
        st.pyplot(fig3)

        ## Plot 4: Beliefs Evolution
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        for col in mean_beliefs.columns:
            ax4.plot(mean_beliefs.index, mean_beliefs[col], label=f"Creencia {col}")

        saturacion_etiquetada = False
        for i, row in history.iterrows():
            if row['shortcut_saturated']:
                label_text = "Atajo saturado" if not saturacion_etiquetada else ""
                ax4.axvspan(row['round'] - 0.5, row['round'] + 0.5, color='red', alpha=0.2, label=label_text)
                saturacion_etiquetada = True

        ax4.set_title("Evolución de Creencias")
        ax4.set_ylim(0, 1)
        ax4.set_xlabel("Ronda")
        ax4.set_ylabel("Creencia de Saturación")
        ax4.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
        ax4.legend()
        st.pyplot(fig4)

    
    
else:
    st.info("Ajustá los parámetros en el panel izquierdo y hacé clic en 'Correr Experimento' para ver los resultados.")


