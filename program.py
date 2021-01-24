"""Main application. Defines the classes and methods of the application gui."""

import tkinter as tk
import tkinter.simpledialog
import tkinter.filedialog
import tkinter.messagebox
from tkinter import (Tk, Canvas, Scrollbar, Menu, Toplevel,
                     Frame, Label, Text)
from network_processing import Network
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys, os
import matplotlib.pyplot as plt
from widgets import (HoverButton)
from phylonetwork import MalformedNewickException
from dialogs import (MultiChoicePrompt, StringInputPrompt)

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
        scale = self._get_dpi() / ORIGINAL_DPI
        self.tk.call("tk", "scaling", scale + 0.5)
        
        self.net_frame = None
        self.directory = ""
        self.scale = scale
        self.net_fig = None
        self._trees_window = None
        
        self.title("Phylogenetic network")
        
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
        self.net_canvas.get_tk_widget().pack(side=tkinter.TOP, fill="both", expand=1)
        
        #prompt windows
        self.enter_network_prompt = None
        self.select_leaves_prompt = None
        self.about_window = None
        self.manual_window = None
    
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
        self.info_label.pack(anchor="c")
        
    
    def _update_info_bar(self):
        """For private use. Update the network info when new network is opened"""
        num_reticulations = self.network.num_reticulations
        num_labelled_leaves = self.network.num_labelled_leaves
        info_text = f"{num_reticulations} reticulations, {num_labelled_leaves} labelled leaves"
        self.info_label["text"] = info_text
    
        
    def _initialise_menu_bar(self):
        """For private use. Initialise the top menu bar and bind shortcuts"""
        self.menu_bar = Menu(self)
        
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        
        self.file_menu.add_command(label="Enter network", command=self.new_network, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open network...", command=self.open_network, accelerator="Ctrl+O")
        
        self.save_sub_menu = Menu(self.file_menu, tearoff=0)
        self.save_sub_menu.add_command(label="Text file", command=self.save_text, accelerator="Ctrl+Shift+T")
        self.save_sub_menu.add_command(label="Images", command=self.save_image, accelerator="Ctrl+Shift+I")
        self.file_menu.add_cascade(label="Save as...", menu=self.save_sub_menu, state="disabled")
        
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.about)
        self.help_menu.add_command(label="Manual", command=self.manual)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        self.config(menu=self.menu_bar)
        
        self.bind_all("<Control-n>", self.new_network)
        self.bind_all("<Control-o>", self.open_network)
        self.bind_all("<Control-T>", self.save_text)
        self.bind_all("<Control-I>", self.save_image)
        
    def _initialise_tool_bar(self):
        """For private use. Initialise the tool bar"""
        self.toolbar = Frame(self, bd=1, relief="raised")
        self.toolbar.pack(fill="x")
        
        self.select_leaves_button = HoverButton(self.toolbar, text ="Select leaves", relief="raised",
                                         command=self._select_leaves, state="disabled")
        
        self.display_trees_button = HoverButton(self.toolbar, text ="Show trees", relief="raised",
                                                command=self.display_trees, state="disabled")
        
    def _enable_tree_tools(self):
        """For private use. Buttons involving trees are enabled when a network has successfully been processed and displayed."""
        self.select_leaves_button.config(state = "normal")
        self.display_trees_button.config(state = "normal")
    
    def _enable_save(self):
        """For private use. Save functions are enabled when a network and trees has successfully been processed and displayed."""
        self.file_menu.entryconfigure("Save as...", state = "normal")
        
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
        if self.about_window and self.about_window.winfo_exists():
            print("deiconified")
            self.about_window.deiconify()
        else:
            self.about_window = Window(title="About")
            path = resource_path("about.txt")
            f = open(path, "r")
            about_text = f.read()
            text_widget = Text(self.about_window)
            text_widget.insert("1.0", about_text)
            text_widget.pack(expand=True, fill="both")
    
    def manual(self):
        """Display program manual on window"""
        if self.manual_window and self.manual_window.winfo_exists():
            self.manual_window.deiconify()
        else:
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
        
    def new_network(self):
        """Displays dialog and gets network in extended newick format inputted by the user."""
        if self.enter_network_prompt:
            self.enter_network_prompt.update()
            self.enter_network_prompt.deiconify()
        else:
            self.enter_network_prompt = StringInputPrompt(self, "Enter network", "Enter network in extended newick format")

            
    def open_network(self):
        """Displays open file prompt and processes a text file that contains the network in extended newick format."""
        filename =  tkinter.filedialog.askopenfilename(initialdir = self.directory, title = "Open text file",
                                                       filetypes = (("text files","*.txt"),("all files","*.*")))
        if self.directory == "":
            #Set the directory to directory of file that was just opened
            #self.directory = filename[:filename.rfind("/")]
            path = os.path.split(filename)
            self.directory = path[0]
            
        if filename != "":
            f = open(filename, "r")
            text = f.read().strip()
            
            if text != None:
                network_newick = text[:text.find(";") + 1]
                try:
                    self.display_network(network_newick)
                except MalformedNewickException:
                    error_message = "Could not read network.\n\nNetwork requirements:\nNetwork must contain at least one labelled leaf and string must terminate with semicolon."
                    tkinter.messagebox.showerror(title="Open network error", message=error_message)
        
    def display_network(self, net_newick):
        """Display input network in the main window."""
        if self._trees_window:
            self._trees_window.withdraw()
            
        self.net_fig.gca().clear()
        
        self.network = Network(net_newick, self.net_fig)
        self.net_canvas.draw()
        
        self._update_info_bar()
        self._enable_tree_tools()
        
    def display_trees(self):
        """
        Displays trees in a window when user clicks "Show trees" or selects leaves. Only one trees window is
        displayed at a time
        """
        #Get Trees object
        self.trees = self.network.process()
        
        if self._trees_window:
            self._trees_window.deiconify()
            self._trees_window.replace_trees(self.trees)
        else:
            #Create window
            self._trees_window = TreesWindow(self, self.trees, width=self.scaled_width,
                                  height=self.scaled_height, title="Trees")
        
        self._enable_save()
    
    def save_text(self, event=None):
        """Saves network and trees in newick format as a text file in the directory that the user specifies."""
        f =  tkinter.filedialog.asksaveasfile(initialdir = self.directory, title = "Saving network and trees as text file", 
                                      filetypes = [("Text file","*.txt")], 
                                      defaultextension = [("Text file", "*.txt")])
        
        if f is None: #if dialog closed with "cancel".
            return
        
        file_contents = f"{self.network.newick}\n\nTotal trees: {self.network.total_trees}\nDistinct trees: {self.trees.num_unique_trees}\n\n"
        
        for tree, count in self.trees.data.items():
            file_contents += f"{tree}  x{count}\n"
        
        f.write(file_contents)
        f.close()
        
    def save_image(self, event=None):
        """Saves all figures as a series of images in the directory that the user specifies."""
        directory = tkinter.filedialog.askdirectory(initialdir = self.directory, title = "Select directory to save images")
        
        abs_path = os.path.dirname(__file__)
        export_path = abs_path + directory 

        #Export network
        if f is None: #if dialog closed with "cancel".
            return
        
        self.net_fig.savefig(export_path + "/network.png", bbox_inches="tight")
        
        #Export trees
        count = 1
        for tree_fig in self.trees.figures:
            tree_fig.savefig(f"{abs_path}{directory}/trees{str(count)}.png", bbox_inches="tight")
            count += 1
        
    def _exit(self):
        """Display prompt dialog when user exits application."""
        MsgBox = tk.messagebox.askquestion ("Exit Application","Are you sure you want to exit the application?",
                                            icon = "warning")
        if MsgBox == "yes":
            self.destroy()
            

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
        
    def _bound_to_mousewheel(self, event):
        """Bind the mouse scroll wheel when cursor enters the window."""
        self.top_canvas.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, event):
        """Unbind the mouse scroll wheel when cursor exits the window."""
        self.top_canvas.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        """Configure scroll movement."""
        self.top_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def __handle_canvas_resize(self, event):
        """Resize canvas when window is resized."""
        self.top_canvas.itemconfigure(self.scroll_window, width=event.width)

    def __handle_frame_resize(self, event):
        """Resize frame when window is resized."""
        self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"))

        
