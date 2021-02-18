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
            

        number_nodes = self.graph.number_of_nodes()
        first_vertex = list(self.graph.nodes())[0]
        hamilton_path = RsprGraph.hamiltonian_cycle(self.graph, first_vertex, (), first_vertex, number_nodes)
            
            
        #hamilton_path = self.hamiltonian_cycle(self.graph)
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
    
            
    @staticmethod
    def hamiltonian_cycle(graph, current_vertex, path, root, num_nodes):
        """
        Static class method that finds hamiltonian cycle in a graph
        
        Parameters
        ----------
        graph : Graph
            Networkx graph
            
        current_vertex : str
            Current vertex in graph traversal
            
        path : tuple[str]
            Contains current path from root to current vertex
            
        root : str
            First vertex where path starts
            
        num_nodes : int
            Number of nodes in graph
            
        Returns
        -------
        tuple[str]
            Returns cycle path if there is a hamiltonian cycle, else returns None
        """
        path += (current_vertex,)
        
        #Base case
        if len(path)==num_nodes:
            #If path has all nodes and the last node is adjacent to the root
            if root in list(graph.neighbors(current_vertex)):
                return (path + (root,)) #Return cycle path
        
        neighbours = graph.neighbors(current_vertex)
        
        for neighbour in neighbours:
            if neighbour not in path:
                result = RsprGraph.hamiltonian_cycle(graph, neighbour, path, root, num_nodes)
                if result:
                    return result
            
        return None

if __name__ == "__main__":
    trees = []
    trees.append("((1,2),3);")
    trees.append("((1,3),2);")
    trees.append("(1,(2,3));")
    trees_str = "\n".join(trees)
    
    f = open("20.txt", "r")
    trees_string = f.read()
    
    rspr_graph = RsprGraph(trees_string)
    print(rspr_graph.text)
    


#     graph = nx.Graph()
#     
#     graph.add_node('a')
#     graph.add_node('b')
#     graph.add_node('c')
#     graph.add_node('d')
#     graph.add_node('e')
#     graph.add_node('f')
#     
#     graph.add_edge('a', 'b')
#     graph.add_edge('a', 'c')
#     graph.add_edge('a', 'd')
#     
#     graph.add_edge('b', 'c')
#     graph.add_edge('b', 'e')
#     
#     graph.add_edge('c', 'd')
#     graph.add_edge('c', 'e')
#     
#     graph.add_edge('d', 'e')
#     graph.add_edge('d', 'f')
#     
#     graph.add_edge('e', 'f')
#         
#     nx.draw(graph, node_color="#57f542", with_labels=True)
#     plt.show()
