#!/usr/bin/env python
from typing import Union
from pathlib import Path

def get_pyproject(directory: Union[Path,str,None] = None) -> Path :
    if directory == None :
        d = Path().cwd()
    elif isinstance(directory, Path) :
        d = directory
    elif isinstance(directory, str) :
        d = Path(directory)
    else :
        raise ValueError("get_pyproject requires either None (use CWD), an str,  or a Path")
    d = d.expanduser().resolve()
    if not d.is_dir() :
        raise ValueError("get_pyproject should be given the name of a directory")
    while d not in [Path(x) for x in ['/', '/home', '/var', '/tmp']] :
        if (d / 'pyproject.toml').is_file() :
            return (d / 'pyproject.toml')
        else :
            d = (d / "..").resolve()
    raise ValueError(f"get_pyproject did not find a pyproject.toml file starting at {directory}")
        
