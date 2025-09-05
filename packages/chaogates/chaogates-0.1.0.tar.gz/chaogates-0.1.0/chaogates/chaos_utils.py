import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

class ChaosUtils:
    """High-level utilities for chaotic logic gates and custom circuits."""

    def __init__(self):
        pass

    # -------------------- Truth Table Comparison --------------------
    def compare_truth_table(self, outputs, truth_table):
        """Check if computed outputs match the target truth table."""
        return all(outputs.get(key) == value for key, value in truth_table.items())

    # -------------------- Gate Search (Logistic) --------------------
    def logistic_search(self, system, inputs, gate_func, trials=500,
                        r_range=(3.5, 3.99), threshold_range=(0.2, 0.8),
                        low_range=(0.2, 0.5), high_range=(0.5, 0.8)):
        """Randomized parameter search for LogisticMap gates."""
        successful_params = []

        # Reference truth tables
        truth_tables = {
            "logistic_and":  {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
            "logistic_xor":  {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0},
            "logistic_or":   {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 1},
            "logistic_nand": {(0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): 0},
            "logistic_nor":  {(0, 0): 1, (0, 1): 0, (1, 0): 0, (1, 1): 0},
        }

        for _ in range(trials):
            r = np.random.uniform(*r_range)
            system.r = r
            outputs = {}

            if gate_func.__name__ == "logistic_xor":
                # XOR uses low/high bands instead of single threshold
                low = np.random.uniform(*low_range)
                high = np.random.uniform(*high_range)
                for k, v in inputs.items():
                    traj = system.simulate(v)
                    outputs[k] = gate_func(traj, low=low, high=high)
                if self.compare_truth_table(outputs, truth_tables["logistic_xor"]):
                    successful_params.append((r, low, high))
            else:
                threshold = np.random.uniform(*threshold_range)
                for k, v in inputs.items():
                    traj = system.simulate(v)
                    outputs[k] = gate_func(traj, threshold=threshold)
                real_table = truth_tables.get(gate_func.__name__)
                if real_table and self.compare_truth_table(outputs, real_table):
                    successful_params.append((r, threshold))

        # Compute averages
        if gate_func.__name__ == "logistic_xor" and successful_params:
            return successful_params, (
                np.mean([p[0] for p in successful_params]),
                np.mean([p[1] for p in successful_params]),
                np.mean([p[2] for p in successful_params]),
            )
        elif successful_params:
            return successful_params, (
                np.mean([p[0] for p in successful_params]),
                np.mean([p[1] for p in successful_params]),
            )
        else:
            return [], (0, 0)

    # -------------------- Gate Search (Lorenz) --------------------
    def lorenz_search(self, system, inputs, gate_func, trials=500,
                      sigma_range=(8, 12), rho_range=(20, 35),
                      beta_range=(2, 3), window_range=(100, 1000),
                      low_range=(0.2, 0.5), high_range=(0.5, 0.8)):
        """Randomized parameter search for Lorenz gates."""
        successful_params = []

        truth_tables = {
            "logistic_and":  {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
            "logistic_xor":  {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0},
        }

        for _ in range(trials):
            system.sigma = np.random.uniform(*sigma_range)
            system.rho   = np.random.uniform(*rho_range)
            system.beta  = np.random.uniform(*beta_range)
            window_size  = np.random.randint(*window_range)

            outputs = {}
            if gate_func.__name__ == "logistic_xor":
                low = np.random.uniform(*low_range)
                high = np.random.uniform(*high_range)
                for (a, b), initial in inputs.items():
                    t, y = system.simulate(initial)
                    avg_x = np.mean(y[0, -window_size:])
                    outputs[(a, b)] = gate_func(np.array([avg_x]), low=low, high=high)
                if self.compare_truth_table(outputs, truth_tables["logistic_xor"]):
                    successful_params.append((system.sigma, system.rho, system.beta, window_size, low, high))
            else:
                threshold = 0.75
                for (a, b), initial in inputs.items():
                    t, y = system.simulate(initial)
                    avg_x = np.mean(y[0, -window_size:])
                    outputs[(a, b)] = gate_func(np.array([avg_x]), threshold=threshold)
                real_table = truth_tables.get(gate_func.__name__)
                if real_table and self.compare_truth_table(outputs, real_table):
                    successful_params.append((system.sigma, system.rho, system.beta, window_size))

        if gate_func.__name__ == "logistic_xor" and successful_params:
            return successful_params, (
                np.mean([p[0] for p in successful_params]),
                np.mean([p[1] for p in successful_params]),
                np.mean([p[2] for p in successful_params]),
                np.mean([p[3] for p in successful_params]),
                np.mean([p[4] for p in successful_params]),
                np.mean([p[5] for p in successful_params]),
            )
        elif successful_params:
            return successful_params, (
                np.mean([p[0] for p in successful_params]),
                np.mean([p[1] for p in successful_params]),
                np.mean([p[2] for p in successful_params]),
                np.mean([p[3] for p in successful_params]),
            )
        else:
            return [], (0, 0, 0, 0)

    # -------------------- Circuit Evaluation --------------------
    def evaluate_circuit(self, circuit_func, inputs, **kwargs):
        """
        Evaluate a pre-built or custom circuit.

        Args:
            circuit_func: Callable from LogicGates or CircuitBuilder (e.g., half_adder).
            inputs: Input mapping (dict).
            kwargs: Thresholds or search params.

        Returns:
            dict: Circuit outputs (truth tables or nested dicts).
        """
        return circuit_func(inputs, **kwargs)

    # -------------------- Save & Plot --------------------
    def save_results(self, values, headers, filename):
        os.makedirs("results/tables", exist_ok=True)
        df = pd.DataFrame(values, columns=headers)
        df.to_csv(f"results/tables/{filename}.csv", index=False)

    def plot_histogram(self, values, column_index, title, filename, headers=None):
        os.makedirs("results/figures", exist_ok=True)
        data = [v[column_index] for v in values] if values else []
        plt.figure()
        plt.hist(data, bins=10, color="blue")
        plt.title(title)
        if headers:
            plt.xlabel(headers[column_index])
        plt.ylabel("Frequency")
        plt.savefig(f"results/figures/{filename}.png")
        plt.close()


if __name__ == "__main__":
    from chaotic_systems import LogisticMap, LorenzSystem
    from logic_gates1 import LogicGates

    # Example usage
    logistic = LogisticMap()
    lorenz   = LorenzSystem()
    gates    = LogicGates(logistic)
    utils    = ChaosUtils()

    x0_map_logistic = {(0,0): 0.1, (0,1): 0.3, (1,0): 0.7, (1,1): 0.9}
    x0_map_lorenz   = {(0,0): [1,1,1], (0,1): [2,2,2], (1,0): [3,3,3], (1,1): [4,4,4]}

    # Search for Logistic XOR
    params, averages = utils.logistic_search(logistic, x0_map_logistic, gates.logistic_xor)
    print("Logistic XOR Search:", len(params), "successes, Avg:", averages)

    # Search for Lorenz AND
    params, averages = utils.lorenz_search(lorenz, x0_map_lorenz, gates.logistic_and)
    print("Lorenz AND Search:", len(params), "successes, Avg:", averages)

    # Evaluate a compound circuit directly
    half_adder_result = utils.evaluate_circuit(gates.half_adder, x0_map_logistic)
    print("Half Adder (Logistic):", half_adder_result)
