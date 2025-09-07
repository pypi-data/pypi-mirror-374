import numpy as np
import pandas as pd

from PyBACCHUS.helper_methods import *

class Par(object):
    def __init__(self,path):
        self.path = path   
        self.atomic_symbols = ['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al',
 'Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe',
 'Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y',
 'Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te',
 'I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb',
 'Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt',
 'Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa',
 'U']

        self.update()

    def update(self):
        self.read()
        self.models, self.model = self.get_values('MODEL')
        self.convols, self.convol = self.get_values('convol')
        self.metallics, self.metallic = self.get_values('METALLIC')
        self.turbovels, self.turbovel = self.get_values('TURBVEL')

        for i in self.atomic_symbols:
            all_values, current = self.get_values(i)
            setattr(self, i, current)
            setattr(self, i+'_hist', all_values)
        

    def get_values(self, target):
        current = None
        history = []
        for count, i in enumerate(self.lines):
            line = i.split(' ')
            if len(line) > 1:
                if line[1] == target:
                    value = line[-1].replace('\n','')
                    if np.isin(target, ['convol','METALLIC','TURBVEL']) or np.isin(target, self.atomic_symbols):
                        try:
                            value = float(value.split("'")[1])
                        except:
                            value = float(value.split("'")[0])
                    history.append(value)
                    current = history[-1]
        return history, current

    def show(self):
        for n, i in enumerate(self.lines):
            print('{}, {}'.format(n, i))
            
    def read(self):
        with open(self.path) as file:
            self.lines = file.readlines()
        file.close()
        
    def write(self,newfile=False, newfilename=''):
        if newfile==True:
            with open(newfilename, "w") as file:
                file.writelines(output)
            file.close()
        else:
            with open(self.path, "w") as file:
                file.writelines(output)
            file.close()  

    def edit(self, line_number, text):
        new_lines = []
        for count,i in enumerate(self.lines):
            if count != line_number:
                self.lines[count] = i

    def add_line(self, line2add, line_num = -1):
        if line_num == -1:
            self.lines = np.insert(self.lines,len(self.lines), line2add)
        else:
            self.lines = np.insert(self.lines,line_num, line2add)
                    
    def add_lines(self, lines2add, linenumbers = []):
        if linenumbers != []:
            for count, i in enumerate(lines2add):
                self.add_line(i, linenumbers[count])
        else:
            for count, i in enumerate(lines2add):
                self.add_line(i)

    def remove_lines(self, lines2remove):
        truth = np.isin(self.lines,lines2remove)
        self.lines = np.array(self.lines)[truth==False]
            