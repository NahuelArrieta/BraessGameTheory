import globals
import random
import math

random.seed(42)  # For reproducibility

class Agente:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        learning_rate_range = globals.AGENT_LEARNING_RATE_RANGE[type]
        self.learning_rate = random.uniform(learning_rate_range[0], learning_rate_range[1])
        self.p = 0.5  + random.uniform(-0.05, 0.05)
        self.snapshots = []  
        self.expected_saturated_shortcut_cost = globals.SATURATED_SHORTCUT_COST

    def update_belief(self, shortcut_saturated):
        self.p = (1 - self.learning_rate) * self.p + self.learning_rate * shortcut_saturated

    def update_expected_saturated_shortcut_cost(self, real_shortcut_cost):
        self.expected_saturated_shortcut_cost = (1 - self.learning_rate) * self.expected_saturated_shortcut_cost + self.learning_rate * real_shortcut_cost

    def calculate_expected_cost_shortcut(self):
        raise NotImplementedError("Subclasses must implement this method")

    def calculate_expected_cost_safe(self):
        return globals.SAFE_ROAD_COST

    def decide(self, expected_cost_shortcut, expected_cost_safe):
        diff = expected_cost_shortcut - expected_cost_safe
        
        try:
            prob_shortcut = 1 / (1 + math.exp(globals.BETA * diff))
        except OverflowError:
            prob_shortcut = 1.0 if diff < 0 else 0.0

        if random.random() < prob_shortcut:
            return globals.SHORTCUT_KEY
        else:
            return globals.SAFE_ROAD_KEY

    def iterate(self, round, shortcut_saturated):
        self.update_belief(shortcut_saturated)

        expected_cost_shortcut = self.calculate_expected_cost_shortcut() * random.uniform(0.9, 1.1)
        expected_cost_safe = self.calculate_expected_cost_safe()

        decision = self.decide(expected_cost_shortcut, expected_cost_safe)
        self.snapshots.append({
            "round": round,
            "belief": self.p,
            "expected_cost_shortcut": expected_cost_shortcut,
            "expected_cost_safe": expected_cost_safe,
            "decision": decision
        })

        return decision
        
        


class AdverseAgent(Agente):
    def __init__(self, id):
        super().__init__(id, type=globals.ADVERSE_AGENT_KEY)

    def calculate_expected_cost_shortcut(self):
        expected_cost = (self.p * (self.expected_saturated_shortcut_cost ** 2)) + ((1 - self.p) * (globals.FREE_SHORTCUT_COST ** 2))
        return expected_cost ** 0.5  # Return the square root to get back to original scale

class NeutralAgent(Agente):
    def __init__(self, id):
        super().__init__(id, type=globals.NEUTRAL_AGENT_KEY)

    def calculate_expected_cost_shortcut(self):
        expected_cost = (self.p * self.expected_saturated_shortcut_cost) + ((1 - self.p) * globals.FREE_SHORTCUT_COST)
        return expected_cost