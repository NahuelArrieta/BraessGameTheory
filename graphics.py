import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import ticker
import random
import pandas as pd
import numpy as np
import globals
from controller import run_simulation


def draw_cars_in_shortcut_graph(results):
    ## Calculate average and std deviation of cars in shortcut across iterations for each round
    cars_in_shortcut = []
    for round in range(globals.NUMBER_OF_ROUNDS):
        round_data = [results[i]["history"][round] for i in range(globals.NUMBER_OF_ITERATIONS)]
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
        label='Autos en Atajo', 
        color='#1f77b4', linewidth=0.8, marker='.', markersize=4
    )

    ax.fill_between(
        df_cars_in_shortcut['round'], 
        df_cars_in_shortcut['avg'] - df_cars_in_shortcut['std'], 
        df_cars_in_shortcut['avg'] + df_cars_in_shortcut['std'], 
        color='#1f77b4', alpha=0.15
    )

    shortcut_capacity = globals.SHORTCUT_THRESHOLD
    optimal_agents = globals.OPTIMAL_AGENTS_IN_SHORTCUT
    ax.axhline(y=shortcut_capacity, color='#d62728', linestyle='--', label=f'Capacidad ({shortcut_capacity})')
    ax.axhline(y=optimal_agents, color='#2ca02c', linestyle='--', label=f'Óptimo ({int(optimal_agents)})')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.set_title("Autos en el Atajo", fontsize=14, pad=15)
    ax.set_xlabel("Ronda", fontsize=11)
    ax.set_ylabel("Cantidad de Autos", fontsize=11)

    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
        
    return fig

def draw_cars_in_shortcut_per_type_graphic(results):
    all_snapshots = []
    for i, iteration in enumerate(results):
        agentes = iteration["agents"] 

        for a in agentes:
            for s in a.snapshots:
                s['agent_type'] = a.type
                s['iteration'] = i
                all_snapshots.append(s)

            
    df_snap = pd.DataFrame(all_snapshots)

    print(df_snap)


    df_snap['shortcut_choosen'] = (df_snap['decision'] == globals.SHORTCUT_KEY).astype(int)

    count_per_round = df_snap.groupby(['iteration', 'round', 'agent_type'])['shortcut_choosen'].sum().reset_index()

    stats = count_per_round.groupby(['round', 'agent_type'])['shortcut_choosen'].agg(['mean', 'std']).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    
    tipos_agentes = stats['agent_type'].unique()
    colores = ['#1f77b4', '#ff7f0e']

    for idx, tipo in enumerate(tipos_agentes):
        df_tipo = stats[stats['agent_type'] == tipo]
        color = colores[idx % len(colores)]
        
        ax.plot(df_tipo['round'], df_tipo['mean'], label=f'{tipo}', color=color, linewidth=1.5)
        
        ax.fill_between(df_tipo['round'], 
                        df_tipo['mean'] - df_tipo['std'], 
                        df_tipo['mean'] + df_tipo['std'], 
                        color=color, alpha=0.15)

   
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    plt.xticks(rotation=0)
    
    ax.set_title("Autos en el Atajo por Tipo de Agente")
    ax.set_ylabel("Cantidad de Autos")
    ax.set_xlabel("Ronda")
    ax.legend(loc='upper right')

    return fig


