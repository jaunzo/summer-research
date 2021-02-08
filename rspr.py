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
    distance = int(distance[equals_index+1:])
    
    clusters = forest.split()[2:]
    
    return (distance, clusters)
    
    
if __name__ == "__main__":
    tree1 = "(((1,2),3),4);"
    tree2 = "(((1,4),2),3);"
    print(rspr(tree1, tree2))