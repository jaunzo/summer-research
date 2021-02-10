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
import subprocess
from subprocess import PIPE

def rspr(tree1, tree2):
    """
    Runs an external executable that calculates the rspr of 2 binary
    phylogenetic trees
    """
    input_string = tree1 + "\n" + tree2
    
    if platform.system() == "Windows":
        executable = subprocess.Popen(executable="rspr.exe", args="", stdin=PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True, shell=True)

    out, err = executable.communicate(input=input_string)
    
    out = out.strip()
    output_list = out.split("\n")
    
    if err:
        print("test")
        
    executable.wait()
    executable.terminate()
    
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
    """
    length = len(trees)
    
    distance_array = [["-" for i in range(length)] for j in range(length)]
    clusters_array = [["-" for i in range(length)] for j in range(length)]
    
    for i in range(len(trees)):
        for j in range(i, len(trees)):
            (distance, clusters) = rspr(trees[i], trees[j])
            distance_array[i][j] = distance
            clusters_array[i][j] = clusters
            
    return (distance_array, clusters_array)

    
if __name__ == "__main__":
    trees = []
    trees.append("(((((((1,9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10)),5);")
    trees.append("((((((((((14,6),4),7),11),(1,9)),2),((13,3),8)),15),(10,12)),5);")
    trees.append("(((((((14,6),4),7),11),(10,12)),((((1,9),2),((13,3),8)),15)),5);")
    trees.append("((((((((((14,6),4),7),11),((1,5),9)),2),((13,3),8)),12),15),10);")
    trees.append("(((((((1,5),9),2),((13,3),8)),12),15),(((((14,6),4),7),11),10));")
    
    (distances, clusters) = rspr_pairwise(trees)
    
    length = len(distances)

    
    for i in range(length):
        print(", ".join(distances[i]))
        
    print()
        
    for i in range(length-1):
        print(f"Clusters compared with t{i+1}:")
        for j in range(i+1, len(clusters[i])):
            print(f"t{j+1} (drSPR = {distances[i][j]}): {' '.join(clusters[i][j])}")
            
        print()
        
        
    
    
    
    