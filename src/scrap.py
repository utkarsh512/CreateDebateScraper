# scrap.py -- for scrapping the CreateDebate dataset
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default=None, type=str, required=True, help="directory to store .log file of Thread objects")
    parser.add_argument("--tag", default=None, type=str, required=True, help="domain of the comments")
    parser.add_argument("--page_count", default=None, type=int, required=True, help="number of pages (when viewed in 96 offset mode)")
    parser.add_argument("--show_comments", default=False, type=bool, required=False, help="whether to print comments during processing")
    args = parser.parse_args()

    writer_addr = os.path.join(args.data_dir, 'threads.log')
    writer = open(writer_addr, 'wb')
    
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
            try:
                post = requests.get(final[i])
                sp = BeautifulSoup(post.text, "html.parser")
                thread_title = sp.find_all("h1", class_="debateTitle")
                comment_body = sp.find_all("div", class_="argBody")
                comment_time_polarity = sp.find_all("div", class_="subtext when")
                comment_authors = sp.find_all("a", class_="points")
                thrd = Thread()

                # Decoding thread title
                thread_title = str(thread_title[0])[25: -6]
                thrd.set_title(thread_title)
                thrd.set_tag(args.tag)
                thrd_author = comment_authors[0]
                thrd_author = thrd_author['href']
                thrd_author = thrd_author[35:]
                thrd.set_author(thrd_author)

                comment_authors = comment_authors[1:]

                assert(len(comment_body) == len(comment_time_polarity))
                assert(len(comment_body) == len(comment_authors))

                # Processing individual comment
                for j in range(len(comment_body)):
                    cur_body = comment_body[j]
                    cur_time_polarity = comment_time_polarity[j]
                    cur_author = comment_authors[j]
                    comment = Comment()

                    # Decoding author name
                    cur_author = cur_author['href']
                    cur_author = cur_author[35:]
                    comment.set_author(cur_author)

                    # Decoding time and polarity
                    cur_time_polarity = str(cur_time_polarity).split()
                    tic = cur_time_polarity[3][10:-1]
                    pol = cur_time_polarity[-2]

                    comment.set_time(tic)
                    comment.set_polarity(pol)

                    # Decoding comment body
                    cur_body = str(cur_body).split()
                    cur_body = cur_body[2: -1]
                    cur_body = ' '.join(cur_body)
                    comment.set_body(cur_body)

                    if args.show_comments:
                        print(comment)

                    # Adding comment to Thread object
                    thrd.add_comment(comment)

                pickle.dump(thrd, writer)
                # print(thrd)
                
            except:
                pass
        
    writer.close()

if __name__ == '__main__':
    main()
        
