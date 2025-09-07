from .triplets import get_triplets
from .nhx_tools import tralda_to_nxTree

from tralda.supertree.Build import greedy_BUILD
from bmgedit.Build import Build2
from tralda.datastructures import Tree
from itertools import chain
from collections import Counter

class WrongHeuristicError(Exception):
    """Raised when a input parameter specifies an heuristic not avaliable for an algorithm"""

def from_gene_forest(gTrees, method= 'louvain_weight', numb_repeats= 3, doble_build= True, binary= False):
    """
    Obtain triples rooted at symbol 'S' from a Series of gene trees.
    Then searchs for an approximated maximum set of consistent using an heuristic,
    and returns a species S_1 tree that explains such a set.

    "doble build" means that instead of returning the species tree S_1,
    triples will be retrivered from this tree and then run build in this
    set of triples, obtaining another tree S_2 which may be less resolved
    than S_1 see [REFERENCE].

    Input:
    - gTrees : pandas.Series of nxTree
               Each element is a gene tree where the node attributes are:
               - 'event' for gene name in leafs and symbol in inner nodes
               - 'color' for the species in the leafs
    - method : str
               Meta parameter of the heuristics, specifies a comunity-detection
               algorithm. See more in [REFERENCE]
    - numb_repeats : int
                     Meta parameter of the heuristics, specifies how many time
                     run the algorithm for community detection.
    - doble_build :  bool
                     Run build algorithm twice aimed to obtain less-resolved tree. See [REFERENCE]
    """
    weights= _count_triples(gTrees,
                           event='accession',
                           color= 'species',
                           root_event= 'S')
    triples= set(weights)
    leafs= set(chain.from_iterable(triples))

    T= build(triples,
             leafs,
             method= method,
             numb_repeats= numb_repeats,
             doble_build= doble_build,
             name_attr= 'species',
             weights= weights,
             binary= binary,
            )

    return T

def build(triples,
          leafs,
          method= 'louvain_weight',
          numb_repeats= 3,
          doble_build= True,
          name_attr= 'accession',
          weights= None,
          binary= False,
         ):


    if weights==None:
        weights= {x:1 for x in triples}

    if binary:
        binary= 'b'

    if method == 'naive': # add triples one by one and checks consistency via BUILD
        tree= greedy_BUILD(triples ,leafs)

    elif method in ('louvain','mincut'):
        build = Build2(triples, leafs,
                       allow_inconsistency=True,
                       part_method=method,
                       greedy_repeats=numb_repeats,
                       triple_weights= weights, #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<is it used?
                       binarize= binary
                      )
        tree = build.build_tree() # use recursive Aho-algorithm with 1 greedy repeat

    elif method == 'louvain_weight':
        build = Build2(triples, leafs,
                       allow_inconsistency=True,
                       part_method='louvain',
                       greedy_repeats=numb_repeats,
                       weighted_mincut=True,
                       triple_weights= weights,
                       binarize= binary
                      )
        tree = build.build_tree() # use recursive Aho-algorithm with 1 greedy repeat
    else:
        raise WrongHeuristicError(f'The method "{method}" is not implemented. Avaliable: naive, louvain, mincut, louvain_weight')

    # Compute second tree
    if doble_build:
        common_triples=[tuple(x.label for x in triple) for triple in Tree.get_triples(tree)]
        build = Build2(common_triples, leafs,
                       allow_inconsistency=False)
        tree = build.build_tree() # use recursive Aho-algorithm

    # Transform to nxTree
    tree= tralda_to_nxTree(tree, name_attr= name_attr)

    return tree

def _count_triples(tree_list, **kwargs):
    triples= chain.from_iterable((get_triplets(T, **kwargs)
                                  for T in tree_list
                                 ))
    weights= Counter(triples)
    return weights
