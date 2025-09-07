import numpy as np

from PyBACCHUS.helper_methods import *

class Eqwidt(object):
    def __init__(self,path):
        self.path = path
        with open(self.path) as file:
            self.lines = file.readlines()
            self.original = file.readlines()
        file.close()

    def show(self):
        for count,i in enumerate(self.lines):
            line = '{}, {}'.format(count, i)
            print(line)
        

    def edit(self, path,line_number, text, new_filename='',make_new=False):
        new_init = []
        for count,i in enumerate(init):
            line = '{}, {}'.format(count, i)
            if count != line_number:
                new_init.append(i)
            else:
                new_init.append(text)
        if make_new == False:
            command_path = self.path + '/{}'.format(module_name)
        else:
            command_path = self.path + '/{}'.format(new_filename)
        with open(self.path, "w") as file:
            file.writelines(new_init)
        file.close()
