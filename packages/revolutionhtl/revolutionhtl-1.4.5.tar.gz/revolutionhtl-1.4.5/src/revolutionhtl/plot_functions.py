from .nxTree import is_leaf, get_children, get_dad, BFS_graph
from .error import notAllowedAttributeValue
from networkx import dfs_postorder_nodes, dfs_preorder_nodes
import matplotlib.pyplot as plt
from upsetplot import from_memberships
from pandas import DataFrame

##################
# Main functions #
##################
def plot_recon(Tg, Ts, mu,
               eventAttr= 'event',
               eventSymbols= {'S':'.r', 'D':'db'},
               sColor= '#97a4bd',
               gLineStyle= '-k',
               sRoot= 0,
               leafLabelAttr= 'label',
               leafLabelStyle= {'fontsize': 10, 'color': '#B37700'},
               pipe_r= 2,
               ax= None,
              ):
    # Compute graphics
    pos, branch_w, branch_d= get_tree_layoult(Ts, branch_r= pipe_r)
    Xpipe, Ypipe= get_pipe_layoult(Ts, pos, branch_w, sRoot)
    gPos= get_gTree_layoult(Tg, Ts, mu, pos, branch_w, eventAttr)

    # Plot
    if ax==None:
        fig, ax= plt.subplots(1,1,figsize=(6,6))

    Dsymbols= lambda x: eventSymbols.get(Tg.nodes[x][eventAttr], '.k')

    ax.fill(Xpipe, Ypipe, sColor)
    for vNode in filter(lambda x: (x!=Ts.root)and(not is_leaf(Ts,x)), Ts):
        x_mid, y= pos[vNode]
        x0,x1= x_mid-(branch_w/2),x_mid+(branch_w/2)
        ax.plot([x0,x1],[y,y],'gray')

    for xNode in dfs_postorder_nodes(Tg,Tg.u_lca):
        X= [x[0] for x in gPos[xNode]]
        Y= [x[1] for x in gPos[xNode]]

        if mu[xNode]==mu[get_dad(Tg,xNode)]:
            X= [X[0],X[-1]]
            Y= [Y[0],Y[-1]]

        ax.plot(X,Y,gLineStyle)

    for xNode in dfs_postorder_nodes(Tg,Tg.u_lca):
        x0= gPos[xNode][0][0]
        y0= gPos[xNode][0][1]
        ax.plot(x0,y0,Dsymbols(xNode))
        if is_leaf(Tg, xNode) and Tg.nodes[xNode][eventAttr]!='X':
            ax.text(x0,y0,f"{Tg.nodes[xNode].get(leafLabelAttr)}",
                    fontdict= leafLabelStyle,
                    rotation= -30,
                    rotation_mode= 'anchor',
                   )

    ax.axis('off')
    return ax


##############################################
# Back end functions for reconciliation plot #
##############################################

def get_leaves_pos(T, leaves= None, length= 1, r= 1, root= 0):
    """
    X-position of leaves in [0,length] with r = (branch width)/(branch separation)

    Arguments
    ---------
    T      : Tree
    leaves : Leaves sorted in the desired order
    length : Length of x-range to place leafs.
    r      : ratio (branch width)/(branch separation)

    Output
    ------
    lPos : Map node -> x-position
    w    : Branch width
    d    : Branch separation
    """
    if leaves==None:
        leaves= list(filter( lambda x: is_leaf(T,x), dfs_postorder_nodes(T, root) ))
    # Compute branch width and branch separation (assume length=1)
    n= len(leaves)
    d= 1/(n*r +n-1)
    w= r*d
    # Init output
    lPos= dict()
    i= w/2
    # Compute positions
    for x in leaves:
        lPos[x]= i * length
        i+= w+d
    return lPos, w, d, leaves

