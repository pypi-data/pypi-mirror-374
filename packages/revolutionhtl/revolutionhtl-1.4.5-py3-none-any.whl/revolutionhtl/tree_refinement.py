from .DMSeries import compute_distance_matrix, low_diag_distance_matrix
from .NanNeighborJoining import resolve_tree_with_nan
from .parse_prt import load_all_hits_raw, normalize_scores
from .nhx_tools import get_nhx, read_nhx, f_get_attrs, _nhxFlag
from .nxTree import induced_colors, is_leaf

from Bio.Phylo.TreeConstruction import DistanceTreeConstructor, DistanceMatrix

import re
import pandas as pd
import numpy as np
from Bio import Phylo
from io import StringIO
from networkx import dfs_postorder_nodes

from numpy import tril, isnan

from itertools import chain
import re

def is_polytomie(T, node):
    return len(T[node]) > 2

#def get_polytomies(T):
#    return [node for node in T if is_polytomie(T, node)]

_lenght_pattern= r':\d+\.\d+'

class TreePolytomies:
    def __init__(self, tree, label_attr= 'label'):
        self.tree= tree
        self.label_attr= label_attr
        self.polytomies= list()
        self.partition= dict()
        self.resolutions= dict()
        self.info= dict()
        self.get_polytomies()
        self.is_resolved= len(self.polytomies)==0

        self.id_preffix= 'NODEID'
        self.id_suffix= 'END'

    def nodehash(self, node):
        return f'{self.id_preffix}{node}{self.id_suffix}'

    def get_polytomies(self):
        induced= dict()

        for xNode in dfs_postorder_nodes(self.tree, self.tree.u_lca):
            if is_leaf(self.tree, xNode):
                induced[xNode]= {self.tree.nodes[xNode][self.label_attr]}
            else:
                children= list(self.tree.successors(xNode))
                clusters= [induced[child] for child in children]
                induced[xNode]= set(chain.from_iterable((clusters)))

                if is_polytomie(self.tree, xNode) and self.tree.nodes[xNode][self.label_attr]=='D':
                    self.polytomies+= [xNode]
                    self.partition[xNode]= (children, clusters)

    def process_tree_polytomies(self, distance_pairs):
        constructor = DistanceTreeConstructor()
        self.success= []
        for xNode in self.polytomies:
            children, clusters= self.partition[xNode]
            names= [self.nodehash(child) for child in children]

            D_matrix= low_diag_distance_matrix(distance_pairs, clusters, children)

            if isnan(D_matrix.sum()):
                self.resolutions[xNode]= f'({",".join(names)})D'
                self.success+= [False]
                self.info[xNode]= f'Matrix contains NaN: {str(D_matrix)}.'

            else:
                try:
                    LTM= tril(D_matrix).tolist()
                    LTM= [X[:i+1] for i,X in enumerate(LTM)]
                    dm = DistanceMatrix(names= names, matrix= LTM)
                    nj_tree = constructor.nj(dm)
                    nj_tree.root_at_midpoint()
                    rename_inner_nodes(nj_tree)
                    nhx= nj_tree.format("newick").strip()[:-1]
                    self.resolutions[xNode]= nhx
                    self.success+= [True]
                    self.info[xNode]= 'Success.'

                except UnboundLocalError as e:
                    self.resolutions[xNode]= f'({",".join(names)})D'
                    self.success+= [False]
                    self.info[xNode]= f'Bio.Phylo UnboundLocalError: {e}.'

    def compile_resolution(self):
        """This function is a modification to revolutionhtl.nhx_tools.get_nhx"""
        T= self.tree
        resolutions= self.resolutions
        root= root= T.u_lca
        name_attr= self.label_attr
        nhxFlag= _nhxFlag
        attr_sep= ':'
        ignore_attrs= []
        ignore_inner_name= False
        include_none= False
        use_nhx_flag=True
        get_attrs= f_get_attrs(T, name_attr, ignore_attrs, include_none)

        # Create newick integratin the resolutions
        newick= {}
        for node in dfs_postorder_nodes(T, source= root):
            children= list(T[node])
            if len(children)==0 :
                nwk_n= str(T.nodes[node].get(name_attr, ''))
            elif node in resolutions:
                nwk_n= resolutions[node]
                for child in children:
                    nwk_n= nwk_n.replace(self.nodehash(child), newick[child])
            else:
                nwk_n= '(' + ','.join([ newick[child] for child in T[node] ]) + ')'
                if not ignore_inner_name:
                    nwk_n+= str(T.nodes[node].get(name_attr, ''))

            c_attrs= get_attrs(node)
            if len(c_attrs) > 0:
                nwk_n+= '[' + nhxFlag + attr_sep.join((f'{x}={T.nodes[node][x]}' for x in c_attrs)) +']'

            newick[ node ]= nwk_n

        # Convert nxTree
        nhx= re.sub(_lenght_pattern, '', newick[root]+';')
        tree= read_nhx(nhx, name_attr= self.label_attr)

        return tree



def rename_inner_nodes(tree):
    """Rename all inner nodes of a tree."""
    for idx, clade in enumerate(tree.find_clades()):
        if not clade.is_terminal():  # Check if it's an inner node
            clade.name= 'D'

def refine_df(df_distances, gTrees, label_attr= 'label', inplace= False):
    if not inplace:
        gTrees= gTrees.copy()
    print('Processing distances...')
    F= lambda row: frozenset(row)
    df_distances['genes']= df_distances[['Query_accession',
                                     'Target_accession']
                                   ].apply(F, axis= 1)

    F= lambda df: df.set_index('genes').score_distance.to_dict()
    og_distances= df_distances.groupby('OG')[['genes', 'score_distance']].progress_apply(F)


    F= lambda T: TreePolytomies(T, 'accession')
    polytomies= gTrees.set_index('OG').tree.apply(F).reset_index(name= 'solver')

    print('Processing polytomies...')
    F= lambda row: row.solver.process_tree_polytomies(og_distances.loc[row.OG])
    polytomies.progress_apply(F, axis=1)

    resolved= polytomies.solver.apply(lambda X: X.compile_resolution())

    original_polytomies= polytomies.solver.apply(lambda X: len(X.polytomies))
    resolved_polytomies= polytomies.solver.apply(lambda X: sum(X.success))

    gTrees.tree= resolved.to_list()
    gTrees['original_polytomies']= original_polytomies.to_list()
    gTrees['resolved_polytomies']= resolved_polytomies.to_list()

    return gTrees, polytomies

def is_diagonal_zero_and_nan_elsewhere(D: np.ndarray) -> bool:
    """
    Checks if a matrix has zeros on the diagonal and NaN everywhere else.

    Args:
        D (np.ndarray): The input matrix.

    Returns:
        bool: True if the matrix satisfies the condition, False otherwise.
    """

    # Check if diagonal elements are all zeros
    diagonal_zero = np.all(np.diag(D) == 0)

    # Create a mask for the off-diagonal elements
    off_diagonal_mask = ~np.eye(D.shape[0], dtype=bool)  # True for off-diagonal elements

    # Check if off-diagonal elements are all NaN
    off_diagonal_nan = np.all(np.isnan(D[off_diagonal_mask]))

    return diagonal_zero and off_diagonal_nan
