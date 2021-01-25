"""Module that contains classes for the dialogue boxes"""

from tkinter import (Toplevel, Frame, Button, Label, IntVar, Radiobutton)
from widgets import (TextWithPlaceholder, HoverButton)
from phylonetwork import MalformedNewickException
from network_processing import InvalidLeaves

class MultiChoicePrompt(Toplevel):
    """Class that creates a multiple choice prompt window for selecting leaves."""
    def __init__(self, main_window, title, prompt, options, customise_option=False, text_placeholder="", **kwargs):
        super().__init__(**kwargs)
        self.title(title)
        self.customise_value = len(options)
        self.main = main_window
        self.text_placeholder = text_placeholder
        self.protocol("WM_DELETE_WINDOW", self._exit)
        
        
        self.prompt_frame = Frame(self)
        self.prompt_frame.pack(side="top")
        self.prompt_frame.bind("<ButtonRelease-1>", self._text_focus_off)
        
        prompt_message = Label(self.prompt_frame, text=prompt)
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
        
    def _text_focus_off(self, event):
        """Removes focus from the TextWithPlaceholder object."""
        self.focus_set()
        
    def _text_on_click(self, event):
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
    def __init__(self, main_window, title, prompt, **kwargs):
        super().__init__(**kwargs)
        self.main = main_window
        self.title(title)
        self.example_network = "e.g. ((a,(b)#H1), (#H1,c));"
        self.protocol("WM_DELETE_WINDOW", self._exit)
        
        self.prompt_frame = Frame(self)
        self.prompt_frame.pack(side="top")
        prompt_message = Label(self.prompt_frame, text=prompt)
        prompt_message.pack(pady=(20, 10), padx=20)
        
        self.text_entry_frame = Frame(self)
        self.text_entry = TextWithPlaceholder(self.text_entry_frame, self.example_network, height=2, width=40)
        #self.text_entry = Text(self.text_entry_frame, height=2, width=20)
        self.text_entry.pack(anchor="c", expand=True, fill="both")
        self.text_entry_frame.pack(padx=(20), pady=(0,20), expand=True, fill="both")
        
        self.error_message_frame = Frame(self)
        self.error_message_frame.pack(anchor="c", pady=(0,20))
        
        self.buttons_frame = Frame(self)
        self.buttons_frame.pack(side="bottom", anchor="c", pady=(10, 20))
        self.ok_button = Button(self.buttons_frame, text="OK", width=20, command=self._get_input_network)
        self.cancel_button = Button(self.buttons_frame, text="Cancel", width=20, command=self._exit)
        self.ok_button.pack(side="left", padx=(20,10))
        self.cancel_button.pack(side="right", padx=(10,20))
        
        
    def _get_input_network(self):
        """Get network entered"""
        self._clear_error_messages()
        
        input_network = self.text_entry.get("1.0", "end").strip()
        
        try:
            self.main.generate_network(input_network)
            self._exit()
        
        except MalformedNewickException as e:
            print("MalformedNewickException")
            print("Input not empty check")
            if not input_network or input_network == self.example_network:
                
                Label(self.error_message_frame,
                      text="Please enter network", fg="red").pack(anchor="c")
                return
            
            #Check the input
            print("Input terminates with semicolon")
            if input_network[-1] != ";":
                Label(self.error_message_frame,
                      text="String not terminated by semicolon",
                      fg="red").pack(anchor="c")
                
            #Count brackets
            opening_brackets = 0
            closing_brackets = 0
            
            for character in input_network:
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
            #No labelled leaves in the entered network
            Label(self.error_message_frame,
                  text="Network must have at least one labelled leaf",
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