def get_tree_layoult(T, sorted_leaves= None, x_length= 1, y_length= 1, branch_r= 1, root= 0):
    """
    Return node position for a tree plot.

    The output layoult is the skeleton of a pipe-like tree
    where the branch-with and the branch-separation is defined by
    the argument branch_r = (branch width)/(branch separation).

    Arguments
    ---------
    T: Tree

    Keyword arguments
    -----------------
    sorted_leaves: list or tuple in the desired order of the leaves
    x_length     : x-length of the plot
    y_length     : y-length of the plot
    branch_r     : ratio (branch width)/(branch separation)
    root         : root of the tree for the plot

    Output
    ------
    pos  : Map node -> (x,y) position
    branch_w    : Branch width
    branch_d    : Branch separation
    """
    # Get leaf x-position
    leafs_pos, branch_w, branch_d,_= get_leaves_pos(T, leaves= sorted_leaves, length= x_length, r= branch_r)
    # Init output
    pos= dict()
    maxLevel= 0
    minX= dict()
    maxX= dict()
    # Compute output
    for uNode in dfs_postorder_nodes(T, root):
        if is_leaf(T, uNode):
            pos[uNode]= (leafs_pos[uNode], 0)
            minX[uNode]= maxX[uNode]= leafs_pos[uNode]
        else:
            # Compute position for node
            children= get_children(T, uNode)
            minX[uNode]= min((minX[ch] for ch in children))
            maxX[uNode]= max((maxX[ch] for ch in children))
            xu= (minX[uNode]+maxX[uNode])/2
            yu= max((pos[ch][1] for ch in children))+1
            pos[uNode]= (xu, yu)
            # update max level
            maxLevel= max((maxLevel, yu))
    # Normalize height
    norm= maxLevel/y_length
    pos= {x:(y[0], y[1]/norm) for x,y in pos.items()}
    return pos, branch_w, branch_d

def get_pipe_layoult(T, pos, branch_w, root= 0):
    """
    Return the perimeter of the pipe of a tree.

    Arguments
    ---------
    T        : Tree
    pos      : Map node -> (x,y) position. This is the skeleton of the pipe
    branch_w : Branch width

    Keyword arguments
    -----------------
    root : root of the tree for the plot

    Output
    ------
    Xpipe : List of x-positions of the pipe
    Ypipe : List of y-positions of the pipe
    """
    # Constant to compute spesiation interval
    w2= branch_w/2
    # Init output
    Xpipe= dict()
    Ypipe= dict()
    # compute output
    for uNode in dfs_postorder_nodes(T, root):
        # compute speciation interval of uNode
        x_u= pos[uNode][0]
        x0_u, x1_u= x_u-w2, x_u+w2
        y_u= pos[uNode][1]
        # compute pipe of uNode
        if is_leaf(T, uNode):
            Xpipe[uNode]= [x0_u, x1_u]
            Ypipe[uNode]= [y_u, y_u]
        else:
            uChildren= list(get_children(T, uNode))
            # Init pipe for uNode
            Xpipe[uNode]= [x0_u]
            Ypipe[uNode]= [y_u]
            # Add pipe of children at the left side of a bifurcation
            for v0Node,v1Node in consecutive_children_pairs(uChildren):
                # Compute point of bifurcation
                x1_v0, y_v0= Xpipe[v0Node][-1], Ypipe[v0Node][0]
                x0_v1, y_v1= Xpipe[v1Node][0], Ypipe[v1Node][0]
                xMid, yMid= midpoint(x0_u, x1_u, y_u, x1_v0, y_v0, x0_v1, y_v1)
                # Update pipe
                Xpipe[uNode]+= Xpipe[v0Node] + [xMid]
                Ypipe[uNode]+= Ypipe[v0Node] + [yMid]
            # Add pipe of the last child
            v1Node= uChildren[-1]
            Xpipe[uNode]+= Xpipe[v1Node] + [x1_u]
            Ypipe[uNode]+= Ypipe[v1Node] + [y_u]
            # Delete pipe of children
            for vNode in uChildren:
                del Xpipe[vNode]
                del Ypipe[vNode]

    return Xpipe[root], Ypipe[root]

