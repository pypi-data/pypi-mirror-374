"""Top-level package for Jlop."""

__author__ = """dribeiro"""
__version__ = '0.1.0'

from .load_style import set_style
from .colors import set_colorcycle

#
# Note: Jplot overwrites the default keyword arguments of the
# errorbar function so that points are never connected by
# default
#

import matplotlib.pyplot as plt

plt._default_errorbar = plt.errorbar
plt.Axes._default_errorbar = plt.Axes.errorbar

_dkwargs = {
    'ls': '',
    'lw': 0.8,
    'ms': 3.0,
    'capsize': 2.0,
}

#Check that only ls is used 
def __check_ls(**kwargs):
    if 'linestyle' in kwargs.keys(): 
        raise ValueError('jlop styles do not support linestyle as a keyword. Use ls instead.')

#Overwrite plt.errorbar()
def _custom_errorbar(*args, **kwargs):
    __check_ls(**kwargs)
    nkwargs = {**_dkwargs, **kwargs}
    plt._default_errorbar(*args, **nkwargs)  

#Overwrite axex.errorbar()
def _custom_ax_errorbar(self, *args, **kwargs):
    __check_ls(**kwargs)
    nkwargs = {**_dkwargs, **kwargs}
    self._default_errorbar(*args, **nkwargs)  

plt.errorbar = _custom_errorbar
plt.Axes.errorbar = _custom_ax_errorbar

set_style('modern')

