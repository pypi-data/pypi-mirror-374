from .nxTree import copy_tree, is_leaf, induced_colors, set_sparce_matrix
from .nhx_tools import read_nhx, tralda_to_nxTree, get_nhx
from .in_out import get_digraph_cols, write_digraphs_list

from numpy import argsort
from itertools import product, combinations
import networkx as nx
from bmgedit import BMGEditing
import pandas as pd
from math import ceil
from tqdm import tqdm
tqdm.pandas()


def build_graph(G,
                method='louvain',
                objective='cost',
                color_attr= None,
                use_binary_triples=True,
                force_binary= False,
                double_build= True,
               ):
    """
    ARG1: method - this param will be use to select the method
    """
    if color_attr != None:
        G1= G.copy()
        for x in G:
            G1.nodes[x]['color']= G.nodes[x][color_attr]
    else:
        G1= G

    solver = BMGEditing.BMGEditor(G1, binary= force_binary, use_binary_triples= use_binary_triples)
    solver.build(method, objective)

    hug_free= solver.get_bmg(extract_triples_first=False, update_tree= double_build)

    accession_2_species= {}
    nId_2_accession= {}
    for x in G:
        XX= G.nodes[x]['accession']
        YY= G.nodes[x]['species']
        hug_free.nodes[x]['accession']= XX
        hug_free.nodes[x]['species']= YY
        accession_2_species[XX]= YY
        nId_2_accession[x]= XX

    nxT= tralda_to_nxTree(solver._tree, name_attr= 'accession')
    # color_attr
    for x in nxT:
        if len(nxT[x])==0:
            nId= int(nxT.nodes[x].get('accession','NO_LABEL'))
            accession= nId_2_accession[nId]
            color= accession_2_species.get(accession)
            nxT.nodes[x]['species']= color
            nxT.nodes[x]['accession']= accession
        else:
            nxT.nodes[x]['species']= None

    return hug_free, nxT

def build_graph_series(G, args):
    lens= G.apply(len)
    is_sorted= all([lens.iloc[i] <= lens.iloc[i+1]
                    for i in range(lens.shape[0]-1)])
    if not is_sorted:
        order= argsort(lens.values)
        G= G.iloc[order]
        lens= lens.iloc[order]

    G_T= G.progress_apply(lambda X: build_graph(X,
                                                color_attr= 'species',
                                                method= args.bmg_heuristic,
                                                use_binary_triples= args.no_binary_triples,
                                                force_binary= args.force_binary_gene_tree,
                                                double_build= args.gene_tree_no_double_build,
                                                ))
    G= G_T.apply(lambda X: X[0])
    Tg= G_T.apply(lambda X: X[1])
    Tg.name='tree'

    Tg= Tg.progress_apply( lambda x: get_augmented_tree(x, 'accession', 'species') ).reset_index()

    return Tg, G


##################################################################
##################################################################
##################################################################

def _addN(T,idx, tree, n):
    T.add_node(idx, **(tree.nodes[n].copy()))

def get_augmented_tree(tree, geneAttr, speciesAttr):
    """
    Constructs the color intersection graph
    Schaller et. al. 2020:
    Complete characterization of incorrect orthology assiments in BMGs
    """

    T= nx.DiGraph()
    T.root= 0
    _addN(T, 0, tree, 0)
    w_idx= 1
    mu= {1 : 0} # node x in tree --> corresponding dad in T

    for node in list(nx.dfs_preorder_nodes(tree, source= 1)):

        _addN(T, w_idx, tree, node)
        T.add_edge(mu[node], w_idx)
        for child in tree[node]:
            mu[child]= w_idx
        current= w_idx
        w_idx+= 1

        if (not is_leaf(tree, node)) and (node != tree.root):
            CIG= get_CIG(tree, node, speciesAttr)
            CC= list(nx.connected_components(CIG))
            if len(CC)>1:
                T.nodes[current][geneAttr]= 'S'
                for cc in (X for X in CC if len(X)>1):
                    _create_redundant_node(T, w_idx, current, tree, node, cc, mu, geneAttr, speciesAttr)
                    w_idx+= 1
            else:
                T.nodes[current][geneAttr]= 'D'
    T.nodes[T.root][geneAttr]= None
    set_sparce_matrix(T)
    return T

def get_CIG(tree, node, speciesAttr):
    """
    Color Intersection Graph
    """
    children= set(tree[node])
    CIG= nx.Graph()
    CIG.add_nodes_from(children)
    for v0,v1 in combinations(children, 2):
        colors0= induced_colors(tree, v0, speciesAttr)
        colors1= induced_colors(tree, v1, speciesAttr)
        if not colors0.isdisjoint(colors1):
            CIG.add_edge(v0, v1)
    return CIG

def _create_redundant_node(T, w_idx, current, tree, node, cc, mu, geneAttr, speciesAttr):
    T.add_node(w_idx, **{geneAttr: 'D', speciesAttr: None})
    T.add_edge(current, w_idx)
    for child in cc:
        mu[child]= w_idx
