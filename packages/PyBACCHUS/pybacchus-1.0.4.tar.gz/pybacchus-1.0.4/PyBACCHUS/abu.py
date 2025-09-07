import numpy as np

from astropy import *
import astropy.units as u
from astropy.io import fits
from astropy.table import Table,vstack,hstack
from astropy.io import ascii

from PyBACCHUS.helper_methods import *

class Abu(object):
    def __init__(self,path):
        self.path = path
        colnames = ['lambda','eqw_obs','syn','flag_syn','eqw','flag_eqw','int','flag_int','chi2','flag_chi2','chi2_val','SNR','rvcor','limit_syn','limit_eqw','limit_int']
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
