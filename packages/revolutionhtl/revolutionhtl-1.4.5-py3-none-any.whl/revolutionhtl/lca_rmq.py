from math import log, ceil
from itertools import chain
import pandas as pd

def LCA(T, nodes):
    if len(nodes)==0:
        raise ValueError(f'Parameter "nodes" must be a non-empty set.')
    idxs= {T.R[x] for x in nodes}
    i,j= get_min_max(idxs)
    #i,j= min(idxs), max(idxs)
    lcaIdx= st_rqm(T.L,i,j,T.st)
    node= T.E[lcaIdx]
    return node

def get_min_max(L):
    L= list(L)
    i=j=L[0]
    for x in L:
        if x<i: i=x
        if x>j: j=x
    return i,j

def get_posible_normalized_blocks(block_size):
    """
    Returns a dictionary where the keys are all the posible
    normalized blocks of size block_size, and the keys are
    the index of the minimum vale.
    """
    res= [(0,)]
    for i in range(block_size-1):
        res= [X+(X[-1]+d,) for X in res for d in [1,-1]]
    #res= {X: X.index(min(X)) for X in res}
    return res

def compute_perfect_size(L):
    k= ceil(log(len(L), 2))
    n= 2**k
    return n, k


def adjust_array_size(L, n):
    L= L.copy()
    n0= len(L)
    l= L[-1]
    for i in range(n-n0):
        L= L+[l]
    return L

def get_blocks(L, block_size, n_blocks):
    return (tuple(L[block_size*i : block_size*(i+1)])
            for i in range(n_blocks))

def normalize_block(L):
    y0= L[0]
    return tuple((y-y0 for y in L))

def normalize_array(L, block_size, n_blocks):
    return list(chain.from_iterable((normalize_block(L0)
                                     for L0 in get_blocks(L, block_size, n_blocks))))

def aux_arrays(L, block_size, n_blocks, norm_block_2_min_idx):
    A=[]
    B=[]
    for L0 in get_blocks(L, block_size, n_blocks):
        b= norm_block_2_min_idx.get(normalize_block(L0),
                                    L0.index(min(L0)))
        A+= [L0[b]]
        B+= [b]
    return A,B

# ST-RMQ
def st_rqm(L,i,j,st):
    if i==j:
        return i
    i,j= sorted((i,j))
    k= int( log(j-i+1, 2) )
    a= int( st.loc[i, k-1] )
    b= int( st.loc[j-(2**k)+1, k-1] )

    return choose_argmin(L, a, b)

# Compute sparse table
######################
def get_range(n0, j):
    w_size= 2**(j)
    return range(n0 - w_size +1)

def choose_argmin(L,i,j):
    if L[i] <= L[j] :
        return i
    return j

def compute_sparce_table(L):
    n0,k= compute_perfect_size(L)
    L= adjust_array_size(L, n0)

    M= [[choose_argmin(L, i, i+1) for i in get_range(n0, 1)]]

    for j in range(2, k+1):
        dM= []
        R= get_range(n0, j)
        for i in R:
            b0= i+(2**(j-1))
            a= M[ j-2 ][ i ]
            b= M[ j-2 ][ b0 ]
            dM+= [choose_argmin(L, a, b)]
        M+= [dM]

    return pd.DataFrame(M).T

