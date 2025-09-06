import string
import numpy as np
import pandas as pd


# Numpy array
ex_array = np.array([
    [11, 12, 13, 14, 15],
    [21, 22, 23, 24, 25],
    [31, 32, 33, 34, 35],
    [41, 42, 43, 44, 45],
])

# Dataframe
ex_df = pd.DataFrame(
    columns=["Surname", "Forename", "Born", "years", "Nationality", "Known for"],
    data=[
        ["Descartes", "Rene", np.datetime64("1596-03-31"), 53, "French", ("Cartesian coordinates", "cogito, ergo sum")],
        ["Newton", "Isaac ", np.datetime64("1643-01-04"), 84, "British", ("Gravity", "Calculus", "Principia")],
        ["Euler", "Leonhard ", np.datetime64("1707-04-15"), 76, "Swiss", ("Graph theory", "topology", "exponential")],
        ["Gauss", "Johann", np.datetime64("1777-04-30"), 77, "German", ("Normal distribution", "Lens", "Ceres")],
        ["Hilbert", "David", np.datetime64("1862-01-23"), 81, "German", ("Hilbert space", "Set theory",)],
        ["Russell", "Bertrand ", np.datetime64("1872-05-18"), 97, "British", ("Paradoxes", "Principia Mathematica")],
        ["Nash", "John", np.datetime64("1928-06-13"), 86, "American", ("Game theory", "Nash equilibrium")],
    ],
)

# Dictionary
ex_dict: dict = {
    "England": 130_462,
    "Scotland": 78_803,
    "Wales": 20_782,
    "Northern Ireland": 14_333,
}

# String
ex_str: str = 'abcdefghijklmnopqrstuvwxyz'

# List
ex_list: list = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa']





