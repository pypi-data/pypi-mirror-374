"""
Functions to run diamond

Includes standalon usage:
python -m revolutionhtl.diamond -h
"""

from .common_tools import norm_path
from .error import DirectoryExist

from tqdm import tqdm
from itertools import combinations, combinations_with_replacement
import os
from subprocess import run
from joblib import Parallel, delayed
# constants
_default_out_dir= 'tl_project_alignment_all_vs_all'
_default_fasta_ext='.fa'
_default_diamond='diamond'
_diamond_columns= 'qseqid sseqid qlen slen length bitscore evalue'.split()

# Functions

def diamond_all_vs_all(fastas_dir,
                       out_dir= _default_out_dir,
                       fasta_ext= _default_fasta_ext,
                       diamond= _default_diamond,
                       quiet= True,
                       evalue= 0.00001, identity= 25, cov= 50,
                       max_target_seqs= 25,
                       num_threads=1,
                       num_jobs=1
                      ):
    # Normalize and check directories
    fastas_dir, out_dir= _check_path(fastas_dir, out_dir)
    # List fasta files
    is_fasta= lambda x: x.endswith(fasta_ext)
    fasta_files= list(filter(is_fasta, os.listdir(fastas_dir)))
    # Create file names
    species= {file: '.'.join(file.split('.')[0:-1])
              for file in fasta_files}
    reference= {file:f'{out_dir}{species[file]}' for file in fasta_files}
    f_path= {file:f'{fastas_dir}{file}' for file in fasta_files}
    # Create index
    for file in tqdm(fasta_files, desc= 'Generating index'):
        std_out= diamond_makedb(diamond, f_path[file], reference[file], quiet= quiet)
    # Run pairwise
    n= len(fasta_files)
    if num_jobs==1:
        for query ,target in tqdm(combinations_with_replacement(fasta_files, 2), total= int(n*n/2),
                      desc= 'Running alignments'):

            fout= f'{out_dir}{species[query]}.vs.{species[target]}.diamond.alignment_hits'
            std_out= diamond_blastp(diamond, f_path[query],
                                reference[target], fout, quiet= quiet,
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               )
            if query!=target:
                fout= f'{out_dir}{species[target]}.vs.{species[query]}.diamond.alignment_hits'
                std_out= diamond_blastp(diamond, f_path[target],
                                reference[query], fout, quiet= quiet,
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               )
    else:
        diamond_both_ways = lambda query,target: ( diamond_blastp(diamond, f_path[query],
                                reference[target], f'{out_dir}{species[query]}.vs.{species[target]}.diamond.alignment_hits', quiet= quiet,
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               ), diamond_blastp(diamond, f_path[target],
                                reference[query], f'{out_dir}{species[target]}.vs.{species[query]}.diamond.alignment_hits', quiet= quiet,
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               ))
        Parallel(n_jobs=num_jobs,verbose=3)(delayed(diamond_both_ways)(query,target) for query,target in combinations(fasta_files, 2))

    # End

def diamond_makedb(diamond, fpath, f_reference, quiet= False, num_threads=1):
    command= [diamond, 'makedb',
            '-p', str(num_threads),
            '--in', fpath, '-d', f_reference]
    if quiet:
        command+= ['--quiet']
    return run(command)

def diamond_blastp(diamond, fpath, f_reference, f_out, quiet= False, evalue= 0.00001, identity= 25, cov= 50, max_target_seqs= 25, num_threads=1):
    command= [diamond, 'blastp',
            '-p', str(num_threads),
              '-d', f_reference, '-q', fpath, '-o', f_out,
              '-e', evalue, '--id', identity,
              '--query-cover', cov, '--subject-cover', cov, '-k', max_target_seqs,
              '-f', '6'
             ] + _diamond_columns
    command= list(map(str, command))
    if quiet:
        command+= ['--quiet']
    return run(command)

# Auxiliary function
####################

def _check_path(fastas_dir, out_dir):
    # Fastas directory
    fastas_dir= norm_path(fastas_dir)
    if not os.path.exists(fastas_dir):
        raise DirectoryExist(f'There is not directory "{fastas_dir}"')
    # ourput directory
    if out_dir==None:
        out_dir= fastas_dir
    else:
        out_dir= norm_path(out_dir)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
    # return
    return fastas_dir, out_dir

# Stand-alone usage
###################

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('fastas_dir', type= str)
    parser.add_argument('-o', '--out_dir', default= _default_out_dir, type= str)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-f_ext', '--fasta_ext', default= _default_fasta_ext, type= str)
    parser.add_argument('-d_command', '--diamond', default= _default_diamond, type= str)
    parser.add_argument('-e', '--evalue', default= 0.00001, type= float)
    parser.add_argument('-id', '--identity', default= 25, type= int)
    parser.add_argument('-cov', '--coverture', default= 50, type= int)
    parser.add_argument('-k', '--max_target_seqs', default= 25, type= int)
    args = parser.parse_args()

    # Run
    ######
    hello_diamond= "\n-------------------------------------------------"
    hello_diamond+= "\nRunnng DIAMOND to create REvolutionH-tl input files"
    hello_diamond+= "\n-------------------------------------------------\n"
    print(hello_diamond)
    diamond_all_vs_all(args.fastas_dir,
                       out_dir= args.out_dir,
                       fasta_ext= args.fasta_ext,
                       diamond= args.diamond,
                       quiet= not args.verbose,
                       evalue= args.evalue, identity= args.identity, cov= args.coverture,
                       max_target_seqs= args.max_target_seqs,
                      )
    print("Process finished succesffully\n")
