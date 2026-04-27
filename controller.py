import globals
from agents import *


def run_simulation():
    ## Agent creation
    agents = []

    for agent_type in globals.AGENT_COUNT_MAP:
        for i in range(globals.AGENT_COUNT_MAP[agent_type]):
            if agent_type == globals.ADVERSE_AGENT_KEY:
                agent = AdverseAgent(id=i)
            elif agent_type == globals.NEUTRAL_AGENT_KEY:
                agent = NeutralAgent(id=i)

            agents.append(agent)

    ## Calculate expected cost
    globals.SATURATED_SHORTCUT_COST = globals.SAFE_ROAD_COST * 1.05 

    ## Calculate optimal Number of Agents in Shortcut TODO
    optimal_n = (globals.SAFE_ROAD_COST + globals.CONGESTION_FACTOR * globals.SHORTCUT_THRESHOLD - globals.FREE_SHORTCUT_COST) / (2 * globals.CONGESTION_FACTOR)
    optimal_n = max(globals.SHORTCUT_THRESHOLD, min(optimal_n, len(agents)))  # Ensure it's between 0 and total agents
    globals.OPTIMAL_AGENTS_IN_SHORTCUT = optimal_n

    optimal_shortcut_cost = globals.FREE_SHORTCUT_COST + globals.CONGESTION_FACTOR * max(0, optimal_n - globals.SHORTCUT_THRESHOLD)
    optimal_cost = (optimal_n * optimal_shortcut_cost + (len(agents) - optimal_n) * globals.SAFE_ROAD_COST) 
    optimal_average_cost = optimal_cost / len(agents)  
    globals.OPTIMAL_COST = optimal_average_cost


    ## Simulation loop
    shortcut_saturated = 0
    history = []
    for round in range(globals.NUMBER_OF_ROUNDS):
        decisions = [a.iterate(round, shortcut_saturated) for a in agents]
        cars_in_shortcut = decisions.count(globals.SHORTCUT_KEY)
        
        # Calculate real shortcut cost based on saturation
        shortcut_saturated = 1 if cars_in_shortcut > globals.SHORTCUT_THRESHOLD else 0
        if shortcut_saturated:
            real_shortcut_cost = globals.FREE_SHORTCUT_COST + globals.CONGESTION_FACTOR * (cars_in_shortcut - globals.SHORTCUT_THRESHOLD)
        else:
            real_shortcut_cost = globals.FREE_SHORTCUT_COST
        
        ## Store history for analysis
        history.append({
            "round": round,
            "cars_in_shortcut": cars_in_shortcut,
            "shortcut_saturated": shortcut_saturated,
            "real_shortcut_cost": real_shortcut_cost
        })

        for a in agents:
            a.update_belief(shortcut_saturated)
            if shortcut_saturated:
                a.update_expected_saturated_shortcut_cost(real_shortcut_cost)


    ## Return data
    return {
        "agents": agents,
        "history": history
    }