"""
Module that contains classes for the dialogue boxes
"""

from tkinter import (Toplevel, Frame, Button, Label, IntVar, Radiobutton)
from widgets import (TextWithPlaceholder)
from phylonetwork import MalformedNewickException
from network_processing import InvalidLeaves
import drspr as d

class MultiChoicePrompt(Toplevel):
    """Class that creates a multiple choice prompt window for selecting leaves."""
    def __init__(self, main_window, title, prompt, options, customise_option=False, text_placeholder="", **kwargs):
        """
        Parameters
        ----------
        main_window : Program
            Program object which is the main window
            
        title : str
            Title of prompt window
            
        prompt : str
            Prompt text in dialog window
            
        options : list[str]
            List of options that will be displayed in multiple choice prompt
            
        customise_option : bool
            Logic to add option that includes text widget where user can type (default is False)
            
        text_placeholder : str
            Grey placeholder text in text widget (default = "")
        """
        super().__init__(**kwargs)
        self.title(title)
        self.customise_value = len(options)
        self.main = main_window
        self.text_placeholder = text_placeholder
        self.protocol("WM_DELETE_WINDOW", self._exit)
        
        prompt_frame = Frame(self)
        prompt_frame.pack(side="top")
        prompt_frame.bind("<ButtonRelease-1>", self._text_focus_off)
        
        prompt_message = Label(prompt_frame, text=prompt)
        prompt_message.pack(pady=(20, 10), padx=20)
        
        self.radio_frame = Frame(self)
        self.radio_frame.pack(anchor="c", fill="x", padx=50)
        self.radio_frame.bind("<ButtonRelease-1>", self._text_focus_off)
        
        self.v = IntVar()
        for i, option in enumerate(options):
            radio_button = Radiobutton(self.radio_frame, text=option, variable=self.v, value=i)
            radio_button.bind("<ButtonRelease-1>", self._text_focus_off)
            radio_button.pack(anchor="w", padx=20, pady=10)
            
        if customise_option:
            radio_button = Radiobutton(self.radio_frame, text="Customise", variable=self.v, value=self.customise_value)
            radio_button.pack(anchor="w",padx=20, pady=10)
            
            self.customise_text = TextWithPlaceholder(self.radio_frame, self.text_placeholder, height=2, width=40)
            self.customise_text.bind("<ButtonRelease-1>", self._text_on_click)
            self.customise_text.pack(anchor="w", padx=(40, 40), pady=(0,20))
            
        self.v.set(0) #Set default selected radio button
        
        self.error_message_frame = Frame(self)
        self.error_message_frame.pack(anchor="c", fill="x")

        self.ok_button = Button(self, text="OK", width=20, command=self._get_input_leaves)
        self.ok_button.pack(pady=(20, 20))
        
    def _text_focus_off(self, *_):
        """Removes focus from the TextWithPlaceholder object."""
        self.focus_set()
        
    def _text_on_click(self, *_):
        """Automatically selects the "Customise" radio button when user clicks on text field"""
        self.v.set(1)
        
    def _get_input_leaves(self):
        """Get the input leaves from the text field."""
        if self.v.get() == 0:
            input_leaves = self.main.network.labelled_leaves
        else:
            input_leaves = self.customise_text.get("1.0", "end")
        
        try:
            if input_leaves == self.text_placeholder:
                raise InvalidLeaves
            
            self.main.network.set_current_selected_leaves(input_leaves)
            self.main.generate_trees()
            self._exit()
            
        except InvalidLeaves as e:
            #Display error message
            error_message = Label(self.error_message_frame, text=e, fg="red")
            error_message.pack(pady=(10, 10), padx=20)
            
    def _clear_error_messages(self):
        """Clear any error messages in dialog"""
        for widget in self.error_message_frame.winfo_children():
            widget.destroy()
        
        empty_frame = Frame(self.error_message_frame)
        empty_frame.pack()
        
        self.error_message_frame.update()
            
    def _exit(self):
        """Hide window"""
        self._clear_error_messages()
        self.withdraw()
        

