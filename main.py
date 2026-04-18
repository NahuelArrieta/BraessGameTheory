import globals
from agents import *


## Agent creation
agents = []

for agent_type in globals.AGENT_COUNT_MAP:
    for i in range(globals.AGENT_COUNT_MAP[agent_type]):
        if agent_type == globals.ADVERSE_AGENT_KEY:
            agent = AdverseAgent(id=i)
        elif agent_type == globals.NEUTRAL_AGENT_KEY:
            agent = NeutralAgent(id=i)

        agents.append(agent)

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


## Print final 5 snapshots of the first agent
for snapshot in agents[0].snapshots[-5:]:
    print(snapshot)

# Print history
for entry in history[-5:]:
    print(f"Ronda {entry['round']+1}: {entry['cars_in_shortcut']} agentes eligieron el atajo, costo real del atajo: {entry['real_shortcut_cost']:.2f}")