class TreesWindow(Window):
    """Class for window that displays visualisation of trees."""
    def __init__(self, main_window, trees_obj, **kwargs):
        super().__init__(**kwargs)
        self.main = main_window
        self.tree_figures = trees_obj.figures
        self.canvases = []
        self.protocol("WM_DELETE_WINDOW", self._exit)
        
        self.scroll_setup()
        self._initialise_info_bar()
        self.display_figures()
        
    def display_figures(self):
        """Display the figures from the Trees object."""
        for fig in self.tree_figures:
            trees_canvas = FigureCanvasTkAgg(fig, master=self.frame)
            trees_canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
            self.canvases.append(trees_canvas)
            
        self.after_idle(self.top_canvas.yview_moveto, 0)
        plt.close("all") #Close all figures
        
        #Update number of unique trees
        self._update_info_bar()
        
        
    def _update_info_bar(self):
        """Update trees info"""
        num_unique_trees = self.main.trees.num_unique_trees
        info_text = f"{num_unique_trees} distinct trees, {self.num_total_trees} total trees"
        self.info_label["text"] = info_text
      
        
    def _initialise_info_bar(self):
        """Setup info bar at bottom which displays number of trees"""
        info_frame = Frame(self)
        self.num_total_trees = len(self.main.network.all_trees)
        info_frame.pack(side="bottom", fill="x")
        
        num_unique_trees = self.main.trees.num_unique_trees
        info_text = f"{num_unique_trees} distinct trees, {self.num_total_trees} total trees"
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
        self.trees_obj = new_trees_obj
        self.tree_figures = self.trees_obj.figures
        self.canvases = []
        self.clear_figures()
        self.display_figures()
        
        
    def _exit(self):
        """Hide window"""
        self.main.trees_window = None
        self.withdraw()
        

if __name__ == "__main__":
    program = Program()
    program.mainloop()