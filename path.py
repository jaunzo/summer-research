"""Helper module to get resource path"""

import sys, os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Parameters
    ----------
    relative_path : str
        Relative path to file from script/executable's location
        
    Returns
    -------
    str
        Absolute path to file
    """
    if getattr(sys, 'frozen', False):
        #Get directory where executable is located
        executable_path = sys.executable
        base_path = os.path.split(executable_path)[0]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    path = os.path.join(base_path, relative_path)
    
    print(f"\nOpening file at {path}")
    return path