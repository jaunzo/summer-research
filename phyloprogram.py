"""
Main application. Defines the classes and methods of the application gui.
"""

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import (Tk, Canvas, Scrollbar, Menu, Toplevel,
                     Frame, Label, Text, IntVar, Checkbutton)
from network_processing import Network
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys, os, platform, webbrowser
import matplotlib.pyplot as plt
from widgets import HoverButton
from phylonetwork import MalformedNewickException
from dialogs import (MultiChoicePrompt, StringInputPrompt)
from widgets import ToolTip
import drspr as d
from rspr_graph import RsprGraph

# def executable_path():
#     if getattr(sys, 'frozen', False):
#         #application_path = sys._MEIPASS
#         application_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
#     else:
#         print("else")
#         application_path = os.path.dirname(os.path.abspath(__file__))
#         
#     print("Executable path")
#     print(application_path)

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Parameters
    ----------
    relative_path : str
        Relative path to file from script's location
        
    Returns
    -------
    str
        Absolute path to file
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print(os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    print(path)
    return path

class Program(Tk):
    """
    Class for application that takes a network in extended newick format and displays trees.
    This program can save the network and trees as images or text file.
    """
    def __init__(self):
        super().__init__()
        ORIGINAL_DPI = 96.0
        #Scale the window depending on current monitor's dpi
        self.current_dpi = self._get_dpi()
        self.scale = self.current_dpi / ORIGINAL_DPI
        self.tk.call("tk", "scaling", self.scale + 0.5)
        
        self.net_frame = None
        self.net_directory = ""
        self.trees_directory = ""
        self.save_directory = ""
        self.net_fig = None
        self.graph_window = None
        
        self.title("PhyloProgram")
        
        self.scaled_width = self._scale_window(750)
        self.scaled_height = self._scale_window(600)
        
        self.geometry(f"{self.scaled_width}x{self.scaled_height}")
        self.protocol("WM_DELETE_WINDOW", self._exit)
        
        #prompt windows
        self.input_prompt = None
        self.select_leaves_prompt = None
        
        self._initialise_menu_bar()
        self._initialise_tool_bar()
        self._initialise_info_bar()
        
        self.main_frame = Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=1)
        
        #initialise network figure canvas in main window
        self.net_fig = plt.figure("Input network")
        self.net_fig.gca().clear()
        self.net_canvas = FigureCanvasTkAgg(self.net_fig, master=self.main_frame)
        
        self._initialise_main_text_widget()
