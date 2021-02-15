"""Helper module that gets the absolute path to a file"""

import os

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
    except Exception:
        base_path = os.environ.get("_MEIPASS2",os.path.abspath("."))

    return os.path.join(base_path, relative_path)