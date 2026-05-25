import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import ticker
import random
import pandas as pd
import numpy as np
import globals
from controller import run_simulation


def draw_cars_in_shortcut_graph(results):
    iteration_results = results["iteration_results"]

    ## Calculate average and std deviation of cars in shortcut across iterations for each round
    cars_in_shortcut = []
    for round in range(globals.NUMBER_OF_ROUNDS):
        round_data = [iteration_results[i]["history"][round] for i in range(globals.NUMBER_OF_ITERATIONS)]
        avg_cars_in_shortcut = np.mean([d["cars_in_shortcut"] for d in round_data])
        std_cars_in_shortcut = np.std([d["cars_in_shortcut"] for d in round_data])
        cars_in_shortcut.append({
            "round": round,
            "avg": avg_cars_in_shortcut,
            "std": std_cars_in_shortcut
        })
    
    df_cars_in_shortcut = pd.DataFrame(cars_in_shortcut)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        df_cars_in_shortcut['round'], 
        df_cars_in_shortcut['avg'], 
        label='Promedio de Autos en Atajo', 
        color='#1f77b4', linewidth=0.8, marker='.', markersize=4
    )

    ax.fill_between(d
        f_cars_in_shortcut['round'], 
        df_cars_in_shortcut['avg'] - df_cars_in_shortcut['std'], 
        df_cars_in_shortcut['avg'] + df_cars_in_shortcut['std'], 
        color='#1f77b4', alpha=0.15, label='Desviación Estándar'
    )

    ax.axhline(
        y=globals.SHORTCUT_THRESHOLD, color='#d62728', linestyle='--', 
        linewidth=1.5, label=f'Capacidad Atajo ({globals.SHORTCUT_THRESHOLD})'
    )

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.set_title("Promedio de Autos en el Atajo por Ronda", fontsize=14, pad=15)
    ax.set_xlabel("Ronda", fontsize=11)
    ax.set_ylabel("Cantidad de Autos", fontsize=11)

    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
        
    return fig


def draw_graphics(results):
    fig = draw_cars_in_shortcut_graph(results)
    st.pyplot(fig)

    return

    agents = results["agents"]
    iteration_results = results["iteration_results"]

    ## Construct an average history across iterations for analysis
    cars_in_shortcut = {
        "avg": np.mean([iteration_results[i]["history"][round]["cars_in_shortcut"] for i in range(globals.NUMBER_OF_ITERATIONS) for round in range(globals.NUMBER_OF_ROUNDS)]),
        "std": np.std([iteration_results[i]["history"][round]["cars_in_shortcut"] for i in range(globals.NUMBER_OF_ITERATIONS) for round in range(globals.NUMBER_OF_ROUNDS)])
    }

    df_cars_in_shortcut = pd.DataFrame(cars_in_shortcut)
    st.line_chart(df_cars_in_shortcut)

    # avg_history = []
    # for round in range(globals.NUMBER_OF_ROUNDS):
    #     round_data = [iteration_results[i]["history"][round] for i in range(globals.NUMBER_OF_ITERATIONS)]
    #     avg_cars_in_shortcut = np.mean([d["cars_in_shortcut"] for d in round_data])
    #     avg_shortcut_saturated = np.mean([d["shortcut_saturated"] for d in round_data])
    #     avg_real_shortcut_cost = np.mean([d["real_shortcut_cost"] for d in round_data])

    #     avg_history.append({
    #         "round": round,
    #         "cars_in_shortcut": avg_cars_in_shortcut,
    #         "shortcut_saturated": avg_shortcut_saturated,
    #         "real_shortcut_cost": avg_real_shortcut_cost
    #     })

    ## Post processing for visualization
    ## history = pd.DataFrame(avg_history)
    shortcut_capacity = globals.SHORTCUT_THRESHOLD
    optimal_agents = globals.OPTIMAL_AGENTS_IN_SHORTCUT

    ## Calculate shortcut occupation by agent type
    all_snapshots = []
    for a in agents:
        for s in a.snapshots:
            s['agent_type'] = a.type
            all_snapshots.append(s)
    df_snap = pd.DataFrame(all_snapshots)

    safe_cost = globals.SAFE_ROAD_COST

    round_by_type = df_snap.groupby(['round', 'agent_type'])

    shortcut_counts_by_type = round_by_type['decision'].apply(
        lambda x: (x == globals.SHORTCUT_KEY).sum()/globals.NUMBER_OF_ITERATIONS
    ).unstack(fill_value=0)

    shortcut_counts_total = df_snap.groupby('round')['decision'].apply(
        lambda x: (x == globals.SHORTCUT_KEY).sum()/globals.NUMBER_OF_ITERATIONS
    )

    ## Calculate mean beliefs and expected costs
    mean_beliefs = round_by_type['belief'].mean().unstack()
    mean_expected_cost = round_by_type['expected_cost_shortcut'].mean().unstack()

    ## Visualización
    st.header("Resultados de la Simulación")

    col1, col2 = st.columns(2)

    with col1:
        # Plot 1: Shortcut Occupation by Agent Type
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        shortcut_counts_by_type.plot(kind='bar', stacked=True, ax=ax1, alpha=0.8)
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

    
    


