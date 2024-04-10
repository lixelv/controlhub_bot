import os
import os.path as p
c = 0

def count(lnk):
    c = 0
    if p.isdir(lnk):
        for i in os.listdir(lnk):
            if p.splitext(i)[1] in ('.py', '.bat', '.env', '.json'):
                with open(p.join(lnk, i), 'r') as f:
                    for line in f.readlines():
                        if line != '\n':
                            c += 1
            elif p.isdir(p.join(lnk, i)) and i[0] != '.':
                c += count(p.join(lnk, i))
    return c

print(count(os.getcwd()))