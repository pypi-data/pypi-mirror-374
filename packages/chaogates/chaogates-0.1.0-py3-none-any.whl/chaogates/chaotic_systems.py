import numpy as np
from scipy.integrate import solve_ivp

class LogisticMap:
    """A class to simulate the logistic map.

    Attributes:
        r (float): Growth rate parameter.
        n (int): Number of iterations.

    Methods:
        simulate(x0): Returns the trajectory as a NumPy array.
    """

    def __init__(self, r=3.9, n=200):
        self.r = r
        self.n = n

    def simulate(self, x0):
        """Simulate the logistic map for given initial condition.

        Args:
            x0 (float): Initial value.

        Returns:
            numpy.ndarray: Trajectory of the logistic map.
        """
        traj = [x0]
        x = x0
        for _ in range(self.n):
            x = self.r * x * (1 - x)
            traj.append(x)
        return np.array(traj)


class LorenzSystem:
    """A class to simulate the Lorenz system.

    Attributes:
        sigma (float): Prandtl number.
        rho (float): Rayleigh number.
        beta (float): Aspect ratio.
        t_span (tuple): Time span for integration.
        dt (float): Time step for evaluation.

    Methods:
        equations(t, state): Returns the derivatives [dx, dy, dz].
        simulate(initial_state): Integrates the system using solve_ivp.
    """

    def __init__(self, sigma=10, rho=28, beta=8/3, t_span=(0, 30), dt=0.01):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.t_span = t_span
        self.t_eval = np.arange(t_span[0], t_span[1] + dt, dt)

    def equations(self, t, state):
        """Compute the derivatives of the Lorenz system.

        Args:
            t (float): Time.
            state (list): Current state [x, y, z].

        Returns:
            list: Derivatives [dx/dt, dy/dt, dz/dt].
        """
        x, y, z = state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return [dx, dy, dz]

    def simulate(self, initial_state):
        """Simulate the Lorenz system for given initial conditions.

        Args:
            initial_state (list): Initial state [x0, y0, z0].

        Returns:
            tuple: (t, y) where t is time vector and y is state trajectory.
        """
        sol = solve_ivp(self.equations, self.t_span, initial_state, t_eval=self.t_eval)
        return sol.t, sol.y


if __name__ == "__main__":
    # Lightweight testing
    logistic = LogisticMap()
    traj = logistic.simulate(0.5)
    print("Logistic Map last 5 values:", traj[-5:])

    lorenz = LorenzSystem()
    t, y = lorenz.simulate([1.0, 1.0, 1.0])
    print("Lorenz System last state:", y[:, -1])


# Usage Example:
# from chaotic_systems import LogisticMap, LorenzSystem
#
# # Logistic Map example
# logistic = LogisticMap(r=3.7, n=100)
# trajectory = logistic.simulate(0.4)
# print(trajectory)
#
# # Lorenz System example
# lorenz = LorenzSystem(rho=25, t_span=(0, 20))
# t, states = lorenz.simulate([1.0, 1.0, 1.0])
# print(f"Time: {t[-1]}, Final state: {states[:, -1]}")