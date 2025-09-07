from .nxTree import induced_leafs, is_leaf
from revolutionhtl.triplets import get_triplets

import pandas as pd
from itertools import chain, combinations, product
from tqdm import tqdm
tqdm.pandas()

def get_orthologs(T, x= None, event= 'S', event_attr= 'event', label_attr= 'label', forbidden_nodes= [], forbidden_leaf_name= 'X'):
    """
    returns a list of lists, where each sublist is a pair of orthologous nodes
    i.e. leafs of the tree `T` such that their last common ancestor is an event of type `event`.
    """
    return _rec_orthologs(T,
                          forbidden_nodes,
                          forbidden_leaf_name,
                          x= x,
                          event= event,
                          event_attr= event_attr,
                          label_attr= label_attr)

def orthologs_from_trees_df(df, forbidden_leaf_name= 'X', tree_col= 'gene_tree', orthogroup_column= 'OG'):
    df_orthologs= df.progress_apply(lambda row: _get_row_orth_table(row,
                                                                    tree_col,
                                                                    [],
                                                                    forbidden_leaf_name,
                                                                    'S',
                                                                    orthogroup_column,
                                                                   ), axis= 1)
    df_orthologs= pd.DataFrame(list(chain.from_iterable(df_orthologs)), columns= ['a', 'b', 'species_a', 'species_b', orthogroup_column])
    return df_orthologs

def _get_row_orth_table(row, tree_col, forbidden_nodes, forbidden_leaf_name, s_event, orthogroup_column):
    ind_leafs,orths= get_orthologs(row[tree_col],
                         event= s_event,
                         event_attr= 'accession',
                         label_attr= 'accession',
                         forbidden_nodes= forbidden_nodes,
                         forbidden_leaf_name= forbidden_leaf_name
                        )
    DD= {row[tree_col].nodes[x]['accession'] : row[tree_col].nodes[x]['species']
         for x in row[tree_col] if row[tree_col].nodes[x]['accession'] in ind_leafs}
    orths= (list(X) for X in orths)
    return [X + [DD[X[0]], DD[X[1]], row[orthogroup_column]] for X in orths]

def _rec_orthologs(T,
                   forbidden_nodes,
                   forbidden_leaf_name,
                   x= None,
                   event= 'S',
                   event_attr= 'event',
                   label_attr= 'label',
                  ):
    """
    Recursive function: a pos-order DFS traveling throug the nodes of 'T'.
    At each step it is returned the induced leaves and orthology relations induced
    by the node 'x'.
    """
    if x==None:
        x= T.root

    leaf_name= T.nodes[x][label_attr]
    if is_leaf(T, x) and leaf_name != forbidden_leaf_name:
        induced_leafs= [ leaf_name ]
        orths= []
    else:
        lefs_wrt_children= []
        orths= []
        for y in T[x]:
            y_leafs, y_orths= _rec_orthologs(T,
                                             forbidden_nodes,
                                             forbidden_leaf_name,
                                             x= y,
                                             event= event,
                                             event_attr= event_attr,
                                             label_attr= label_attr
                                            )
            lefs_wrt_children+= [y_leafs]
            orths+= y_orths

        induced_leafs= list(chain.from_iterable(lefs_wrt_children))

        if T.nodes[x][event_attr] == event and x not in forbidden_nodes:
            orths+= [set((a,b))
                     for A,B in combinations(lefs_wrt_children, 2)
                     for a,b in product(A,B)]

    return induced_leafs, orths

###############################
###############################
###############################

if __name__ == "__main__":
    import argparse
    from .nhx_tools import read_nhx

    parser = argparse.ArgumentParser(prog= 'revolutionhtl.orthology',
                                     description='Obtain orthology relations from a list of gene trees.',
                                    )
    # Parameters
    ############
    parser.add_argument('trees',
                        help= '.tsv file containing a gene tree in .nhx format (new newick) for each row in the column specified by -c',
                        type= str,
                       )

    parser.add_argument('-tc', '--tree_column',
                        help= 'column name for gene trees in the input .tsv file. (default="tree")',
                        default="tree",
                        type= str,
                       )

    parser.add_argument('-oc', '--orthogroup_column',
                        help= 'column name for gene trees ID in the input .tsv file. (default="OG")',
                        default="OG",
                        type= str,
                       )

    parser.add_argument('-l', '--loss_leafs',
                        help= 'Label of the leafs associated with a gene loss event. (default="X")',
                        default="X",
                        type= str,
                       )

    parser.add_argument('-o', '--output_prefix',
                    help= 'Prefix used for output files (default "tl_project").',
                    type= str,
                    default= 'tl_project',
                   )

    args= parser.parse_args()

    # Run program
    #############
    print('\n')
    print('revolutionhtl.orthology')
    print('----------------------------\n')

    # Read input
    print('Reading trees...')
    df_trees= pd.read_csv(args.trees, sep= '\t')
    df_trees[ args.tree_column ]= df_trees[ args.tree_column ].apply(lambda x: read_nhx(x, name_attr= 'accession'))

    # Run
    print('Computing orthology...')
    df_orthologs= orthologs_from_trees_df(df_trees,
                                          forbidden_leaf_name= args.loss_leafs,
                                          tree_col= args.tree_column,
                                          orthogroup_column= args.orthogroup_column
                                         )

    # Write output
    print('Writing results...')
    opath= f'{args.output_prefix}.orthologs.tsv'
    df_orthologs.to_csv(opath, sep= '\t', index= False)
    print(f'Orthologs successfully written to {opath}')
#
