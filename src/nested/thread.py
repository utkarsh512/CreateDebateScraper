# thread.py -- containing Comment and Thread classes
#
# author: @utkarsh512
#

import textwrap as tw
import json

class Comment:
    '''Comment class for storing comments and additional information'''
    def __init__(self):
        self.body = None         # str: Body of the comment
        self.polarity = None     
        self.author = None       # str: Author of the comment
        self.time = None         # str: Time of creation of comment

    def set_body(self, body: str):
        self.body = tw.fill(body)

    def set_polarity(self, polarity: str):
        self.polarity = polarity

    def set_author(self, author: str):
        self.author = author

    def set_time(self, tic: str):
        self.time = tic

    def __str__(self):
        return self.Str()

    def Str(self, indent=0):
        s = ''
        lst = tw.wrap(self.body)
        for x in lst:
            s += '\t' * indent + x.strip() + '\n'
        s += '\t' * indent + '[Posted by ' + self.author + ' at ' + self.time + ' - Side: ' + self.polarity + ']\n'
        return s

class Thread:
    '''Thread class for storing all the comments belonging to a given thread'''
    def __init__(self):
        self.title = None       # Title of the thread
        self.comments = dict()  # List of comments in the the thread
        self.tag = None         # Relevant tag of the thread
        self.author = None
        self.url = None         # URL of the thread
        self.metaL = None       # Comment structure of Left side of thread
        self.metaR = None       # Comment structure of Right side of thread

    def set_author(self, author: str):
        self.author = author

    def set_url(self, url: str):
        self.url = url

    def set_title(self, title: str):
        self.title = title

    def set_tag(self, tag: str):
        self.tag = tag

    def set_meta(self, metaL: dict, metaR: dict):
        self.metaL = metaL
        self.metaR = metaR

    def add_comment(self, cid: str, comment: Comment):
        self.comments[cid] = comment

    def __str__(self):
        s = f'Title: {self.title}\n'
        s += f'Posted by {self.author}\n'
        s += f'Tag: {self.tag}\n'
        s += f'URL: {self.url}\n\n'

        s += 'Comments:\n\n'

        s = [s]

        def dfs(s, cid, lookup, depth=-1):
            if (cid != 'root'):
                s[0] += self.comments[cid].Str(depth) + '\n'
            for key in lookup[cid].keys():
                dfs(s, key, lookup[cid], depth + 1)

        if 'root' in self.metaL.keys():
            dfs(s, 'root', self.metaL)
        if 'root' in self.metaR.keys():
            dfs(s, 'root', self.metaR)

        s[0] += '_' * 100 + '\n'
        return s[0]
