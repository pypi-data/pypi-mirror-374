from .lca_rmq import LCA, compute_sparce_table

from itertools import product, takewhile, combinations, chain
import pandas as pd
import numpy as np
from collections.abc import Iterable
import networkx as nx

__forbidden_attributes_phylo= ['_color', 'clades']


#> Define some functions
########################

# Para árboles

def get_dad(tree, n):
    in_edgs= list(tree.in_edges(n))
    if len(in_edgs)==0:
        if n in tree:
            raise ValueError('Node "{}" has no dad'.format(n))
        else:
            raise ValueError('Node "{}" not in tree'.format(n))
    return in_edgs[0][0]

def get_children(tree, node):
    return list(tree[node])

def get_path(tree, x0, x1):
    P= [x1]
    while( x1 != x0 ):
        x1= get_dad(tree, x1)
        P+= [x1]
    return P[::-1]

def are_the_same(X):
    x0= X[0]
    F= lambda x: x==x0
    return all(map(F, X))

def LCA_naive(tree, nodes):
    if len(nodes)==0:
        raise ValueError(f'Parameter "nodes" must be a non-empty set.')
    P= [get_path(tree, tree.root, n) for n in nodes]
    L= min(map(len, P))
    P= [X[:L] for X in P]
    M= len(nodes)
    #X= list( takewhile(lambda x: are_the_same(P[:,x]) , range(L)) )[-1]
    X= list( takewhile(lambda x: are_the_same( [P[i][x] for i in range(M)] ) , range(L)) )[-1]
    return P[0][X]


def LCA_color(tree, colors, color_attr= 'color'):
    if len(colors)==0:
        raise ValueError(f'Parameter "colors" must be a non-empty set.')
    nodes= {x for x in tree if tree.nodes[x][color_attr] in colors}
    return LCA(tree, nodes)

def set_sparce_matrix(T):
    # Add attributes for rmq-lca
    E, L, R= euler_tour(T)
    T.E= E
    T.R= R
    T.L= L
    T.st= st= compute_sparce_table(L)
    # Update universal common ancestor
    T.u_lca= LCA(T, induced_leafs(T,T.root))
    return None

def induced_leafs(tree, n):
    Q= [n]
    L= []
    while len(Q) > 0:
        n= Q.pop()
        sons= list(tree[n])
        if len(sons) == 0:
            L+= [n]
        else:
            Q+= sons
    return L

def get_inner_nodes(tree):
    return set(tree) - set(induced_leafs(tree, tree.root))

def is_leaf(tree, node):
    return len(tree[node]) == 0

def count_leafs(T):
    return sum((is_leaf(T, x) for x in T))

def get_color2leafs(tree, color_attr= 'color'):
    leafs= induced_leafs(tree, tree.root)
    colors= set((tree.nodes[leaf][color_attr] for leaf in leafs))
    color_2_leaf= {color:set() for color in colors}
    for leaf in leafs:
        color_2_leaf[ tree.nodes[leaf][color_attr] ].add(leaf)
    return color_2_leaf

def get_leaf2color(T, color_attr= 'color'):
    leaves= filter(lambda x: is_leaf(T,x), T)
    return {x:T.nodes[x][color_attr] for x in leaves}

def get_symbolic_relations(T, sym, nAttr, forbidden_nodes= [], leaf_attr= None, forbidden_leaf_symbol= 'X'):
    if leaf_attr==None:
        F= lambda X: X
    else:
        F= lambda X: [T.nodes[x_l][leaf_attr]
                      for x_l in X
                      if T.nodes[x_l][leaf_attr] !=forbidden_leaf_symbol
                     ]
    edges= []
    for node in T:
        if T.nodes[node][nAttr]==sym and node not in forbidden_nodes:
            for x0,x1 in combinations(T[node], 2):
                edges+= list(product(F(induced_leafs(T, x0)),
                                     F(induced_leafs(T, x1)),
                                    ))
    return edges

def copy_tree(tree):
    root= tree.root
    tree= tree.copy()
    tree.root= root
    return tree

def subtree(T, root):
    nodes= BFS_graph(T, root)
    T1= nx.induced_subgraph(T, nodes)
    T1.root= root
    return T1

# Edge compacting
def compact_nondiscriminant_edges(T, attr= 'label', attr_val= None, root= None):
    # Set parameters
    if attr_val == None:
        are_equal= lambda x0,x1: T.nodes[x0][attr] == T.nodes[x1][attr]
    else:
        are_equal= lambda x0,x1: T.nodes[x0][attr] == T.nodes[x1][attr] == attr_val
    if root==None:
        root= T.root
    # Compact edges
    edges= list((x0,x1) for x0 in nx.dfs_postorder_nodes(T, root) for x1 in T[x0])
    for x0,x1 in edges:
        if are_equal(x0,x1):
            compact_edge(T, x0, x1, update_lca= False)
    # Update LCA matrix
    set_sparce_matrix(T)
    return None

def compact_edge(T, x0, x1, delete= 'lower', update_lca= True):
    if delete=='lower':
        Y= set(T[x1])
        T.remove_node(x1)
        for y in Y:
            T.add_edge(x0,y)
    elif delete=='upper':
        Y= set(T[x0]) - {x1}
        dad= get_dad(T, x0)
        T.remove_node(x0)
        T.add_edge(dad,x1)
        for y in Y:
            T.add_edge(x1,y)
    else:
        ValueError('delete parameter must be one of ["lower", "upper"]')
    if update_lca:
        set_sparce_matrix(T)
    return None

