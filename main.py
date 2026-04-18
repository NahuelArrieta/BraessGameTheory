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

for round in range(globals.NUMBER_OF_ROUNDS):
    decisions = [a.decide() for a in agents]
    cars_in_shortcut = decisions.count(globals.SHORTCUT_KEY)
    
    # Dynamic cost
    shortcut_saturated = 1 if cars_in_shortcut > globals.SHORTCUT_THRESHOLD else 0
    if shortcut_saturated:
        real_shortcut_cost = globals.FREE_SHORTCUT_COST + globals.CONGESTION_FACTOR * (cars_in_shortcut - globals.SHORTCUT_THRESHOLD)
    else:
        real_shortcut_cost = globals.FREE_SHORTCUT_COST
    
    # Feedback
    for a in agents: a.update_belief(shortcut_saturated)

    print(f"Ronda {round+1}: {cars_in_shortcut} agentes eligieron el atajo, costo real del atajo: {real_shortcut_cost:.2f}")

