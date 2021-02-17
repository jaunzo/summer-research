"""
Module that calculates spr neighbours

Source code for spr_dense_graph executable:
https://github.com/cwhidden/spr_neighbors
"""
import platform
import path
from subprocess import PIPE, Popen
import networkx as nx
import matplotlib.pyplot as plt
    
class RsprGraph:
    """Class for creating rspr graph"""
    def __init__(self, trees_string):
        """
        Parameters
        ----------
        trees_string : str
            String of all tree newick strings, each terminated by semicolon.
        """
        self.spr_dense_graph(trees_string)
        input_trees = trees_string.translate(str.maketrans('', '', ' \n\t\r'))
        self.trees_array = input_trees.split(";")
        
        if not self.trees_array[-1]:
            self.trees_array.pop()
        self.create_graph()
    
    @property
    def text(self):
        """
        Text of all trees.
        
        Returns
        -------
        str
            Text representation of all trees.
        """
        text = ""
        for i, tree in enumerate(self.trees_array, start=1):
            text += f"t{i}:\n{tree};\n\n"
            
        hamilton_path = self.hamilton(self.graph)
        if hamilton_path:
            hamilton_cycle = f"Yes\n{' -> '.join(hamilton_path)}\n"
        else:
            hamilton_cycle = "No\n"
            
        text += f"\nHAMILTONIAN CYCLE: {hamilton_cycle}\n"
            
        text += "\nADJACENCY LIST:\n"
            
        for node, neighbour_array in self.adjacency_dict.items():
            text += f"{node}: {', '.join(neighbour_array)}\n"
        
        return text
        

    def spr_dense_graph(self, trees_string):
        """
        Gets neighbours of a single tree
        
        Parameters
        ----------
        trees_string : str
            String of all tree newick strings, each terminated by semicolon.
        """
        if platform.system() == "Windows":
            file = path.resource_path("spr_dense_graph.exe")
            executable = Popen(executable=file, args="", stdin=PIPE,
                                   stdout=PIPE, stderr=PIPE,
                                   universal_newlines=True, shell=True)
            
            out, err = executable.communicate(input=trees_string) 
            
            executable.wait()
            executable.kill()
            
        else:
            file = path.resource_path("spr_dense_graph")
            executable = subprocess.run(file, stdout=PIPE, stderr=PIPE,
                                        input=trees_string.encode("utf-8"),
                                        shell=True)
            
            out = executable.stdout.decode("utf-8")
            err = executable.stderr.decode("utf-8")
        
        out = out.strip()
        output_list = out.split("\n")
        
        if err:
            print(err)
            print("Error occured in spr_dense_graph")
            
        #Create adjacency dict
        lines_array = out.split()
        self.adjacency_dict = {}
        
        for line in lines_array:
            array = line.split(",")
            node = f"t{int(array[0])+1}"
            neighbour = f"t{int(array[1])+1}"
            
            if node in self.adjacency_dict:
                self.adjacency_dict[node].append(neighbour)
            else:
                self.adjacency_dict[node] = [neighbour]
        
        
    def create_graph(self):
        """Draw graph using networkx"""
        self.figure = plt.figure()
        self.graph = nx.Graph()
        
        length = len(self.trees_array)
        
        for i, tree in enumerate(self.trees_array, start=1):
            self.graph.add_node(f"t{i}")
        
        for node, neighbor_array in self.adjacency_dict.items():
            for neighbor in neighbor_array:
                self.graph.add_edge(node, neighbor)
            
        nx.draw(self.graph, node_color="#57f542", with_labels=True, ax=self.figure.gca())
        plt.show()
        
        
    def hamilton(self, G):
        F = [(G,[list(G.nodes())[0]])]
        n = G.number_of_nodes()
        while F:
            graph,path = F.pop()
            confs = []
            neighbors = (node for node in graph.neighbors(path[-1]) 
                         if node != path[-1]) #exclude self loops
            for neighbor in neighbors:
                conf_p = path[:]
                conf_p.append(neighbor)
                conf_g = nx.Graph(graph)
                conf_g.remove_node(path[-1])
                confs.append((conf_g,conf_p))
            for g,p in confs:
                if len(p)==n:
                    return p
                else:
                    F.append((g,p))
        return None
        

if __name__ == "__main__":
    trees = []
    trees.append("((1,2),3);")
    trees.append("((1,3),2);")
    trees.append("(1,(2,3));")
    
    #f = open("graph1.txt", "r")
    #trees_string = f.read()
    
    rspr_graph = RsprGraph("\n".join(trees))
    print(rspr_graph.text)
    
