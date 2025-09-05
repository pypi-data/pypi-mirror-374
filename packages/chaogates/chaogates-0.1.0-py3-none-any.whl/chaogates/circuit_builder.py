import numpy as np
from typing import Dict, Any, Callable, List

class CircuitBuilder:
    """
    A high-level interface for building custom logic circuits using chaotic gates.
    """

    def __init__(self, gates: Any):
        """
        Initialize with a LogicGates object.

        Args:
            gates: Instance of LogicGates (from logic_gates1.py).
        """
        self.gates = gates
        self.steps = {}

    def add_gate(self, name: str, gate_func: Callable, inputs: Dict[tuple, Any], **kwargs):
        """
        Add a gate to the circuit.

        Args:
            name (str): Unique name for this gate.
            gate_func (Callable): Gate function (e.g., gates.logistic_and).
            inputs (dict): Mapping of inputs to initial conditions.
            kwargs: Extra parameters (thresholds, bounds, etc.).
        """
        outputs = self.gates.evaluate_gate(inputs, gate_func, **kwargs)
        self.steps[name] = outputs
        return outputs

    def add_compound(self, name: str, compound_func: Callable, inputs: Dict[tuple, Any], **kwargs):
        """
        Add a compound circuit (half-adder, full-adder, etc.).

        Args:
            name (str): Unique name for this circuit.
            compound_func (Callable): Compound function (e.g., gates.half_adder).
            inputs (dict): Mapping of inputs to initial conditions.
            kwargs: Extra parameters.
        """
        outputs = compound_func(inputs, **kwargs)
        self.steps[name] = outputs
        return outputs

    def get_outputs(self, name: str):
        """
        Retrieve outputs of a circuit component by name.

        Args:
            name (str): Step name.

        Returns:
            dict: Outputs of the gate or circuit.
        """
        return self.steps.get(name, None)

    def summary(self):
        """
        Print all circuit components added so far.
        """
        print("Circuit Summary:")
        for name, outputs in self.steps.items():
            print(f"{name}: {outputs}")




if __name__ == "__main__":
    from chaotic_systems import LogisticMap
    from logic_gates1 import LogicGates

    # Init system and gates
    system = LogisticMap()
    gates = LogicGates(system)
    builder = CircuitBuilder(gates)

    # Define basic inputs
    x0_map = {(0, 0): 0.1, (0, 1): 0.3, (1, 0): 0.7, (1, 1): 0.9}

    # Step 1: Add AND gate
    and_out = builder.add_gate("AND1", gates.logistic_and, x0_map)

    # Step 2: Add XOR gate
    xor_out = builder.add_gate("XOR1", gates.logistic_xor, x0_map)

    # Step 3: Build half-adder (compound circuit)
    half_adder_out = builder.add_compound("HalfAdder1", gates.half_adder, x0_map)

    # Show everything
    builder.summary()

    print("\nRetrieve specific outputs:")
    print("AND1 ->", builder.get_outputs("AND1"))
    print("XOR1 ->", builder.get_outputs("XOR1"))
    print("HalfAdder1 ->", builder.get_outputs("HalfAdder1"))