def get_gTree_layoult(Tg, Ts, mu, sPos, branch_w, eventAttr):
    """
    Return the layoult of a reconciliated gene tree inside a species tree layoult

    Arguments
    ---------
    Tg        : Gene tree
    Ts        : Species tree
    mu        : Map gNode -> sNode. Reconciliation map
    sPos       : Map sNode -> (x,y) position. Species tree layoult
    branch_w  : Branch width of species tree layoult
    eventAttr : Attribute in gene tree indicating evolutionary event

    Output
    ------
    gPos
    """

    node_level, D_branch_roots= compute_levels_in_branch(Tg, Ts, mu, Tg.u_lca, eventAttr)
    y_gPos= get_y_pos(Tg, Ts, mu, sPos, eventAttr, node_level)
    y_cumulative, eMap, y_spots= count_genes(Tg, Ts, mu, y_gPos, D_branch_roots, node_level, eventAttr)
    gPos= get_xy_pos(Tg, y_gPos, Ts, sPos, y_spots, y_cumulative, mu, D_branch_roots, eMap, branch_w)
    return gPos

def get_xy_pos(Tg, y_gPos, Ts, sPos, y_spots, y_cumulative, mu, D_branch_roots, eMap, branch_w):
    idxNext= {X:0 for X,count in y_cumulative.items()}
    gPos= {Tg.root:[sPos[mu[Tg.root]]]}
    for uNode in dfs_preorder_nodes(Tg, Tg.u_lca):
        vNode= mu[uNode]
        spot= y_gPos[uNode]
        gPos[uNode]= get_branch_root_edge(uNode, vNode, spot, eMap, Ts, sPos, idxNext, y_spots, branch_w, y_cumulative, gPos, Tg, D_branch_roots)
    return gPos

def get_branch_root_edge(uNode, vNode, spot, eMap, Ts, sPos, idxNext, y_spots, branch_w, y_cumulative, gPos, Tg, D_branch_roots):
    getX= lambda vNode,spot: set_x_pos(Ts, vNode, spot, sPos, idxNext, branch_w, y_cumulative)
    ret= []

    top= gPos[get_dad(Tg, uNode)][0]
    top_x,top_y= top
    F= lambda x: top_y>x>=spot

    for vUpper in eMap[uNode]:
        ret+= [(getX(vUpper,Spot1), Spot1) for Spot1 in filter(F, y_spots[vUpper])]
    if uNode!=Tg.u_lca:
        ret+= [top]
    return ret

def set_x_pos(Ts, vNode, spot, sPos, idxNext, branch_w, y_cumulative):
    X= (vNode,spot)
    x0,y0= sPos[vNode]
    x1,y1= sPos[get_dad(Ts, vNode)]
    if x0==x1:
        x_s= x0
    else:
        m= (y1-y0)/(x1-x0)
        b= y0 - m*x0
        x_s= (spot-b)/m
    idxNext[X]+= 1
    return x_s - (branch_w/2) + ( idxNext[X]*branch_w / (y_cumulative[X]+1) )

