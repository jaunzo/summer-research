"""
Module that runs external executable compiled from cwhidden's rSPR program which calculates rSPR.

Source code for rspr executable:
https://github.com/cwhidden/rspr

Copyright 2009-2014 Chris Whidden
whidden@cs.dal.ca
http://kiwi.cs.dal.ca/Software/RSPR
April 29, 2014
Version 1.2.2

rspr is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

rspr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with rspr.  If not, see <http://www.gnu.org/licenses/>.

"""

import platform
from subprocess import PIPE, Popen
from phylonetwork import MalformedNewickException, PhylogeneticNetwork

def rspr(tree1, tree2):
    """
    Runs an external executable that calculates the rspr of 2 binary
    phylogenetic trees
    """
    input_string = tree1 + "\n" + tree2
    
    if platform.system() == "Windows":
        executable = Popen(executable="rspr.exe", args="", stdin=PIPE,
                               stdout=PIPE, stderr=PIPE,
                               universal_newlines=True, shell=True)

    out, err = executable.communicate(input=input_string)
    
    out = out.strip()
    output_list = out.split("\n")
    
    if err:
        print("test")
        
    executable.wait()
    executable.kill()
    
    length = len(output_list)
    
    
    #Check if the trees were valid
    t1 = output_list[0].split()[1].strip()
    t2 = output_list[1].split()[1].strip()
    
    if t1 == "p":
        return ("X", "")
    elif t2 == "p":
        return ("X", "")
    else:
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
    """
    length = len(trees)
    
    distance_array = [["-" for i in range(length)] for j in range(length)]
    clusters_array = [["-" for i in range(length)] for j in range(length)]
    
    for i in range(len(trees)):
        for j in range(i, len(trees)):
            try:
                t1 = Tree(trees[i] + ";", f"t{i+1}")
                t2 = Tree(trees[j] + ";", f"t{j+1}")
                (distance, clusters) = rspr(t1.eNewick(), t2.eNewick())
                distance_array[i][j] = distance
                clusters_array[i][j] = clusters
                
            except MalformedNewickException:
                distance_array[i][j] = "X"
                clusters_array[i][j] = ["Error occured. Check tree newick string."]
            
            
    return (distance_array, clusters_array)

def calculate_drspr(trees_array):
    length = len(trees_array)
    
    if length < 2:
        raise MalformedNewickException
    
    elif length == 2:
        for i in range(len(trees_array)):
            try:
                trees_array[i] = Tree(trees_array[i] + ";", f"t{i+1}")
                
            except MalformedNewickException as e:
                trees_array[i] = ""
                distances = ["X"]
                clusters = [f"Error occured. Check newick string of t{i+1}"]
                return (distances, clusters)
            
        #print(trees_array[0].eNewick() +"\n"+ trees_array[1].eNewick())
        (distances, clusters) = rspr(trees_array[0].eNewick(), trees_array[1].eNewick())
            
        
    else:
        (distances, clusters) = rspr_pairwise(trees_array)
        
    return (distances, clusters)
    
class Tree(PhylogeneticNetwork):
    def __init__(self, tree, number):
        super().__init__(tree)
        self.id = number
        
    
if __name__ == "__main__":
    trees = []
    #trees.append("(((((((1,9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10)),5)")
    trees.append("(((((((1,9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10)),5);")
    trees.append("((((((((((14,6),4),7),11),(1,9)),2),((13,3),8)),15),(10,12)),5);")
    trees.append("(((((((14,6),4),7),11),(10,12)),((((1,9),2),((13,3),8)),15)),5);")
    trees.append("((((((((((14,6),4),7),11),((1,5),9)),2),((13,3),8)),12),15),10);")
    trees.append("(((((((1,5),9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10));")
    
    (distances, clusters) = calculate_drspr(trees)
    
    
    length = len(distances)

    if length == 1:
        print(f"drSPR = {distances[0]}")
        print(f"Clusters: {clusters[0]}")
        
        
    else:
        #Printing matrix
        for i in range(length):
            print(", ".join(distances[i]))
            
        print()
            
        for i in range(length-1):
            print(f"Clusters compared with t{i+1}:")
            for j in range(i+1, len(clusters[i])):
                print(f"t{j+1} (drSPR = {distances[i][j]}): {' '.join(clusters[i][j])}")
                
            print()
        
        
    
    
    
    