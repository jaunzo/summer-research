"""
Module that runs external executable compiled from cwhidden's rSPR program which calculates drSPR.

Source code for rspr executable:
https://github.com/cwhidden/rspr
"""

import platform
import subprocess
from subprocess import PIPE, Popen
from phylonetwork import MalformedNewickException, PhylogeneticNetwork
import network_processing as np
import matplotlib.pyplot as plt
import path

def rspr(tree1, tree2):
    """
    Runs an external executable that calculates the rspr of 2 binary
    phylogenetic trees
    
    Parameters
    ----------
    tree1 : str
    tree2 : str
        Two trees to compute distance
        
    Returns
    -------
    tuple[list[str], list[str]]
        Tuple of array of distances and array of clusters
    """
    input_string = tree1 + "\n" + tree2
    
    if platform.system() == "Windows":
        executable = Popen(executable="rspr.exe", args="", stdin=PIPE,
                               stdout=PIPE, stderr=PIPE,
                               universal_newlines=True, shell=True)
        
        out, err = executable.communicate(input=input_string) 
        
        executable.wait()
        executable.kill()
        
    else:
        path = path.resource_path("rspr")
        executable = subprocess.run(path, stdout=PIPE, stderr=PIPE,
                                    input=input_string.encode("utf-8"),
                                    shell=True)
        
        out = executable.stdout.decode("utf-8")
        err = executable.stderr.decode("utf-8")
    
    out = out.strip()
    output_list = out.split("\n")
    
    if err:
        print(err)
        print("Error occured in rspr")
        
    
    length = len(output_list)

    forest = output_list[length - 3]
    distance = output_list[-1].split()
    distance = distance[-1]
    equals_index = distance.index("=")
    distance = distance[equals_index+1:]
    
    clusters = forest.split()[2:]
    
    return (distance, clusters)


def rspr_pairwise(trees):
    """
    Takes a list of trees and runs rspr for every pair of trees
    
    Parameters
    ----------
    trees : list[str]
        Array of trees in newick format
        
    Returns
    -------
    tuple(list[str], list[str], list[Tree])
        Tuple of distance array, clusters array and trees array
    """
    length = len(trees)
    
    trees_array = [None] * length
    
    distance_array = [["-" for i in range(length)] for j in range(length)]
    clusters_array = [["-" for i in range(length)] for j in range(length)]
    
    for i in range(len(trees)):
        for j in range(i, len(trees)):
            try:
                t1 = Tree(trees[i] + ";", f"t{i+1}")
                t2 = Tree(trees[j] + ";", f"t{j+1}")
                trees_array[i] = t1
                
                #Check if leaf set the same
                t1_leaves = t1.leaves 
                t2_leaves = t2.leaves
                if t1_leaves == t2_leaves:
                    (distance, clusters) = rspr(t1.eNewick(), t2.eNewick())
                    distance_array[i][j] = distance
                    clusters_array[i][j] = clusters
                    
                else:
                    missing_leaves = (t1_leaves.difference(t2_leaves)).union(t2_leaves.difference(t1_leaves))
                    distance_array[i][j] = "X"
                    clusters_array[i][j] = [f"Error occured. Trees don't have same taxa set.  Missing taxa: {', '.join(missing_leaves)}"]
                
            except MalformedNewickException:
                distance_array[i][j] = "X"
                clusters_array[i][j] = ["Error occured. Check tree newick string."]
            
            
    return (distance_array, clusters_array, trees_array)

def calculate_drspr(trees_array):
    """
    Calculates drSPR. If more than 2 trees are given, distances are calculated pairwise
    
    Parameters
    ----------
    trees_array : list[str]
        Array of trees in newick format
        
    Returns
    -------
    tuple[list[str], list[str], Trees]
        Tuple of distance array, clusters array and Trees object
    """
    length = len(trees_array)
    
    if length < 2:
        raise MalformedNewickException
    
    elif length == 2:
        for i in range(len(trees_array)):
            try:
                trees_array[i] = Tree(trees_array[i] + ";", f"t{i+1}") 
                
            except MalformedNewickException as e:
                trees_array[i] = None
                distances = ["X"]
                clusters = [f"Error occured. Check newick string of t{i+1}"]
                return (distances, clusters, Trees(trees_array))
        
        t1_leaves = trees_array[0].leaves
        t2_leaves = trees_array[1].leaves
        if t1_leaves == t2_leaves:
            (distances, clusters) = rspr(trees_array[0].eNewick(), trees_array[1].eNewick())
        else:
            missing_leaves = (t1_leaves.difference(t2_leaves)).union(t2_leaves.difference(t1_leaves))
            return ("X", f"Error occured. Trees don't have same taxa set. Missing taxa: {', '.join(missing_leaves)}", trees_array)
            
    else:
        (distances, clusters, trees_array) = rspr_pairwise(trees_array)
        
    trees_obj = Trees(trees_array)
    
    return (distances, clusters, trees_obj)


    
