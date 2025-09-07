import numpy as np
import pandas as pd

from astropy import *
import astropy.units as u
from astropy.io import fits
from astropy.table import Table,vstack,hstack
from astropy.io import ascii

from PyBACCHUS.helper_methods import *

class EQW(object):
    def __init__(self,path):
        self.path = path
        colnames = ['element','ionization','lambda','chi','loggf','eqw_calc','eqw_obs','eqw_error','abundance']
        self.table = Table.read(self.path,names=colnames, format='ascii')

    def show(self):
        display(self.table)

    def get(self):
        return self.table
        
    def write(self,newfile=False, newfilename=''):
        if newfile:
            ascii.write(self.table, newfilename, overwrite=True,format="no_header")
        else:
            ascii.write(self.table, self.path, overwrite=True,format="no_header")