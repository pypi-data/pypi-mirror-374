import numpy as np
import pandas as pd

from itertools import combinations, product

def get_pair_distance(distance_pairs_series: pd.Series, leaf_1: str, leaf_2: str) -> float:
    """
    Retrieve the pairwise distance for two leaves from a pandas Series indexed by frozensets.

    :param distance_pairs_series: pandas Series where the index is frozensets of leaf pairs.
    :param leaf_1: The first leaf identifier.
    :param leaf_2: The second leaf identifier.
    :return: The distance between the pair of leaves if present, else np.nan.
    """
    pair = frozenset({leaf_1, leaf_2})
    return distance_pairs_series.get(pair, np.nan)

def _add_missing_pair(my_dict:dict[str, list[str]], key: str, value: str):
    if key in my_dict:
        my_dict[key].append(value)
    else:
        my_dict[key] = [value]

    return my_dict


def __text__(D:np.ndarray, Y: list[int | str], missing_pairs: dict[str, list[str]]) ->  str:
    text = f"Taxa for matrix D: {Y}\n" \
           f"Distance matrix D:\n{D}\n" \
           f"Missing pairs:"

    if missing_pairs:
        text += "\n"
        for key in missing_pairs.keys():
            text += f"\t{key}: {missing_pairs[key]}\n"
    else:
        text += " {}"
    return text

def low_diag_distance_matrix(PD: pd.Series,
                            C: list[list[str]],
                            Y: list[str]
                           ) -> tuple[np.ndarray, dict[str, list[str]], str]:
    """
    Compute the estimated distance matrix D based on the given "estimate" conditions.

    :param PD: pandas Series where the index is frozensets of IDs (tuples) and values are floats or np.nan.
    :param C: list of lists, where each sublist contains IDs corresponding to a cluster.
    :param Y: list of taxa labels corresponding to each cluster in C.
    :return: Symmetric distance matrix D as a 2D numpy array, a dictionary with missing pairs and a str representation
    """

    # Ensure Y matches the length of C
    if len(C) != len(Y):
        raise ValueError("The length of taxa labels (Y) must match the number of clusters (C).")

    idx_2_node= dict(enumerate(Y))

    k = len(C)  # Number of clusters
    missing_pairs= dict()
    matrix= np.zeros((k, k))

    for i,j in combinations(idx_2_node, 2):
        gene_pairs= list(map(frozenset, product(C[i], C[j])))
        distances= [PD.get(X, np.nan) for X in gene_pairs]
        distances= pd.Series(distances, index= gene_pairs)
        matrix[i,j]= distances.dropna().mean()

    return matrix. T



def compute_distance_matrix(PD: pd.Series,
                            C: list[list[str]],
                            Y: list[str]
                           ) -> tuple[np.ndarray, dict[str, list[str]], str]:
    """
    Compute the estimated distance matrix D based on the given "estimate" conditions.

    :param PD: pandas Series where the index is frozensets of IDs (tuples) and values are floats or np.nan.
    :param C: list of lists, where each sublist contains IDs corresponding to a cluster.
    :param Y: list of taxa labels corresponding to each cluster in C.
    :return: Symmetric distance matrix D as a 2D numpy array, a dictionary with missing pairs and a str representation
    """

    missing_pairs: dict[str, list[str]] = {}
    # key = 'Y[i],Y[j]'
    # value = [ 'zi_1,zj_2', ...]
    #
    # missing_pairs = {
    #     'Y[i],Y[j]': [ 'zi_1,zj_2', ...]
    # }

    # Ensure Y matches the length of C
    if len(C) != len(Y):
        raise ValueError("The length of taxa labels (Y) must match the number of clusters (C).")

    k = len(C)  # Number of clusters
    D = np.zeros((k, k))  # Initialize the distance matrix with zeros

    # Iterate over all pairs of clusters (i, j)
    for i in range(k):
        for j in range(i, k):  # Compute only the upper triangle (i <= j)
            if i == j:
                D[i, j] = 0  # Diagonal is zero
            else:
                total = len(C[i]) * len(C[j])  # Initial total
                numerator = 0.0

                # Compute numerator and adjust total
                for z_i in C[i]:
                    for z_j in C[j]:
                        value = get_pair_distance(PD, z_i, z_j)
                        if value is not None:
                            if not np.isnan(value):
                                numerator += value
                            else:  # PD[pair] = NaN
                                total -= 1
                                missing_pairs = _add_missing_pair(missing_pairs, f"{Y[i]},{Y[j]}", f"{z_i},{z_j}")
                        else:  # Pair not in PD
                            total -= 1
                            missing_pairs = _add_missing_pair(missing_pairs, f"{Y[i]},{Y[j]}", f"{z_i},{z_j}")

                # Avoid division by zero
                if total > 0:
                    D[i, j] = numerator / total
                else:
                    D[i, j] = np.nan  # Assign NaN if no valid pairs exist

                D[j, i] = D[i, j]  # Ensure symmetry

    return D, missing_pairs, __text__(D, Y, missing_pairs)
