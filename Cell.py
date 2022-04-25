import numpy as np

class Cell:

    x_proj: np.ndarray
    y_proj: np.ndarray
    z_proj: np.ndarray

    def __init__(self, edge_v1, edge_v2, lower_bound, upper_bound):
        x = np.linspace(edge_v1[0], edge_v2[0], 3)
        y = np.linspace(lower_bound, upper_bound, 3)

        self.x_proj, self.z_proj = np.meshgrid(x, y)
        self.y_proj = np.linspace(edge_v1[1], edge_v2[1], 3)
