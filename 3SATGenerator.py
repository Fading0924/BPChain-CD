import os
import sys
import argparse
import time
import numpy as np
from transformer import cnf2uai
# https://github.com/RalfRothenberger/Power-Law-Random-SAT-Generator
parser = argparse.ArgumentParser(description='Generate random 3SAT instance dataset')

parser.add_argument('-n', type=int, default=1, help="number of instances generated for a given dataset")
parser.add_argument('-k', type=int, help="clauses length", default=3)
parser.add_argument('-p', type=float, help="power-law exponent of variables", default=2.5)
parser.add_argument('-b', type=float, help="double power-law exponent of variables")
parser.add_argument('-u', type=int, default=1, help=""'"1"'" for unique varibles in a single clause, 0 otherwise")
args = parser.parse_args()

def generator(nbv, nbc):
    for i in range(args.n):
        time.sleep(1)
        file_name = "sat_var{:d}_c{:d}_no{:d}".format(nbv, nbc, i)
        command_string = "/home/ding274/CD/satdata/CreateSAT -g u -v {} -c {} -k {} -f {} -u {}".format(
                                nbv, nbc, str(args.k), file_name, str(args.u))
        try:
            os.system(command_string)
        except:
            sys.exit(1)


if __name__ == "__main__":
    variables = [3*i for i in range(3, 11)]
    clauses = [3*variables[i]  for i in range(len(variables))]
    # with open("configure", "w") as f:
    #         f.write(str(args))
    for i in range(len(variables)):
        print("Generating var{} const{}".format(variables[i], clauses[i]))
        generator(variables[i], clauses[i])
    
    mv_command = "mv sat_var*c* /home/ding274/CD/satdata/cnf/"                                                                     
    os.system(mv_command)

    indir = "/home/ding274/CD/satdata/cnf/"
    outdir = "/home/ding274/CD/satdata/sat/"
    infiles = os.listdir(indir)
    outfiles = []
    for i in range(len(infiles)):
        file = infiles[i]
        infiles[i] = indir + file
        outfiles.append(outdir + os.path.splitext(file)[0] + ".uai")
        print('file:', file)
    cnf2uai(infiles, outfiles)

