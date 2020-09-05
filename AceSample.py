import os
import math
import numpy as np
import sys
from loaduai import readUai
from mrf import MRF
from pyGM.messagepass import LBP
from pyGM.graphmodel import GraphModel, eliminationOrder
from pyGM.factor import Factor

def log10partition(fname_extend):
    fname = fname_extend[:-4]
    seed = "7"
    runcommand = "TMPDIR=./ && "
    runcommand += "ACEDIR=$TMPDIR/ace_v3.0_linux86 && "
    runcommand += "C2D=c2d_linux && "
    runcommand += "export LD_LIBRARY_PATH=$ACEDIR && "
    runcommand += "export ACEDIR=$ACEDIR && "
    runcommand += "export C2D=$C2D && "
    runcommand += "java -DACEC2D=\"$ACEDIR/$C2D\" -Xmx90000m -classpath \"$ACEDIR/ace.jar:$ACEDIR/inflib.jar:$ACEDIR/jdom.jar\" mark.reason.apps.BnUai08 -z {} empty.uai.evid {} > {} 2>{}.stat".format(fname_extend, seed, fname, fname)
    os.system(runcommand)
    # print(runcommand)
    # f = open(fname+'.stat', 'r')
    # line=f.readline()
    # while(line):
    #     print(line)
    #     line=f.readline()
    f = open(fname, 'r')
    log10Z = f.readline()[2:]
    try:
        res = float(log10Z)
        return res
    except:
        print('ACE WRONG! log10Z:',log10Z)
        sys.exit(0)
    

if __name__ == '__main__':
    filename = 'uaidata/uai2.uai'
    log10partition(filename)
    with open (filename[:-4], 'r') as f:
        log10Z = f.readline()[2:]
        print('log10Z:',log10Z)
    
   

    