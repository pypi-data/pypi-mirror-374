from rpy2 import robjects
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
from pandas import isna

plt.style.use('fivethirtyeight')

def read_gene_trees(gTrees_path, OGs_mask, prefix, customEventAttr):
    df_rec= read_csv(gTrees_path, sep= '\t',  dtype= {'OG':str})
    # Mask gene trees
    if OGs_mask:
        df_rec= df_rec[ df_rec.OG.isin(OGs_mask) ]
    # Newick to nxTree
    df_rec.tree= df_rec.tree.apply(read_nhx)
    # Set mu map in proper format
    df_rec.reconciliation_map= df_rec.reconciliation_map.apply(txtMu_2_dict)
    # Set mu with nx node identifier
    df_rec.reconciliation_map= df_rec.apply(lambda row: update_mu(row.tree,
                                                    Ts, row.reconciliation_map,
                                                    'node_id', 'node_id'),
                                            axis=1)

    # Add custom event attr
    F= lambda T: add_eventAttr(T, 'label', customEventAttr)
    df_rec.tree.apply(F)
    return df_rec

desc_def= """
"""

class R_out:
    def __init__(self):
        self.capture_r_output()

    def capture_r_output(self):
        """
        Will cause all the output that normally goes to the R console,
        to end up instead in a python list.
        """
        # Import module #
        import rpy2.rinterface_lib.callbacks
        # Record output #
        self.stdout = []
        self.stderr = []
        # Dummy functions #
        def add_to_stdout(line): self.stdout.append(line)
        def add_to_stderr(line): self.stderr.append(line)
        # Keep the old functions #
        self.stdout_orig = rpy2.rinterface_lib.callbacks.consolewrite_print
        self.stderr_orig = rpy2.rinterface_lib.callbacks.consolewrite_warnerror
        # Set the call backs #
        #rpy2.rinterface_lib.callbacks.consolewrite_print     = add_to_stdout
        rpy2.rinterface_lib.callbacks.consolewrite_warnerror = add_to_stderr

