import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PyBACCHUS.bacchus import *
from PyBACCHUS.par import *
from PyBACCHUS.plt import *
from PyBACCHUS.abu import *
from PyBACCHUS.eqw import *
from PyBACCHUS.results import *
from PyBACCHUS.tab import *

from astropy import *
import astropy.units as u
from astropy.io import fits
from astropy.table import Table,vstack,hstack
from astropy.io import ascii

class Star(object):
    def __init__(self,name):
        self.name = name
        self.path = None
        self.best_parameters = None
        self.par = None

        self.atomic_symbols = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al',
 'Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe',
 'Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y',
 'Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te',
 'I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb',
 'Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt',
 'Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa',
 'U']
        self.Abundance = dict() 
        for i in self.atomic_symbols:
            self.Abundance[i] = None
        

    def set_initial_values(self, spectra_path, teff, logg, m_h, v_micro, conv):
        
        self.spectra_path = spectra_path
        self.teff = teff[0]
        self.logg = logg[0]
        self.m_h = m_h[0]
        self.vmicro = v_micro[0]
        self.conv = conv[0]

        self.e_teff = teff[1]
        self.e_logg = logg[1]
        self.e_m_h = m_h[1]
        self.e_vmicro = v_micro[1]
        self.e_conv = conv[1]

        params = dict()
        params['Teff'] = teff
        params['logg'] = teff
        params['m_h'] = logg
        params['vmicro'] = v_micro
        params['conv'] = conv

        self.params = params

    def get_spectrum(self, has_uncertainties=False):
        data = np.loadtxt(self.spectra_path)
        self.waves = data[:,0]
        self.flux = data[:,1]
        if has_uncertainties == True:
            self.flux = data[:,2]

    def view_obs_spectra(self,xlabel='Wavelength [Angstroms]',ylabel='Rectified Flux',savefig=False):
        """
        View the observed spectra to make sure it's 100% okay. Useful for smoothbrains like me who get their file indexing wrong.
        """
        plt.figure(figsize=(14,4))
        plt.plot(self.waves,self.flux)
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel(ylabel, fontsize=15)
        plt.title(self.name, fontsize=15)
        plt.tight_layout()
        if savefig==True:
            plt.savefig('{}_observed_spectrum.jpg'.format(self.name))

    ##### STAR PARAMETERS #####
    def get_par(self, path):
        self.path = path
        self.par = Par(self.path + '{}.par'.format(self.name))
        
    def get_best_parameters(self):
        self.best_parameters = Tab(self.path + '/best_parameters.tab')

    def make_best_parameters(self):
        self.best_parameters = Tab(self.path + '/best_parameters.tab',self.params)
        self.best_parameters.make()
    

    ##### ABUNDANCE INFORMATION #####

    def get_abundance(self, element):
        self.Abundance[element] = Results(self.path,self.name,element)

    def make_abundance_table(self,metric, threshold=1):
        #take only good flags
        pass
        

    
        

    


