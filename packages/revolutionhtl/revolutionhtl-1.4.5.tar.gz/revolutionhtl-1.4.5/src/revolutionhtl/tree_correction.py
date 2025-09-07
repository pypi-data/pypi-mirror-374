from .nxTree import compact_edge, get_dad, set_sparce_matrix,get_leaf2color, is_leaf
from .nhx_tools import read_nhx, get_nhx
from .triplets import get_triplets

import networkx as nx
from networkx import dfs_postorder_nodes
import pandas as pd
from itertools import chain
from tqdm import tqdm
tqdm.pandas()

def correct_tree(Tg, Rs, root= 1,
                 label_attr= 'label',
                 species_attr= 'species',
                 event_attr= 'event',
                 algorithm= 'prune_L',
                 force_phylogeny= True,
                 update_lca= True,
                 inplace= True,
                ):

    # Inconsistent gene triples
    leaf_2_color= {Tg.nodes[x][label_attr] : Tg.nodes[x][species_attr]
                   for x in Tg if is_leaf(Tg, x)}
    F= lambda x: leaf_2_color[x]
    g2c_triple= lambda triple: tuple(sorted(map(F, triple[:2]))) + (F(triple[-1]),)

    R_I= set()
    R_C= set()
    for rg in get_triplets(Tg, event=event_attr, color=label_attr, root_event='S'):
        crg= g2c_triple(rg)
        if len(set(crg))==3:
            if crg in Rs:
                R_C.add(rg)
            else:
                R_I.add(rg)

    # From label to node
    leaf_2_node= {Tg.nodes[x][label_attr] : x
                  for x in Tg if is_leaf(Tg, x)}
    node_2_leaf= {y:x for x,y in leaf_2_node.items()}
    F= lambda triple: tuple(leaf_2_node[x] for x in triple)
    R_C= set(map(F, R_C))
    R_I= set(map(F, R_I))

    # Prune
    if algorithm=='prune_R':
        T_consistent= prune_triples(Tg, R_I, force_phylogeny= force_phylogeny, update_lca= update_lca, inplace= inplace, root= root)
    elif algorithm=='prune_L':
        T_consistent, pruned_leaves= prune_leaves(Tg, R_C, R_I, force_phylogeny= force_phylogeny, update_lca= update_lca, inplace= inplace, root= root)
        pruned_leaves= [node_2_leaf[x] for x in pruned_leaves]
    else:
        raise ValueError(f'"{algorithm}" is not a valid algorithm for tree edition')

    return T_consistent, len(R_I), pruned_leaves

def prune_leaves(T, R_C, R_I, w_r= None, force_phylogeny= True, update_lca= True, inplace= True, root= 1):
    if not inplace:
        T= T.copy()
    T.root= root
    if w_r==None:
        w_r= {r:1 for r in chain(R_C,R_I)}
    # Invert wheight of consistent triples
    w_r.update({rg:-w_r[rg] for rg in R_C})
    # Function for leaf prune-weight
    out_w= lambda x,G: sum((w_r[y] for y in G[x]))
    #out_w= lambda x,G: 0
    in_w= lambda x,G: sum((w_r[y[0]] for y in G.in_edges(x)))
    #in_w= lambda x,G: 0
    prune_w= lambda x,G: (out_w(x, G), in_w(x, G), x)

    # Construct three-partite graph
    leafs= set(filter(lambda x: is_leaf(T,x) , T))
    G= nx.DiGraph()
    G.add_nodes_from(chain(leafs,R_C,R_I))
    G.add_edges_from(((x,ri)
                      for ri in R_I
                      for x in ri
                     ))
    G.add_edges_from(((rc,x)
                      for rc in R_C
                      for x in rc
                     ))

    F= lambda leafs, G: sum(map(G.out_degree, leafs)) > 0
    flag= F(leafs, G)

    # Choose subset of leafs
    prune= []
    while flag:
        leaf= _choose_best(G, leafs, prune_w)
        prune+= [leaf]
        leafs= leafs-{leaf}
        del_I= list(G[leaf])
        del_C= list((y[0] for y in G.in_edges(leaf)))
        G.remove_nodes_from([leaf]+del_I+del_C)
        flag= F(leafs, G)

    # Obtain induced tree
    #leaf_names= [T.nodes[x][] for x in prune]
    for x in prune:
        T.remove_node(x)

    # Compcat edges if necesary
    if force_phylogeny:
        for x_node in list(dfs_postorder_nodes(T, T.root)):
            if is_leaf(T, x_node):
                if x_node not in leafs:
                    # Delete node
                    T.remove_node(x_node)
                    if x_node==T.root:
                        T.root= None
            else:
                children= list(T[x_node])
                if len(children) == 1:
                    x1= children[0]
                    if x_node==T.root:
                        T.root= x1
                    compact_edge(T, x_node, x1, delete= 'upper', update_lca= False)

    # Update LCA
    if update_lca:
        set_sparce_matrix(T)
    return T, prune

def _choose_best(G, leafs, prune_w):
    df= [prune_w(x,G) for x in leafs]
    best= sorted(df, reverse= True)[0][2]
    return best