class StringInputPrompt(Toplevel):
    """Class for prompt dialog that asks for string input"""
    def __init__(self, main_window, title, prompt, placeholder="", operation="Network", **kwargs):
        """
        Parameters
        ----------
        main_window : Program
            Program object which is the main window
            
        title : str
            Title of prompt window
            
        prompt : str
            Prompt text in dialog window
            
        placeholder : str
            Grey placeholder text in text widget (default = "")
            
        network : bool
            True if input prompt is for processing network manually entered by user, else for processing
            multiple trees manually entered by user (default is True)
        """
        super().__init__(**kwargs)
        self.main = main_window
        self.title(title)
        self.placeholder = placeholder
        self.protocol("WM_DELETE_WINDOW", self._exit)
        #self.is_network = network
        self.operation = operation
        
        prompt_frame = Frame(self)
        prompt_frame.pack(side="top")
        self.prompt_message = Label(prompt_frame, text=prompt)
        self.prompt_message.pack(pady=(20, 10), padx=20)
        
        self.text_entry_frame = Frame(self)
        self.text_entry = TextWithPlaceholder(self.text_entry_frame, self.placeholder, height=6, width=40)
        self.text_entry.pack(anchor="c", expand=True, fill="both")
        self.text_entry_frame.pack(padx=(20), pady=(0,20), expand=True, fill="both")
        
        self.error_message_frame = Frame(self)
        self.error_message_frame.pack(anchor="c", pady=(0,20))
        
        self.buttons_frame = Frame(self)
        self.buttons_frame.pack(side="bottom", anchor="c", pady=(10, 20))
        self.ok_button = Button(self.buttons_frame, text="OK", width=20, command=self._get_input)
        self.cancel_button = Button(self.buttons_frame, text="Cancel", width=20, command=self._exit)
        self.ok_button.pack(side="left", padx=(20,10))
        self.cancel_button.pack(side="right", padx=(10,20))
        
    def change_contents(self, title, prompt, placeholder=""):
        """
        Change title, prompt and placeholder text of this dialog
        
        Parameters
        ----------
        title : str
            Title of prompt window
            
        prompt : str
            Prompt text in dialog window
            
        placeholder : str
            Grey placeholder text in text widget (default = "")
            
        """
        self.title(title)
        self.prompt_message.configure(text=prompt) 
        self.text_entry.put_placeholder(placeholder)
        self.placeholder = placeholder
        
        
    def _get_input(self):
        """Get network/trees entered"""
        self._clear_error_messages()
        
        input_text = self.text_entry.get("1.0", "end").strip()
        
        try:
            if self.operation == "Network":
                self.main.generate_network(input_text)
            elif self.operation == "Calculate drSPR":
                self.main.get_drspr(input_text)
            else:
                self.main.get_rspr_graph(input_text)
                
            self._exit()
        
        
        except MalformedNewickException:
            if not input_text or input_text == self.placeholder or input_text.count(";") < 2:
                if self.is_network:
                    error_text = "Please enter network"
                else:
                    error_text = "Please enter at least 2 trees"
                    
                Label(self.error_message_frame,
                      text=error_text, fg="red").pack(anchor="c")
                return
            
            #Check the input
            if input_text[-1] != ";":
                Label(self.error_message_frame,
                      text="String not terminated by semicolon",
                      fg="red").pack(anchor="c")
                
            #Count brackets
            opening_brackets = 0
            closing_brackets = 0
            
            for character in input_text:
                if character == "(":
                    opening_brackets += 1
                elif character == ")":
                    closing_brackets += 1
                    
            if opening_brackets > closing_brackets:
                Label(self.error_message_frame,
                      text=f"Missing {opening_brackets - closing_brackets} closing bracket(s)",
                      fg="red").pack(anchor="c")
                
            elif closing_brackets > opening_brackets:
                Label(self.error_message_frame,
                      text=f"Missing {closing_brackets - opening_brackets} closing bracket(s)",
                      fg="red").pack(anchor="c")
                
            elif opening_brackets == 0 or closing_brackets == 0:
                Label(self.error_message_frame,
                      text="Missing brackets", fg="red").pack(anchor="c")
        
        
        except InvalidLeaves:
            #No labelled leaves in the input
            Label(self.error_message_frame,
                  text="Must have at least one labelled leaf",
                  fg="red").pack(anchor="c")
            
        
    def _clear_error_messages(self):
        """Clear any error messages in dialog"""
        for widget in self.error_message_frame.winfo_children():
            widget.destroy()
        
        empty_frame = Frame(self.error_message_frame)
        empty_frame.pack()
        
        self.error_message_frame.update()
        
    def _exit(self):
        """Hide window"""
        self._clear_error_messages()
        self.withdraw()
        
    