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

import phylonetwork as pn
import matplotlib.pyplot as plt
import copy
import dendropy
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



class Network:
    """
    Class that uses the PhylogeneticNetwork class and handles generation of trees.
    Any labels of internal nodes are removed leaving only leaves labelled.
    """
    def __init__(self, network_newick, network_figure, graphics):
        self._original_network = pn.PhylogeneticNetwork(eNewick=network_newick)
        self._current_network = copy.deepcopy(self._original_network)
        
        self._newick = network_newick
        self.figure = network_figure
        
        self.graphics = graphics

        self.set_current_selected_leaves(self.labelled_leaves)
        self.retain_labelled_leaves()
                
        #Get reticulations
        self._current_reticulations = tuple(self._current_network.reticulations)
        self.trees_dict = {} #Dictionary that stores the selected leaves and corresponding generated Trees object

        
    @cached_property
    def num_reticulations(self):
        """Number of reticulations in input network"""
        return len(self._original_network.reticulations)
        
    @cached_property
    def num_labelled_leaves(self):
        """Number of labelled leaves in input network"""
        return len(self.labelled_leaves)
        
    @cached_property
    def labelled_leaves(self):
        """Labelled leaves of the input network."""
        #Get all labelled leaves from input network
        labelled_leaves = []
        leaves = list(self._original_network.leaves)
        
        for net_leaf in leaves:
            label = self._original_network.label(net_leaf)
            if label != None:
                labelled_leaves.append(label)
                
        labelled_leaves.sort()
        return labelled_leaves
    
    @property
    def text(self):
        """Text of network details"""
        contents = f"NETWORK:\n{self._newick}\n\n"
        contents += f"Reticulations: {self.num_reticulations}\n"
        contents += f"Network leaves:\n{self.labelled_leaves}\n"
        return contents
    
    @property
    def newick(self):
        """Extended newick string of network"""
        return self._newick

    @property
    def current_network(self):
        """PhylogeneticNetwork instance of the current network"""
        return self._current_network
    
    def draw(self):
        """Draws the network on the main window of the program."""
        #Display input network
        create_graph(self._original_network, self.figure.gca())
        
    def set_current_selected_leaves(self, selected_leaves):
        """Method that takes in a string of leaves and sets the leaves to filter trees"""
        if isinstance(selected_leaves, str):
            leaves = [x.strip() for x in selected_leaves.split(",")]
            leaves.sort()
            selected_leaves = tuple(leaves)
        else:
            selected_leaves = tuple(self.labelled_leaves)
        
        #Delete invalid leaves
        valid_leaves = []    
        
        for leaf in selected_leaves:
            if leaf in self.labelled_leaves:
                valid_leaves.append(leaf)
            
        if not valid_leaves:
            raise InvalidLeaves()
        else:
            valid_leaves.sort()
            self.current_selected_leaves = tuple(valid_leaves)
    
    @cached_property
    def total_trees(self):
        """Total number of trees. For binary networks, returns 2^reticulations"""
        return len(self.all_trees)
            
    @cached_property
    def all_trees(self):
        """Part of initialisation process. Get all 2^r unsuppressed trees"""
        
        #Unique node ids are labelled in DFS order
        #Get number of reticulations
        number_reticulations = len(self._current_reticulations)
        
        #Creating trees
        prev_networks = [self._current_network]

        #Removing one edge per reticulation
        for i in range(number_reticulations):
            new_networks = []
            reticulation = self._current_reticulations[i]
            
            for parent in self._current_network.predecessors(reticulation):
                for prev_net in prev_networks:
                    new_net = copy.deepcopy(prev_net)
                    new_net.remove_edge(parent, reticulation)
                    new_networks.append(new_net)
                    
            prev_networks = copy.deepcopy(new_networks)
        
        return prev_networks #array of PhylogeneticNetwork objects
        
    
    def process(self):
        """Process the current_network with currently labelled leaves and return tree figures"""
        if self.current_selected_leaves in self.trees_dict:
            return self.trees_dict[self.current_selected_leaves]
            
        else:
            trees = Trees(self, self.current_selected_leaves)
            trees.generate()
            
            self.trees_dict[trees.leaves] = trees
            return trees
        
        
    def retain_labelled_leaves(self):
        """Modify the current network to remove labels of nodes not specified in leaves argument"""
        
        labels_to_remove = []
        labelled_nodes = self._original_network.labeled_nodes
        
        for node in labelled_nodes:
            label = self._original_network.label(node)
            
            if label not in self.labelled_leaves:
                labels_to_remove.append(label)
                
        self._current_network.remove_taxa(labels_to_remove)

