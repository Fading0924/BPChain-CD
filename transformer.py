import sys
import os
import numpy as np
import re

def cnf2uai(infiles, outfiles):
    comment = re.compile(r"^c ")
    intro = re.compile(r"(p cnf )([0-9]+ )([0-9]+)")
    triplet = re.compile(r"( [-]?[1-9][0-9]+){3}")
    for fi in range(len(infiles)):
        nbvar = 0
        nbcla = 0
        constraints = []

        ifp = infiles[fi]
        with open(ifp, 'r') as f:
            for line in f.readlines():
                line = re.split("\n",line)[0]
                # print(line)

                c = comment.match(line)
                if c is not None:
                    continue
                
                p = intro.match(line)
                if p is not None:
                    nbvar = int(p.group(2))
                    nbcla = int(p.group(3))
                    continue

                nbs = re.split(' ', line)
                constraint = []
                for i in range(len(nbs) - 1):
                    if nbs[i] == '':
                        continue
                    else:
                        constraint.append(int(nbs[i]))
                # print(constraint)
                constraints.append(constraint)
        
        ofp = outfiles[fi]
        with open(ofp, 'w+') as f:
            f.write("MARKOV\n")
            f.write("{:d}\n".format(nbvar))
            for i in range(nbvar):
                f.write("2 ")
            f.write('\n')
            f.write("{:d}\n".format(len(constraints) + nbvar))
            for i in range(nbvar):
                f.write("1   %d\n" % (i))
            for i in range(len(constraints)):
                if (len(constraints[i]) == 2):
                    var1 = abs(constraints[i][0])
                    var2 = abs(constraints[i][1])
                    f.write("2\n{:d} {:d}\n".format(
                        var1-1, var2-1))
                elif (len(constraints[i]) == 3):
                    var1 = abs(constraints[i][0])
                    var2 = abs(constraints[i][1])
                    var3 = abs(constraints[i][2])
                    f.write("3\n{:d} {:d} {:d}\n".format(var1-1, var2-1, var3-1)) 

            for i in range(nbvar):
                f.write("2\n")
                f.write("1   1\n")

            for i in range(len(constraints)):
                if (len(constraints[i]) == 2):
                    res = np.random.uniform(10, 1000, 4)
                    var1 = constraints[i][0]
                    var2 = constraints[i][1]
                    res[int((1-var1/abs(var1))+(1-var2/abs(var2))/2)] = np.random.uniform(0.1, 1, 1)[0]
                    f.write("4\n{:.12f}\n{:.12f}\n{:.12f}\n{:.12f}\n".format(
                        res[0], res[1], res[2], res[3]))
                elif (len(constraints[i]) == 3):
                    res = np.random.uniform(10, 1000, 8)
                    var1 = constraints[i][0]
                    var2 = constraints[i][1]
                    var3 = constraints[i][2]
                    res[int((1-var1/abs(var1))*2+(1-var2/abs(var2))+(1-var3/abs(var3))/2)] = np.random.uniform(0.1, 1, 1)[0]
                    f.write("8\n{:.12f}\n{:.12f}\n{:.12f}\n{:.12f}\n{:.12f}\n{:.12f}\n{:.12f}\n{:.12f}\n".format(
                        res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7]))
        print(ofp + " written succeed!")
               
if __name__ == "__main__":
    indir = "/home/ding274/CD/satdata/cnf/"
    outdir = "/home/ding274/CD/satdata/SAT/"
    infiles = os.listdir(indir)
    outfiles = []
    for i in range(len(infiles)):
        file = infiles[i]
        infiles[i] = indir + file
        outfiles.append(outdir + os.path.splitext(file)[0] + ".uai")
        print('file:', file)
    cnf2uai(infiles, outfiles)