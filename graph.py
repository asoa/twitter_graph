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
        Args:
            file: (str) filename that contains ids/screen_names
            twitter_api: (twitter api) authenticated twitter api object
            use_name: (boolean) if true, get screen names for ids
            g: (Graph) nx.Graph object
    """
    def __init__(self, *args, **kwargs):
        self.kwargs = {k:v for k,v in kwargs.items()}
        self.screen_name = self.kwargs.get('screen_name', None)
        self.file = f'twitter_graph_{self.screen_name}.txt'
        self.twitter_api = self.kwargs.get('twitter_api', None)
        self.use_name = self.kwargs.get('use_name', False)
        self.g = nx.Graph()
        self.nodelist = []
        self.name_id_lookup = {}

        self.build_graph()
        self.build_graphViz()
        self.graph_statistics()

    def build_graph(self):
        """loads the json object from file and formats the nodes to be passed to the Graph constructor
        Variables:
              dicts: (dict) list of dicts of twitter ids and reciprocal friends
              node_list_dict: (dict) k,v pairs where v is a list of reciprocal friends
              node_list_tup: (list) of tuples of (id, friend1), (id, friend2) ... argument to Graph.add_edges_from()
              names: (dict) of screen name: id
              name_tuple: (list) of (screen name, id) tuples
        """
        with open(self.file, 'r') as f:
            dicts = [json.loads(node.strip()) for node in f.readlines() if node.strip() != '']

        node_list_dict = {k:v2 for dict in dicts for k,v in dict.items() for k2,v2 in v.items()}
        node_list_tup = [(int(k),node) for k,nodes in node_list_dict.items() for node in nodes]

        if self.use_name:  # get screen names for ids
            ids = list(set([id for ids in node_list_tup for id in ids]))
            # ids = ','.join(str(id) for id in ids)
            self.get_screen_name(Profile(twitter_api=self.twitter_api, user_ids=ids).items_to_info)
            name_tuple = [(self.name_id_lookup.get(tup[0]), self.name_id_lookup.get(tup[1])) for tup in node_list_tup]

            # create graph object with edges and implicit nodes
            self.g = nx.Graph()
            self.g.add_edges_from(name_tuple)
            # self.nodelist = [names.get(node) for node in node_list_dict.keys()]
            plt.axis('off')
            nx.draw_networkx(self.g, with_labels=True, font_size=6, node_size=100)
            plt.savefig('networkx-names.png')
            plt.show()

        else:
            self.g = nx.Graph()
            self.g.add_edges_from(node_list_tup)
            plt.axis('off')
            nx.draw_networkx(self.g, with_labels=True, font_size=6, node_size=100)
            plt.savefig('networkx-ids.png')
            plt.show()

        # write to graphViz format
        self.write_graph()

    def write_graph(self):
        pos = nx.nx_agraph.graphviz_layout(self.g)
        nx.draw(self.g, pos=pos)
        write_dot(self.g, 'file.dot')

    def build_graphViz(self):
        render('dot', 'png', 'file.dot')  # saves the graphViz plot to current working directory
        graphviz.Source.from_file('file.dot')  # does the same thing, but renders the plot if ran interactively

    def graph_statistics(self):
        diameter = nx.diameter(self.g)
        avg_shortest_path = nx.average_shortest_path_length(self.g)
        node_count = nx.number_of_nodes(self.g)
        edge_count = nx.number_of_edges(self.g)

        fmt = f"Graph diamter: {diameter}\nAverage distance: {avg_shortest_path}\nTotal nodes: {node_count}\n" \
            f"Total edges: {edge_count}"
        print(fmt)

    def get_screen_name(self, profiles):
        for k,v in profiles.items():
            self.name_id_lookup[k] = v['screen_name']
            # self.name_id_lookup[user_info['id']] = user_info['screen_name']



# def main():
#     a = authenticate.Authenticate(creds_file='twitter_creds.BU')
#     g = Graph(twitter_api=a.twitter_api, file='twitter_graph.txt', use_name=True)
#
#
# if __name__ == "__main__":
#     main()


