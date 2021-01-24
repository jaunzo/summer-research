"""Helper module for constructing gui of application. Defines customised widgets."""

from tkinter import (Button, Text)
            
class TextWithPlaceholder(Text):
    """Extension of Tkinter Text widget with the added function of placeholder text."""
    def __init__(self, master, placeholder, placeholder_colour="grey", **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = placeholder_colour
        self.default_fg_color = self["fg"]

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self._put_placeholder()

    def _put_placeholder(self):
        """Inserts placeholder text in text field."""
        self.insert("1.0", self.placeholder)
        self["fg"] = self.placeholder_color

    def focus_in(self, event):
        """Removes the placeholder text when user clicks on text field"""
        if self["fg"] == self.placeholder_color:
            self.delete("1.0", "end")
            self["fg"] = self.default_fg_color

    def focus_out(self, event):
        """Put placeholder text in the text field if user clicks out of the text field and hasn"t typed in it"""
        string = self.get("1.0", "end").strip()
        if string == "":
            self._put_placeholder()
            
class HoverButton(Button):
    """
    Class for buttons that change background colour when mouse hovers over it.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.bind("<Enter>", self._button_enter)
        self.bind("<Leave>", self._button_leave)
        
        self.pack(side="left", padx=5, pady=5)
        
    def _button_enter(self, event):
        """Button background colour changes when mouse hovers over enabled button"""
        if self["state"] == "normal":
            event.widget["background"] = "light gray"
        
    def _button_leave(self, event):
        """Button background reverts when mouse leaves button"""
        event.widget["background"] = "SystemButtonFace"
            