class InvalidLeaves(Exception):
    """Exception raised for errors in the input leaves."""

    def __init__(self, message="Couldn't find any of the specified leaves in the network."):
        self.message = message
        super().__init__(self.message)
    
class Trees:
    """
    Class that handles the generation of displayed trees from network.
    """
    def __init__(self, network, leaves):
        self.trees_data = {} #Dictionary of unique tree newicks with count
        self.tree_figs = []
        self.network = network
        self._selected_leaves = leaves
        
    @property
    def num_unique_trees(self):
        """Returns of unique trees"""
        return len(self.data)
        
    @property
    def data(self):
        """
        Dictionary with the tree in newick format as the key and the number of occurences
        and phylonetwork object as the value.
        """
        return self.trees_data
        
    @property
    def figures(self):
        """Figures of the trees."""
        return self.tree_figs
    
    @property
    def leaves(self):
        """Leaves of the trees."""
        return tuple(self._selected_leaves)
    
    @cached_property
    def text(self):
        """Text representation of the network and the trees."""
        contents = f"\n\nTREES\nLeaves\n{self._selected_leaves}\n\nTotal trees: {self.network.total_trees}\nDistinct trees: {self.num_unique_trees}\n\n"
        
        for tree, data in self.trees_data.items():
            contents += f"{tree}  x{data[0]}\n"
            
        return contents
        
    def draw(self):
        tree_axes = {} #Dictionary of unique tree newicks with plot axes
        unique_plot_count = 1
        
        unique_trees_fig = plt.figure("Output trees")
        self.tree_figs.append(unique_trees_fig)
        
        rows = 1
        cols = 2
        
        for tree_newick, data in self.trees_data.items():
            #Draw the output trees
            #Display rows * cols trees per figure
            if unique_plot_count > rows * cols:
                
                unique_plot_count = 1
                
                #Close open figures
                plt.close("all")
                
                #Create new figure
                unique_trees_fig = plt.figure()
                
                #Add new figure
                self.tree_figs.append(unique_trees_fig)
                
            tree_ax = unique_trees_fig.add_subplot(rows, cols, unique_plot_count)
            
            #Store ax subplots to title later
            tree_axes[tree_newick] = tree_ax
            
            create_graph(data[1], unique_trees_fig.gca())
            unique_plot_count += 1
                
        #Add number above subplot
        for tree_newick in self.trees_data.keys():
            tree_ax = tree_axes[tree_newick]
            tree_count = self.trees_data[tree_newick][0]
            tree_ax.title.set_text(tree_count)
    
    def generate(self):
        """Get and plot all unique trees displayed by the given network with the number of occurence displayed above the plot."""
        unique_tree_newicks = set()

        for tree in self.network.all_trees:
            #Reduce tree
            tree.remove_elementary_nodes()
            tree_string = "[&R] " + tree.eNewick()
            dendro_tree = dendropy.Tree.get_from_string(tree_string,"newick")
            dendro_tree.retain_taxa_with_labels(self._selected_leaves)
            
            newick_string = dendro_tree.as_string(schema="newick")
            
            try:
                new_string = newick_string[newick_string.index("("):newick_string.index(";") + 1]
            except ValueError: #If tree only has one node
                index = newick_string.index(";")
                new_string = newick_string[index - 1: index + 1]
            
            new_tree = pn.PhylogeneticNetwork(eNewick=new_string)
            tree_newick = new_tree.eNewick()
            
            warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
            
            #Check if tree is unique
            if tree_newick in unique_tree_newicks:
                self.trees_data[tree_newick][0] += 1
            
            elif tree_newick not in unique_tree_newicks:
                self.trees_data[tree_newick] = [1]
                unique_tree_newicks.add(tree_newick)

            self.trees_data[tree_newick].append(new_tree)
            