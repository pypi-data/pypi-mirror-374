from .nxTree import is_leaf, get_dad
from .lca_rmq import LCA
from .triplets import get_triplets, _get_triples_from_root
from .prune import prune_losses
from .nhx_tools import get_nhx

import networkx as nx
import pandas as pd
from itertools import chain

from tqdm import tqdm
tqdm.pandas()

# Extra variables for consistency testing:
# - ind_leafs
# - Ts_triples

def assign_id(T, idAttr= 'node_id'):
    for i,x in enumerate(T):
        T.nodes[x][idAttr]= f'ID{x}X'

def _try_recon(Tg, Ts, Ts_triples, root, gene_attr, species_attr, event_attr, fix_inconsistencies):

    X= reconciliate(Tg, Ts, Ts_triples, root, gene_attr, species_attr, event_attr, fix_inconsistencies)

    Tr, mu, epsilon, flip_nodes= X
    return Tr, mu, epsilon, flip_nodes

def reconciliate_many(gTrees,
                      Ts,
                      gene_attr= 'accession',
                      species_attr= 'species',
                      event_attr= 'accession',
                      fix_inconsistencies= True,
                      orthogroup_column= 'OG',
                      tree_column= 'tree',
                     ):
    for y in Ts:
        if len(Ts[y])>0:
            Ts.nodes[y][event_attr]= 'S'

    Ts_triples= set(get_triplets(Ts, event=event_attr, color=species_attr, root_event='S'))

    for y in Ts:
        if len(Ts[y])>0:
            del Ts.nodes[y][event_attr]


    # Reconciliate trees
    #   Note:
    #   Each element X of the list bellow is a tuple
    #   containing: X[0]-> Tr, X[1]-> mu, X[2]-> epsilon, X[3]-> flip_nodes
    recons= [(OG,) + _try_recon(Tg,
                                 Ts,
                                 Ts_triples,
                                 Tg.u_lca,
                                 gene_attr,
                                 species_attr,
                                 event_attr,
                                 fix_inconsistencies)
             for Tg, OG in tqdm(gTrees[[tree_column, orthogroup_column]].values)
            ]

    df_recs= pd.DataFrame(recons, columns= [orthogroup_column,
                                            'reconciliated_tree',
                                            'reconciliation_map',
                                            'equivalence_map',
                                            'flipped_nodes'],
                         )

    return df_recs[[orthogroup_column, 'reconciliated_tree',
                    'reconciliation_map', 'equivalence_map']]

def recon_table_to_str(Ts, df_recs, orthogroup_column= 'OG'):
    # Assign node-IDs for the newick output
    assign_id(Ts)
    df_recs.reconciliated_tree.apply(assign_id)

    df_r= pd.DataFrame(dict(tree= df_recs.reconciliated_tree.apply( lambda x: get_nhx(x, name_attr= 'accession') ),
                            reconciliation_map= df_recs.apply(lambda row: recon_2_text(row.reconciliation_map,
                                                                                       row.reconciliated_tree,
                                                                                       Ts
                                                                                      ), axis= 1),
                           ))
    df_r[orthogroup_column]= df_recs[orthogroup_column]

    return df_r[[orthogroup_column, 'tree', 'reconciliation_map']]

def flipped_to_str(flipped, Tr, idAttr= 'node_id'):
    return ','.join( (str(get_node_id(Tr, x, idAttr)) for x in flipped) )

def get_node_id(T, x, idAttr= 'node_id'):
    return T.nodes[x][idAttr]

def recon_2_text(mu, T0, T1, idAttr= 'node_id'):
    G= lambda X: f'{ get_node_id(T0, X[0], idAttr) }:{ get_node_id(T1, X[1], idAttr) }'
    return ','.join( (G(X) for X in mu.items()) )

def reconciliate(Tg, Ts, Ts_triples, root= None, gene_attr= 'accession', species_attr= 'species', event_attr= 'event', fix_inconsistencies= True):
    Tr= nx.DiGraph()
    mu= dict()
    epsilon= dict()
    x_node= 0
    flip_nodes= []
    ind_leafs= {} # Induced species for nodes into the input tree
    if root == None:
        root= Tg.u_lca

    for u_node in nx.dfs_postorder_nodes(Tg, source= root):
        if is_leaf(Tg, u_node):
            rho_x, x_node= _map_leaf(Tg, u_node, Tr, x_node, Ts, mu, species_attr, gene_attr)
            ind_leafs[u_node]= { Tg.nodes[u_node][species_attr] }
        else:
            lamb_x= [epsilon[v] for v in Tg[u_node]]
            lamb_y= {mu[x] for x in lamb_x}
            y= LCA(Ts, lamb_y)
            rho_x, x_node= _rarefy(Ts, Tr, Tg, ind_leafs, Ts_triples, y, u_node, event_attr, lamb_y, fix_inconsistencies, mu, lamb_x, x_node, flip_nodes)
            ind_leafs[u_node]= set(chain.from_iterable((ind_leafs[u_child] for u_child in Tg[u_node])))
        epsilon[u_node]= rho_x

    Tr.u_lca= epsilon[root]

    return Tr, mu, epsilon, flip_nodes


################################################################################
################################################################################
def _map_leaf(Tg, u_node, Tr, x_node, Ts, mu, species_attr, gene_attr):
    rho_x= x_node
    x_node+= 1
    species= Tg.nodes[u_node][species_attr]
    gene= Tg.nodes[u_node][gene_attr]
    Tr.add_node(rho_x, **{species_attr:species, gene_attr:gene})
    sleafs= [x for x in Ts if len(Ts[x])==0 and Ts.nodes[x][species_attr] == species]
    ks= len(sleafs)
    if ks!=1:
        raise ValueError(f'There should be exactly one leaf in the species tree with species "{species}", but there are {ks}')
    mu[rho_x]= sleafs[0]
    return rho_x, x_node

