from astropy import *
import astropy.units as u
from astropy.io import fits
from astropy.table import Table,vstack,hstack
from astropy.io import ascii

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os

from PyBACCHUS.helper_methods import *
from PyBACCHUS.init_com import *
from PyBACCHUS.elements_wln import *
from PyBACCHUS.stellar_parameters import *
from PyBACCHUS.bsyn_com import *
from PyBACCHUS.babsma_com import *
from PyBACCHUS.eqwidt_com import *
from PyBACCHUS.linelists import *

class BACCHUS(object):
    def __init__(self,path):
        """
        Initializes a BACCHUS object. Has to be fed a path to a BACCHUS directory.
        """
        self.path = path
        self.init = Init(self.path + '/init.com')
        self.eqwidt = Eqwidt(self.path + '/eqwidt.com')
        self.stellar_parameters = StellarParameters(self.path + '/stellar_parameters.tab')
        self.bsyn = Bsyn(self.path + '/bsyn.com')
        self.babsma = Babsma(self.path + '/babsma.com')
        self.elements_wln = ElementsWLN(self.path + '/elements.wln')
        self.linelists = Linelist(self.path + '/linelists/')


    def make_backup(self):
        """
        Probably should check if a backups directory already exists. But if not, makes a copy of all the key bacchus modules so that if smtg goes wrong 
        your whole distribution isn't bricked.
        """
        module_names = ['babsma.com','bacchus.abund','bacchus.eqw','bacchus.param','bsyn.com','eqwidt.com','eqwidt.sm',
                        'load_parameters.com','solabu.dat','stellar_parameters.tab', 'init.com']
        
        backup_filename = '{}/module_backups'.format(self.path)
        if os.path.isdir(backup_filename):
            print('backup directory already exists!')
        else:
            subprocess.call(['mkdir',backup_filename])
            p = subprocess.Popen(['mkdir',backup_filename], cwd=self.path)
            for i in module_names:
                backup_path = '/module_backups/'.format(i)
                subprocess.call(['cp',current_path, backup_path])
                p = subprocess.Popen(['cp',i, backup_path], cwd=self.path)
 
    ##### OPERATIONS ON STARS #####

    # def stellar

    def load_parameters(self, Star):
        """
        Runs load_parameters.com
        """
        p = subprocess.Popen(['load_parameters.com',Star.name], cwd=self.path)
        p.wait()
        
        p.kill()
        Star.get_par(self.path + '/{}/'.format(Star.name))

        

    def param(self, Star, elem ='Fe'):
        """
        Runs bacchus.param to perform Fe excitation-ionization balancing. ****ONLY USE IF YOU HAVE X I / X II lines.****
        """
        p = subprocess.Popen(['bacchus.param',Star.name, elem], cwd=self.path)
        p.wait()
        p.kill()

        Star.get_abundance(elem)

    def eqw(self, Star, elem = 'Fe', lines=[],ranges=[]):
        """
        Runs bacchus.eqw . If initial guesses or specific lines are specified it will run on those instead of the default BACCHUS A(x) range & elements.wln line selection.
        """
        lines_str = ''
        if len(lines) > 0:
            for i in lines:
                lines_str = ' ' + lines_str

        ranges_str = ''
        if len(ranges) > 0:
            for i in ranges:
                ranges_str = ' ' + ranges_str
                
        p = subprocess.Popen(['bacchus.eqw',Star.name, elem, lines_str, ranges_str], cwd=self.path)
        p.wait()
        p.kill()

        Star.get_abundance(elem)

    def abund(self, Star, elem='Fe', lines=[],ranges=[]):
        """
        Runs bacchus.abund . If initial guesses or specific lines are specified it will run on those instead of the default BACCHUS A(x) range & elements.wln line selection.
        """
        
        lines_str = ''
        if len(lines) > 0:
            for i in lines:
                lines_str = ' ' + lines_str

        ranges_str = ''
        if len(ranges) > 0:
            for i in ranges:
                ranges_str = ' ' + ranges_str
                
        p = subprocess.Popen(['bacchus.abund',Star.name, elem], cwd=self.path)
        p.wait()
        p.kill()

        Star.get_abundance(elem)

    
    ##### LINELISTS & SELECTION #####


    ##### STRUCTURAL #####
    def set_linelist(self, linelist):
        lpath = 'linelists/' + linelist
        self.init.set_linelist(lpath)
        self.bsyn.add_linelists([lpath])

    def set_line_selection(self, lineselection):
        self.init.set_waveref_file(lineselection)

    def show_module(self, module_name):
        """
        Displays modules such as init.com, bsyn.com. etc...
        """
        command_path = self.path + '/{}'.format(module_name)
        with open(command_path) as file:
            init = file.readlines()
            for count,i in enumerate(init):
                line = '{}, {}'.format(count, i)
                print(line)
        file.close()

    def edit_module(self, module_name,line_number, text, new_filename='',make_new=False):
        #opens init.com for editing. Should be able to make a new init.com if asked. 
        
        """
        Actually allows for updating init.com. Maybe should have a way of specifying what lines set_{} are to make individual methods easier?
        """
        command_path = self.path + '/{}'.format(module_name)
        new_init = []
        with open(command_path) as file:
            init = file.readlines()
            for count,i in enumerate(init):
                line = '{}, {}'.format(count, i)
                if count != line_number:
                    new_init.append(i)
                else:
                    new_init.append(text)
        file.close()

        if make_new == False:
            command_path = self.path + '/{}'.format(module_name)
        else:
            command_path = self.path + '/{}'.format(new_filename)
        with open(command_path, "w") as file:
            file.writelines(new_init)
        file.close()

    ##### PARALLELIZE #####

    def make_maenads(self, n_copies):
        """
        Creates copies of the bacchus directory pointed at. WILL NOT copy the marcs model files. 
        """
        #returns list of BACCHUS objects that can be used for parallelized analysis. 
        #****** COMPUTATIONALLY INTENSIVE, recommended setting n_cpu in init.com = 1 and memory wall to 8 GB *******
        #Only create as many workers as you have CPUs
        pass
        
    def remove_maenads(self,directory):
        """
        Destroys all bacchus copies made except the source.
        """
        #destroys bacchus copies
        pass

    def run_monte_carlo_eqw(self, directories, Star, elem):
        """
        To be used when trying to determine stellar parameter uncertainties & abundance sensitivity. 
        """
        # *****DEPENDENT ON WHAT PARAMETERS IN INIT.COM ARE FIXED*****
        
        #Performs a Monte-Carlo on a Star object's atmospheric parameters to determine element eqw and/or metallicity/convolution/microturbulance.

        #Will need to make Star instance in each maenad using MC-ed parameters.
        #Run load_params on each star instance
        #Run eqw
        #saves all in an elem_mc_dictionary
        #exports .plt, .list files. If set to solve for atmospheric parameter, also return that parameter

    def run_monte_carlo_abund(self, directories, Star, elem):
        """
        To be used when trying to determine stellar parameter uncertainties & abundance sensitivity. 
        """
        #Performs a Monte-Carlo on a Star object's atmospheric parameters. Will need to make Star copy in each maenad
        #Run load_params on each star instance
        #update each Star instance's .par file with MC-ed abundances
        #Run abundance analysis
        #saves all in an elem_mc_dictionary
        #exports .abu files, and median A(x)
