from . import nxTree as nxt
import networkx as nx
from itertools import chain, product, combinations

def get_triplets(tree, event='event', color= 'color', root_event= 'S', loss_leafs= 'X', root= None):
    """
    return a tuple (a,b,c), where a and b are the ingroup
    and c is the outgroup.
    """
    if root == None:
        root= tree.u_lca

    I= {} # Dictionary for induced leafs
    for x in nx.dfs_postorder_nodes(tree, root):
        if nxt.is_leaf(tree, x):
            if tree.nodes[x][color] == loss_leafs:
                I[x]= {  }
            else:
                I[x]= { tree.nodes[x][color] }
        else:
            I[x]= set( chain.from_iterable((I[x1] for x1 in tree[x])) )
            if tree.nodes[x][event] == root_event:
                for triple in _get_triples_from_root(tree, x, I):
                    yield triple

def _get_triples_from_root(tree, node, I):
    for x0, x1 in combinations(tree[node], 2):
        for triple in chain(_get_triplets_from_groups(tree, x0, x1, I),
                            _get_triplets_from_groups(tree, x1, x0, I)):
            yield triple

def _get_triplets_from_groups(tree, x_out, x_in, I):
    P= combinations( I[x_in], 2 )
    for (a,(b,c)) in product( I[x_out], P ):
        if len({a,b,c})==3:
            yield tuple(sorted((b,c)))+(a,)
