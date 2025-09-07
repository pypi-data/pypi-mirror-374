desc_def= """ | Steps :
1. Alignment hits computation
2. Best hit selection
3. Gene tree reconstruction and orthology inference
4. Species tree reconstruction
5. Gene and species trees reconciliation
6. Refine (New!!!) |
More details at: https://pypi.org/project/revolutionhtl/
"""

from itertools import chain
def check_species_in_trees(gTrees, sTree, color_attr='species'):
    all_species= gTrees.apply(lambda T: induced_colors(T, T.u_lca, color_attr=color_attr))
    all_species= set(chain.from_iterable(all_species.to_list()))
    connected_species= set(induced_colors(sTree,
                                          sTree.u_lca,
                                          color_attr=color_attr))
    missed_species= all_species - connected_species
    nMissed= len(missed_species)

    return missed_species, nMissed

e_message_0= lambda e: f'\nERROR:\n{e}\n'
e_message_1= "See the documentation at https://pypi.org/project/revolutionhtl/\nor run 'python -m revolutionhtl -h' to display help message.\n"




if __name__ == "__main__":
    from importlib.metadata import version
    from .constants import _default_f
    from .common_tools import norm_path
    import argparse


    V_tl= version('revolutionhtl')
    V_tl

    txt= f'REvolutionH-tl: Reconstruction of Evolutionaty Histories TooL (V{V_tl})'

    parser = argparse.ArgumentParser(prog= 'revolutionhtl',
                                     description=f'{txt}{desc_def}',
                                     usage='python -m revolutionhtl <arguments>',
                                     formatter_class=argparse.MetavarTypeHelpFormatter,
                                    )

    # Arguments
    ###########

    # Input data
    # ..........
    parser.add_argument('-steps',
                        help= 'List of steps to run (default: 1 2 3 4 5 6).',
                        type= int,
                        nargs= '*',
                        default= [1, 2, 3, 4, 5, 6]
                       )

    parser.add_argument('-F', '--fastas',
                        help= '[str | Input for step 1] Directory containing fasta files.',
                        type= str,
                        default= None
                       )

    parser.add_argument('-alignment_h', '--alignment_hits',
                        help= '[str | Input for steps 2 and 4] Directory containing alignment hits.',
                        type= norm_path,
                        default= None
                       )

    parser.add_argument('-OG', '--orthogroup_file',
                        help= f'[str | Optional input for step 2] File specifying orthogroups for the best hit graph construction.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('-best_h', '--best_hits',
                        help= '[str | Input for step 3] .tsv file containing best hits.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('-T', '--gene_trees',
                        help= '[str | Input for steps 4 and 5, and 6] .tsv file containing gene trees in nhx format.',
                        type= str,
                       )

    parser.add_argument('-D', '--distances',
                        help= '[str | Input for step 4] .tsv file containing gene-to-gene distances.',
                        type= str,
                        default= None,
                       )

    parser.add_argument('-S', '--species_tree',
                        help= '[str | Input for step 5] .nhx file containing a species tree.',
                        type= str,
                        default= None,
                       )

    # Parameters
    # ..........
    al_default= 'diamond'
    parser.add_argument('-aligner', '--aligner',
                        help= f'[str | Parameter for step 1 | Default: {al_default}] Command or path to the program for computation of aligment hits. Supported: diamond, blastn, blastp, blastx',
                        type= str,
                        default= al_default,
                       )
    parser.add_argument('-v', '--verbose_diamond', action='store_true',
                        help= '[flag | Parameter for step 1 ] Use to display diamond messages.')
    e_default= 0.00001
    parser.add_argument('-e', '--evalue', default= e_default, type= float,
                        help= f'[float | Parameter for step 1 | Default: {e_default}] Maximum evalue required to consider significant an aligment hit.'
                       )
    mk_def= 'makeblastdb'
    parser.add_argument('-m_command', '--makeblastdb', default= mk_def, type= str,
                        help= f'[str | Parameter for step 1 | Default: {mk_def}] BLAST command or path to the BLAST program for database creation.')
    id_def= 25
    parser.add_argument('-id', '--identity', default= id_def, type= int,
                        help= f'[float | Parameter for step 1 | Default: {id_def}] Minimum percentage of identity required to report an alignment hit.')
    cov_def= 50
    parser.add_argument('-cov', '--coverture', default= cov_def, type= int,
                        help= f'[float | Parameter for step 1 | Default: {cov_def}] Minimum percentage of query coverture required to report an alignment hit.')
    kh_def= 100
    parser.add_argument('-k_hits', '--max_target_seqs', default= kh_def, type= int,
                        help= f'[int | Parameter for step 1 | Default: {kh_def}] Maximum number of alignment hits per gene againist a fixed species.')

    num_threads_def= 1
    parser.add_argument('-t', '--num_threads', default= num_threads_def, type= int,
                        help= f'[int | Parameter for step 1 | Default: {num_threads_def}] Number of threads to use for diamond or blastp.')

    num_jobs_def= 1
    parser.add_argument('-j', '--num_jobs', default= num_jobs_def, type= int,
            help= f'[int | Parameter for step 1 | Default: {num_jobs_def}] Number of concurrent jobs to run for the aligner. Note: the total number of threads used will be num_threads*num_jobs. ')

    bhh_def= 'target'
    from .parse_prt import normalization_modes
    parser.add_argument('-bh_heuristic', '--besthit_heuristic',
                        help= f'[str | Parameter for step 2 | Default: {bhh_def}] Indicates how to normalize bit-score. Normalize by sequence lenght: query, target, alignment, smallest. No normalization: raw.',
                        type= str,
                        choices= normalization_modes,
                        default= bhh_def,
                       )

    parser.add_argument('-f', '--f_value',
                        help= f'[float | Parameter for step 2 | Defualt: {_default_f}] Number between 0 and 1. Defines the adaptative threshhold for best-hit selection as: f*max_bit_score.',
                        type= float,
                        default= _default_f,
                       )

    com_def= 'Louvain'
    com_opt= ['Mincut', 'BPMF', 'Karger', 'Greedy', 'Gradient_Walk', 'Louvain', 'Louvain_Obj']
    parser.add_argument('-bmg_h', '--bmg_heuristic',
                        help= f'[str | Parameter for step 3 | Defult: {com_def}] Comunity detection method for MaxConsistentTriples heuristic. Options: {", ".join(com_opt)}.',
                        type= str,
                        default= com_def,
                        choices= com_opt,
                       )

    parser.add_argument('-no_binary_R', '--no_binary_triples',
                        help= '[flag | Parameter for step 3 ] Use to avoid the usage of binary triples from best-hit graph.',
                        action= 'store_false',
                       )


    parser.add_argument('-f_bT', '--force_binary_gene_tree',
                        help= '[flag | Parameter for step 3 ] Use to force gene trees to be binary.',
                        action= 'store_true',
                       )

    parser.add_argument('-T_no_db', '--gene_tree_no_double_build',
                        help= '[flag | Parameter for step 3 ] Use to avoid running build twice in the MaxConsistentTriples heuristic.',
                        action= 'store_false',
                       )

    com_def= 'louvain_weight'
    com_opt= ['naive', 'louvain', 'mincut', 'louvain_weight']
    parser.add_argument('-stree_h', '--species_tree_heuristic',
                        help= f'[str | Parameter for step 4 | Default: {com_def}] Comunity detection method for MaxConsistentTriples heuristic. Options: {", ".join(com_opt)}.',
                        type= str,
                        default= com_def,
                        choices= com_opt
                       )

    sr_def= 3
    parser.add_argument('-streeh_repeats', '--stree_heuristic_repeats',
                        help= f'[int | Parameter for step 4 | Default: {sr_def}] Specifies how many times run the MaxConsistentTriples heuristic.',
                        type= int,
                        default= sr_def
                       )

    parser.add_argument('-streeh_b', '--streeh_binary',
                        help= '[flag | Parameter for step 4] Use to force specis tree to be binary.',
                        action= 'store_true',
                       )

    parser.add_argument('-streeh_ndb', '--streeh_no_doble_build',
                        help= '[flag | Parameter for step 4] Use to avoid running build twice in the MaxConsistentTriples heuristic.',
                        action= 'store_false',
                       )

    parser.add_argument('-n_edit_T', '--do_not_edit_inconsistent_trees',
                        help= '[flag | Prameter for step 5] Use to avoid editing of inconsistent gene trees.',
                        action= 'store_true',
                       )
    # Format parameters
    # .................

    pr_def= 'tl_project'
    parser.add_argument('-o', '--output_prefix',
                        help= f'[str | Default: {pr_def}] Prefix for output files.',
                        type= str,
                        default= pr_def,
                       )

    fa_def= '.fa'
    parser.add_argument('-fext', '--fasta_ext',
                        help= f'[str | Default: {fa_def}] Extesion for fasta files.',
                        type= str,
                        default= fa_def,
                       )

    parser.add_argument('--no_singletons',
                        help= "[flag | Prameter for step 2] Use to avoid singletons identification, i.e. genes that are in fasta files but are not assigned to an orthogroup.",
                        action= 'store_true',
                       )


    og_def= 'OG'
    parser.add_argument('-og', '--orthogroup_column',
                        help= f'[str | Default: {og_def}] Column specifying orthogroup ID in input and output .tsv files.',
                        type= str,
                        default= og_def,
                       )

    nm_def= 2000
    parser.add_argument('-Nm', '--N_max',
                        help= f'[int | Default: {nm_def}] Maximum number of genes in a orithogroup, bigger orthogroups are splitted. If 0, no orthogroup is splitted.',
                        type= int,
                        default= nm_def,
                       )

    sep_def= ';'
    parser.add_argument('-S_attr', '--S_attr_sep',
                        help= f'[str | Default: {sep_def}] Attribute delimiter in the input .nhx file (Input of step 5).',
                        type= str,
                        default= sep_def,
                       )

    args= parser.parse_args()

    ################
    # Process data #
    ################
    from .error import MissedData, ParameterError, InconsistentData
    from .nhx_tools import read_nhx, get_nhx
    from pandas import DataFrame, Series, read_csv
    from os import listdir, cpu_count
    from datetime import datetime

    from .hello import hello5
    print(f'{hello5}V{V_tl}\n')

    allowed_steps= {1, 2, 3, 4, 5, 6}
    bad_steps= set(args.steps) - allowed_steps
    if len(bad_steps) > 0:
        raise ParameterError(f'Only steps 1, 2, 3, 4, 5 and 6 are allowed to be used in the parameter -steps. ')
    else:
        args.steps= sorted(set(args.steps))

    print(f'Running steps {", ".join(map(str, args.steps))}')

    # set num_threads num_jobs
    cpu_count=cpu_count()
    num_threads=args.num_threads
    if num_threads <= 0:
        num_threads = num_threads_def
    if num_threads > cpu_count:
        num_threads=cpu_count
    num_jobs=args.num_jobs
    if num_jobs <= 0:
        num_jobs = num_jobs_def
    if num_jobs*num_threads > cpu_count:
        num_jobs=cpu_count//num_threads
    total_workers= num_jobs*num_threads
    print(f'Running {num_jobs} jobs usign {num_threads} threads each.')

    log_init= False
    logfile= f'{args.output_prefix}.log.txt'
    def log_print(message, logfile=logfile):
        with open(logfile, 'a') as F:
            F.write(message)


    try:
        DD= vars(args)
        keys= sorted(DD)
        log= (f'{k}={DD[k]}' for k in keys)
        log= '\n'.join(log)+'\n'
        log= f'> {datetime.now()}\n> REvolutionH-tl V{V_tl}\n{log}'
        log= f'----------------------------------------------\n{log}'
        log_print(log, logfile)
        log_init= True

        inputedFastas= type(args.fastas)==str
        inputed_alignment_hits= type(args.alignment_hits)==str
        inputed_best_hits= type(args.best_hits)==str
        inputed_distances= type(args.distances)==str
        inputedTg= type(args.gene_trees)==str
        inputedTs= type(args.species_tree)==str

        # 1. Alignment hits computation
        ###############################

        if 1 in args.steps:
            if not inputedFastas:
                raise MissedData('Step 1 needs a value for the parameter --fastas')
            print('\nStep 1: Alignment hits computation')
            print('----------------------------------')
            o_alignment_hits= f'{args.output_prefix}.alignment_all_vs_all/'


            print(f'Genomes for alignment: {args.fastas}*{args.fasta_ext}')

            if 'diamond' in args.aligner:
                from .diamond import diamond_all_vs_all
                diamond_all_vs_all(args.fastas,
                                   out_dir= o_alignment_hits,
                                   fasta_ext= args.fasta_ext,
                                   diamond= args.aligner,
                                   quiet= not args.verbose_diamond,
                                   evalue= args.evalue,
                                   identity= args.identity,
                                   cov= args.coverture,
                                   max_target_seqs= args.max_target_seqs,
                                   num_threads=num_threads,
                                   num_jobs=num_jobs
                                   )
            elif 'blast' in args.aligner:
                from .blast import blast_all_vs_all
                blast_all_vs_all(args.fastas,
                                 out_dir= o_alignment_hits,
                                 fasta_ext= args.fasta_ext,
                                 blast_command= args.aligner,
                                 makeblastdb= args.makeblastdb,
                                 evalue= args.evalue,
                                 identity= args.identity,
                                 cov= args.coverture,
                                 max_target_seqs= args.max_target_seqs,
                                 num_threads=num_threads,
                                 num_jobs=num_jobs
                        )
            else:
                ValueError(f'Unrecognized aligner "{args.aligner}"')
            log_print('> Step 1 completed\n')
            print(f'Alignment hits successfully written to {o_alignment_hits}')
            generated_hits= True
            if 2 in args.steps:
                print('This data will be used as input of step 2')
        else:
            generated_hits= False

        # 2. Best hit selection
        #######################
        if 2 in args.steps:
            from .parse_prt import _parse
            from pandas import isna
            print("\nStep 2: Best hit selection")
            print("--------------------------")

            if generated_hits:
                alignment_hits= o_alignment_hits
            elif inputed_alignment_hits:
                alignment_hits= args.alignment_hits
            else:
                raise MissedData('Step 2 needs a value for the parameter --alignment_hits. You can create it running step 1')
            print(f'Input alignment hits: {alignment_hits}*.alignment_hits')

            if not args.no_singletons:
                if inputedFastas:
                    fasta_path= norm_path(args.fastas)
                    text= f'\nInput fasta files: {fasta_path}*{args.fasta_ext}'
                    try:
                        fasta_files= {f'{fasta_path}{x}' for x in listdir(fasta_path) if x.endswith(args.fasta_ext)}
                    except FileNotFoundError as e:
                        raise MissedData(f'{e}')

                else:
                    raise MissedData('Step 2 needs the argument --fastas <fastas directory> for singletons identification.\nAlternatively, use --no_singletons flag.')
            else:
                fasta_files= None
                text= ''


            if args.orthogroup_file:
                print(f'Input orthogroups: {args.orthogroup_file}')
                from .parse_prt import load_orthogroups_df
                OGs_table= load_orthogroups_df(args.orthogroup_file)
            else:
                OGs_table= None

            df_hits, OGs_table, df_distances= _parse(alignment_hits,
                                       args.f_value,
                                       not args.no_singletons,
                                       fasta_files,
                                       args.besthit_heuristic,
                                       N_max= args.N_max,
                                       n_jobs= total_workers,
                                       OGs_table= OGs_table,
                                       )

            opath= args.output_prefix+'.best_hits.tsv'
            df_hits.reset_index(drop=True).to_csv(opath, sep='\t', index= False)
            print(f'Best hits successfully written to {opath}')


            opath= args.output_prefix+'.orthogroups.tsv'
            speciesCols= list(OGs_table.columns[3:])
            Fstr= lambda X: X if isna(X) else ','.join(X)
            OGs_table[speciesCols]= OGs_table[speciesCols].map(Fstr)
            OGs_table.to_csv(opath, sep='\t', index= False)
            del OGs_table
            print(f'Orthogroups successfully written to {opath}')

            opath= args.output_prefix+'.distances.tsv'
            df_distances.to_csv(opath, sep='\t', index= False)
            print(f'Distances successfully written to {opath}')

            if 3 in args.steps:
                print('These files will be used as input for step 3')

            log_print('> Step 2 completed\n', logfile)
            computed_best_hits= True
        else:
            computed_best_hits= False

        #######################################################
        # 3. Gene tree reconstruction and orthology inference #
        #######################################################
        if 3 in args.steps:
            from .hug_free import build_graph_series
            from .orthology import orthologs_from_trees_df
            from .in_out import read_tl_digraph, tl_digraph_from_pandas, write_digraphs_list

            print("\nStep 3: Gene tree reconstruction and orthology inference")
            print("--------------------------------------------------------")

            if computed_best_hits:
                print('Processing best hit graphs of step 2...')
                best_hit_G= tl_digraph_from_pandas(df_hits, og_col= args.orthogroup_column)
                del df_hits
            elif inputed_best_hits:
                print(f'Processing best hit graphs at {args.best_hits}...')
                best_hit_G= read_tl_digraph(args.best_hits, og_col= args.orthogroup_column)
            else:
                raise MissedData('Step 3 needs a value for the parameter -best_hits. You can create it by running step 2')


            # Store bit score and add weight for missed (non symmetric) hits
            F= lambda x,y,G0: (G0.nodes[x]['accession'], G0.nodes[y]['accession'])
            DD= {F(x,y,G0): G0[x][y]['weight'] for G0 in best_hit_G for (x,y) in G0.edges}
            missed= ((y,x) for (x,y) in DD if (y,x) not in DD)
            DD.update({(y,x): DD[(x,y)] for (y,x) in missed})

            print('Reconstructing BMG gene trees...')
            gTrees, best_hit_G= build_graph_series(best_hit_G, args)
            computedTg= True

            # Write trees and BMGs
            bmg_opath= f'{args.output_prefix}.best_matches.tsv'
            write_digraphs_list(best_hit_G, bmg_opath)
            print(f'Best match graph successfully written to {bmg_opath}')

            gtr_opath= f'{args.output_prefix}.gene_trees.tsv'
            Tgtxt= gTrees.copy()
            Tgtxt.tree= Tgtxt.tree.apply(lambda x: get_nhx(x, name_attr= 'accession'))
            Tgtxt.to_csv(gtr_opath, sep='\t', index= False)
            del Tgtxt
            print(f'BMG trees successfully written to {gtr_opath}')

            del best_hit_G

            if 4 in args.steps:
                print('These gene trees will be used as input for step 4')
            else:
                if 5 in args.steps:
                    print('These gene trees will be used as input for step 5')
                if 6 in args.steps:
                    print('These gene trees will be used as input for step 6')

            # Compute orthologs
            df_orthologs= orthologs_from_trees_df(gTrees, forbidden_leaf_name= 'X', tree_col= 'tree')
            # Add bit-score
            df_orthologs['Normalized_bit_score']= df_orthologs.apply(lambda row: DD.get((row.a, row.b),'*') , axis=1 )
            del DD

            # Print orthologs
            opath= f'{args.output_prefix}.orthologs.tsv'
            df_orthologs.to_csv(opath, sep= '\t', index= False)
            del df_orthologs
            print(f'Orthologs successfully written to {opath}')

            log_print('> Step 3 completed\n')

        else:
            computedTg= False

        ######################################
        # 4. Resolution of duplication nodes #
        ######################################
        if 4 in args.steps:

            print("\nStep 4: Refine duplications in BMG trees")
            print("----------------------------------------")

            from .parse_prt import load_hits_compute_scoredist
            from .tree_refinement import refine_df

            if computedTg:
                print(f'Using gene trees generated at step 3...')
            elif inputedTg:
                print(f'Reading gene trees from {args.gene_trees}')
                gTrees= read_csv(args.gene_trees, sep= '\t')
                gTrees.tree= gTrees.tree.apply(lambda x: read_nhx(x, name_attr= 'accession'))
            else:
                raise MissedData('Step 4 needs a value for the parameter --T. You can create it running step 3.')


            if computed_best_hits:
                print(f'Using distances generated at step 4...')
            elif inputed_distances:
                print(f'Reading distances from {args.distances}')
                #distances= load_hits_compute_scoredist(args.alignment_hits)
                df_distances= read_csv(args.distances, sep='\t')
            else:

                raise MissedData('Step 4 needs a value for the parameter --distances. You can create it running step 2.')

            gTrees, _= refine_df(df_distances, gTrees, label_attr= 'accession', inplace= True)

            del df_distances

            opath= f'{args.output_prefix}.resolved_trees.tsv'
            Tgtxt= gTrees.copy()
            Tgtxt.tree= Tgtxt.tree.apply(lambda x: get_nhx(x, name_attr= 'accession'))
            Tgtxt.to_csv(opath, sep='\t', index= False)
            del Tgtxt
            print(f'Resolved trees successfully written to {opath}')


            log_print('> Step 6 completed\n', logfile)


            if 5 in args.steps:
                print('These gene trees will be used as input for step 5')
            if 6 in args.steps:
                print('These gene trees will be used as input for step 6')


            resolvedTree= True
        else:
            resolvedTree= False

        # 5. Reconstruct species tree
        #############################
        if 5 in args.steps:
            from .supertree import from_gene_forest
            from .nxTree import induced_colors
            print("\nStep 5: Species tree reconstruction")
            print("-----------------------------------")

            if resolvedTree:
                print(f'Using gene trees generated at step 4...')
            elif computedTg:
                print(f'Using gene trees generated at step 3...')
            elif inputedTg:
                print(f'Reading gene trees from {args.gene_trees}')
                gTrees= read_csv(args.gene_trees, sep= '\t')
                gTrees.tree= gTrees.tree.apply(lambda x: read_nhx(x, name_attr= 'accession'))
            else:
                raise MissedData('Step 4 needs a value for the parameter -gene_trees. You can create it by running step 3')

            print("Reconstructing species tree...")
            species_tree= from_gene_forest(gTrees.tree,
                                           method= args.species_tree_heuristic,
                                           numb_repeats= args.stree_heuristic_repeats,
                                           doble_build= args.streeh_no_doble_build,
                                           binary= args.streeh_binary)
            # Check if all the species are present
            missed_species, nMissed= check_species_in_trees(gTrees.tree, species_tree)

            if nMissed > 0:
                txt= '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
                txt+= 'WARNING! There are not enough input trees for the\n'
                txt+= 'full reconstruction of species tree.\n'
                txt+= 'The resulting species tree will raise an error at step 5.\n'
                txt+= f'This tree misses {nMissed} species:\n'
                txt+= ', '.join(missed_species) + '\n'
                txt+= '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
                print(txt)
                log_print(txt, logfile)

            computedTs= True

            s_newick= get_nhx(species_tree, root= 1, name_attr= 'species', ignore_inner_name= True) + '\n'
            opath= f'{args.output_prefix}.species_tree.nhx'
            with open(opath, 'w') as F:
                F.write(s_newick+'\n')
            print(f'Species tree successfully written to {opath}')
            if 6 in args.steps:
                print('This species tree will be used as input for step 5')

            log_print('> Step 4 completed\n', logfile)
        else:
            computedTs= False

        # 6. Reconciliate gene trees and species tree
        ##############################################
        if 6 in args.steps:
            from .nxTree import induced_colors
            from .reconciliation import reconciliate_many, recon_table_to_str
            from networkx import DiGraph
            print("\nStep 6: Gene and species trees reconciliation")
            print("---------------------------------------------")

            if resolvedTree:
                print(f'Using gene trees generated at step 4...')
            elif computedTg:
                print(f'Using gene trees generated at step 3...')
            elif inputedTg:
                print(f'Reading gene trees from {args.gene_trees}')
                gTrees= read_csv(args.gene_trees, sep= '\t')
                gTrees.tree= gTrees.tree.apply(lambda x: read_nhx(x, name_attr= 'accession'))
            else:
                raise MissedData('Step 5 needs a value for the parameter -gene_trees. You can create it by running step 3')

            if computedTs:
                print(f'Using species tree generated at step 5...')
                sTree= species_tree
            elif inputedTs:
                print(f'Reading species tree from {args.species_tree}')
                with open(args.species_tree) as F:
                    sTree= read_nhx(''.join( F.read().strip().split('\n') ),
                                     name_attr= 'species', attr_sep= args.S_attr_sep)
            else:
                raise MissedData('Step 5 needs a value for the parameter -species_tree. You can create it by running step 4')

            # Check if the species tree has all the required species
            if not computedTs:
                missed_species, nMissed= check_species_in_trees(gTrees.tree, sTree, color_attr='species')
            if nMissed > 0:
                txt= f'Species tree is incomplete, it misses th species: {', '.join(missed_species)}.'
                raise MissedData(txt)

            if not args.do_not_edit_inconsistent_trees:
                from .tree_correction import correct_tree_df

                print('Editing inconsistent gene trees...')
                gTrees= correct_tree_df(gTrees, sTree, tree_col= 'tree', root= 1,
                                        label_attr= 'accession',
                                        species_attr= 'species',
                                        event_attr= 'accession',
                                        inplace= False
                                       )

                # Write to file
                F= lambda T: get_nhx(T, root= T.root, name_attr= 'accession')
                for_file= gTrees.copy()
                for_file.tree= for_file.tree.apply(F)
                opath= f'{args.output_prefix}.corrected_trees.tsv'
                for_file.to_csv(opath, sep= '\t', index= False)
                print(f'Corrected gene trees successfully written to {opath}')

            print('Reconciling trees...')
            gTrees= reconciliate_many(gTrees, sTree)
            reconciliedTg= True

            # Write resolved trees
            df_r= recon_table_to_str(sTree, gTrees, args.orthogroup_column)
            opath= f'{args.output_prefix}.reconcilied_trees.tsv'
            df_r.to_csv(opath, sep= '\t', index= False)
            print(f'Reconciliation successfully written to {opath}')

            # Write labeled species tree
            nhx_s= get_nhx(sTree, name_attr= 'species', root= sTree.u_lca, ignore_inner_name= True)
            opath= f'{args.output_prefix}.labeled_species_tree.nhx'
            with open(opath, 'w') as F:
                F.write(nhx_s+'\n')
            print(f'Indexed species tree successfully written to {opath}')

            log_print('> Step 5 completed\n', logfile)

        else:
            reconciliedTg= False



        print("\nREvolutionH-tl finished all the tasks without any problem")
        print("---------------------------------------------------------\n")

    except (MissedData, InconsistentData) as e:
        message= e_message_0(e) + "Please provide proper input data.\n" + e_message_1
        print(message)
        log_print('!!! '+message+'\n'+"---------------------------------------------------------\n", logfile)

    except PermissionError as e:
        message= e_message_0(e)
        print(message)
        if log_init:
            log_print('!!! '+message+'\n'+"---------------------------------------------------------\n", logfile)

    except NotImplementedError as e:
        message= e_message_0(e) + "We are working on this feature.\n" + e_message_1
        print(message)
        log_print('!!! '+message+'\n'+"---------------------------------------------------------\n", logfile)
