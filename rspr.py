"""Module that handles the generation of trees displayed by input network"""

#! /usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
##  DendroPy Phylogenetic Computing Library.
##
##  Copyright 2010-2015 Jeet Sukumaran and Mark T. Holder.
##  All rights reserved.
##
##  See "LICENSE.rst" for terms and conditions of usage.
##
##  If you use this work or any portion thereof in published work,
##  please cite it as:
##
##     Sukumaran, J. and M. T. Holder. 2010. DendroPy: a Python library
##     for phylogenetic computing. Bioinformatics 26: 1569-1571.
##
##############################################################################

from phylonetwork import PhylogeneticNetwork
import matplotlib.pyplot as plt
import warnings
import matplotlib.cbook

from cached_property import cached_property


def create_graph(graph, ax):
    """Variant of draw method from phylonetwork library"""
    import networkx as nx
    from networkx.drawing.nx_agraph import graphviz_layout
    pos = graphviz_layout(graph, prog="dot")
    nx.draw_networkx_nodes(graph, pos, graph.tree_nodes, node_size=200, node_color="#57f542", ax=ax)
    nx.draw_networkx_nodes(graph, pos, graph.reticulations, node_size=150, node_shape="s", node_color="#57f542", ax=ax)
    nx.draw_networkx_edges(graph, pos, ax=ax)
    nx.draw_networkx_labels(graph, pos, ax=ax, labels=graph.labeling_dict)

    
class Tree(PhylogeneticNetwork):
    """
    Class that handles the trees.
    """
    def __init__(self, newick):
        super().__init__(newick)
        
    def draw(self):
        figure = plt.figure()
        create_graph(self, figure.gca())
        
        return figure
        
        
if __name__ == "__main__":
    tree1_newick = "((A,B),(C,(D,E)));"
    tree2_newick = "((A,C),(D,(B,E)));"
    tree1 = Tree(tree1_newick)
    tree2 = Tree(tree2_newick)
    
    fig1 = tree1.draw()
    fig2 = tree2.draw()
    
    plt.show()
            
