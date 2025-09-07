"""
Functions to run blast

Includes standalon usage:
python -m revolutionhtl.blast -h
"""

from .common_tools import norm_path
from .error import DirectoryExist

from tqdm import tqdm
from itertools import combinations
import os
from subprocess import run
from joblib import Parallel, delayed
# constants
_default_out_dir= 'tl_project_alignment_all_vs_all'
_default_fasta_ext='.fa'
_default_blast='blastn'
_default_makeblastdb='makeblastdb'
_blast_columns= 'qseqid sseqid qlen slen length bitscore evalue'

# Functions
def blast_all_vs_all(fastas_dir,
                     out_dir= _default_out_dir,
                     fasta_ext= _default_fasta_ext,
                     blast_command= _default_blast,
                     makeblastdb= _default_makeblastdb,
                     evalue= 0.00001,
                     identity= 25,
                     cov= 50,
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
    # Set fasta type
    dbtype= _blast_2_seq_type(blast_command)
    # Create index
    for file in tqdm(fasta_files, desc= 'Generating index'):
        std_out= blast_makedb(makeblastdb, f_path[file], reference[file], dbtype)
    # Run pairwise
    n= len(fasta_files)
    if num_jobs==1:
        for query ,target in tqdm(combinations(fasta_files, 2), total= int(n*n/2),
                      desc= 'Running alignments'):

            fout= f'{out_dir}{species[query]}.vs.{species[target]}.blast.alignment_hits'
            std_out= blast_blastp(blast_command, f_path[query],
                                reference[target], fout,
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               )

            fout= f'{out_dir}{species[target]}.vs.{species[query]}.blast.alignment_hits'
            std_out= blast_blastp(blast_command, f_path[target],
                                reference[query], fout,
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               )
    else:
        blast_both_ways = lambda query, target: ( blast_blastp(blast_command, f_path[query],
                                reference[target], f'{out_dir}{species[query]}.vs.{species[target]}.blast.alignment_hits',
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               ), blast_blastp(blast_command, f_path[target],
                                reference[query], f'{out_dir}{species[target]}.vs.{species[query]}.blast.alignment_hits',
                                evalue= evalue, identity= identity, cov= cov,
                                max_target_seqs= max_target_seqs, num_threads=num_threads
                               ))
        Parallel(n_jobs=num_jobs,verbose=3)(delayed(blast_both_ways)(query,target) for query,target in combinations(fasta_files, 2))

    # End

def blast_makedb(makeblastdb, fpath, f_reference, dbtype):
    command= [makeblastdb, '-in', fpath,
              '-dbtype', dbtype,
              '-out', f_reference,
             ]
    return run(command)

def blast_blastp(blast_command, fpath, f_reference, f_out, evalue= 0.00001, identity= 25, cov= 50, max_target_seqs= 25, num_threads=1):
    command= [blast_command,
              '-num_threads', num_threads,
              '-db', f_reference, '-query', fpath, '-out', f_out,
              '-evalue', evalue,
              '-qcov_hsp_perc', cov,
              '-max_target_seqs', max_target_seqs,
              '-outfmt', f'6 {_blast_columns}'
             ]
    if blast_command=='blastn':
        command+= ['-perc_identity', identity]

    command= list(map(str, command))
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

def _blast_2_seq_type(blast_command):
    if 'blastn' in blast_command:
        return 'nucl'
    elif 'blastp' in blast_command:
        return 'prot'
    elif 'blastx' in blast_command:
        raise ValueError('blastx not suported yet')
    raise ValueError(f'Command {blast_command} not recognized')
    return None

# Stand-alone usage
###################

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('fastas_dir', type= str)
    parser.add_argument('-o', '--out_dir', default= _default_out_dir, type= str)
    parser.add_argument('-f_ext', '--fasta_ext', default= _default_fasta_ext, type= str)
    parser.add_argument('-b_command', '--blast', default= _default_blast, type= str, choices= ['blastn', 'blastp'])
    parser.add_argument('-m_command', '--makeblastdb', default= _default_makeblastdb, type= str)
    parser.add_argument('-e', '--evalue', default= 0.00001, type= float)
    parser.add_argument('-id', '--identity', default= 25, type= int)
    parser.add_argument('-cov', '--coverture', default= 50, type= int)
    parser.add_argument('-k', '--max_target_seqs', default= 25, type= int)
    args = parser.parse_args()

    # Run
    ######
    hello_blast= "\n-------------------------------------"
    hello_blast+= "\nRunnng BLAST to compute alignment hits"
    hello_blast+= "\n------------------------------------\n"
    print(hello_blast)
    blast_all_vs_all(args.fastas_dir,
                     out_dir= args.out_dir,
                     fasta_ext= args.fasta_ext,
                     blast_command= args.blast,
                     makeblastdb= args.makeblastdb,
                     evalue= args.evalue,
                     identity= args.identity,
                     cov= args.coverture,
                     max_target_seqs= args.max_target_seqs,
                    )
    print("Process finished succesffully\n")
