import numpy as np
import pandas as pd

from astropy import *
import astropy.units as u
from astropy.io import fits
from astropy.table import Table,vstack,hstack
from astropy.io import ascii

from PyBACCHUS.helper_methods import *

class Tab(object):
    def __init__(self, path, parameters):
        self.path = path
        self.params = parameters
        self.table = None

    def read(self):
        try:
            # with open(self.path) as file:
            #     self.lines = file.readlines()
            # file.close()
            self.table = Table.read(self.path, format='ascii')
            
        except:
            print('No best parameter file found!!!')

    def make(self):
        with open(self.path, "w") as file:
            file.write("#conv Teff +/- err initTeff conv_Teff  logg +/- err initlogg conv_logg met +/- err  initmet xit +/- err initxit conv_xit\n")
        with open(self.path, "a") as file:
            file.write("1  {a} +/- {e_a} {a} 1    {b} +/- {e_b} {b} 1    {c} +/- {e_c}  {c}     {d} +/- {e_d} {d} 1\n".format(a=self.params['Teff'][0],e_a=self.params['Teff'][1], b=self.params['logg'][0],e_b=self.params['logg'][1], 
                                                                                                                              c=self.params['m_h'][0],e_c=self.params['m_h'][1], d=self.params['vmicro'][0],e_d=self.params['vmicro'][1]))
            file.write("1  {a} +/- {e_a} {a} 1    {b} +/- {e_b} {b} 1    {c} +/- {e_c}  {c}     {d} +/- {e_d} {d} 1\n".format(a=self.params['Teff'][0],e_a=self.params['Teff'][1], b=self.params['logg'][0],e_b=self.params['logg'][1], 
                                                                                                                              c=self.params['m_h'][0],e_c=self.params['m_h'][1], d=self.params['vmicro'][0],e_d=self.params['vmicro'][1]))
        self.table = Table.read(self.path, format='ascii')

    
    def show(self):
        for n, i in enumerate(self.lines):
            print('{}, {}'.format(n, i))

        
    def write(self,newfile=False, newfilename=''):
        if newfile:
            ascii.write(self.table, newfilename, overwrite=True,format="no_header")
        else:
            ascii.write(self.table, self.path, overwrite=True,format="no_header")