def count_genes(Tg, Ts, mu, gPos, D_branch_roots, node_level, eventAttr):
    """
    For each branch of the species tree return:
    - y-axis spots over the brach where nodes of gene tree has been mapped, and
    - the cumulative number of genes in the species as the y-axis decreases.
    Additionally, for each edge uv of the gene tree return:
    - The sequense of node S of the species tree such that mu[v] < S <= mu[u]
    """
    y_cumulative= dict()
    y_spots= dict()

    eMap= {uNode : edge_map(uNode, Tg, Ts, mu) for uNode in Tg}

    for vNode in BFS_graph(Ts, Ts.u_lca):
        # Track duplication of genes w.r.t. a spot in parental branch of vNode
        branch_roots= D_branch_roots[vNode]
        spot_2_increase= dict()
        for uNode in branch_roots:
            for uPrime in branch_bfs(Tg, uNode, mu):
                spot= gPos[uPrime]
                if node_level[uPrime] > 1:
                    spot_2_increase[spot]= spot_2_increase.get(spot, 0) + len(Tg[uPrime]) - 1
                else:
                    spot_2_increase[spot]= spot_2_increase.get(spot, 0)

        # Count total genes w.r.t y spot
        y_cumulative[vNode]= dict() # Map : spot -> number of genes just befor a time, i.e. at the minimum time > spot
        y_spots[vNode]= sorted(spot_2_increase)
        #cumulative_count= sum(map(lambda uNode: node_level[uNode]>1, branch_roots))
        cumulative_count= len(branch_roots)
        for spot in y_spots[vNode][::-1]:
            y_cumulative[vNode][spot]= cumulative_count
            cumulative_count+= spot_2_increase[spot]
        # Track the y positions of parental edges
        for uNode in branch_roots:
            bottom= gPos[uNode]
            #top= gPos[get_dad(Tg, uNode)]
            top= y_spots[vNode][-1]
            F= lambda x: top>x>bottom
            for vUpper in eMap[uNode]:
                for spot in filter(F, y_spots[vUpper]):
                    y_cumulative[vUpper][spot]+= 1

    # Flatten output
    y_cumulative= {(vNode,spot) : count
                   for vNode,spot2count in y_cumulative.items()
                   for spot,count in spot2count.items()}

    return y_cumulative, eMap, y_spots

def edge_map(uNode, Tg, Ts, mu):
    """
    Tracks the position of the parental edge of uNode in parental branches of the species tree
    """
    if uNode==Tg.root:
        return []
    uUpper= get_dad(Tg, uNode)
    vNode= mu[uNode]
    vUpper= mu[uUpper]
    if vNode==vUpper:
        return [vNode]
    ret= []
    while vNode!=vUpper:
        ret+= [vNode]
        vNode= get_dad(Ts, vNode)
    return ret

def branch_bfs(Tg, xNode, mu):
    queue= [xNode]
    idx= 0
    n= 1
    while idx<n:
        xNode= queue[idx]
        ch= list(branch_descendants(Tg, xNode, mu))
        queue+= ch
        n+= len(ch)
        idx+= 1
    return queue


def branch_descendants(Tg, xNode, mu):
    yNode= mu[xNode]
    return filter(lambda xPrime: mu[xPrime]==yNode, Tg[xNode])

def get_y_pos(Tg, Ts, mu, sPos, eventAttr, node_level):
    """
    y-axis position of all the nodes of the gene tree
    """
    gPos= {Tg.root:sPos[Ts.root][1]}
    for uNode in BFS_graph(Tg, Tg.u_lca):
        # See current node
        event= Tg.nodes[uNode][eventAttr]
        dad_u= get_dad(Tg,uNode)
        # map of current node
        vNode= mu[uNode]
        dad_v= get_dad(Ts, vNode)
        y_pos_v=  sPos[vNode][1]
        # Compute spot in branch
        if is_leaf(Tg, uNode) and event!='X':
            spot= 0
        elif event=='S':
            spot= y_pos_v
        elif event in ['D', 'X']:
            if vNode==mu[dad_u]:
                up= gPos[dad_u]
            else:
                up= sPos[dad_v][1]
            spot= y_pos_v + (up-y_pos_v)*(1-(1/node_level[uNode]))
        else:
            raise notAllowedAttributeValue(f'Unknown event "{event}"')
        gPos[uNode]= spot
    return gPos

def compute_levels_in_branch(Tg, Ts, mu, gRoot, eventAttr):
    """
    For each branch of the species tree return:
    - level of nodes in the sub-gene trees restructed to the branch of the species tree
    - the roots of the sub-gene trees restructed to the branch of the species tree

    Note:
    Each edge uv is represented by the child node v.
    The level 0 corresponds to genes mapping to the speciation event v.
    """
    node_level= {}
    D_branch_roots= {y:list() for y in Ts}
    for xNode in dfs_postorder_nodes(Tg, gRoot):
        event= Tg.nodes[xNode][eventAttr]
        yNode= mu[xNode]
        if yNode!=mu[get_dad(Tg, xNode)]:
            D_branch_roots[yNode].append(xNode)
        if is_leaf(Tg, xNode):
            if event=='X': node_level[xNode]= 2
            else: node_level[xNode]= 1
        else:
            if event=='S': node_level[xNode]= 1
            elif event=='D': node_level[xNode]= compute_d_level(Tg, xNode, mu, node_level)
            else: raise notAllowedAttributeValue(f'Unknown event "{event}"')
    return node_level, D_branch_roots

