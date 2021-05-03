# scrape.py -- for scraping the CreateDebate dataset
#
# author: @utkarsh512
#

import requests
from bs4 import BeautifulSoup
from thread import Comment, Thread
import argparse
import os
from tqdm import tqdm
import pickle
import networkx as nx
import glom
import re
import json

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

def getPolarityandTime(x):
    try:
        y = str(x).split()
        tic = y[3][10:-1]
        pol = []
        it = -2
        while y[it] != 'Side:':
            pol.append(y[it])
            it -= 1
        pol = pol[::-1]
        pol = ' '.join(pol)
        return (tic, pol)
    except:
        return ('Not Available', 'Not Available')

def getCommentbyID(sp, cid):
    # Fetches comment by its id
    
    c = Comment()

    # Decoding author of comment
    div = sp.find('div', id=cid)
    div = div.find_all('a')[0]
    athr = str(div['href'].split('/')[-1])
    c.set_author(athr)

    # Decoding body of comment
    cid = cid[3:]
    cid = 'argBody' + cid
    div = sp.find('div', id=cid)
    lst = str(div).strip().split('\n')
    comment_body = lst[2]
    clean = re.compile('<.*?>')
    comment_body = str(re.sub(clean, ' ', comment_body))
    comment_body = str(re.sub(' +', ' ', comment_body))
    c.set_body(comment_body)

    # Decoding Time and Polarity
    tic, pol = getPolarityandTime(lst[3])
    c.set_time(tic)
    c.set_polarity(pol)
    
    return c

def dfs(thrd, sp, lookup, cid):
    if cid != 'root':
        thrd.comments[cid] =  getCommentbyID(sp, cid)
    for key in lookup[cid].keys():
        dfs(thrd, sp, lookup[cid], key)
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default=None, type=str, required=True, help="directory to store .log file of Thread objects")
    parser.add_argument("--tag", default=None, type=str, required=True, help="domain of the comments")
    parser.add_argument("--page_count", default=None, type=int, required=True, help="number of pages (when viewed in 96 offset mode)")
    args = parser.parse_args()

    writer_addr = os.path.join(args.data_dir, 'threads.log')
    writer = open(writer_addr, 'wb')

    json_addr = os.path.join(args.data_dir, 'threads.json')
    jsonw = open(json_addr, 'w', encoding='utf-8')
    
    for page_no in range(args.page_count):
        print(f'Scrapping page {page_no + 1} of 104...')
        url = 'https://www.createdebate.com/browse/debates/all/mostheated/alltypes/alltime/{0}/{1}/96/open'.format(args.tag, page_no * 96)
        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")
        lst = soup.findAll('a') # Finding all the outgoing links from the page
        links = list()

        for i in range(len(lst)):
            try:
                x = lst[i]['href']
                links.append(x)
            except:
                pass

        # The links need to be filtered as we want the links that lead to a thread
        filt = '//www.createdebate.com/debate/show/'
        filtered = list()

        for x in links:
            if x.startswith(filt):
                filtered.append('http:' + x)

        # As one thread links occurs twice, we need to remove the second occurence
        final = list()
        for i in range(0, len(filtered), 2):
            final.append(filtered[i])

        print(f'Number of threads identified for given page is {len(final)}')
        print('Building Thread objects...')

        for i in tqdm(range(len(final)), unit=' threads', desc='Processing threads'):
            post = requests.get(final[i])
            sp = BeautifulSoup(post.text, "lxml")
            thread_title = sp.find_all("h1", class_="debateTitle")
            comment_authors = sp.find_all("a", class_="points")
            thrd = Thread()

            # Decoding thread title
            try:
                thread_title = str(thread_title[0])[25: -6]
            except IndexError:
                # Cannot extract thread title, possibly Thread is a private post
                continue
            thrd.set_title(thread_title)
            thrd.set_tag(args.tag)
            thrd_author = comment_authors[0]
            thrd_author = thrd_author['href']
            thrd_author = thrd_author[35:]
            thrd.set_author(thrd_author)
            thrd.set_url(final[i])

            comment_authors = comment_authors[1:]

            try:
                LTree = getCommentTree(sp, 'debateSideBox sideL')
                RTree = getCommentTree(sp, 'debateSideBox sideR')
                thrd.set_meta(LTree, RTree)

                # print(json.dumps(LTree, indent=4))
                # print(json.dumps(RTree, indent=4))

                if 'root' in LTree.keys():
                    dfs(thrd, sp, LTree, 'root')
                if 'root' in RTree.keys():
                    dfs(thrd, sp, RTree, 'root')
            except:
                # Given page doesn't has a Left / Right side
                LTree = getCommentTree(sp, 'bothsidesbox')
                RTree = dict()
                thrd.set_meta(LTree, RTree)

                # print(json.dumps(LTree, indent=4))
                # print(json.dumps(RTree, indent=4))

                if 'root' in LTree.keys():
                    dfs(thrd, sp, LTree, 'root')
                if 'root' in RTree.keys():
                    dfs(thrd, sp, RTree, 'root')
                
            pickle.dump(thrd, writer)
            jsoned_thrd = thrd.jsonify()
            
            jsonw.write(json.dumps(jsoned_thrd) + '\n')
     
    jsonw.close()
    writer.close()

if __name__ == '__main__':
    main()
