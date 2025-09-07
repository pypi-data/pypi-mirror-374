def norm_path(path):
    if not path.endswith('/'):
        return path + '/'
    return path

def txtMu_2_dict(txt):
    return dict(map(lambda x: x.split(':'), txt.split(',')))

def update_mu(T0, T1, mu, attr0, attr1):
    DD0= attr_2_node(T0, attr0)
    DD1= attr_2_node(T1, attr1)
    return {DD0[x0]:DD1[x1] for x0,x1 in mu.items()}

def attr_2_node(T, attr):
    ret= {T.nodes[node][attr] : node for node in T}
    if len(ret)!=len(T):
        raise ValueError('There are nodes with the same attribute.')
    return ret

Devents= {'speciation' : 'S', 'duplication' : 'D', 'S':'S','D':'D','X':'X'}
def add_eventAttr(Tg, oAttr, nAttr):
    for xNode in Tg:
        ev= Tg.nodes[xNode][oAttr]
        Tg.nodes[xNode][nAttr]= Devents.get(ev, 'S')
    return Tg
