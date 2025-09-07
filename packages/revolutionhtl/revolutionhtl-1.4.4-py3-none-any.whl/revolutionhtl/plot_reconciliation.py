

def plot(row, treeCol, muCol, Ts, eventAttr, leafLabelAttr, prefix, oformat):
    ax= plot_recon(row[treeCol], Ts, row[muCol],
                   eventAttr= eventAttr,
                   eventSymbols= {'S':'.r', 'D':'db'},
                   sColor= '#97a4bd',
                   gLineStyle= '-k',
                   sRoot= 0,
                   leafLabelAttr= leafLabelAttr,
                   leafLabelStyle= {'fontsize': 10, 'color': '#B37700'},
                   pipe_r= 2,
                   ax= None,
                   )
    SAVE(ax, row, prefix, oformat)
    return None

def SAVE(ax, row, prefix, oformat):
    opath1= f"{prefix}{row.OG}.{oformat}"
    ax.figure.savefig(opath1)
    print(f'Saved to {opath1}')


desc_def= """
"""


if __name__ == "__main__":
    from .plot_functions import plot_recon
    from .nhx_tools import read_nhx
    from .common_tools import norm_path, txtMu_2_dict, update_mu, add_eventAttr

    import argparse
    from importlib.metadata import version
    from pandas import read_csv
    from tqdm import tqdm
    tqdm.pandas()

    V_tl= version('revolutionhtl')
    txt= f'REvolutionH-tl: Reconstruction of Evolutionaty Histories TooL (V{V_tl})'

    parser = argparse.ArgumentParser(prog= 'revolutionhtl',
                                     description=f'{txt}{desc_def}',
                                     usage='python -m revolutionhtl <arguments>',
                                     formatter_class=argparse.MetavarTypeHelpFormatter,
                                    )

    #############
    # Arguments #
    #############

    parser.add_argument('OGs_mask',
                        help= '[str] List of orthogroups IDs to mask gene trees at the file "gene_trees"',
                        type= str,
                        nargs= '*',
                        default= None,
                       )

    parser.add_argument('-files_path',
                        help= '[str] Path of files outpued by REvolutionH-tl.',
                        type= norm_path,
                        #nargs='?',
                        default= './',
                       )

    parser.add_argument('--files_prefix',
                        help= '[str] Prefix of files outpued by REvolutionH-tl.',
                        type= str,
                        nargs='?',
                        default= 'tl_project.',
                       )


    args= parser.parse_args()
    ################
    # Process data #
    ################

    from .hello import hello5
    print(f'{hello5}V{V_tl}\n')

    prefix= f'{args.files_path}{args.files_prefix}'
    oformat= 'pdf'
    args.species_tree= f'{prefix}labeled_species_tree.nhx'
    args.gene_trees=   f'{prefix}reconcilied_trees.tsv'
    args.tree_column= 'tree'
    args.mu_column= 'reconciliation_map'
    args.OG_column= 'OG'
    args.event_attr= 'label'
    args.label_attr= 'label'
    args.node_id= 'node_id'

    # Load data
    #----------

    # Read species tree
    with open(args.species_tree) as F:
        Ts= read_nhx(''.join( F.read().strip().split('\n') ))
    # Read gene trees table
    df= read_csv(args.gene_trees, sep= '\t',  dtype= {args.OG_column:str})
    # Mask gene trees
    if args.OGs_mask:
        df= df[ df[args.OG_column].isin(args.OGs_mask) ]
    else:
        raise ValueError('Missing parameter: OGs_mask (list of orthogroup IDs to plot).')
    # Read gene trees
    df[args.tree_column]= df[args.tree_column].apply(read_nhx)
    # Set mu map in proper format
    df[args.mu_column]= df[args.mu_column].apply(txtMu_2_dict)
    # Set mu with nx node identifier
    df[args.mu_column]= df.apply(lambda row: update_mu(row[args.tree_column],
                                                    Ts, row[args.mu_column],
                                                    args.node_id, args.node_id),
                                 axis=1)
    df[args.mu_column].apply(lambda D: D.update({0:0}))
    # Add custom event attr
    customEventAttr= 'customEventAttr'
    F= lambda T: add_eventAttr(T, args.event_attr, customEventAttr)
    df[args.tree_column].apply(F)

    # Plot
    #-----
    F= lambda row: plot(row, args.tree_column, args.mu_column,
                        Ts, customEventAttr, args.label_attr, prefix, oformat)

    df.apply(F, axis= 1)
