import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

class ChaosUtils:
    """Helper methods for tuning chaotic logic gates with randomized search."""

    def __init__(self):
        pass

    def compare_truth_table(self, outputs, truth_table):
        return all(outputs.get(key) == value for key, value in truth_table.items())

    def logistic_search(self, system, inputs, gate_func, trials=500,
                        r_range=(3.5, 3.99), threshold_range=(0.2, 0.8)):
        successful_params = []

        # Real truth tables
        truth_tables = {
            "logistic_and": {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
            "logistic_xor": {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0},
            "logistic_or":  {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 1},
            "logistic_nand":{(0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): 0},
            "logistic_nor": {(0, 0): 1, (0, 1): 0, (1, 0): 0, (1, 1): 0},
        }

        for _ in range(trials):
            r = np.random.uniform(*r_range)
            system.r = r
            threshold = np.random.uniform(*threshold_range)

            outputs = {}
            for k, v in inputs.items():
                traj = system.simulate(v)

                # Special handling for XOR: randomize low/high instead of threshold
                if gate_func.__name__ == "logistic_xor":
                    low = np.random.uniform(0.2, 0.5)
                    high = np.random.uniform(0.5, 0.8)
                    outputs[k] = gate_func(traj, low=low, high=high)
                else:
                    outputs[k] = gate_func(traj, threshold=threshold)

            real_table = truth_tables.get(gate_func.__name__)
            if real_table and self.compare_truth_table(outputs, real_table):
                if gate_func.__name__ == "logistic_xor":
                    successful_params.append((r, low, high))
                else:
                    successful_params.append((r, threshold))

        # Compute averages
        if gate_func.__name__ == "logistic_xor" and successful_params:
            avg_r = np.mean([p[0] for p in successful_params])
            avg_low = np.mean([p[1] for p in successful_params])
            avg_high = np.mean([p[2] for p in successful_params])
            return successful_params, (avg_r, avg_low, avg_high)
        else:
            avg_r = np.mean([p[0] for p in successful_params]) if successful_params else 0
            avg_threshold = np.mean([p[1] for p in successful_params]) if successful_params else 0
            return successful_params, (avg_r, avg_threshold)

    def lorenz_search(self, system, inputs, gate_func, trials=500,
                      sigma_range=(8, 12), rho_range=(20, 35),
                      beta_range=(2, 3), window_range=(100, 1000)):
        successful_params = []

        truth_tables = {
            "logistic_and": {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1},
            "logistic_xor": {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0},
            "logistic_or":  {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 1},
        }

        for _ in range(trials):
            system.sigma = np.random.uniform(*sigma_range)
            system.rho = np.random.uniform(*rho_range)
            system.beta = np.random.uniform(*beta_range)
            window_size = np.random.randint(*window_range)

            outputs = {}
            for (a, b), initial in inputs.items():
                t, y = system.simulate(initial)
                avg_x = np.mean(y[0, -window_size:])
                traj = np.array([avg_x])

                # Same XOR handling here
                if gate_func.__name__ == "logistic_xor":
                    low = np.random.uniform(0.2, 0.5)
                    high = np.random.uniform(0.5, 0.8)
                    outputs[(a, b)] = gate_func(traj, low=low, high=high)
                else:
                    outputs[(a, b)] = gate_func(traj, threshold=0.75)

            real_table = truth_tables.get(gate_func.__name__)
            if real_table and self.compare_truth_table(outputs, real_table):
                if gate_func.__name__ == "logistic_xor":
                    successful_params.append((system.sigma, system.rho, system.beta, window_size, low, high))
                else:
                    successful_params.append((system.sigma, system.rho, system.beta, window_size))

        if gate_func.__name__ == "logistic_xor" and successful_params:
            avg_sigma = np.mean([p[0] for p in successful_params])
            avg_rho = np.mean([p[1] for p in successful_params])
            avg_beta = np.mean([p[2] for p in successful_params])
            avg_window = np.mean([p[3] for p in successful_params])
            avg_low = np.mean([p[4] for p in successful_params])
            avg_high = np.mean([p[5] for p in successful_params])
            return successful_params, (avg_sigma, avg_rho, avg_beta, avg_window, avg_low, avg_high)
        else:
            avg_sigma = np.mean([p[0] for p in successful_params]) if successful_params else 0
            avg_rho = np.mean([p[1] for p in successful_params]) if successful_params else 0
            avg_beta = np.mean([p[2] for p in successful_params]) if successful_params else 0
            avg_window = np.mean([p[3] for p in successful_params]) if successful_params else 0
            return successful_params, (avg_sigma, avg_rho, avg_beta, avg_window)

    def save_results(self, values, headers, filename):
        os.makedirs('results/tables', exist_ok=True)
        df = pd.DataFrame(values, columns=headers)
        df.to_csv(f'results/tables/{filename}.csv', index=False)

    def plot_histogram(self, values, column_index, title, filename, headers=None):
        os.makedirs('results/figures', exist_ok=True)
        data = [v[column_index] for v in values] if values else []
        plt.figure()
        plt.hist(data, bins=10, color='blue')
        plt.title(title)
        if headers:
            plt.xlabel(headers[column_index])
        plt.ylabel('Frequency')
        plt.savefig(f'results/figures/{filename}.png')
        plt.close()


if __name__ == "__main__":
    from chaotic_systems import LogisticMap, LorenzSystem
    from logic_gates1 import LogicGates

    x0_map_logistic = {(0, 0): 0.1, (0, 1): 0.3, (1, 0): 0.7, (1, 1): 0.9}
    x0_map_lorenz = {(0, 0): [1.0, 1.0, 1.0], (0, 1): [2.0, 2.0, 2.0],
                     (1, 0): [3.0, 3.0, 3.0], (1, 1): [4.0, 4.0, 4.0]}

    logistic_system = LogisticMap()
    lorenz_system = LorenzSystem()
    gates = LogicGates(logistic_system)
    utils = ChaosUtils()

    # Test Logistic AND & XOR
    for gate in [gates.logistic_and, gates.logistic_xor]:
        params, averages = utils.logistic_search(logistic_system, x0_map_logistic, gate)
        print(f"Logistic {gate.__name__}: {len(params)} successes, Averages: {averages}")

    # Test Lorenz AND & XOR
    for gate in [gates.logistic_and, gates.logistic_xor]:
        params, averages = utils.lorenz_search(lorenz_system, x0_map_lorenz, gate)
        print(f"Lorenz {gate.__name__}: {len(params)} successes, Averages: {averages}")
