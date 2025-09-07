import numpy as np
import pandas as pd

from astropy import *
import astropy.units as u
from astropy.io import fits
from astropy.table import Table,vstack,hstack
from astropy.io import ascii

from PyBACCHUS.helper_methods import *

class Plt(object):
    def __init__(self,path):
        self.path = path
        self.read()


    def show(self):
        for n, i in enumerate(self.lines):
            print('{}, {}'.format(n, i))
            
    def read(self):
        colnames = ['lambda','slope','scale factor','y axis zoom','lambda min','lambda max','delta window','flag norm']
        self.table = Table(names=colnames)
        with open(self.path) as file:
            self.lines = file.readlines()
        file.close()

        self.header = self.lines[0]
        self.txt_colnames = self.lines[1]

        for i in self.lines[2:]:
            row = np.array(i.split(' '))
            row = row[row != '']
            row = row[0:len(row)-1]
            new_row = []
            for count, j in enumerate(row):
                if count != len(row)-1:
                    new_row.append(float(j))
                else:
                    new_row.append(int(j))
            self.table.add_row(new_row)
            
        
    def write(self,newfile=False, newfilename=''):
        outlines = [self.header, self.txt_colnames]
        for i in self.table:
            lam = np.round(i['lambda'],1)
            if i['slope'] >= 0:
                line = ' {:<.1f}   {:<.3e}   {:<.3e}   {:>.3f}  {:>.4f}  {:>.4f}    {:>.3f} {:>} \n'.format(i['lambda'],i['slope'],
                                                                  i['scale factor'],i['y axis zoom'],i['lambda min'],
                                                                  i['lambda max'],i['delta window'],int(i['flag norm']))
            else:
                line = ' {:<.1f}  {:<.3e}   {:<.3e}   {:>.3f}  {:>.4f}  {:>.4f}    {:>.3f} {:>} \n'.format(i['lambda'],i['slope'],
                                                                  i['scale factor'],i['y axis zoom'],i['lambda min'],
                                                                  i['lambda max'],i['delta window'],int(i['flag norm']))
        
            outlines.append(line)
            
        if newfile==True:
            with open(newfilename, "w") as file:
                file.writelines(output)
            file.close()
        else:
            with open(self.path, "w") as file:
                file.writelines(output)
            file.close()  
