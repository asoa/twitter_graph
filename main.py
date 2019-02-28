#!/usr/bin/env python3

import authenticate
from twitter_cookbook.crawl import Crawl
from graph import Graph
import traceback


def main():
    try:
        # create authenticated twitter api object
        auth = authenticate.Authenticate(creds_file='twitter_creds.BU')
        #  crawl the given twitter profile for reciprocal friends
        # crawl = Crawl(twitter_api=auth.twitter_api, screen_name='BarackObama', node_max=60)
        # crawl = Crawl(twitter_api=auth.twitter_api, screen_name='smerconish', node_max=25)
        crawl = Crawl(twitter_api=auth.twitter_api, screen_name='COOLVISIONLLC', node_max=50)
        crawl.crawl_followers()
        crawl.file_output.close()  # close file

        #create a graph object using networkx and visualize it using graphviz
        g = Graph(file=crawl.file_output, use_name=True, twitter_api=auth.twitter_api)

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
