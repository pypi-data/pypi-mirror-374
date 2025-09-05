import matplotlib.pyplot as plt
import numpy as np
import os

def plot_logistic_trajectory(traj, threshold=None, title="Logistic Trajectory", filename=None):
    plt.figure()
    plt.plot(range(len(traj)), traj, label="Trajectory")
    if threshold is not None:
        plt.axhline(threshold, color="red", linestyle="--", label="Threshold")
    plt.xlabel("Iteration")
    plt.ylabel("x")
    plt.title(title)
    plt.legend()
    if filename:
        os.makedirs("results/figures", exist_ok=True)
        plt.savefig(f"results/figures/{filename}.png")
    plt.close()

def plot_lorenz_attractor(states, title="Lorenz Attractor", filename=None):
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(states[0], states[1], states[2])
    ax.set_title(title)
    if filename:
        os.makedirs("results/figures", exist_ok=True)
        plt.savefig(f"results/figures/{filename}.png")
    plt.close()

def plot_truth_table(table, title="Truth Table", filename=None):
    inputs = list(table.keys())
    outputs = list(table.values())
    size = int(len(inputs) ** 0.5)

    matrix = np.array(outputs).reshape(size, size)
    plt.figure()
    plt.imshow(matrix, cmap="coolwarm", interpolation="nearest")
    plt.colorbar(label="Output")
    plt.xticks(range(size), [inp[1] for inp in inputs[:size]])
    plt.yticks(range(size), [inp[0] for inp in inputs[::size]])
    plt.xlabel("Input B")
    plt.ylabel("Input A")
    plt.title(title)
    if filename:
        os.makedirs("results/figures", exist_ok=True)
        plt.savefig(f"results/figures/{filename}.png")
    plt.close()