if __name__ == "__main__":
    from .plot_functions import get_tree_layoult, add_numbers, init_numbers, plot_dendogram, og_class_statistics, get_leaves_pos, dfs_postorder_nodes
    from .common_tools import norm_path, txtMu_2_dict, update_mu, add_eventAttr
    from .nhx_tools import read_nhx
    from .nxTree import is_leaf, induced_leafs

    import argparse
    from importlib.metadata import version
    from pandas import read_csv
    import matplotlib.pyplot as plt
    from upsetplot import plot, UpSet

    from pandas import DataFrame, Series
    from collections import Counter
    from itertools import chain
    import seaborn as sns
    import matplotlib.patches as mpatches
    from math import ceil

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

    parser.add_argument('files_path',
                        help= '[str] Path of files outpued by REvolutionH-tl.',
                        type= norm_path,
                        nargs='?',
                        default= './',
                       )

    parser.add_argument('--files_prefix',
                        help= '[str] Prefix of files outpued by REvolutionH-tl.',
                        type= str,
                        nargs='?',
                        default= 'tl_project.',
                       )

    parser.add_argument('-S', '--species_tree',
                        help= '[str] .nhx file containing a species tree.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('-R', '--reconciled_trees',
                        help= '[str] .tsv file containing reconcilied trees in nhx format.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('-OG', '--orthogroup_file',
                        help= f'[str] File specifying orthogroups.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('-OR', '--orthologs_file',
                        help= f'[str] File specifying orthology relations.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('--species_order',
                        help= '[str] List of species in the desired order to plot.',
                        type= str,
                        nargs= '*',
                        default= None,
                       )

    parser.add_argument('--OGs_mask',
                        help= '[str] List of orthogroups IDs to mask gene trees at the file "gene_trees"',
                        type= str,
                        nargs= '*',
                        default= None,
                       )

    parser.add_argument('--size',
                        help= '[float | default: 10] size of the side of the output figures',
                        type= float,
                        default= 10,
                       )

    """
    parser.add_argument('--percentage_upsetplot',
                        help= '[int | default: 100] percentage of rows shown in upsetplot.',
                        type= int,
                        default= 100,
                       )
    """

    args= parser.parse_args()

    from .hello import hello5
    print(f'{hello5}V{V_tl}\n')

    f_name= lambda name: f"{prefix}{name}.pdf"

    ####################
    # Define constants #
    ####################
    customEventAttr= 'customEventAttr'
    prefix= f'{args.files_path}{args.files_prefix}'

    numbers_path= f'{prefix}gene_counts_reconciliation.tsv'
    upset_path= f'{prefix}orthogroups_upset.tsv'
    path_single_vs_multy= f"{prefix}single_vs_multy_copy_orthogroups.tsv"
    path_species_per_og= f"{prefix}species_per_orthogroup.tsv"
    path_og_relations= f"{prefix}orthogroups_relations.tsv"
    path_orthologs_per_gene= f"{prefix}orthologs_per_gene.tsv"

    if args.species_tree:
        s_tree_path_py= args.species_tree
    else:
        s_tree_path_py= f'{prefix}labeled_species_tree.nhx'

    if args.reconciled_trees:
        gTrees_path= args.reconciled_trees
    else:
        gTrees_path= f'{prefix}reconcilied_trees.tsv'

    if args.orthogroup_file:
        OGs_path= args.orthogroup_file
    else:
        OGs_path= f'{prefix}orthogroups.tsv'

    if args.orthologs_file:
        orthologs_path= args.orthologs_file
    else:
        orthologs_path= f'{prefix}orthologs.tsv'

    #############
    # Load data #
    #############
    print("Loading data...")
    # Species tree
    #-------------
    with open(s_tree_path_py) as F:
        Ts= read_nhx(''.join( F.read().strip().split('\n') ))

    # Species order and sorted leaves
    #--------------------------------
    if not args.species_order:
        _,_,_,aux= get_leaves_pos(Ts)
        args.species_order= [Ts.nodes[x]['label'] for x in aux]
    # Create a list of leaves sorted as specified by args.species_order
    label2node= {Ts.nodes[x]['label']:x for x in Ts if is_leaf(Ts,x)}
    sorted_leaves= [label2node[x] for x in args.species_order]

    # Gene trees table
    #-----------------
    df_rec= read_gene_trees(gTrees_path, args.OGs_mask, prefix, customEventAttr)

    # Orthogroups
    #------------
    df_ogs= read_csv(OGs_path, sep='\t').set_index('OG')
    if args.OGs_mask:
        try:
            df_ogs= df_ogs.loc[args.OGs_mask]
        except Exception as e:
            raise ValueError('The mask of orthogroups contain non-existing IDs.')

    singletonMask= df_ogs.n_genes==1
    # Sort columns of orthogroups dataframe
    df_ogs= df_ogs[ args.species_order ]
    # Count genes at each cell of orthogroups dataframe.
    F= lambda X: 0 if isna(X) else len(X.split(','))
    df_ogs= df_ogs.map(F)


    # Singletones
    #------------
    singletons= df_ogs[singletonMask].apply(lambda col: col.dropna().sum())
    singletons.name = "Singletons"  # Asigna nombre a la Serie
    singletons.index.name = "species"  # Asigna nombre al índice

    # Orthologs
    #----------
    df_orth= read_csv(orthologs_path, sep='\t')

    ################
    # Process data #
    ################
    print("Processing data...")

    # Species tree
    #-------------
    s_numbers= init_numbers(Ts)
    # Add reconcilied gene trees
    F= lambda row: add_numbers(row.tree, Ts, row.reconciliation_map, s_numbers)
    df_rec.progress_apply(F, axis= 1)
    # Add singletons
    for vNode in induced_leafs(Ts, Ts.u_lca):
        s_numbers[vNode]['Sr']+= singletons[Ts.nodes[vNode]['label']]

    df_numbers= [[Ts.nodes[vNode]['node_id'], # node_id
                  Dcounts['Dr'],              # duplication_roots
                  Dcounts['D'],               # gene_gain_by_duplication
                  Dcounts['Sr'],              # speciation_roots
                  Dcounts['S'],               # genes_at_speciation
                  Dcounts['X'],               # gene_loss
                 ]
                 for vNode,Dcounts in s_numbers.items() if vNode!=Ts.root]
    df_numbers= DataFrame(df_numbers, columns= ['node_id','duplication_roots','gene_gain_by_duplication','speciation_roots','genes_at_speciation','gene_loss'])
    df_numbers.to_csv(numbers_path,sep='\t',index=False)

    """
    # UpSetPlot
    #----------
    class_statistics= og_class_statistics(df_ogs, args.species_order)

    nrows= class_statistics.shape[0]
    showRows= ceil( nrows*(args.percentage_upsetplot/100) )

    class_statistics.to_csv(upset_path)
    """

    # Barplots
    #---------
    dropzero= lambda series: series[series!=0]

    # How many times an species apper in single copy OG vs multy copy?
    species_is_present= df_ogs>0
    OG_is_single_copy= df_ogs[~singletonMask].apply(lambda row: (dropzero(row)==1).all(), axis=1)
    class_single_copy= DataFrame({'Single copy' : species_is_present[~singletonMask].apply( lambda X: X & OG_is_single_copy ).sum(),
                                  'Multi copy' : species_is_present[~singletonMask].apply( lambda X: X & ~OG_is_single_copy ).sum(),
                                 })
    class_single_copy.index.name= 'species'

    # How many times an species apper in an orthogroup with N species?
    count_species= lambda X: dropzero(X).shape[0]
    mask_sp= lambda species: df_ogs.loc[species_is_present[species]]
    class_n_species= DataFrame({species:Counter(mask_sp(species).apply(count_species, axis=1))
                                for species in df_ogs.columns})
    class_n_species.index.name= 'n_species'
    class_n_species.columns.name= None
    class_n_species= class_n_species.T
    class_n_species.index.name= 'species'

    class_n_species= class_n_species[ sorted(class_n_species.columns) ]
    if 1 in class_n_species.columns:
        class_n_species.rename(columns= {1: 'singletons'}, inplace=True)
        class_n_species= class_n_species.drop('singletons', axis= 1)

    # How many times an species have a gene with N orthologs?
    def get_n_orthologs_per_gene(df):
        df= DataFrame(chain(df[['species_a','a']].values,  df[['species_b','b']].values),
                      columns= ['species','gene'])
        df['one']= 1
        df= df.groupby('species')[['gene', 'one']].apply( lambda df: df.groupby('gene').one.sum().values ).to_dict()
        df= DataFrame([[species,x] for species,X in df.items() for x in X],
                      columns= ['species','n'])
        return df.set_index('species').n
    class_n_orthologs= get_n_orthologs_per_gene(df_orth)
    class_n_orthologs= class_n_orthologs.fillna(0).reset_index()

    # Convert to table...
    #class_n_orthologs= class_n_orthologs.groupby('species').apply(Counter)
    #auxLevel= sorted(set(class_n_orthologs.reset_index().level_1))
    #class_n_orthologs= DataFrame([[class_n_orthologs[(species, N)]
    #                               for N in auxLevel]
    #                              for species in args.species_order],
    #                             columns= auxLevel,
    #                             index= args.species_order,
    #                            )


    # For each species classify orthogroups as 1-1, 1-n, n-1, n-m
    species_is_single_copy= df_ogs==1
    species_is_multiple_copy= df_ogs>1

    species_is_1_n= lambda species: (species_is_single_copy[species] & species_is_multiple_copy.drop(species, axis=1).any(axis=1) ).sum()
    species_is_n_1= lambda species: (species_is_multiple_copy[species] & species_is_single_copy.drop(species, axis=1).all(axis=1) ).sum()
    species_is_n_m= lambda species: (species_is_multiple_copy[species] & species_is_multiple_copy.drop(species, axis=1).any(axis=1) ).sum()

    class_nm_orthogroups= DataFrame({'1-1' : species_is_present[~singletonMask].apply( lambda X: X & OG_is_single_copy ).sum(),
                                     '1-n' : {species: species_is_1_n(species) for species in df_ogs.columns},
                                     'n-1' : {species: species_is_n_1(species) for species in df_ogs.columns},
                                     'n-m' : {species: species_is_n_m(species) for species in df_ogs.columns},
                                    })
    class_nm_orthogroups.index.name= 'species'



    ################
    # Plot figures #
    ################

    # Species tree
    #-------------
    fig, ax= plt.subplots(1,1, figsize= (3*args.size,args.size))
    num_species = len(Ts.nodes)
    fontsize = max(7, 15 - int(num_species / 10))

    with plt.rc_context({'lines.linewidth': 3, 'font.size': fontsize}):
        plot_dendogram(Ts, s_numbers, ax, sorted_leaves=sorted_leaves)

    ax.axis('off')

    legend_elements = [
    Line2D([0], [0], color='blue', lw=4, label='Duplications'),
    Line2D([0], [0], color='red', lw=4, label='Losses'),
    Line2D([0], [0], color='green', lw=4, label='Genes'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=fontsize + 4)

    filename_tree = f_name("species_tree")
    fig.savefig(filename_tree, format="pdf", bbox_inches="tight")
    print(f'Written to {filename_tree}')

    width, height = fig.get_size_inches()
    uniform_figsize = (0.98*width, 1.5*height)

    # UpSet plot
    #-----------
    """
    upset= UpSet(class_statistics, sum_over='No. OGs',
                 sort_categories_by='input',
                 sort_by= '-cardinality',
                 intersection_plot_elements= 0,
                 orientation= 'vertical',
                 max_subset_rank= showRows,
                )
    upset.add_catplot(value="No. OGs", kind="bar", color="gray")
    upset.add_catplot(value="No. genes", kind="bar", color="gray")
    upset.add_catplot(value="Av. genes per OG", kind="bar", color="gray")
    upset.add_catplot(value="Av. genes per species", kind="bar", color="gray")

    upset.plot()

    fig= plt.gcf()
    fig.set_size_inches(3*args.size,args.size)

    filename_upset = f_name("upset_plot")
    fig.savefig(filename_upset, format="pdf", bbox_inches="tight")
    print(f'Written to {filename_upset}')
    """

    # Barplots
    #---------
    class_single_copy = class_single_copy[class_single_copy.columns[::-1]]
    class_n_species_reversed = class_n_species[class_n_species.columns[::-1]]
    class_nm_orthogroups = class_nm_orthogroups[class_nm_orthogroups.columns[::-1]]

    class_n_species_filtered = class_n_species_reversed.drop(columns=["Singletones"], errors="ignore")

    fig, axs = plt.subplots(5, 1, sharex=True, figsize=uniform_figsize)

    class_single_copy.plot.bar(stacked=True, ax=axs[0], rot=0, legend='reverse')
    class_n_species_reversed.plot.bar(stacked=True, ax=axs[1], rot=0, legend='false')
    class_nm_orthogroups.plot.bar(stacked=True, ax=axs[2], rot=0, legend='reverse')
    #class_n_orthologs.plot.bar(ax=axs[3], stacked=False, rot=0, width=0.5, legend='reverse')
    sns.violinplot(x='species',y='n', data=class_n_orthologs, ax = axs[3], color='#54b4b0')
    singletons.plot.bar(ax=axs[4], rot=0, color='#54b4b0')


    # remove blue color
    #tab10_colors = list(plt.get_cmap("tab10").colors)
    #blue_rgb = tab10_colors[0]
    #filtered_colors = [color for color in tab10_colors if color != blue_rgb]
    #class_n_species_filtered.plot.bar(ax=axs[3], stacked=False, rot=0, width=0.5, legend='reverse', color=filtered_colors[:len(class_n_species_filtered)])
    #

    axs[0].set_ylabel('Orthogroups')
    axs[1].set_ylabel('Orthogroups')
    axs[2].set_ylabel('Orthogroups')
    axs[3].set_ylabel('Orthologs')
    axs[4].set_ylabel('Genes')

    axs[0].set_title('Single vs multy copy orthogroups')
    axs[1].set_title('Species per orthogroup')
    axs[2].set_title('Orthology relations')
    axs[3].set_title('Orthologs per gene')
    axs[4].set_title('Singletons')


    filename_barplots = f_name("barplots")
    fig.savefig(filename_barplots, format="pdf", bbox_inches="tight")
    print(f'Written to {filename_barplots}')

    # Save dfs
    #class_single_copy
    table_single_copy = class_single_copy.copy()
    table_single_copy['Total'] = table_single_copy.sum(axis=1)
    table_single_copy.to_csv(path_single_vs_multy, sep="\t", float_format="%.0f")

    #class_n_species_reversed
    table_n_species = class_n_species_reversed.copy()
    table_n_species['Total'] = table_n_species.sum(axis=1)
    table_n_species.to_csv(path_species_per_og, sep="\t", float_format="%.0f")

    #class_nm_orthogroups
    table_nm_orthogroups = class_nm_orthogroups.copy()
    table_nm_orthogroups['Total'] = table_nm_orthogroups.sum(axis=1)
    table_nm_orthogroups.to_csv(path_og_relations, sep="\t", float_format="%.0f")

    #class_n_orthologs
    stats_orthologs = class_n_orthologs.groupby('species')['n'].describe(percentiles=[0.25, 0.5, 0.75])
    stats_orthologs = stats_orthologs[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    stats_orthologs.rename(columns={'50%': 'median'}, inplace=True)
    stats_orthologs.to_csv(path_orthologs_per_gene, sep="\t", float_format="%.2f")


####

    from PyPDF2 import PdfReader, PdfWriter

    pdf_writer = PdfWriter()

    pdf_files = [filename_tree, filename_barplots]


    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            pdf_writer.add_page(page)

    outName= f_name('reconciliation_tree')
    with open(outName, 'wb') as f:
        pdf_writer.write(f)
    print(f'Written to {outName}')

####

    ##################
    # Plot R summary #
    ##################
    from .r_plot_summary import modules

    # Run R modules
    rout= R_out()
    robjects.r( modules.Module_1 )
    robjects.r(f'bars_log <- FALSE')
    robjects.r(f'species_tree_file <- "{s_tree_path_py}"')
    robjects.r(f'numbers_file <- "{numbers_path}"')
    robjects.r( modules.Module_2 )
    robjects.r( modules.Module_3 )
    robjects.r( modules.Module_4 )
    robjects.r( modules.Module_5 )
    robjects.r( f'o_format <- "pdf"' )
    robjects.r( f'prefix <- "{prefix}"' )
    robjects.r( modules.Module_6 )

    #filename_geneContent = f_name("change_gene_content")
    #print(f'Written to {filename_geneContent}')

    from datetime import datetime

    message= lambda log: f'> {datetime.now()}\n> REvolutionH-tl V{V_tl}\n{log}\n'
    opath= f"{prefix}r_stderr.txt"
    with open(opath, 'a') as F:
        F.write(message(''.join(rout.stderr)))
    print(f'Written to {opath}')

    #######
    # End #
    #######
