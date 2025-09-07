from revolutionhtl.in_out import read_tl_digraph
import matplotlib.pyplot as plt
from itertools import combinations, chain
import networkx as nx
from tqdm import tqdm
from statistics import median
from math import sqrt
from collections import Counter

# Reduce giant family
# --------------------

def reduce_graph(giant_0, N_max= 2000):
    undirected_0= nx.Graph()
    undirected_0.add_edges_from(giant_0.edges())
    Q= [(giant_0, undirected_0)]
    res= []
    singles= []
    while len(Q) > 0:
        giant, undirected= Q.pop(0)
        CCs= _search_better(giant, undirected)

        for X in CCs:
            L= len(X)
            if L==1:
                singles+= X
            else:
                if L<=N_max:
                    res+= [X]
                else:
                    Q+= [(nx.induced_subgraph(giant_0, X), nx.induced_subgraph(undirected_0, X))]
                    
    return res, singles

def _compute_partition(undirected):
    CCs= nx.algorithms.community.kernighan_lin_bisection(undirected)
    CCs= list(chain.from_iterable((nx.connected_components(nx.induced_subgraph(undirected, X)) for X in CCs)))
    return CCs

def _search_better(giant, undirected, repetitions= 3):
    CCs= [_compute_partition(undirected) for i in range(repetitions)]
    scores= [_partition_score(X, giant) for X in CCs]
    CCs= CCs[scores.index( max(scores) )]
    return CCs

def _partition_score(CCs, G):
    """
    The biggest, the better
    """
    lens= list(map(len, CCs))
    L= len(lens)
    M= max(lens)

    x1= sum((x>1 for x in lens))/L # proportion of not singletons
    x2= nx.algorithms.community.partition_quality(G, CCs)[0] # proportion of intra-edges
    x3= sum((x/M for x in lens))/L # proportion of size w.r.t. bigest CC

    return sqrt( x1**2 + x2**2 + x3**2 ) # Euclidean norm
