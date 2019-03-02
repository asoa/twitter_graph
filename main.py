#!/usr/bin/env python3

import authenticate
from twitter_cookbook.crawl import Crawl
from graph import Graph
import traceback
import time


def prompt():
    screen_name = input("What screen name would you like to crawl? ")
    return screen_name


def main():
    try:
        name = prompt()
        # create authenticated twitter api object
        auth = authenticate.Authenticate(creds_file='twitter_creds.BU')
        # crawl the given twitter profile for reciprocal friends
        # crawl = Crawl(twitter_api=auth.twitter_api, screen_name=name, node_max=100)
        # # crawl = Crawl(twitter_api=auth.twitter_api, screen_name='smerconish', node_max=100)
        # crawl.crawl_followers()
        # crawl.file_output.close()  # close file

        #create a graph object using networkx and visualize it using graphviz
        g = Graph(use_name=True, twitter_api=auth.twitter_api, screen_name=name)

    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
