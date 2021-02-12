"""Main application. Defines the classes and methods of the application gui."""

import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import (Tk, Canvas, Scrollbar, Menu, Toplevel,
                     Frame, Label, Text, IntVar, Checkbutton)
from network_processing import Network
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys, os
import matplotlib.pyplot as plt
from widgets import (HoverButton)
from phylonetwork import MalformedNewickException
from dialogs import (MultiChoicePrompt, StringInputPrompt)
from widgets import ToolTip
import platform
import webbrowser
import drspr as d

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.environ.get("_MEIPASS2",os.path.abspath("."))

    return os.path.join(base_path, relative_path)


class Program(Tk):
    """
    Class for application that takes a network in extended newick format and displays trees.
    This program can save the network and trees as images or text file.
    """
    def __init__(self):
        super().__init__()
        ORIGINAL_DPI = 96.0
        #Scale the window depending on current monitor's dpi
        self.scale = self._get_dpi() / ORIGINAL_DPI
        self.tk.call("tk", "scaling", self.scale + 0.5)
        
        self.net_frame = None
        self.directory = ""
        self.net_fig = None
        self._trees_window = None
        
        self.title("PhyloProgram")
        
        self.scaled_width = self._scale_window(750)
        self.scaled_height = self._scale_window(600)
        
        self.geometry(f"{self.scaled_width}x{self.scaled_height}")
        self.protocol("WM_DELETE_WINDOW", self._exit)
        
        self._initialise_menu_bar()
        self._initialise_tool_bar()
        self._initialise_info_bar()
        
        self.main_frame = Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=1)
        
        #initialise network figure canvas in main window
        self.net_fig = plt.figure("Input network")
        self.net_canvas = FigureCanvasTkAgg(self.net_fig, master=self.main_frame)
        
        self._initialise_main_text_widget()
        
        #prompt windows
        self.input_prompt = None
        self.select_leaves_prompt = None
    
    
    def _initialise_main_text_widget(self):
        
        self.main_text_widget = Text(self.main_frame, width=25)
        scroll = Scrollbar(self.main_text_widget, command=self.main_text_widget.yview)
        self.main_text_widget['yscrollcommand'] = scroll.set
        scroll.pack(side="right", fill="y")
    
    
    @property
    def trees_window(self):
        """Return instance of TreeWindow object"""
        return self._trees_window
    
    @trees_window.setter
    def trees_window(self, value):
        """Set the program's tree window"""
        self._trees_window = value
        
    def _get_dpi(self):
        """For private use. Get the dpi of the current screen"""
        screen = Tk()
        current_dpi = screen.winfo_fpixels("1i")
        screen.destroy()
        return current_dpi
    
    
    def _initialise_info_bar(self):
        """For private use. Info bar that displays number of reticulations and labelled leaves in network"""
        self.info_frame = Frame(self)
        self.info_frame.pack(side="bottom", fill="x")
        
        self.info_label = Label(self.info_frame, text="")
        self.info_label.pack(side="right", padx=(0,10))
        
        self.network_label = Label(self.info_frame, text="")
        self.network_label.pack(side="left", padx=(10, 0))
        
    
    def _update_info_bar(self, filename):
        """For private use. Update the network info when new network is opened"""
        num_reticulations = self.network.num_reticulations
        num_labelled_leaves = self.network.num_labelled_leaves
        info_text = f"{num_reticulations} reticulations, {num_labelled_leaves} labelled leaves"
        self.info_label["text"] = info_text
        
        if filename:
            network_text = filename
        else:
            network_text = ""
        
        self.network_label["text"] = network_text
    
        
    def _initialise_menu_bar(self):
        """For private use. Initialise the top menu bar and bind shortcuts"""
        menu_bar = Menu(self)
        
        self.file_menu = Menu(menu_bar, tearoff=0)
        
        self.file_menu.add_command(label="Enter network", command=self.new_network, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open network...", command=self.open_network, accelerator="Ctrl+O")
        
        self.file_menu.add_separator()
        
        self.file_menu.add_command(label="Enter trees", command=self.new_trees)
        self.file_menu.add_command(label="Open trees...", command=self.open_trees)
        
        self.file_menu.add_separator()
        
        self.save_sub_menu = Menu(self.file_menu, tearoff=0)
        self.save_sub_menu.add_command(label="Text file", command=self.save_text, accelerator="Ctrl+Shift+T")
        self.save_sub_menu.add_command(label="Images", command=self.save_image, accelerator="Ctrl+Shift+I")
        self.file_menu.add_cascade(label="Save as...", menu=self.save_sub_menu)
        self.file_menu.entryconfigure("Save as...", state = "disabled")
        self.save_sub_menu.entryconfigure("Images", state="disabled")
        
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._exit)
        menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        help_menu.add_command(label="Manual", command=self.manual)
        help_menu.add_command(label="More info", command=self.open_github)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
        
        self.bind_all("<Control-n>", self.new_network)
        self.bind_all("<Control-o>", self.open_network)
        self.bind_all("<Control-T>", self.save_text)
        self.bind_all("<Control-I>", self.save_image)
        
    def _initialise_tool_bar(self):
        """For private use. Initialise the tool bar"""
        self.toolbar = Frame(self, bd=1, relief="raised")
        self.toolbar.pack(fill="x")
        
        self.select_leaves_button = HoverButton(self.toolbar, text ="Select leaves", relief="raised",
                                         command=self._select_leaves, state="disabled",
                                                tooltip_text="Enter set leaves to be displayed in trees. By default, all labelled leaves in network are selected")
        
        self.display_trees_button = HoverButton(self.toolbar, text ="Show trees", relief="raised",
                                                command=self.generate_trees, state="disabled",
                                                tooltip_text="Generate trees with currently selected leaves")
        
        self.graphics_enabled = IntVar()
        self.graphics = False
        graphics_check_box = Checkbutton(self.toolbar, text = "Enable graphics",
                                              variable=self.graphics_enabled, command=self.set_graphics)
        graphics_check_box.pack(side="right", padx=(0,10))
        ToolTip(graphics_check_box, "Enable graph visualisation for the next entered network")
        
    
        
    def set_graphics(self, *_):
        """Set if the program draws the network and trees."""
        if self.graphics_enabled.get() == 1:
            self.graphics = True
        else:
            self.graphics = False
        
    def _enable_tree_tools(self):
        """For private use. Buttons involving trees are enabled when a network has successfully been processed and displayed."""
        self.select_leaves_button.config(state = "normal")
        self.display_trees_button.config(state = "normal")
    
    def _enable_tree_display(self):
        """For private use. Only enables show trees button when user displays drSPR trees"""
        self.display_trees_button.config(state = "normal")
    
    def _enable_save(self):
        """For private use. Save functions are enabled when a network and trees has successfully been processed and displayed."""
        self.file_menu.entryconfigure("Save as...", state = "normal")
        self.save_sub_menu.entryconfigure("Images", state="normal")
        
    def _enable_text_save(self):
        """For private use. Used when visualisation is disabled. Only save as text enabled"""
        self.file_menu.entryconfigure("Save as...", state = "normal")
        self.save_sub_menu.entryconfigure("Images", state="disabled")
        
        
    def _scale_window(self, window_length):
        """For private use. Scales the window based on calculated scale"""
        return round(window_length * self.scale)
    
    def _select_leaves(self):
        """For private use. Opens multiple choice dialog prompt to select the leaves that will be displayed in the generated trees."""
        if self.select_leaves_prompt:
            self.select_leaves_prompt.update()
            self.select_leaves_prompt.deiconify()
        else:
            self.select_leaves_prompt = MultiChoicePrompt(self, "Select leaves", "Specify the leaves that will be included in the generated trees.", ["All"],
                          customise_option=True, text_placeholder="e.g. 1, 2, 3, 4")
            
    def about(self):
        """Display overview of program on window"""
        self.about_window = Window(title="About")
        path = resource_path("about.txt")
        f = open(path, "r")
        about_text = f.read()
        text_widget = Text(self.about_window)
        text_widget.insert("1.0", about_text)
        text_widget.pack(expand=True, fill="both")
        text_widget.config(state="disabled")
    
    def manual(self):
        """Display program manual on window"""
        self.manual_window = Window(title="Manual", width=self.scaled_width,
                                    height=self.scaled_height//2)
        path = resource_path("manual.txt")
        f = open(path, "r")
        manual_text = f.read()
        text_widget = Text(self.manual_window, width=30)
        text_widget.insert("1.0", manual_text)
        scroll = Scrollbar(text_widget, command=text_widget.yview)
        text_widget['yscrollcommand'] = scroll.set
        scroll.pack(side="right", fill="y")
        text_widget.pack(expand=True, fill="both")
        text_widget.config(state="disabled")
        
    def open_github(self):
        """Open this program's github page."""
        webbrowser.open("https://github.com/jaunzo/summer-research", new=2)
        
    def new_network(self, *_):
        """Displays dialog and gets network in extended newick format inputted by the user."""
        if self.input_prompt:
            self.input_prompt.change_contents("Enter network", "Enter network in extended newick format", "e.g. ((a,(b)#H1), (#H1,c));")
            self.input_prompt.update()
            self.input_prompt.deiconify()
        else:
            self.input_prompt = StringInputPrompt(self, "Enter network", "Enter network in extended newick format", "e.g. ((a,(b)#H1), (#H1,c));")
    
        print(sys.getrefcount(self.input_prompt))
    
    def new_trees(self):
        """Displays dialog and gets at least 2 trees in newick format inputted by the user"""
        if self.input_prompt:
            self.input_prompt.change_contents("Enter trees", "Enter at least 2 trees in newick format", "e.g.\n(((1,2),3),4);\n(((1,4),2),3);")
            self.input_prompt.update()
            self.input_prompt.deiconify()
        else:
            self.input_prompt = StringInputPrompt(self, "Enter trees", "Enter at least 2 trees in newick format", "e.g.\n(((1,2),3),4);\n(((1,4),2),3);", False)
        
        #print(sys.getrefcount(self.input_prompt))
    
    def open_trees(self):
        """Opens file that contains at least 2 trees in newick format"""
        filename =  tkinter.filedialog.askopenfilename(initialdir = self.directory, title = "Open text file",
                                                       filetypes = (("text files","*.txt"),("all files","*.*")))

        path = os.path.split(filename)
        self.directory = path[0]
        text_file = path[1]
            
        if filename != "":
            f = open(filename, "r")
            text = f.read().strip()
            
            if text != None:
                try:
                    self.get_drspr(text)
                except MalformedNewickException:
                    error_message = "Could not read trees.\n\Trees must contain at least one labelled leaf and trees must terminate with semicolon."
                    tkinter.messagebox.showerror(title="Open network error", message=error_message)
                    
            
    def get_drspr(self, input_trees):
        """Get the rspr distance"""
        self.network = None
        input_trees = input_trees.translate(str.maketrans('', '', ' \n\t\r'))
        trees_array = input_trees.split(";")
        
        if not trees_array[-1]:
            trees_array.pop()
        
        (distances, clusters, self.trees) = d.calculate_drspr(trees_array)
        
        self.net_canvas.get_tk_widget().pack_forget()
        self.main_text_widget.pack(expand=True, fill="both")
        self.print_drspr(self.trees.trees, distances, clusters)
        
        if self.graphics:
            self._enable_save()
            #Implement tree visualisation here
            self._enable_tree_display()
            
        else:
            self._enable_text_save()
        
                
    def print_drspr(self, trees_array, distances, clusters):
        """Output rspr distance information in the main window"""
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        
        
        self.main_text_widget.insert("end", "TREES:\n")
        for i, tree in enumerate(trees_array, start=1):
            self.main_text_widget.insert("end", f"t{i}:\n{tree};\n\n")
        
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
        
            
    def open_network(self, *_):
        """Displays open file prompt and processes a text file that contains the network in extended newick format."""
        filename =  tkinter.filedialog.askopenfilename(initialdir = self.directory, title = "Open text file",
                                                       filetypes = (("text files","*.txt"),("all files","*.*")))

        path = os.path.split(filename)
        self.directory = path[0]
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
        
        
    def generate_network(self, net_newick, filename=None):
        """Generate the network object and display it depending on graphics mode"""
        self.network = Network(net_newick, self.net_fig, self.graphics)
        self._update_info_bar(filename)
        self._enable_tree_tools()
        self.net_newick = net_newick
        
        if self.graphics:
            self.main_text_widget.pack_forget()
            self.net_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
            self.display_network()
        else:
            self.net_canvas.get_tk_widget().pack_forget()
            self.main_text_widget.pack(expand=True, fill="both")
            self.print_network()
            
            
    def print_network(self):
        """Print out the network in main window. Hide tree window"""
        if self._trees_window:
            self._trees_window.destroy()
            self._trees_window = None
        
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        self.main_text_widget.insert("1.0", self.network.text)
        self.main_text_widget.config(state="disabled")
        
        
    def display_network(self):
        """Display input network in the main window."""
        if self._trees_window:
            self._trees_window.withdraw()
            
        self.net_fig.gca().clear()
        
        try:
            self.network.draw()
            self.net_canvas.draw()
        except (ValueError, ImportError) as e:
            self.net_fig.clear()
            self.net_canvas.get_tk_widget().pack_forget()
            
            error_message = f"Error: {e}\n\nGraphviz must be installed and it's executables must be in the system's PATH."
            tkinter.messagebox.showerror(title="Open network error", message=error_message)
            
            self.graphics_enabled.set(0)
            self.graphics = False
        
        
    def generate_trees(self):
        """Generate the tree objects and display them depending on graphics mode."""
        #Get Trees object
        if self.network:
            self.trees = self.network.process()
        
            if self.network.graphics:
                self.display_trees()
            else:
                self.print_trees()
                
        else:
            if self.graphics:
                self.display_trees(embedded_trees=False)
        
        
    def print_trees(self):
        """Displays trees generated as text in the main window"""
        self.main_text_widget.config(state="normal")
        self.main_text_widget.delete('1.0', "end")
        self.main_text_widget.insert("1.0", self.network.text)
        self.main_text_widget.insert("end", self.trees.text)
        self.main_text_widget.config(state="disabled")
        
        self._enable_text_save()
    
    def display_trees(self, **kwargs):
        """
        Displays trees in a window when user clicks "Show trees" or selects leaves. Only one trees window is
        displayed at a time
        """
        self.trees.draw() #Draw the trees before calling the window
        
        if self._trees_window:
            self._trees_window.deiconify()
            self._trees_window.replace_trees(self.trees)
        else:
            #Create window
            self._trees_window = TreesWindow(self, self.trees, width=self.scaled_width, height=self.scaled_height, title="Trees", **kwargs)            
        
        self._enable_save()
        print(sys.getrefcount(self._trees_window))
    
    def save_text(self, *_):
        """Saves network and trees in newick format as a text file in the directory that the user specifies."""
        f =  tkinter.filedialog.asksaveasfile(initialdir = self.directory, title = "Saving network and trees as text file", 
                                      filetypes = [("Text file","*.txt")], 
                                      defaultextension = [("Text file", "*.txt")])
        
        if f is None: #if dialog closed with "cancel".
            return
        
        file_contents = self.network.text
        file_contents += self.trees.text
        
        f.write(file_contents)
        f.close()
        
    def save_image(self, *_):
        """Saves all figures as a series of images in the directory that the user specifies."""
        directory = tkinter.filedialog.askdirectory(initialdir = self.directory, title = "Select directory to save images")
        
        abs_path = os.path.dirname(__file__)
        export_path = abs_path + directory 

        #Export network
        if directory is None: #if dialog closed with "cancel".
            return
        
        if self.network:
            self.net_fig.savefig(export_path + "/network.png", bbox_inches="tight")
        
        #Export trees
        count = 1
        for tree_fig in self.trees.figures:
            tree_fig.savefig(f"{abs_path}{directory}/t{str(count)}.png", bbox_inches="tight")
            count += 1
        
    def _exit(self):
        """Display prompt dialog when user exits application."""
        MsgBox = tk.messagebox.askquestion ("Exit Application","Are you sure you want to exit the application?",
                                            icon = "warning")
        if MsgBox == "yes":
            self.destroy()
            exit()
            

class Window(Toplevel):
    """Base class for customised windows."""
    def __init__(self, title, width=0, height=0, **kwargs):
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

        
class TreesWindow(Window):
    """Class for window that displays visualisation of trees."""
    def __init__(self, main_window, trees_obj, embedded_trees=True, **kwargs):
        super().__init__(**kwargs)
        self.main = main_window
        self.trees_obj = trees_obj
        #self.tree_figures = self.trees_obj.figures
        #self.canvases = []
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self.embedded = embedded_trees
        
        self.scroll_setup()
        if self.embedded:
            self._initialise_info_bar()
        self.display_figures()
        
        
    def display_figures(self):
        """Display the figures from the Trees object."""
        self.canvases = []
        for fig in self.trees_obj.figures:
            trees_canvas = FigureCanvasTkAgg(fig, master=self.frame)
            trees_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
            self.canvases.append(trees_canvas)
            
        self.after_idle(self.top_canvas.yview_moveto, 0)
        plt.close("all") #Close all figures
        
        #Update number of unique trees
        if self.embedded:
            self._update_info_bar()
        
        
    def _update_info_bar(self):
        """Update trees info"""
        num_unique_trees = self.main.trees.num_unique_trees
        num_total_trees = self.main.network.total_trees
        info_text = f"{num_unique_trees} distinct trees, {num_total_trees} total trees"
        self.info_label["text"] = info_text
      
        
    def _initialise_info_bar(self):
        """Setup info bar at bottom which displays number of trees"""
        info_frame = Frame(self)
        num_total_trees = self.main.network.total_trees
        info_frame.pack(side="bottom", fill="x")
        
        num_unique_trees = self.main.trees.num_unique_trees
        info_text = f"{num_unique_trees} distinct trees, {num_total_trees} total trees"
        self.info_label = Label(info_frame, text=info_text)
        self.info_label.pack(anchor="c")
            
            
    def clear_figures(self):
        """Remove the figures currently displayed in the TreesWindow."""
        for canvas in self.canvases:
            canvas.get_tk_widget().destroy()
            
        for widget in self.frame.winfo_children():
            widget.destroy()
            
            
    def replace_trees(self, new_trees_obj):
        """Replace the trees currently displayed."""
        if self.trees_obj != new_trees_obj:
            self.clear_figures()
            self.trees_obj = new_trees_obj
            self.display_figures()
        
        
    def _exit(self):
        """Hide window"""
        #self.main.trees_window = None
        self.withdraw()
        

if __name__ == "__main__":
    program = Program()
    program.mainloop()