def _rarefy(Ts, Tr, Tg, ind_leafs, Ts_triples, y, u_node, event_attr, lamb_y, fix_inconsistencies, mu, lamb_x, x_node, flip_nodes):
    if Tg.nodes[u_node][event_attr]=='S':
        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< In the future we should use the "indirect" function (now commented)
        #rho_x, x_node= _in_direct_triple_testing(u_node, y, Tr, Ts, mu, lamb_x, lamb_y, x_node, event_attr, flip_nodes)
        rho_x, x_node= _direct_triple_testing(u_node, y, Tr, Tg, Ts, ind_leafs, Ts_triples, mu, lamb_x, lamb_y, x_node, event_attr, flip_nodes)
    elif Tg.nodes[u_node][event_attr]=='D':
        rho_x, x_node= _rarefy_duplication(u_node, y, Tr, Ts, mu, lamb_x, x_node, event_attr)
    else:
        raise ValueError(f'Wrong symbol "{Tg.nodes[u_node][event_attr]}" in the gene tree.')
    return rho_x, x_node

def _compute_xi(rho_y, Y_0, Ts):
    Xi= {rho_y}
    Y_nodes= {get_dad(Ts, y) for y in Y_0 if rho_y not in (y, get_dad(Ts, y))}
    while len(Y_nodes)>0:
        y_node= Y_nodes.pop()
        if y_node in Y_0:
            return set()
        if y_node not in Xi:
            Xi.add(y_node)
            Y_nodes.add(get_dad(Ts, y_node))
    return Xi

def _rarefy_speciation(Xi, X_0, Y_0, Ts, Tr, mu, y_0, x_node, event_attr):
    """
    We assume Y_0 < y_0
    """
    Ts_p= nx.induced_subgraph(Ts, Xi.union(Y_0))
    delta= {mu[x]:x for x in X_0}
    for y_node in nx.dfs_postorder_nodes(Ts_p, source= y_0):
        children_Ts_p= list(Ts_p[y_node])

        if len(children_Ts_p) > 0:
            # Create the node
            x_iter_p= x_node
            x_node+= 1
            Tr.add_node(x_iter_p, **{event_attr:'S'})
            mu[x_iter_p]= y_node
            delta[y_node]= x_iter_p
            # Identify the map of the children of x_iter
            children_Tr= map(lambda y: delta[y], children_Ts_p)
            # Connect the childres via inverse map delta
            for x_pp in children_Tr:
                Tr.add_edge(x_iter_p, x_pp)
            # Create missed child-withness
            for y_pp in set(Ts[y_node]) .difference( children_Ts_p ) :
                Tr.add_node(x_node, **{event_attr:'X'})
                Tr.add_edge(x_iter_p, x_node)
                mu[x_node]= y_pp
                x_node+= 1
    return x_iter_p, x_node

def _rarefy_duplication(u_node, rho_y, Tr, Ts, mu, X_nodes, x_node, event_attr):
    # Create the duplication
    rho_x= x_node
    x_node+= 1
    Tr.add_node(rho_x, **{event_attr:'D'})
    mu[rho_x]= rho_y
    # Create descendant linages
    for x_node_p in X_nodes:
        if rho_y==mu[x_node_p]:
            Tr.add_edge(rho_x, x_node_p)
        else:
            lamb_x= {x_node_p}
            lamb_y= {mu[x_node_p]}
            Xi= _compute_xi(rho_y, lamb_y, Ts)
            rho_x_p, x_node= _rarefy_speciation(Xi, lamb_x, lamb_y, Ts, Tr, mu, rho_y, x_node, event_attr)
            Tr.add_edge(rho_x, rho_x_p)
    return rho_x, x_node

def _direct_triple_testing(u_node, y, Tr, Tg, Ts, ind_leafs,
                           Ts_triples, mu, lamb_x, lamb_y,
                           x_node, event_attr, flip_nodes):
    Tg_color_triples= set(_get_triples_from_root(Tg, u_node, ind_leafs))
    FP= Tg_color_triples - Ts_triples
    if len(FP)>0:
        rho_x, x_node= _rarefy_duplication(u_node, y, Tr, Ts, mu,
                                           lamb_x, x_node, event_attr)
        flip_nodes+= [rho_x]#[u_node]
    else:
        Xi= _compute_xi(y, lamb_y, Ts)
        rho_x, x_node= _rarefy_speciation(Xi, lamb_x, lamb_y, Ts, Tr, mu,
                                          y, x_node, event_attr)
    return rho_x, x_node

def _in_direct_triple_testing(u_node, y, Tr, Ts, mu, lamb_x, lamb_y, x_node, event_attr, flip_nodes):
    if len(lamb_y) < len(lamb_x): # There are nodes sharing the same map
        rho_x, x_node= _rarefy_duplication(u_node, y, Tr, Ts, mu, lamb_x, x_node, event_attr)
        flip_nodes+= [rho_x]#[u_node]
    if y in lamb_y: # Time insocnsistency
        rho_x, x_node= _rarefy_duplication(u_node, y, Tr, Ts, mu, lamb_x, x_node, event_attr)
        flip_nodes+= [rho_x]#[u_node]
    else:
        Xi= _compute_xi(y, lamb_y, Ts)
        if len(Xi)==0: # All refinements are non-consistent
            rho_x, x_node= _rarefy_duplication(u_node, y, Tr, Ts, mu, lamb_x, x_node, event_attr)
            flip_nodes+= [rho_x]#[u_node]
        else:
            rho_x, x_node= _rarefy_speciation(Xi, lamb_x, lamb_y, Ts, Tr, mu, y, x_node, event_attr)
    return rho_x, x_node