# Prunnng
def prune_losses(T, label='label', loss='X', root= None):
    # Set parameters
    if root==None:
        root= T.root
    # Prune losses
    node_2_children= dict()
    induced_L= dict()
    # Do a DFS travel: save children in preorder, prune nodes in posorder
    stack= [root]
    while (len(stack)>0):
        peak= stack[-1]
        if peak in node_2_children:
            prune_if_necessary(T, peak, node_2_children, induced_L, label, loss)
            # Update stack
            stack.pop(-1)
        else:
            # Update children dictionary and stack
            node_2_children[peak]= set(T[peak])
            stack+= list(T[peak])
    # Update LCA matrix
    set_sparce_matrix(T)
    if not T.u_lca in T:
        T.u_lca= LCA
    return None

def prune_if_necessary(T, x_node, node_2_children, induced_L, label, loss):
    # children in unprunned tree
    children= node_2_children[x_node]
    if len(children)==0:
        induced_L[x_node]= {T.nodes[x_node][label]}
    else:
        induced_L[x_node]= set(chain.from_iterable((induced_L[x] for x in children)))
    # Chech if prune
    if induced_L[x_node] == {loss}:
        # All descendants are loss, thus delete node
        T.remove_node(x_node)
    elif len(T[x_node])==1:
        # There is only one child, thus compact node
        x1= list(T[x_node])[0]
        compact_edge(T, x_node, x1, delete= 'upper', update_lca= False)
    return None


# Leafs overlap
def are_overlapping(set_list):
    ret= False
    for s0,s1 in combinations(set_list, 2):
        if not s0.isdisjoint(s1):
            ret= True
            break
    return ret

def leafs_overlap(tree, node):
    if not is_leaf(tree, node):
        return are_overlapping([induced_colors(tree, child)
                                for child in tree[node]])
    else:
        raise ValueError(f'leafs overlap not defined for a leaf ({node})')


def assign_symbolic_date(tree):
    for node in tree:#BFS_graph(tree, tree.root):
        if not is_leaf(tree, node):
            if leafs_overlap(tree, node):
                tree.nodes[node]['color']= 'D'
            else:
                tree.nodes[node]['color']= 'S'

# Pasar a otros tipos de datos

def get_newick(T):
    newick= {}
    for node in nx.dfs_postorder_nodes(T):
        if len(T[node])==0 :
            newick[ node ]= 'spec' + node#nxTree.nodes[node]['label']
        else:
            newick[ node ]= '(' + ','.join([ newick[son] for son in T[node] ]) + ')'
    return newick[node]+';'

def __getNAme(node, idx, tree, label):
    attributes= {a:b for a,b in node.__dict__.items()
                 if b != None
                 and a not in __forbidden_attributes_phylo
                }
    n_label= attributes.get(label, None)
    if n_label==None:
        return idx, attributes
    if n_label in tree:
        raise ValueError('The label "{}" is not unique for every node'.format(n_label))
    return n_label, attributes

def make_directed(X):
    """
    Transforma un árbol con estrucutura de dato nx.Graph  a un objeto de networkx.Digraph sin ningun elemento de biopython
    """
    tree= nx.DiGraph()
    L= []
    for x0 in BFS_graph(X.nx_tree, X.bio_tree.root):
        L+= [x0]
        for x1 in X.nx_tree[x0]:
            if x1 not in L:
                w= X.nx_tree[x0][x1]['weight']
                tree.add_edge(x0, x1, weight= w)

    tree.root= X.bio_tree.root
    return tree


# Recorridos

def BFS_graph(tree, root):
    """
    Returns a list of nodes visited in a BFS travel

    tree: nx.Graph
    root: node in nx.Graph.nodes
    """
    Q= [root]
    L= []
    while len(Q) > 0:
        x= Q.pop(0)
        L+= [x]
        Q+= [neighbor for neighbor in tree[x]
             if neighbor not in L]
    return L

def euler_tour(T):
    """
    input: nxTree
    output:
      E: Euler tour nodes
      L: Levels
      R: Representative index of nodes in E
    """
    stack= [T.root]
    children= {}

    E= []
    R= {}
    L= []
    idx= 0
    lev= 0

    while len(stack)>0:
        node= stack[-1]
        E+= [node]
        L+= [lev]

        if node not in children:
            children[node]= list(T[node])
            R[node]= idx

        if len(children[node])==0:
            stack.pop(-1)
            lev-= 1
        else:
            stack+= [children[node].pop(0)]
            lev+= 1

        idx+= 1

    return E, L, R

# auxiliares

def is_superColor(color):
    return isinstance(color, Iterable) and not type(color)==str

def correct_colors(tree):
    for n in tree:
        colorts= tree.nodes[n]['color']
        #if( type(colorts)==list ):
        #if isinstance(colorts, Iterable) :
        if is_superColor(colorts):
            tree.nodes[n]['color']= list(map(str, colorts))
        else:
            tree.nodes[n]['color']= str(colorts)
    tree.root= '0'
    return tree

def induced_colors(tree, node, color_attr= 'color'):
    sLeafs= set()
    for x in induced_leafs(tree, node):
        xcol= tree.nodes[x][color_attr]
        if is_superColor(xcol):
            sLeafs.update(xcol)
        else:
            sLeafs.add(xcol)
    return sLeafs