#         self.current_path = os.path.abspath(".")
#         self.temp_path = sys._MEIPASS
#         
#         print(self.current_path)
#         print(self.temp_path)
        print(sys.executable)
        resource_path("")
        
        
    def _get_dpi(self):
        """
        For private use. Get the dpi of the current screen
        
        Returns
        -------
        int
            DPI of current monitor
        """
        screen = Tk()
        current_dpi = screen.winfo_fpixels("1i")
        screen.destroy()
        return current_dpi
    
    
    def _initialise_menu_bar(self):
        """For private use. Initialise the top menu bar and bind shortcuts"""
        menu_bar = Menu(self)
        
        file_menu = Menu(menu_bar, tearoff=0)
        
        file_menu.add_command(label="Enter network", command=self.new_network, accelerator="Ctrl+N")
        file_menu.add_command(label="Open network...", command=self.open_network, accelerator="Ctrl+O")
        
        file_menu.add_separator()
        
        #drSPR sub menu
        rspr_graph_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Create rSPR graph", menu=rspr_graph_menu)
        rspr_graph_menu.add_command(label="Enter trees", command=lambda: self.new_trees("Create rSPR graph"), accelerator="Ctrl+G")
        rspr_graph_menu.add_command(label="Open trees...", command=lambda: self.open_trees("Create rSPR graph"), accelerator="Ctrl+Shift+G")
        
        drspr_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Calculate drSPR", menu=drspr_menu)
        drspr_menu.add_command(label="Enter trees", command=lambda: self.new_trees("Calculate drSPR"), accelerator="Ctrl+D")
        drspr_menu.add_command(label="Open trees...", command=lambda: self.open_trees("Calculate drSPR"), accelerator="Ctrl+Shift+D")
        
        file_menu.add_separator()
        
        self.save_sub_menu = Menu(file_menu, tearoff=0)
        self.save_sub_menu.add_command(label="Text file (trees only)", command=self.save_trees_only_text, accelerator="Ctrl+T")
        self.save_sub_menu.add_command(label="Text file", command=self.save_text, accelerator="Ctrl+Shift+T")
        self.save_sub_menu.add_command(label="Images", command=self.save_image, accelerator="Ctrl+Shift+I")
        file_menu.add_cascade(label="Save as...", menu=self.save_sub_menu)
        self.save_sub_menu.entryconfigure("Text file (trees only)", state="disabled")
        self.save_sub_menu.entryconfigure("Text file", state = "disabled")
        self.save_sub_menu.entryconfigure("Images", state="disabled")
        self.text_save_enabled = False
        self.image_save_enabled = False
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        help_menu.add_command(label="Manual", command=self.manual)
        help_menu.add_command(label="More info", command=self.open_github)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
        
        self.bind_all("<Control-n>", self.new_network)
        self.bind_all("<Control-o>", self.open_network)
        self.bind_all("<Control-g>", lambda event: self.new_trees("Create rSPR graph"))
        self.bind_all("<Control-G>", lambda event: self.open_trees("Create rSPR graph"))
        self.bind_all("<Control-d>", lambda event: self.new_trees("Calculate drSPR"))
        self.bind_all("<Control-D>", lambda event: self.open_trees("Calculate drSPR"))
        self.bind_all("<Control-T>", self.save_text)
        self.bind_all("<Control-t>", self.save_trees_only_text)
        self.bind_all("<Control-I>", self.save_image)
        
        
    def _initialise_tool_bar(self):
        """For private use. Initialise the tool bar"""
        self.toolbar = Frame(self, bd=1, relief="raised")
        self.toolbar.pack(fill="x")
        
        self.select_leaves_button = HoverButton(self.toolbar, text ="Select leaves", relief="raised",
                                         command=self._select_leaves, state="disabled",
                                                tooltip_text="Enter set leaves to be displayed in trees. By default, all labelled leaves in network are selected")
        
        self.draw_button = HoverButton(self.toolbar, text ="Draw trees/graph", relief="raised",
                                                command=self.generate_trees_graph, state="disabled",
                                                tooltip_text="Draw embedded/input trees or rSPR graph")
        
        self.graphics_enabled = IntVar()
        self.graphics = False
        graphics_check_box = Checkbutton(self.toolbar, text = "Enable graphics",
                                              variable=self.graphics_enabled, command=self.set_graphics)
        graphics_check_box.pack(side="right", padx=(0,10))
        ToolTip(graphics_check_box, "Enable graph visualisation for the next entered network/trees")
        
    
    def _initialise_info_bar(self):
        """For private use. Info bar that displays file opened, number of reticulations and labelled leaves in network"""
        self.info_frame = Frame(self)
        self.info_frame.pack(side="bottom", fill="x")
        
        self.info_label = Label(self.info_frame, text="")
        self.info_label.pack(side="right", padx=(0,10))
        
        self.file_label = Label(self.info_frame, text="")
        self.file_label.pack(side="left", padx=(10, 0))
        
    
    def _update_info_bar(self, filename=""):
        """
        For private use. Update the network info when new network is opened.
        
        Parameters
        ----------
        filename : str, optional
            Name of network/trees file opened
        """
        if self.network:
            num_reticulations = self.network.num_reticulations
            num_labelled_leaves = self.network.num_labelled_leaves
            info_text = f"{num_reticulations} reticulations, {num_labelled_leaves} labelled leaves"
            self.info_label["text"] = info_text
            
        else:
            self.info_label["text"] = ""
        
        self.file_label["text"] = filename
    
        
    def _initialise_main_text_widget(self):
        """Setup the text widget in the main window"""
        self.main_text_widget = Text(self.main_frame, width=25)
        scroll = Scrollbar(self.main_text_widget, command=self.main_text_widget.yview)
        self.main_text_widget['yscrollcommand'] = scroll.set
        scroll.pack(side="right", fill="y")
        
        #Bind to make text selectable on Mac
        self.main_text_widget.bind("<1>", lambda event: self.main_text_widget.focus_set())
    
        
    def _enable_tree_tools(self):
        """For private use. Buttons involving trees are enabled when a network has successfully been processed and displayed."""
        self.select_leaves_button.config(state = "normal")
        self.draw_button.config(state = "normal")
        
    def _enable_tree_display(self):
        """For private use. Draw button enabled when graphics enabled"""
        self.select_leaves_button.config(state = "disabled")
        self.draw_button.config(state = "normal")
        
    def _disable_tree_tools(self):
        """For private use. Disable tree buttons in toolbar"""
        self.select_leaves_button.config(state = "disabled")
        self.draw_button.config(state = "disabled")
        
    def _enable_select_leaves(self):
        """For private use. Enable select leaves button and disable draw button in toolbar"""
        self.select_leaves_button.config(state = "normal")
        self.draw_button.config(state = "disabled")
    
    def _enable_save(self):
        """For private use. Save functions are enabled when a network and trees has successfully been processed and displayed."""
        self.text_save_enabled = True
        self.image_save_enabled = True
        self.save_sub_menu.entryconfigure("Text file", state = "normal")
        self.save_sub_menu.entryconfigure("Images", state="normal")
        
        if self.network:
            self.save_sub_menu.entryconfigure("Text file (trees only)", state="normal")
        else:
            self.save_sub_menu.entryconfigure("Text file (trees only)", state="disabled")
        
    def _enable_text_save(self):
        """For private use. Used when visualisation is disabled. Only save as text enabled"""
        self.text_save_enabled = True
        self.image_save_enabled = False
        self.save_sub_menu.entryconfigure("Text file", state = "normal")
        self.save_sub_menu.entryconfigure("Images", state="disabled")
        if self.network:
            self.save_sub_menu.entryconfigure("Text file (trees only)", state="normal")
        else:
            self.save_sub_menu.entryconfigure("Text file (trees only)", state="disabled")
        
    def _disable_save(self):
        self.text_save_enabled = False
        self.image_save_enabled = False
        self.save_sub_menu.entryconfigure("Text file", state = "disabled")
        self.save_sub_menu.entryconfigure("Images", state="disabled")
        self.save_sub_menu.entryconfigure("Text file (trees only)", state="disabled")
        
        
    def _scale_window(self, window_length):
        """
        For private use. Scales the window based on calculated scale
        
        Parameters
        ----------
        window_length : int
            Window length dimension
            
        Returns
        -------
        int
            Scaled window length dimension
        """
        return round(window_length * self.scale)
    
    def _select_leaves(self):
        """For private use. Opens multiple choice dialog prompt to select the leaves that will be displayed in the generated trees."""
        if self.select_leaves_prompt:
            self.select_leaves_prompt.update()
            self.select_leaves_prompt.deiconify()
        else:
            self.select_leaves_prompt = MultiChoicePrompt(self, "Select leaves", "Specify the leaves that will be included in the generated trees.", ["All"],
                          customise_option=True, text_placeholder="e.g. 1, 2, 3, 4")
            
            
    def set_graphics(self, *_):
        """Set if the program draws the network and trees."""
        if self.graphics_enabled.get() == 1:
            self.graphics = True
        else:
            self.graphics = False
            
    def about(self):
        """Display overview of program in window"""
        self.about_window = Window(title="About")
        path_file = resource_path("about.txt")
        f = open(path_file, "r")
        about_text = f.read()
        text_widget = Text(self.about_window)
        text_widget.insert("1.0", about_text)
        text_widget.pack(expand=True, fill="both")
        text_widget.config(state="disabled")
    
    def manual(self):
        """Display program manual in window"""
        self.manual_window = Window(title="Manual", width=self.scaled_width,
                                    height=self.scaled_height//2)
        path_file = resource_path("manual.txt")
        f = open(path_file, "r")
        manual_text = f.read()
        text_widget = Text(self.manual_window, width=30)
        text_widget.insert("1.0", manual_text)
        scroll = Scrollbar(text_widget, command=text_widget.yview)
        text_widget['yscrollcommand'] = scroll.set
        scroll.pack(side="right", fill="y")
        text_widget.pack(expand=True, fill="both")
        text_widget.config(state="disabled")
        
    def open_github(self):
        """Open this program's Github page."""
        webbrowser.open("https://github.com/jaunzo/summer-research", new=2)
        
    def new_network(self, *_):
        """Displays dialog and gets network in extended newick format inputted by the user."""
        self.operation = "Network"
        
        if self.input_prompt:
            self.input_prompt.change_contents("Enter network", "Enter network in extended newick format", "e.g. ((a,(b)#H1), (#H1,c));")
            self.input_prompt.update()
            self.input_prompt.deiconify()
        else:
            self.input_prompt = StringInputPrompt(self, "Enter network", "Enter network in extended newick format", "e.g. ((a,(b)#H1), (#H1,c));", self.operation)
        
            
    def open_network(self, *_):
        """Displays open file prompt and processes a text file that contains the network in extended newick format."""
        self.operation = "Network"
        
        filename =  tkinter.filedialog.askopenfilename(initialdir = self.net_directory, title = "Open network...",
                                                       filetypes = (("text files","*.txt"),("all files","*.*")))

        path = os.path.split(filename)
        self.net_directory = path[0]
        text_file = path[1]
            
        if filename != "":
            f = open(filename, "r")
            text = f.read().strip()
            
            if text != None:
                network_newick = text[:text.find(";") + 1]
                try:
                    self.generate_network(network_newick, text_file)
                except MalformedNewickException:
                    error_message = "Could not read network.\n\nNetwork requirements:\nNetwork must contain at least one labelled leaf and string must terminate with semicolon."
                    tkinter.messagebox.showerror(title="Open network error", message=error_message)
        
        
    def generate_network(self, net_newick, filename=""):
        """
        Generate the network object and display it depending on graphics mode
        
        Parameters
        ----------
        net_newick : str
            Network in extended newick format
            
        filename : str, optional
            Filename of network opened (default="")
        """
        self.network = Network(net_newick, self.net_fig, self.graphics)
        self._update_info_bar(filename)
        
        self.net_newick = net_newick
        self._disable_save()
        
        if self.graphics:
            self._enable_tree_tools()
            self.main_text_widget.pack_forget()
            self.net_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
            self.display_network()
        else:
            self._enable_select_leaves()
            self.net_canvas.get_tk_widget().pack_forget()
            self.main_text_widget.pack(expand=True, fill="both")
            self.print_network()
            
            
    def print_network(self):
        """Print out the network in main window. Hide tree window"""
        if self.graph_window:
            self.graph_window.destroy()
            self.graph_window = None
        
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        self.main_text_widget.insert("1.0", self.network.text)
        self.main_text_widget.insert("end", "\n\nSelect leaves to generate embedded trees.")
        self.main_text_widget.config(state="disabled")
        
        
    def display_network(self):
        """Display input network in the main window."""
        
        if self.graph_window:
            self.graph_window.withdraw()
        
        self.net_fig.gca().clear()
        
        try:
            self.network.draw()
            self.net_canvas.draw()
        except (ValueError, ImportError) as e:
            if self.net_fig:
                self.net_fig.clear()
                self.net_canvas.get_tk_widget().pack_forget()
                self.main_text_widget.pack(expand=True, fill="both")
            
            error_message = f"Error: {e}\n\nTo draw networks and trees, Graphviz must be installed and it's executables must be in the system's PATH."
            tkinter.messagebox.showerror(title="Open network error", message=error_message)
            
            self.graphics_enabled.set(0)
            self.graphics = False
            self._disable_tree_tools()
            
            
            self.main_text_widget.config(state="normal")
            self.main_text_widget.delete('1.0', "end")
            self.main_text_widget.insert("1.0", "Error drawing network.\n\nGraphviz must be installed and it's executables must be in the system's PATH.\n")
            self.main_text_widget.insert("end", "Check Github page for more information. \nGithub page can be accessed in Help -> More info.\n\n")
            self.main_text_widget.insert("end", "Please enter network again with graphics disabled or install Graphviz if you \nwould like to proceed with graph visualisation.")
            self.main_text_widget.config(state="disabled")
        
        
    def generate_trees_graph(self):
        """Generate the tree/graph object and display them depending on graphics mode."""
        #Get Trees object
        if self.network:
            self.graph_trees = self.network.process()
            
            if not self.graphics:
                self.print_trees()
                
        if self.graphics:
            try:
                self.graph_trees.draw()
                self.display_trees_graph()
            except (ValueError, ImportError) as e:
                error_message = f"Error: {e}\n\nTo draw networks and trees, Graphviz must be installed and it's executables must be in the system's PATH."
                tkinter.messagebox.showerror(title="Draw error", message=error_message)
                print(" Draw error: Graphviz must be installed to be able to draw graphs\n")
                
                self.graphics_enabled.set(0)
                self.graphics = False
                self._disable_tree_tools()

        
    def print_trees(self):
        """Displays trees generated as text in the main window"""
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        self.main_text_widget.insert("1.0", self.network.text)
        self.main_text_widget.insert("end", self.graph_trees.text)
        self.main_text_widget.config(state="disabled")
        
        self._enable_text_save()
    
    def display_trees_graph(self, **kwargs):
        """
        Displays trees in a window when user clicks "Draw graph/trees" or selects leaves. Only one trees window is
        displayed at a time
        """
        #self.graph_trees.draw()
        
        if self.graph_window:
            self.graph_window.deiconify()
            self.graph_window.replace_graph(self.graph_trees, self.operation)
        else:
            #Create window
            if self.operation == "Network":
                title = "Embedded trees"
            elif self.operation == "Create rSPR graph":
                title = "rSPR Graph"
            else:
                title = "Trees"
            
            self.graph_window = GraphWindow(self, self.graph_trees, width=self.scaled_width, height=self.scaled_height, title=title, operation=self.operation, **kwargs)            
        
        self._enable_save()
    
    def new_trees(self, operation):
        """
        Displays dialog and gets at least 2 trees in newick format inputted by the user
        
        Parameters
        ----------
        operation : str
            Specifies whether program is running rspr graph or drspr
        """
        self.operation = operation
        
        if self.input_prompt:
            self.input_prompt.change_contents(f"{self.operation}: Enter trees", "Enter at least 2 trees in newick format", "e.g.\n(((1,2),3),4);\n(((1,4),2),3);")
            self.input_prompt.operation = operation
            self.input_prompt.update()
            self.input_prompt.deiconify()
        else:
            self.input_prompt = StringInputPrompt(self, f"{operation}: Enter trees", "Enter at least 2 trees in newick format", "e.g.\n(((1,2),3),4);\n(((1,4),2),3);", self.operation)

    
    def open_trees(self, operation):
        """
        Opens file that contains at least 2 trees in newick format
        
        Parameters
        ----------
        operation : str
            Specifies whether program is running rspr graph or drspr
        """
        self.operation = operation
        
        filename =  tkinter.filedialog.askopenfilename(initialdir = self.trees_directory, title = f"{self.operation}: Open trees...",
                                                       filetypes = (("text files","*.txt"),("all files","*.*")))

        path = os.path.split(filename)
        self.trees_directory = path[0]
        text_file = path[1]
            
        if filename != "":
            f = open(filename, "r")
            text = f.read().strip()
            
            if text != None and self.operation == "Calculate drSPR":
                try:
                    self.get_drspr(text, text_file)
                except MalformedNewickException:
                    error_message = "Could not read trees.\n\Trees must contain at least one labelled leaf and trees must terminate with semicolon."
                    tkinter.messagebox.showerror(title="Open network error", message=error_message)
            elif text != None and self.operation == "Create rSPR graph":
                self.get_rspr_graph(text, text_file)
                    
    def get_rspr_graph(self, input_trees_string, filename=""):
        """
        Get rspr graph
        
        Parameters
        ----------
        input_trees_string : str
            String containing at least 2 trees in newick format delimited by semicolon
            
        filename : str, optional
            Filename of trees text file opened (default="")
        """
        if self.graph_window:
            self.graph_window.withdraw()
            
        self.network = None
        
        self.graph_trees = RsprGraph(input_trees_string)
        
        self.net_canvas.get_tk_widget().pack_forget()
        self.main_text_widget.pack(expand=True, fill="both")
        self._update_info_bar(filename)
        self.print_rspr_graph()
        self._enable_text_save()
        
        if self.graphics:
            self._enable_tree_display()     
        else:
            self._disable_tree_tools()
            
    def print_rspr_graph(self):
        """Print all trees and adjacency list"""
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        
        self.main_text_widget.insert("end", self.graph_trees.text)
        self.main_text_widget.config(state="disabled")
        
            
    def get_drspr(self, input_trees, filename=""):
        """
        Get the rspr distance
        
        Parameters
        ----------
        input_trees : str
            String containing at least 2 trees in newick format delimited by semicolon
            
        filename : str, optional
            Filename of trees text file opened (default="")
        """
        if self.graph_window:
            self.graph_window.withdraw()
            
        self.network = None
        input_trees = input_trees.translate(str.maketrans('', '', ' \n\t\r'))
        trees_array = input_trees.split(";")
        
        if not trees_array[-1]:
            trees_array.pop()
        
        (distances, clusters, self.graph_trees) = d.calculate_drspr(trees_array)
        
        self.net_canvas.get_tk_widget().pack_forget()
        self.main_text_widget.pack(expand=True, fill="both")
        self._update_info_bar(filename)
        self.print_drspr(self.graph_trees.trees, distances, clusters)
        self._enable_text_save()
        
        if self.graphics:
            self._enable_tree_display()  
        else:
            self._disable_tree_tools()
            
            
    def print_drspr(self, trees_array, distances, clusters):
        """
        Output rspr distance information in the main window
        
        Parameters
        ----------
        trees_array : list[str, PhylogeneticNetwork]
            Array of str or PhylogeneticNetwork objects
            
        distances : list[str]
            Array of distances
            
        clusters : list[str]
            Array of clusters
        """
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        
        self.main_text_widget.insert("end", "TREES:\n")
        text = ""

        for tree in trees_array:
            if type(tree) != str:
                text += f"{tree.text}\n"
            else:
                text += f"{tree}\n"
        
        self.main_text_widget.insert("end", text)
        
        length = len(distances)

        if length == 1:
            self.main_text_widget.insert("end", f"\ndrSPR = {distances[0]}\n")
            self.main_text_widget.insert("end", f"Clusters: {clusters[0]}\n")
            
        else:
        
            #Printing matrix
            self.main_text_widget.insert("end", "\nDISTANCE MATRIX:\n")
            for i in range(length):
                self.main_text_widget.insert("end", f"{', '.join(distances[i])}\n")
               
            #Printing cluster
            self.main_text_widget.insert("end", "\n\nCLUSTERS:")
            for i in range(length-1):
                self.main_text_widget.insert("end", f"\nClusters compared with t{i+1}:\n")
                for j in range(i+1, len(clusters[i])):
                    self.main_text_widget.insert("end",
                        f"t{j+1} (drSPR = {distances[i][j]}): {' '.join(clusters[i][j])}\n")
        
        self.main_text_widget.config(state="disabled")
        
    def save_trees_only_text(self, *_):
        """Saves just the tree newick strings in text file"""
        if self.text_save_enabled and self.network:
            file_contents = ""
            
            for tree in self.graph_trees.data.keys():
                file_contents += f"{tree}\n"
            
            title = "Saving trees as text file"
            
            f =  tkinter.filedialog.asksaveasfile(initialdir = self.save_directory, title = title, 
                                          filetypes = [("Text file","*.txt")], 
                                          defaultextension = [("Text file", "*.txt")])
            
            if f: #if dialog not closed with "cancel".
                print("\nSaving trees only in text file...")
                path = os.path.split(f.name)
                self.save_directory = path[0]
                
                f.write(file_contents)
                f.close()
                print(f" Text file saved at {f.name}\n")
            
            
    def save_text(self, *_):
        """Saves network and trees with any other information in newick format as a text file in the directory that the user specifies."""
        if self.text_save_enabled:
            if self.network:
                file_contents = self.network.text
                file_contents += self.graph_trees.text
                title = "Saving network, trees and other info as text file"
            else:
                file_contents = self.main_text_widget.get("1.0","end")
                title = "Saving trees and other info as text file"
            
            f =  tkinter.filedialog.asksaveasfile(initialdir = self.save_directory, title = title, 
                                          filetypes = [("Text file","*.txt")], 
                                          defaultextension = [("Text file", "*.txt")])
            
            if f: #if dialog not closed with "cancel".
                print("\nSaving as text file...")
                
                path = os.path.split(f.name)
                self.save_directory = path[0]
                
                f.write(file_contents)
                f.close()
                print(f" Text file saved. at {f.name}\n")
        
        
    def save_image(self, *_):
        """Saves all figures as a series of images in the directory that the user specifies."""
        if self.image_save_enabled:
            if self.operation == "Network":
                title = "Select folder to save network and tree images"
            elif self.operation == "Create rSPR graph":
                title = "Select folder to save graph"
            else:
                title = "Select folder to save tree images"
            
            
            directory = tkinter.filedialog.askdirectory(initialdir = self.save_directory, title = title)
            
            abs_path = os.path.dirname(__file__)
            export_path = abs_path + directory

            #Export network
            if directory: #if dialog not closed with "cancel".
                image_dpi = self.current_dpi * 2
                print("\nSaving image(s)...")
                
                self.save_directory = export_path
                
                if self.network:
                    self.net_fig.savefig(export_path + "/network.png", dpi=image_dpi, format='png', bbox_inches='tight')
                
                if self.operation == "Create rSPR graph":
                    self.graph_trees.figures[0].savefig(f"{abs_path}{directory}/rspr_graph.png", dpi=image_dpi, format='png', bbox_inches='tight')
                    
                else:
                    #Export trees
                    num_figures = len(self.graph_trees.figures)
                    
                    
                    #count = 1
                    for i, tree_fig in enumerate(self.graph_trees.figures, start=1):
                        tree_fig.savefig(f"{abs_path}{directory}/trees{str(i)}.png", dpi=image_dpi, format='png', bbox_inches='tight')
                        #count += 1
                        print(f'\r {round(i / num_figures * 100)}% complete: Saved {i} / {num_figures} trees', end="\r", flush=True)
                    
                print(f" 100% complete: Image(s) saved at {export_path}.\n")
        
        
    def _exit(self):
        """Display prompt dialog when user exits application."""
        MsgBox = tk.messagebox.askquestion ("Exit Application","Are you sure you want to exit the application?",
                                            icon = "warning")
        if MsgBox == "yes":
            sys.exit(0)
            

class Window(Toplevel):
    """Base class for customised windows."""
    def __init__(self, title, width=0, height=0, **kwargs):
        """
        Parameters
        ----------
        title : str
            Title of the window
            
        width : int, optional
            Width of the window
            
        height : int, optional
            Height of the window
        """
        super().__init__(**kwargs)
        if width == 0 or height == 0:
            self.geometry("")
        else:  
            self.geometry(f"{width}x{height}")
        
        self.title(title)
    
    
    def scroll_setup(self):
        """Make the window have a scrollable panel."""
        self.top_canvas = Canvas(self) #Whole background canvas
        scrollbar = Scrollbar(self, command=self.top_canvas.yview)
        self.top_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y") #position of scroll bar
        self.top_canvas.pack(fill="both", expand=True)
        
        self.frame = Frame(self.top_canvas)
        self.scroll_window = self.top_canvas.create_window(0,0, window=self.frame)
        
        #Configure resizing
        self.frame.bind("<Configure>", self.__handle_frame_resize)
        self.top_canvas.bind("<Configure>", self.__handle_canvas_resize)
        
        #Configure mouse scrolling when cursor is in the window
        self.frame.bind("<Enter>", self._bound_to_mousewheel)
        self.frame.bind("<Leave>", self._unbound_to_mousewheel)
        
    def _bound_to_mousewheel(self, *_):
        """Bind the mouse scroll wheel when cursor enters the window."""
        self.top_canvas.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, *_):
        """Unbind the mouse scroll wheel when cursor exits the window."""
        self.top_canvas.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        """Configure scroll movement."""
        if platform.system() == "Darwin": #If OS is Mac
            self.top_canvas.yview_scroll(int(-1*(event.delta)), "units")
        else:
            self.top_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def __handle_canvas_resize(self, event):
        """Resize canvas when window is resized."""
        self.top_canvas.itemconfigure(self.scroll_window, width=event.width)

    def __handle_frame_resize(self, *_):
        """Resize frame when window is resized."""
        self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"))

        