def draw_costs_graphic(results):   
    all_histories = []
    all_snapshots = []

    for i, run in enumerate(results):
        df_temp = pd.DataFrame(run["history"])
        df_temp['iteration'] = i 
        all_histories.append(df_temp)

        for a in run["agents"]:
            for s in a.snapshots:
                s['agent_type'] = a.type
                s['iteration'] = i
                all_snapshots.append(s)
        
    df_hist = pd.concat(all_histories, ignore_index=True)
    
    stats_costo_real = df_hist.groupby('round')['real_shortcut_cost'].agg(['mean', 'std']).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))

    df_snap = pd.DataFrame(all_snapshots)
    mean_expected_cost = df_snap.groupby(['round', 'agent_type'])['expected_cost_shortcut'].mean().unstack()
    std_expected_cost = df_snap.groupby(['round', 'agent_type'])['expected_cost_shortcut'].std().unstack()

    for col in mean_expected_cost.columns:
        ax.plot(mean_expected_cost.index, mean_expected_cost[col], 
                 label=f"Costo atajo según {col}", linewidth=1.5)
        ax.fill_between(
            mean_expected_cost.index,
            mean_expected_cost[col] - std_expected_cost[col],
            mean_expected_cost[col] + std_expected_cost[col],
            alpha=0.4
        )

    ax.plot(stats_costo_real['round'], stats_costo_real['mean'], 
             label="Costo real atajo", color='#707070', linewidth=2)
             
    ax.fill_between(stats_costo_real['round'], 
                     stats_costo_real['mean'] - stats_costo_real['std'], 
                     stats_costo_real['mean'] + stats_costo_real['std'], 
                     color='#707070', alpha=0.15) 
    ax.axhline(y=globals.SAFE_ROAD_COST, color='#2ca02c', linestyle='--', label="Costo Camino Seguro")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title("Variación de Costos")
    ax.set_xlabel("Ronda")
    ax.set_ylabel("Costo")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.legend(loc='upper right')

    return fig

def draw_mean_system_cost_graphic(results):
    safe_cost = globals.SAFE_ROAD_COST
    all_histories = []

    # 1. Extract and calculate the system cost for each iteration
    for i, run in enumerate(results):
        df_temp = pd.DataFrame(run["history"])
        df_temp['iteration'] = i
        
        # Obtenemos la cantidad de agentes de esta corrida para la fórmula
        # Usamos .get() con ambos nombres posibles por si usaste 'agent' o 'agents'
        total_agents = len(run.get("agents", run.get("agent", [])))
        
        # Calculamos el costo del sistema para esta iteración específica
        df_temp['system_cost'] = (
            (df_temp['cars_in_shortcut'] * df_temp['real_shortcut_cost']) + 
            ((total_agents - df_temp['cars_in_shortcut']) * safe_cost)
        ) / total_agents
        
        all_histories.append(df_temp)
        
    df_hist = pd.concat(all_histories, ignore_index=True)

    # 2. Group by round and calculate mean and std
    stats_system_cost = df_hist.groupby('round')['system_cost'].agg(['mean', 'std']).reset_index()

    # 3. Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot the mean line
    ax.plot(stats_system_cost['round'], stats_system_cost['mean'], 
            label='Mean System Cost', color='#1f77b4', linewidth=2)

    # Add the shaded area for variance
    ax.fill_between(stats_system_cost['round'], 
                    stats_system_cost['mean'] - stats_system_cost['std'], 
                    stats_system_cost['mean'] + stats_system_cost['std'], 
                    color='#1f77b4', alpha=0.15)

    # Add reference lines
    ax.axhline(y=safe_cost, color='#2ca02c', linestyle='--', label=f'Safe Path Cost ({safe_cost})')
    ax.axhline(y=globals.OPTIMAL_COST, color='#d62728', linestyle='--', label=f'Optimal Cost ({globals.OPTIMAL_COST:.2f})')

    # Visual cleanup & formatting in English
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title("Average Travel Cost", fontsize=14, pad=15)
    ax.set_ylabel("Minutes", fontsize=11)
    ax.set_xlabel("Round", fontsize=11)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.legend(loc='upper right')

    return fig

def draw_graphics(results):
    #st.pyplot(draw_cars_in_shortcut_graph(results))

    #st.pyplot(draw_cars_in_shortcut_per_type_graphic(results))

    # st.pyplot(draw_costs_graphic(results))

    st.pyplot(draw_mean_system_cost_graphic(results))

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
        

        # Plot 2: Expected Costs vs Real Costs
        fig, ax2 = plt.subplots(figsize=(10, 5))
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

    
    