class Tree(PhylogeneticNetwork):
    """Class for trees involved in drSPR function"""
    def __init__(self, tree, number):
        """
        Parameters
        ----------
        tree : str
            Single tree in newick format
            
        number : str
            Tree id
        """
        super().__init__(tree)
        self.id = number
        
    @property
    def leaves(self):
        """
        Returns
        -------
        set(str)
            Set of labelled leaves in tree
        """
        leaves = super().leaves
        labelled_leaves = set()
        
        labels_dict = self.labeling_dict
        
        for leaf in leaves:
            if leaf in labels_dict:
                labelled_leaves.add(labels_dict[leaf])
            
        return labelled_leaves



class Trees:
    """Class for collection of trees"""
    def __init__(self, trees_array):
        """
        Parameters
        ----------
        trees_array : list[Tree]
            Array of Tree objects
        """
        self.trees = trees_array
        self.figures = []
        
    def draw(self, close_figs=True):
        """
        Draw input trees

        Parameters
        ----------
        close_figs : bool
            Logic to close tree figures that are drawn (default is True). False if you want to use matplotlib's
            figure interface instead of phyloprogram front end.
            
        Returns
        -------
        list[Figure]
            Array of figures where trees are drawn
        """
        
        #Number of rows and cols per figure
        #i.e rows * cols supbplots/trees per figure
        rows = 1
        cols = 2
        
        for i, tree in enumerate(self.trees):
            #Draw the output trees
            #Display rows * cols trees per figure
            plot_number = i % (rows * cols)
            if plot_number == 0:
                
                #Close open figures
                if close_figs:
                    plt.close("all")
                
                #Create new figure
                figure = plt.figure()
                
                #Add new figure
                self.figures.append(figure)
                
                
            if tree:
                tree_ax = figure.add_subplot(rows, cols, plot_number + 1)
                tree_ax.title.set_text(f"t{i+1}")
                
                np.create_graph(tree, figure.gca())
                
        #plt.show()
        
        return self.figures
                
    
if __name__ == "__main__":
    trees = []
    trees.append("(((((((1,9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10)),5)")
    trees.append("((((((((((14,6),4),7),11),(1,9)),2),((13,3),8)),15),(10,12)),5)")
    trees.append("(((((((14,6),4),7),11),(10,12)),((((1,9),2),((13,3),8)),15)),5)")
    trees.append("((((((((((14,6),4),7),11),((1,5),9)),2),((13,3),8)),12),15),10)")
    trees.append("(((((((1,5),9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10))")
#     trees.append("(((1,2),3),4)")
#     trees.append("(((1,4),2),3)")
    
    (distances, clusters, trees_obj) = calculate_drspr(trees)
    length = len(distances)
    
    print("TREES")
    for i, tree in enumerate(trees, start=1):
        print(f"t{i}:\n{tree}\n")

    if length == 1:
        print(f"drSPR = {distances[0]}")
        print(f"Clusters: {clusters[0]}")
        
        
    else:
        print("MATRIX")
        #Printing matrix
        for i in range(length):
            print(", ".join(distances[i]))
            
        print()
            
        print("CLUSTERS")
        for i in range(length-1):
            print(f"Clusters compared with t{i+1}:")
            for j in range(i+1, len(clusters[i])):
                print(f"t{j+1} (drSPR = {distances[i][j]}): {' '.join(clusters[i][j])}")
                
            print()
            
    #Draw trees
    figures = trees_obj.draw(False)
    plt.show()
    
    
    