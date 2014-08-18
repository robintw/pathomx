import os, sys
import numpy as np
import pandas as pd

import pickle, dill

from matplotlib.figure import Figure, AxesStack
from matplotlib.axes import Subplot

from mplstyler import StylesManager

import warnings
from . import displayobjects
from .utils import scriptdir, basedir
from IPython.core import display

MAGIC_TYPES = [
        np.array, np.ndarray,
        pd.Series, pd.DataFrame,
        Figure, Subplot,
        StylesManager,
        displayobjects.Svg, displayobjects.Html,
        display.SVG
        ]


def pathomx_notebook_start(fn, vars):
    
    _keep_input_vars = ['styles']
    # Wipeout variables possibly hang around from previous runs
    for k in list( vars.keys() ):
        if type(vars[k]) in MAGIC_TYPES and \
            not k.startswith('_'):
                del vars[k]

    with open(fn, 'rb') as f:
        ivars = pickle.load(f)

        for k, v in ivars.items():
            vars[k] = v

    vars['_pathomx_exclude_input_vars'] = [x for x in ivars.keys() if x not in _keep_input_vars]
    vars['_pathomx_tempdir'] = os.path.dirname(fn)

    # Handle IO magic
    for k,v in vars['_io']['input'].items():
        if v in vars:
            vars[k] = vars[v]
        else:
            vars[k] = None

    global rcParams
    from matplotlib import rcParams

    # Block warnings from deprecated rcParams here
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k, v in vars['rcParams'].items():
            rcParams[k] = v

    
def figure_prepickle_handler(v):
    v._cachedRenderer = None
    for ax in v._axstack.as_list():
        for axi in ax.images:
            axi._imcache = None
        ax._cachedRenderer = None

    return v
    
    
    
def pathomx_notebook_stop(fn, vars):
    # Export known variable types from globals
    
    # Handle IO magic
    for k,v in vars['_io']['output'].items():
        if k in vars:
            vars[v] = vars[k]
        else:
            vars[v] = None

    with open(fn, 'wb') as f:
        ovars = {}
        for k, v in vars.items():
            # Check it's an accepted type for passing; and not private (starts with _)
            if not k.startswith('_') and \
               not k in vars['_pathomx_exclude_input_vars'] and \
               type(v) in MAGIC_TYPES:
                
                if type(v) == Figure:
                    v = figure_prepickle_handler(v)

                ovars[k] = v
        
        pickle.dump(ovars, f, -1)