def compute_d_level(Tg, xNode, mu, node_level):
    maxLevel= max([node_level[xPrime] for xPrime in branch_descendants(Tg, xNode, mu)]+[0])
    return maxLevel+1

###################################
# Functions for summary dendogram #
###################################

# Graphics
#---------
def plot_dendogram(T, numbers, ax, delta_txt=0.04, sorted_leaves=None):
    pos,_,_= get_tree_layoult(T, sorted_leaves= sorted_leaves)
    for u_node in dfs_postorder_nodes(T, 0):
        if is_leaf(T, u_node):
            plot_leaf(T, pos, u_node, numbers, ax, delta_txt)
        else:
            plot_inner(T, pos, u_node, numbers, ax, delta_txt)
    return None

def n2t(x,p='',s=''):
    if x:
        return f'{p}{x}{s}'
    else:
        return ''

def plot_leaf(T, pos, u_node, numbers, ax, delta_txt):
    x_u,y_u= pos[u_node]
    total_genes= numbers[u_node]['S'] + numbers[u_node]['Sr']
    singletons= numbers[u_node]['Sr']
    txt= f'{n2t(total_genes)}{n2t(singletons,' (',')')}'
    species= T.nodes[u_node]['label']
    ax.text(x_u, y_u, txt, c='green')
    ax.text(x_u, y_u-delta_txt, species, c='k', rotation=0, rotation_mode= 'anchor',)
    return None

def plot_inner(T, pos, u_node, numbers, ax, delta_txt):
    # Positions
    x_u,y_u= pos[u_node]
    ch= list(T[u_node])
    x0,x1= get_range(ch, pos)
    # Plot speciation line
    ax.plot([x0,x1],[y_u,y_u],'k')

    txt= n2t(numbers[u_node]['S'] + numbers[u_node]['Sr'])
    ax.text(x_u, y_u, txt, c='green')

    # Plot children
    for v_node in ch:
        x_v,y_v= pos[v_node]
        y_mid= y_u -  delta_txt#(y_u+y_v)/2
        # Branch
        ax.plot([x_v,x_v], [y_u, y_v],'k')
        # Numbers

        txt= n2t(numbers[v_node]['Dr'] + numbers[v_node]['Sr'],'+')
        ax.text(x_v, y_mid, txt, c='blue')

        txt= n2t(numbers[v_node]['D'],'+')
        ax.text(x_v, y_mid-delta_txt, txt, c='blue')

        txt= n2t(numbers[v_node]['X'],'-')
        ax.text(x_v, y_mid-2*delta_txt, txt, c='red')

    return None

def get_range(ch, pos):
    ch_pos= set((pos[x][0] for x in ch))
    x0,x1= min(ch_pos), max(ch_pos)
    return x0,x1

init_numbers= lambda T: {x:{s:0 for s in ['S','D','X','Sr','Dr','Xr']} for x in T}

def get_symbol(T, x, gRoot):
    label= T.nodes[x]['label']
    if x==gRoot:
        label+= 'r'
    if is_leaf(T,x):
        if label=='X':
            return label
        return 'S'
    return label

def add_numbers(Tg, Ts, mu, numbers=None, gRoot= 1):
    if numbers==None:
        numbers= init_numbers(Ts)
    for x_node in dfs_postorder_nodes(Tg, 1):
        x_symbol= get_symbol(Tg, x_node, gRoot)
        y_node= mu[x_node]
        if x_symbol=='Dr':
            numbers[y_node][x_symbol]+= 1
            numbers[y_node]['D']+= len(Tg[x_node])-1
        elif x_symbol=='D':
            numbers[y_node][x_symbol]+= len(Tg[x_node])-1
        else:
            numbers[y_node][x_symbol]+= 1
    return numbers

