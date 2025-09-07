from PyBACCHUS.helper_methods import *

class Babsma(object):
    def __init__(self,path):
        self.path = path
        self.read()

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