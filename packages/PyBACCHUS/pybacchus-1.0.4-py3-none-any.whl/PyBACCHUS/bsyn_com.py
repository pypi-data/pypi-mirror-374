import numpy as np
import pandas as pd

from PyBACCHUS.helper_methods import *

class Bsyn(object):
    def __init__(self,path):
        self.path = path
        self.read()

        self.nfiles_start_idx = get_linenumber(self.lines, "'NFILES", idx=0)
        self.nfiles_end_idx = get_linenumber(self.lines, "'SPHERICAL:'", idx=0)

        self.files = np.array(self.lines[self.nfiles_start_idx+1:self.nfiles_end_idx])
        
        self.nfiles = int(len(self.files))
        self.lines[self.nfiles_start_idx] = "'NFILES   :' '{}'\n".format(self.nfiles)

    def add_linelists(self, files):
        if len(files) > 0:
            self.nfiles = self.nfiles + len(files)
            self.lines[self.nfiles_start_idx] = "'NFILES   :' '{}'\n".format(self.nfiles)
            for count, i in enumerate(self.lines):
                if count == self.nfiles_start_idx + 1:
                    self.lines = np.insert(self.lines, self.nfiles_start_idx + 2, files)

    def remove_linelists(self, files):
        if len(files) > 0:
            truth = np.isin(self.lines,files)
            self.lines = np.array(self.lines)[truth==False]
            truth = np.isin(self.files,files)
            self.files = np.array(self.files)[truth==False]
            self.nfiles = self.nfiles - len(files)
            
            self.lines[self.nfiles_start_idx] = "'NFILES   :' '{}'\n".format(self.nfiles)

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
        