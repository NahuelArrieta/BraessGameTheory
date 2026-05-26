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
    ax.axhline(y=optimal_agents, color='#2ca02c', label=f'Óptimo ({int(optimal_agents)})')
    ax.axhline(y=shortcut_capacity, color='#202020', linestyle='--', label=f'Capacidad ({shortcut_capacity})')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.set_title("Autos en el Atajo", fontsize=14, pad=15)
    ax.set_xlabel("Ronda", fontsize=11)
    ax.set_ylabel("Cantidad de Autos", fontsize=11)

    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
        
    fig.tight_layout()
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

    fig.tight_layout()
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
    ax.axhline(y=globals.SAFE_ROAD_COST, color='#d62728', label="Costo ruta segura")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title("Variación de Costos")
    ax.set_xlabel("Ronda")
    ax.set_ylabel("Costo")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.legend(loc='upper right')

    fig.tight_layout()
    return fig

def draw_mean_system_cost_graphic(results):
    safe_cost = globals.SAFE_ROAD_COST
    all_histories = []

    for i, run in enumerate(results):
        df_temp = pd.DataFrame(run["history"])
        df_temp['iteration'] = i
        
        total_agents = len(run.get("agents", run.get("agent", [])))
        
        df_temp['system_cost'] = (
            (df_temp['cars_in_shortcut'] * df_temp['real_shortcut_cost']) + 
            ((total_agents - df_temp['cars_in_shortcut']) * safe_cost)
        ) / total_agents
        
        all_histories.append(df_temp)
        
    df_hist = pd.concat(all_histories, ignore_index=True)

    stats_system_cost = df_hist.groupby('round')['system_cost'].agg(['mean', 'std']).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(stats_system_cost['round'], stats_system_cost['mean'], 
            label='Costo promedio', color='#1f77b4', linewidth=2)

    ax.fill_between(stats_system_cost['round'], 
                    stats_system_cost['mean'] - stats_system_cost['std'], 
                    stats_system_cost['mean'] + stats_system_cost['std'], 
                    color='#1f77b4', alpha=0.15)

    ax.axhline(y=safe_cost, color='#d62728', label=f'Costo ruta segura ({safe_cost})') 
    ax.axhline(y=globals.OPTIMAL_COST, color='#2ca02c', label=f'Costo óptimo ({globals.OPTIMAL_COST:.2f})')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title("Costo Promedio de Viaje", fontsize=14, pad=15)
    ax.set_ylabel("Minutos", fontsize=11)
    ax.set_xlabel("Ronda", fontsize=11)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.legend(loc='upper right')

    fig.tight_layout()
    return fig

def draw_beliefs_evolution_graphic(results):
    all_histories = []
    all_snapshots = []

    for i, run in enumerate(results):
        df_temp = pd.DataFrame(run["history"])
        df_temp['iteration'] = i
        all_histories.append(df_temp)

        for a in run.get("agents", run.get("agent", [])):
            for s in a.snapshots:
                s['agent_type'] = a.type
                s['iteration'] = i
                all_snapshots.append(s)

    df_snap = pd.DataFrame(all_snapshots)
    stats_beliefs = df_snap.groupby(['round', 'agent_type'])['belief'].agg(['mean', 'std']).reset_index()

    df_hist = pd.concat(all_histories, ignore_index=True)
    saturation_prob = df_hist.groupby('round')['shortcut_saturated'].mean()

    fig, ax = plt.subplots(figsize=(10, 5))

    agent_types = stats_beliefs['agent_type'].unique()
    colors = ['#1f77b4', '#ff7f0e']

    for idx, agent_type in enumerate(agent_types):
        color = colors[idx % len(colors)]
        df_type = stats_beliefs[stats_beliefs['agent_type'] == agent_type]

        ax.plot(df_type['round'], df_type['mean'], label=f'Creencia {agent_type}', color=color, linewidth=1.5)

        ax.fill_between(df_type['round'],
                        df_type['mean'] - df_type['std'],
                        df_type['mean'] + df_type['std'],
                        color=color, alpha=0.30)

    labeled_saturation = False
    for round_num, prob in saturation_prob.items():
        if prob > 0: 
            label_text = "Atajo Saturado" if not labeled_saturation else ""
            ax.axvspan(round_num - 0.5, round_num + 0.5, color='#000000', alpha=prob * 0.3, lw=0, label=label_text)
            labeled_saturation = True

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title("Evolución de Creencias", fontsize=14, pad=15)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Ronda", fontsize=11)
    ax.set_ylabel("Creencia de Saturación", fontsize=11)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.legend(loc='upper right')

    fig.tight_layout()
    return fig

def draw_graphics(results):
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.pyplot(draw_cars_in_shortcut_graph(results), use_container_width=True)
        st.pyplot(draw_mean_system_cost_graphic(results), use_container_width=True)

    with col2:
        st.pyplot(draw_cars_in_shortcut_per_type_graphic(results), use_container_width=True)
        st.pyplot(draw_beliefs_evolution_graphic(results), use_container_width=True)

    with col3:
        st.pyplot(draw_costs_graphic(results), use_container_width=True)
        with st.container(border=True):
            ## Write parameters
            st.header("  Parametros")
            st.markdown(f"""
        * **N° agentes adversos:** `{globals.AGENT_COUNT_MAP[globals.ADVERSE_AGENT_KEY]}`
        * **N° agentes neutrales:** `{globals.AGENT_COUNT_MAP[globals.NEUTRAL_AGENT_KEY]}`
        * **Costo ruta segura:** `{globals.SAFE_ROAD_COST}`
        * **Costo atajo libre:** `{globals.FREE_SHORTCUT_COST}`
        * **Factor de congestión:** `{globals.CONGESTION_FACTOR}`
        * **Capacidad atajo (K):** `{globals.SHORTCUT_THRESHOLD}`
        """)



    