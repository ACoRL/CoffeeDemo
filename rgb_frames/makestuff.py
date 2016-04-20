import os

for state in map(str, range(19)):
    os.system("mkdir ./" + state)
    for direc in ('0','1','7'):
        os.system("mkdir ./" + state + '/' + direc)
