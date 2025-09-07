import pandas as pd
import numpy as np

def get_linenumber(lines, target, idx=1):
    line_number = -99
    for count,line in enumerate(lines):
        line_text = line.split(' ')
        if len(line_text) > 1:
            if line_text[idx] == target:
                line_number = count
    if line_number > -1:
        return line_number
    else:
        print("couldn't find target!!!!")
        return line_number

# def get_existing_state(lines,target):
#     line_num = get_linenumber(lines, target)
#     if line_num > -1:
#         line = lines[line_num].split(' = ')
#         return line[-1].replace("\n", "").replace('"', '').replace("'", '')
#     else:
#         return None

def get_existing_state(line_num, lines):
    if line_num > -1:
        line = lines[line_num].split(' = ')
        return line[-1].replace("\n", "").replace('"', '').replace("'", '')
    else:
        return None
    

def edit_line(lines,line_number, text):
    """
    Allows for updating file.
    """
    new_lines = []
    for count,i in enumerate(lines):
        if count != line_number:
            new_lines.append(i)
        else:
            new_lines.append(text)

    return new_lines

def update_line(lines, fpath):
    with open(fpath, "w") as file:
        file.writelines(lines)
        file.close()

def get_windows(path, element):
    with open(path) as file:
        init = file.readlines()
        for i in init:
            array = i.split(' ')
            array = list(filter(lambda a: a != '', array))
            try:
                if array[1]==element or array[0]==element:
                    windows = []
                    for j in array[2:len(array)]:
                        if j != '' and j != '\n':
                            windows.append(np.round(float(j),1))
                    return windows
            except:
                pass
                
def justify(txt:str, width:int) -> str:
    prev_txt = txt
    while((l:=width-len(txt))>0):
        txt = re.sub(r"(\s+)", r"\1 ", txt, count=l)
        if(txt == prev_txt): break
    return txt.rjust(width)