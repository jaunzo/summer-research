"""Helper module for constructing gui of application. Defines customised widgets."""

from tkinter import (Button, Text, Toplevel, Label)
            
class TextWithPlaceholder(Text):
    """Extension of Tkinter Text widget with the added function of placeholder text."""
    def __init__(self, master, placeholder, placeholder_colour="grey", **kwargs):
        """
        Parameters
        ----------
        master : Frame
            Frame where this widget will be placed in
            
        placeholder : str
            Placeholder text in text widget (default = "")
            
        placeholder_colour : str
            Colour of placeholder text (default is grey)
        """
        super().__init__(master, **kwargs)

        self.placeholder_color = placeholder_colour
        self.default_fg_color = self["fg"]
        self.placeholder = placeholder

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.put_placeholder(placeholder)

    def put_placeholder(self, placeholder=""):
        """
        Inserts placeholder text in text field.
        
        Parameters
        ----------
        placeholder : str
            Placeholder text in text widget (default = "")
        """
        self.delete('1.0', "end")
        if placeholder:
            self.placeholder = placeholder
        
        self.insert("1.0", self.placeholder)
        self["fg"] = self.placeholder_color

    def focus_in(self, *_):
        """Removes the placeholder text when user clicks on text field"""
        if self["fg"] == self.placeholder_color:
            self.delete("1.0", "end")
            self["fg"] = self.default_fg_color

    def focus_out(self, *_):
        """Put placeholder text in the text field if user clicks out of the text field and hasn"t typed in it"""
        string = self.get("1.0", "end").strip()
        if string == "":
            self.put_placeholder(self.placeholder)
            
class HoverButton(Button):
    """
    Class for buttons that change background colour when mouse hovers over it.
    """
    def __init__(self, master: Frame, tooltip_text="", **kwargs):
        """
        Parameters
        ----------
        master : Frame
            Frame where this widget will be placed in
            
        tooltip_text " str
            Message of tooltip when mouse hovers over button (default="")
        """
        super().__init__(master, **kwargs)
        
        self.bind("<Enter>", self._button_enter)
        self.bind("<Leave>", self._button_leave)
        self.bind("<ButtonPress>", self._button_press)
        
        self.pack(side="left", padx=5, pady=5)
        
        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, False)
        else:
            self.tooltip = None
        
    def _button_enter(self, event):
        """Button background colour changes when mouse hovers over enabled button and displays tooltip"""
        if self["state"] == "normal":
            event.widget["background"] = "light gray"
            
        if self.tooltip:
            self.tooltip.schedule(event)
        
    def _button_leave(self, event):
        """Button background reverts when mouse leaves button and hides tooltip"""
        event.widget["background"] = "SystemButtonFace"
        
        if self.tooltip:
            self.tooltip.unschedule()
            self.tooltip.hidetip()
            
    def _button_press(self, *_):
        """Hide tooltip on button press"""
        if self.tooltip:
            self.tooltip.unschedule()
            self.tooltip.hidetip()
            
class ToolTip:
    """
    Create a tooltip for a given widget
    Class code based from https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    """
    def __init__(self, widget, text, bind=True):
        """
        Parameters
        ----------
        widget : tkinter widget
            Widget to put tooltip
            
        text : str
            Tooltip message
            
        bind : bool
            Bind events to widget if True (default is True)
        """
        self.waittime = 500     #miliseconds
        self.wraplength = 400   #pixels
        self.widget = widget
        self.text = text
        
        if bind: #Bind events to widget if the widget doesn't already have any event handling functions
            #Binding events to a widget that its own event handling may have conflicts
            self.widget.bind("<Enter>", self._on_enter)
            self.widget.bind("<Leave>", self._on_leave)
            self.widget.bind("<ButtonPress>", self._on_leave)
            
        self.id = None
        self.tooltip_window = None

    def _on_enter(self, event):
        """Schedule tooltip on mouse enter"""
        self.schedule(event)

    def _on_leave(self, *_):
        """Hide tooltip on mouse leave"""
        self.unschedule()
        self.hidetip()

    def schedule(self, event):
        """Show tooltip after a certain number of milliseconds"""
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip(event))
        

    def unschedule(self):
        """Cancel schedule of tooltip display"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event):
        """Show tooltip message"""
        x = self.widget.winfo_rootx() + event.x + 10
        y = self.widget.winfo_rooty() + event.y + 15
        
        # creates a toplevel window
        self.tooltip_window = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry("+%d+%d" % (x, y))
        
        label = Label(self.tooltip_window, text=self.text, justify='left', relief='solid',
                       wraplength = self.wraplength, borderwidth=1)
        label.pack(ipadx=10, ipady=10)
        
        self.tooltip_window.update_idletasks()
        self.tooltip_window.lift()

    def hidetip(self):
        """Hide tooltip when mouse leaves or clicks button"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None