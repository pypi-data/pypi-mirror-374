from .nxTree import is_leaf

import networkx as nx


def separe_loss_sons(T, x, label_attr= 'accession', loss_symbol= 'X'):
    L, Lx= [], []
    for x1 in T[x]:
        if T.nodes[x1][label_attr] == loss_symbol:
            Lx+= [x1]
        else:
            L+= [x1]
    return L, Lx

def prune_losses(T, label_attr= 'accession', loss_symbol= 'X'):
    # Init output tree
    Tp= nx.DiGraph()
    Tp.add_node(0, **T.nodes[0])
    Tp.root= 0
    # Add root to de queue and the dad of mu(root)
    Q= [(1, 0)]
    # Init counter of new nodes
    idx= 1

    while len(Q)>0:
        x, d= Q.pop(0)
        if is_leaf(T, x):
            Tp.add_node(idx, **T.nodes[x])
            Tp.add_edge(d, idx)
            idx+= 1
        else:
            L, _= separe_loss_sons(T, x, label_attr, loss_symbol)
            if len(L)>1:
                Tp.add_node(idx, **T.nodes[x])
                Tp.add_edge(d, idx)
                pDad= idx
                idx+= 1
            else:
                pDad= d
            Q+= [(x1, pDad) for x1 in L]
    return Tp
