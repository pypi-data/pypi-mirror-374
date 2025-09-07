import numpy as np
import pandas as pd

from PyBACCHUS.helper_methods import *
from PyBACCHUS.init_com import *
from PyBACCHUS.bsyn_com import *


class Linelist(object):
    def __init__(self,path):
        self.path = path
        # with open(self.path) as file:
        #     self.lines = file.readlines()
        #     self.original = file.readlines()
        # file.close()

    def display_all_linelists(self):
        linelists = []
        for path, subdirs, files in os.walk(self.path):
            for name in files:
                linelist_path = os.path.join(path, name)
                linelists.append(linelist_path.split(self.path)[-1])
                print(linelist_path.split(self.path)[-1])
        return linelists


    def edit_linelist(self, target_list):
        """
        This one actually opens specified linelists to allow editing. Presumable pd.Dataframe and back?
        """