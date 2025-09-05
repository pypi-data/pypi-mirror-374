import numpy as np
from typing import Dict, Callable, Tuple, Any

class LogicGates:
    """A class to implement Boolean gates and compound circuits using chaotic systems."""

    def __init__(self, system: Any):
        """Initialize with a chaotic system object (LogisticMap or LorenzSystem)."""
        self.system = system

    def logistic_and(self, traj: np.ndarray, threshold: float = 0.75, **kwargs) -> int:
        """Evaluate AND gate using average of last 50 values."""
        avg = np.mean(traj[-50:])
        return 1 if avg > threshold else 0

    def logistic_or(self, traj: np.ndarray, threshold: float = 0.5, **kwargs) -> int:
        """Evaluate OR gate using max of last 50 values."""
        max_val = np.max(traj[-50:])
        return 1 if max_val > threshold else 0

    def logistic_xor(self, traj: np.ndarray, threshold: float = None,
                     low: float = 0.3, high: float = 0.7, **kwargs) -> int:
        """Evaluate XOR gate using average of last 50 values."""
        avg = np.mean(traj[-50:])
        if threshold is not None:
            # Interpret threshold as a center, +/- 0.2 band
            low, high = threshold - 0.2, threshold + 0.2
        return 1 if low < avg < high else 0

    def logistic_nand(self, traj: np.ndarray, threshold: float = 0.75, **kwargs) -> int:
        """Evaluate NAND gate, opposite of AND."""
        return 1 - self.logistic_and(traj, threshold=threshold)

    def logistic_nor(self, traj: np.ndarray, threshold: float = 0.5, **kwargs) -> int:
        """Evaluate NOR gate, opposite of OR."""
        return 1 - self.logistic_or(traj, threshold=threshold)

    def evaluate_gate(self, inputs: Dict[Tuple[int, ...], Any], gate_func: Callable, **kwargs) -> Dict[Tuple[int, ...], int]:
        """Evaluate a chaotic gate for given inputs and system."""
        outputs = {}
        for key, initial in inputs.items():
            if hasattr(self.system, "simulate"):
                traj = self.system.simulate(initial)
                # For Lorenz, use x-component only
                if traj is tuple:  # Lorenz returns (t, y)
                    t, y = traj
                    traj = y[0]
                outputs[key] = gate_func(traj, **kwargs)
        return outputs

    def half_adder(self, inputs: Dict[Tuple[int, int], Any], **kwargs) -> Dict[str, Dict[Tuple[int, int], int]]:
        """Half adder: XOR for sum, AND for carry."""
        sum_table = self.evaluate_gate(inputs, self.logistic_xor, **kwargs)
        carry_table = self.evaluate_gate(inputs, self.logistic_and, **kwargs)
        return {"Sum": sum_table, "Carry": carry_table}

    def full_adder(self, inputs: Dict[Tuple[int, int, int], Any], **kwargs) -> Dict[str, Dict[Tuple[int, int, int], int]]:
        """Full adder using two half-adders and OR for carry-out."""
        inputs_ab = {(k[0], k[1]): v for k, v in inputs.items()}
        inputs_bc = {(k[1], k[2]): v for k, v in inputs.items()}

        half1 = self.half_adder(inputs_ab, **kwargs)
        half2 = self.half_adder(inputs_bc, **kwargs)

        carry_in = {}
        for k in inputs:
            a, b, c = k
            carry_in[k] = half1["Carry"].get((a, b), 0) ^ half2["Carry"].get((b, c), 0)

        sum_table = {k: (half1["Sum"].get((k[0], k[1]), 0) ^ carry_in.get(k, 0)) for k in inputs}
        carry_table = {k: (half1["Carry"].get((k[0], k[1]), 0) | half2["Carry"].get((k[1], k[2]), 0)) for k in inputs}
        return {"Sum": sum_table, "Carry": carry_table}

    def sr_latch(self, s_input: Any, r_input: Any, **kwargs) -> Dict[str, int]:
        """SR latch using two NOR gates with feedback."""
        q = self.system.simulate(s_input)
        q_bar = self.system.simulate(r_input)
        q_new = self.logistic_nor(q_bar, **kwargs)
        q_bar_new = self.logistic_nor(q, **kwargs)
        return {"Q": q_new, "Q_bar": q_bar_new}


if __name__ == "__main__":
    from chaotic_systems import LogisticMap
    x0_map = {(0, 0): 0.1, (0, 1): 0.3, (1, 0): 0.7, (1, 1): 0.9}
    system = LogisticMap()
    gates = LogicGates(system)

    print("AND:", gates.evaluate_gate(x0_map, gates.logistic_and))
    print("XOR:", gates.evaluate_gate(x0_map, gates.logistic_xor))
    print("Half Adder:", gates.half_adder(x0_map))
