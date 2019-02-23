#!/usr/bin/env python


import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import matplotlib.pyplot as plt
import json

import authenticate
from profile import Profile
from graphviz import render
import graphviz


class Graph(object):
    """creates a networkx graph for analysis and a graphviz graph for visualization

    """
    def __init__(self, *args, **kwargs):
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.file = self.kwargs.get('file', None)
        self.twitter_api = self.kwargs.get('twitter_api', None)
        self.use_name = self.kwargs.get('use_name', False)
        self.g = nx.Graph()

        self.build_graph()
        self.build_graphViz()

    def build_graph(self):
        with open(self.file, 'r') as f:
            dicts = [json.loads(node.strip()) for node in f.readlines() if node.strip() != '']
            # print(dicts)
        node_list_dict = {k:v2 for dict in dicts for k,v in dict.items() for k2,v2 in v.items()}
        # print(node_list_dict.items())
        # for node in node_list.items():
        #     print(node)
        node_list_tup = [(int(k),node) for k,nodes in node_list_dict.items() for node in nodes]
        # print(node_list_tup)

        if self.use_name:
            ids = [id for ids in node_list_tup for id in ids]
            names = Profile(twitter_api=self.twitter_api, user_ids=ids, get_names=True).get_screen_name()
            # name_tuple = [(names.get(id1), names.get(id2)) for tup in node_list_tup for id1,id2 in tup]
            name_tuple = [(names.get(tup[0]), names.get(tup[1])) for tup in node_list_tup]

            # create graph object with edges and implicit nodes
            self.g = nx.Graph()
            self.g.add_edges_from(name_tuple)
            nx.draw(self.g)
            plt.savefig('networkx-names.png')
            plt.show()

        else:
            self.g = nx.Graph()
            self.g.add_edges_from(node_list_tup)
            nx.draw(self.g)
            plt.savefig('networkx-graph.png')
            plt.show()

        # write to graphViz format
        self.write_graph()

    def write_graph(self):
        pos = nx.nx_agraph.graphviz_layout(self.g)
        nx.draw(self.g, pos=pos)
        write_dot(self.g, 'file.dot')

    def build_graphViz(self):
        render('dot', 'png', 'file.dot')  # saves the graphViz plot to current working directory
        # graphviz.Source.from_file('file.dot')  # does the same thing, but renders the plot if ran interactively

    def diameter(self):
        # nx.diameter()
        return self.diameter()

    def average_distance(self):
        # nx.average_shortest_path_length()
        return self.average_distance()


def main():
    a = authenticate.Authenticate(creds_file='twitter_creds.BU')
    g = Graph(twitter_api=a.twitter_api, file='twitter_graph.txt', use_name=True)


if __name__ == "__main__":
    main()


