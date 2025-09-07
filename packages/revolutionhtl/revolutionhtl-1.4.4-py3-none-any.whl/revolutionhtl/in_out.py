import pandas as pd
import networkx as nx
from itertools import chain
from tqdm import tqdm
tqdm.pandas()

_quey_target= ['Query', 'Target']

def get_og_order(og_list):
    og_order= []
    for ogId in og_list:
        if ogId not in og_order:
            og_order+= [ogId]
    return og_order


def tl_digraph_from_pandas(df, og_col= None):
    if og_col==None:
        og_col= 'OG'
        df[og_col]= 0

    og_order= get_og_order(df[og_col].to_list())

    df= df.set_index(og_col)
    return df.groupby(og_col).progress_apply(create_cBMG).loc[og_order]

def read_tl_digraph(path, og_col= None):
    df= pd.read_csv(path, sep= '\t')
    return tl_digraph_from_pandas(df, og_col)

def write_digraphs_list(G, output_prefix= 'tl_project', n_attrs= ['accession', 'species'], mode= 'w', header= True):
    df= []
    for og, X in zip(G.index, G):
        df+= [ _get_edge_row(X, e, og, n_attrs) for e in X.out_edges ]
    df= pd.DataFrame(df, columns= get_digraph_cols(n_attrs))
    df.to_csv(output_prefix, sep= '\t', index= False, mode= mode, header= header)

def get_digraph_cols(n_attrs= ['accession', 'species']):
    return ['OG'] + [mod+'_'+attr for mod in _quey_target for attr in n_attrs]

def _get_edge_row(X, e, og, n_attrs):
    return [og] + [X.nodes[n][attr] for n in e for attr in n_attrs] #+ list(e)

def create_cBMG(df):
    try:
        og= df.index[0]
    except:
        print(df)
        1/0
    cBMG= nx.DiGraph()
    cBMG.og= og

    genes= set(df.Query_accession).union(df.Target_accession)
    DD= {x:i for i,x in enumerate(genes)}

    aux= chain.from_iterable((df[['Query_accession', 'Query_species']].drop_duplicates().values,
                              df[['Target_accession', 'Target_species']].drop_duplicates().values
                             ))
    aux= pd.DataFrame(list(aux)).drop_duplicates().values

    for gene,species in aux:
        cBMG.add_node(DD[gene],
                      species= species,
                      accession= gene,
                     )

    edges= df.apply(lambda row: (DD[row.Query_accession], DD[row.Target_accession], row.Normalized_bit_score),
                    axis= 1
                   )
    cBMG.add_weighted_edges_from( edges )
    return cBMG
