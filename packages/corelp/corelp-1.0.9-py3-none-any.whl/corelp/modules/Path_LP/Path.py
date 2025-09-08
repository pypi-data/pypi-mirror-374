#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-09-02
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : Path

"""
This function is a wrapper around the pathlib.Path and returns a compatible Path with a windows path copied inside Linux (for WSL)
"""



# %% Libraries
from pathlib import Path as PathlibPath
import os



# %% Function
def Path(path, *args, **kwargs) :
    '''
    This function is a wrapper around the pathlib.Path and returns a compatible Path with a windows path copied inside Linux (for WSL)
    
    Parameters
    ----------
    path : str of pathlib.Path
        path string to convert to Path.

    Returns
    -------
    path : pathlib.Path
        compatible Path.

    Examples
    --------
    >>> from corelp import Path
    >>> import os
    ...
    >>> os.name == "nt"
    False
    >>> Path("C:\\Users\\MyName\\Documents\\")
    PosixPath('/mnt/c/Users/MyName/Documents/')
    '''

    if os.name == "nt" :
        return PathlibPath(path, *args, **kwargs)

    pathstring = str(path)
    pathstring = pathstring.replace("\\", "/")
    drive, rest = pathstring.split(':', 1)
    pathstring = f"/mnt/{drive.lower()}{rest}"
    return PathlibPath(pathstring, *args, **kwargs)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)