def prune_triples(T, R, force_phylogeny= True, update_lca= True, inplace= True, root= 0):
    if not inplace:
        T= T.copy()
    T.root= root
    # Remove leafs present in the triples
    leaves= set(chain.from_iterable(R))
    for x in leaves:
        T.remove_node(x)

    # Compcat edges if necesary
    if force_phylogeny:
        nodes= list(filter(lambda x: len(T[x])==1,
                           dfs_postorder_nodes(T, T.root)
                          ))
        for x_node in nodes:
            x1= list(T[x_node])[0]
            if x_node==T.root:
                T.root= x1
            compact_edge(T, x_node, x1, delete= 'upper', update_lca= False)

    # Update LCA
    if update_lca:
        set_sparce_matrix(T)

    return T

def correct_tree_df(df, Ts, tree_col= 'tree',
                    root= 1,
                    label_attr= 'label',
                    species_attr= 'species',
                    event_attr= 'event',
                    algorithm= 'prune_L',
                    inplace= False
                   ):
    if not inplace:
        df= df.copy()
    # Prepare species triples
    for y in Ts:
        if len(Ts[y])>0:
            Ts.nodes[y][event_attr]= 'S'
    Ts_triples= set(get_triplets(Ts, event=event_attr, color=species_attr, root_event='S'))


    # Correct trees
    out= df[tree_col].progress_apply(lambda T: correct_tree(T, Ts_triples, root= root,
                                                            label_attr= label_attr,
                                                     species_attr= species_attr,
                                                     event_attr= event_attr,
                                                     algorithm= algorithm,
                                                     force_phylogeny= True,
                                                     update_lca= True,
                                                     inplace= True,
                ))
    df[tree_col]= out.str[0]
    df['inconsistent_triples']= out.str[1]
    df['prunned_leaves']= out.apply(lambda X: ','.join(map(str, X[2])) )
    return df

# Standalone usage
##################

if __name__ == "__main__":
    import pandas as pd

    import argparse
    parser = argparse.ArgumentParser(prog= 'revolutionhtl.tree_correction',
                                     description='Correction for gene tree with respect to a species tree',
                                     usage='python -m revolutionhtl.tree_correction <arguments>',
                                     formatter_class=argparse.MetavarTypeHelpFormatter,
                                    )

    # Arguments
    ###########

    # Input data
    # ..........

    parser.add_argument('gene_trees',
                        help= 'A .tsv file containing gene trees in the column specified by "-tree_column" in nhx format',
                        type= str,
                       )

    parser.add_argument('species_tree',
                        help= '.nhx file containing a species tree.',
                        type= str,
                       )

    # Parameters
    # ..........
    parser.add_argument('-alg', '--algorithm',
                        help= 'Algorithm for tree correction (default: prune_L).',
                        type= str,
                        choices= ['prune_L', 'prune_R'],
                        default= 'prune_L',
                       )

    # Format parameters
    # .................

    parser.add_argument('-T', '--tree_column',
                        help= 'Column containing trees in nhx format at the "gene_trees" file. (default: tree).',
                        type= str,
                        default= 'tree'
                       )

    parser.add_argument('-o', '--output_prefix',
                        help= 'Prefix used for output files (default "tl_project").',
                        type= str,
                        default= 'tl_project',
                       )

    parser.add_argument('-T_attr', '--T_attr_sep',
                        help= 'String used to separate attributes in the gene trees. (default: ";").',
                        type= str,
                        default= ';',
                       )

    parser.add_argument('-S_attr', '--S_attr_sep',
                        help= 'String used to separate attributes in the species tree. (default: ";").',
                        type= str,
                        default= ';',
                       )

    args= parser.parse_args()

    # Perform edition
    #################

    print('\n---------------------------')
    print('\nREvolutionH-tl tree edition')
    print('---------------------------\n')

    print('Reading gene trees...')
    gTrees= pd.read_csv(args.gene_trees, sep= '\t')
    gTrees[args.tree_column]= gTrees[args.tree_column].progress_apply(
        lambda x: read_nhx(x, name_attr= 'accession', attr_sep= args.T_attr_sep))

    print('Reading species tree...')
    with open(args.species_tree) as F:
        sTree= read_nhx(''.join( F.read().strip().split('\n') ),
                         name_attr= 'species',
                         attr_sep= args.S_attr_sep
                        )

    print('Editing trees...')
    gTrees= correct_tree_df(gTrees, sTree, tree_col= args.tree_column,
                    root= 1,
                            label_attr= 'accession',
                    species_attr= 'species',
                    event_attr= 'accession',
                    algorithm= args.algorithm,
                    inplace= False
                   )

    F= lambda T: get_nhx(T, root= T.root, name_attr= 'accession')
    gTrees.tree= gTrees.tree.apply(F)

    print('Writting corrected trees...')
    opath= f'{args.output_prefix}.corrected_trees.tsv'
    gTrees.to_csv(opath, sep= '\t', index= False)
    print(f'Successfully written to {opath}')
