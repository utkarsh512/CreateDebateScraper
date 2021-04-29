# thread.py -- containing Comment and Thread classes
#
# author: @utkarsh512
#

class Comment:
    '''Comment class for storing comments and additional information'''
    def __init__(self):
        self.body = None         # str: Body of the comment
        self.polarity = None     
        self.author = None       # str: Author of the comment
        self.time = None         # str: Time of creation of comment

    def set_body(self, body: str):
        self.body = body

    def set_polarity(self, polarity: str):
        self.polarity = polarity

    def set_author(self, author: str):
        self.author = author

    def set_time(self, tic: str):
        self.time = tic

    def __str__(self):
        s = '\nUser: [' + self.author + '] at ' + self.time + ' wrote expressing idea towards [' + self.polarity + ']:\n'
        s += self.body + '\n'
        return s

class Thread:
    '''Thread class for storing all the comments belonging to a given thread'''
    def __init__(self):
        self.title = None       # Title of the thread
        self.comments = list()  # List of comments in the the thread
        self.tag = None         # Relevant tag of the thread
        self.author = None

    def set_author(self, author: str):
        self.author = author

    def set_title(self, title: str):
        self.title = title

    def set_tag(self, tag: str):
        self.tag = tag

    def add_comment(self, comment: Comment):
        self.comments.append(comment)

    def __str__(self):
        s = '\nUser: [' + self.author + '] started new discussion on topic [' + self.title + ']\n\n'
        s += 'The comments in this thread are as follows:\n'
        for comment in self.comments:
            s += comment.__str__()
        return s
