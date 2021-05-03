def getCommentTree(html, side):
    # Utility to get nested comment structure by comment ids
    #
    # :param html: bs4 object
    # :param side: L/ R (left / right)
    
    divelem = html.find('div', class_=side)
    allDivElems = divelem.find_all('div')

    flag = ''
    tree = nx.DiGraph()

    for i in range(len(allDivElems)):
        div = allDivElems[i]
        cls = div.get('class')
        if cls != ['argBox', 'argument'] and cls != ['arg-threaded']:
            continue
        pid = div.parent.get('id')
        cid = div.get('id')
        if cls == ['argBox', 'argument']:
            flag = cid
            if pid is None:
                pid = 'root'
            tree.add_edge(pid, cid)
        else:
            tree.add_edge(flag, cid)

    paths = []

    for x in tree:
        if tree.out_degree(x) == 0: # leaf node
            p = nx.shortest_path(tree, 'root', x)
            tmp = []
            for y in p:
                if y == 'root':
                    tmp.append(y)
                else:
                    div = html.find('div', id=y)
                    cls = div.get('class')
                    if cls == ['argBox', 'argument']:
                        tmp.append(y)
            paths.append(tmp)

    struct = dict()

    for p in paths:
        glom.assign(struct, '.'.join(p), {}, missing=dict)

    return struct
