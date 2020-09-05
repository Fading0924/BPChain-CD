import sys
import math
import os
import argparse

parser = argparse.ArgumentParser(description='Contrasitive Diverfence with Conditional Belief Propagation')

parser.add_argument("infile", help="Graphical model (in UAI format)")
parser.add_argument("outfolder", help="Folder where models are stored")
parser.add_argument('-job', default='uai', help="SAT or UAI or SEQ")
parser.add_argument('-q', '--queue', type=str, default="yexiang", help="qsub queue")
parser.add_argument('-t', '--timeout', type=int, help="Timeout for each instance", default=14400)
args = parser.parse_args()

print("Reading factor graph from " + args.infile)
inputfile = open(args.infile, "r")

ind = 0
origNbrFactor = 0
origNbrVar = 0
for l in inputfile:
    if not l.strip()=='':
        ind = ind +1
        if ind==2:
            origNbrVar=int(l)
        elif ind==3:
            l = l.rstrip("\n")
        elif ind==4:			## add xor cpt tabe
            origNbrFactor = int(l)
        elif ind>5:
            break
print("Model with " + str(origNbrVar) + " variables and "+str(origNbrFactor) +" factors")

fname_extended = os.path.basename(args.infile)
print(fname_extended)
fname = os.path.splitext(fname_extended)[0]
outputdir = os.path.abspath(args.outfolder+'/'+fname+'/')
if not os.path.exists(outputdir):
    os.system("mkdir "+ outputdir)

parafileName = "%s_script.txt" % (fname)
rerunfile = "%s/%s" % (outputdir, "rerun.txt")
if os.path.exists(rerunfile): # all instances finished
    sys.exit(0)
f = open(parafileName, 'w')

outfilenamelog = "%s.ILOGLUE.uai.LOG initials.txt test.txt " % (fname)
modelresult = "%s_results " % (fname)
modelgibbs = "%sgibbs.uai " % (fname)
modelbp = "%sbp.uai " % (fname)
modelcbp = "%scbp.uai " % (fname)
cpname = outfilenamelog + modelgibbs + modelbp + modelcbp + modelresult
targetfile = "%s/%s" % (outputdir, outfilenamelog)
if not os.path.exists(targetfile):
    cmdline = ("python main.py --filename %s --job %s && cp %s %s\n") % (fname_extended, args.job, cpname, outputdir)
    f.write(cmdline)
f.close()

jobdir = "%sdata/%s" % (args.job.lower(), args.job.lower())
core_num = 24
sname = fname+"Launch.sh"
f = open(sname, 'w')
f.write("#!/bin/bash\n")
f.write("#PBS -j oe\n")
f.write("#PBS -N %s\n" % (fname))
f.write("\n")

f.write("set -x\n")
f.write("cd $PBS_O_WORKDIR\n")
# f.write("module load utilities gcc/6.3.0\n")
# f.write("module load utilities boost\n")
f.write("module load utilities parafly\n")
f.write("basedir=/home/ding274/CD/\n")   
f.write("datadir=$basedir/%s\n" %(jobdir))
f.write("TMPDIR=/tmp\n")
f.write("C2D=c2d_linux\n")
f.write("ACEDIR=$TMPDIR/ace_v3.0_linux86\n")
f.write("cp %s $TMPDIR/\n" % (sname))
f.write("cp %s $TMPDIR/\n" % (parafileName))
f.write("cp $basedir/paws $TMPDIR/paws\n")
f.write("cp $datadir/%s $TMPDIR/%s\n" % (fname_extended, fname_extended))
f.write("cp $basedir/loaduai.py $TMPDIR/\n")
f.write("cp $basedir/mrf.py $TMPDIR/\n")
f.write("cp $basedir/AceSample.py $TMPDIR/\n")
f.write("cp $basedir/main.py $TMPDIR/\n")
f.write("cp -r $basedir/pyGM $TMPDIR/\n")
f.write("cp $basedir/ace_v3.0_linux86.tar.gz $TMPDIR/\n")
f.write("cd $TMPDIR\n")
f.write("module load anaconda/5.1.0-py36\n")
f.write("conda create --name py36 python=3.6\n")
f.write("source activate py36\n")
f.write("conda install --name numpy scipy matplotlib pandas sortedcontainers\n")
f.write("echo 0 > empty.uai.evid\n")
f.write("tar -xzvf ace_v3.0_linux86.tar.gz\n")
f.write("export LD_LIBRARY_PATH=$ACEDIR\n")
f.write("export ACEDIR=$ACEDIR\n")
f.write("export C2D=$C2D\n")

f.write("ParaFly -c %s_script.txt -CPU 1 -failed_cmds rerun.txt\n" % (fname))
f.write("cp %s %s\n" % (cpname, outputdir))
f.write("cp rerun.txt %s" % (outputdir))
f.close()

os.system("qsub -q %s -l walltime=20:00:00,nodes=1:ppn=1,naccesspolicy=singleuser %s" % (args.queue, sname))