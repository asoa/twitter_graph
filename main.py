#!/usr/bin/env python3

import authenticate
from twitter_cookbook.crawl import Crawl
from graph import Graph


def main():
    try:
        # create authenticated twitter api object
        auth = authenticate.Authenticate(creds_file='twitter_creds.BU')

        # crawl the given twitter profile for reciprocal friends
        crawl = Crawl(twitter_api=auth.twitter_api, screen_name='COOLVISIONLLC')
        crawl.crawl_followers()
        crawl.file_output.close()  # close file

        # create a graph object using networkx and visualize it using graphviz
        g = Graph(file='twitter_graph.txt', use_name=True, twitter_api=auth.twitter_api)
        g.build_graph()
        g.build_graphViz()

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