class GraphWindow(Window):
    """Class for window that displays visualisation of trees and graphs."""
    def __init__(self, main_window, graph_trees, operation, **kwargs):
        """
        Parameters
        ----------
        main_window : Program
            Program class instance which is the program's main window
            
        graph_trees : EmbeddedTrees or Trees or RsprGraph
            Object that contains the tree figures to be displayed
            
        operation : str
            Specifies what function the program is running (embedded trees,
            rspr graph or drspr)
        """
        super().__init__(**kwargs)
        self.main = main_window
        self.canvases = []
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self.operation = operation
        self.graph_trees = graph_trees
        self.figures_frame = None

        self.scroll_setup()
        self._initialise_info_bar()
        self.display_figures()
        
        
    def display_figures(self):
        """Display the figures from the Trees object."""
        self.canvases = []

        if self.figures_frame == None:
            self.figures_frame = Frame(self.frame)
            self.figures_frame.pack(fill="both", expand=1)

        for fig in self.graph_trees.figures:
            trees_canvas = FigureCanvasTkAgg(fig, master=self.figures_frame)
            trees_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
            self.canvases.append(trees_canvas)
            
        self.after_idle(self.top_canvas.yview_moveto, 0)
        plt.close("all") #Close all figures
        
        #Update number of unique trees
        self._update_info_bar()
        
        
    def _update_info_bar(self):
        """Update trees info"""
        if self.main.network:
            num_unique_trees = self.main.graph_trees.num_unique_trees
            num_total_trees = self.main.network.total_trees
            info_text = f"{num_unique_trees} distinct trees, {num_total_trees} total trees"
            self.info_label["text"] = info_text
        else:
            self.info_label["text"] = ""
      
        
    def _initialise_info_bar(self):
        """Setup info bar at bottom which displays number of trees"""
        info_frame = Frame(self)
        info_frame.pack(side="bottom", fill="x")
        
        if self.main.network:
            num_total_trees = self.main.network.total_trees
            num_unique_trees = self.main.graph_trees.num_unique_trees
            info_text = f"{num_unique_trees} distinct trees, {num_total_trees} total trees"
        else:
            info_text = ""
        
        self.info_label = Label(info_frame, text=info_text)
        self.info_label.pack(anchor="c")
            
    def clear_figures(self):
        """Remove the figures currently displayed in the GraphWindow."""

#         for canvas in self.canvases:
#             canvas.get_tk_widget().pack_forget()
#             canvas.get_tk_widget().delete("all")

#         for widget in self.frame.winfo_children():
#             widget.delete("all")
#             widget.destroy()

        self.figures_frame.destroy()
        self.figures_frame = None
            
            
    def replace_graph(self, new_graph_trees, operation):
        """
        Replace the trees currently displayed.
        
        Parameters
        ----------
        new_graph_trees : EmbeddedTrees or Trees
            Object that replaces the current trees object
        """
        self.operation = operation
        if self.operation == "Network":
            self.title("Embedded trees")
        elif self.operation == "Create rSPR graph":
            self.title("rSPR Graph")
        else:
            self.title("Trees")
        
        if self.graph_trees != new_graph_trees or (self.operation == "Network" and self.graph_trees.leaves != new_graph_trees.leaves):
            self.clear_figures()
            self.graph_trees = new_graph_trees
            self.display_figures()
        

    def _exit(self):
        """Hide window"""
        self.withdraw()
        

if __name__ == "__main__":
    print("PhyloProgram version 2.0")
    program = Program()
    program.mainloop()