###########################
# Functions for UpSetPlot #
###########################

# Classify OGs by precense of species and count
#----------------------------------------------
def og_class_statistics(df, species_list): # previous name of this function: def clade_info()
    """
    Classify orthogroups using the set of species represented by genes members of the orthogroup.
    Then returns numerical descriptions of the classes.

    Arguments
    ---------
    df           : Dataframe describing orthogroups.
                   column names are species, rows names are orthogroups, cells are set of genes.
    species_list : List of the species in df, sorted as desired in the visualization.

    Output
    ------
    class_statistics

    """
    # Classify orthogroups by set of species
    F= lambda row: list( row[row>0].index )
    og_classification= from_memberships(df.progress_apply(F, axis= 1))
    og_classification= og_classification.reset_index().set_index(species_list).ones
    # Count genes per orthogroup
    n_genes_per_orthogroup= df.sum(axis=1)
    n_genes_per_orthogroup.index= og_classification.index
    # Count genes per species per orthogroup
    av_genes_per_speciesper_orthogroup= df.apply(lambda row: row[row>0].mean(), axis=1)
    av_genes_per_speciesper_orthogroup.index= og_classification.index
    # Group by class
    gb_n_genes_per_orthogroup= n_genes_per_orthogroup.groupby(species_list)
    # Compute class statistics
    class_statistics= DataFrame({
        'No. OGs' : og_classification.groupby(species_list).sum(),
        'No. genes' : gb_n_genes_per_orthogroup.sum(),
        'Av. genes per OG' : gb_n_genes_per_orthogroup.mean(),
        'Av. genes per species' : av_genes_per_speciesper_orthogroup.groupby(species_list).mean(),
    })
    return class_statistics

##########################
# Functions for barplots #
##########################


# Clades of the tree in binary code for upSetplot
#------------------------------------------------
def get_bool_clades(T):
    Il= {} # Induced leafs
    X= []
    for u_node in dfs_postorder_nodes(T, 1):
        if is_leaf(T, u_node):
            # Induced species
            leaf_s= T.nodes[u_node]['species']
            Il[u_node]= {leaf_s}
        else:
            ch= list(T[u_node])
            # Compute species in leaves
            Il[u_node]= set(chain.from_iterable((Il[v_node] for v_node in ch)))
            # Determine bool clade
            X+= [tuple(x in Il[u_node] for x in species_list)]
    return X

######################
# Auxiliar functions #
######################

def where_is_inherited(gNode, Tg, Ts, mu, eventAttr, gRoot):
    """
    Returns a list of tuples (sNode,event),
    the first element is the map of gNode,
    and the ancestors of (sNode,event)
    just before the map of gDad.
    """
    # Map of gNode
    X0= (mu[gNode], Tg.nodes[gNode][eventAttr])
    # If gNode is root, then it is mapped to only one element in S
    if gNode==gRoot:
        return [X0]
    # Otherwise, compute the upper limit
    gDad= get_dad(Tg, gNode)
    X1= (mu[gDad], Tg.nodes[gDad][eventAttr])
    # Return the ancestors in S before the upper limit
    if X0==X1:
        return [X0]
    ext_path= []
    while X0!=X1:
        ext_path+= [X0]
        X0= get_map_dad(X0, Ts)
    return ext_path

def get_map_dad(X0, Ts):
    sNode,event= X0
    if event=='S':
        return (sNode,'D')
    return (get_dad(Ts, sNode),'S')

def consecutive_children_pairs(ch):
    return zip(ch[0:], ch[1:])

def midpoint(x0_u, x1_u, y_u, x1_v0, y_v0, x0_v1, y_v1):
    m0= (y_u-y_v0)/(x1_u-x1_v0)
    m1= (y_u-y_v1)/(x0_u-x0_v1)

    xMid=(y_v1-y_v0 +m0*x1_v0-m1*x0_v1)/(m0-m1)
    yMid= m0*(xMid-x1_v0)+y_v0

    return xMid, yMid
