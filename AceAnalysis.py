import os
import re

qsub_single = False
queue = "yexiang"
# variables
homedir = "/home/ding274"
datadir = homedir+"/CD/uaidata/uai"
tmpdir = "/tmp"
seed = "7"
mem = "900000"
vstring = "-v TMPDIR={},mem={},seed={}".format(
                tmpdir, mem, seed)
# node occupation policies
# resources
nodes = "1"
ppn = "24"
walltime = "04:00:00"
rstring = "-l walltime={},nodes={}:ppn={},naccesspolicy=singleuser".format(
                    walltime, nodes, ppn)
# launch script
script = "aceLaunchscript.sh"

cstr = "qsub -q {} {} {}".format(queue, rstring, vstring)

if __name__ == "__main__":
    with open(homedir+"/CD/aceAly.txt", 'w') as tf:
        for (dirpath, dirnames, filenames) in os.walk(datadir):
            for file in filenames:
                of = os.path.splitext(file)[0]
                f = of + ".uai"
                runcommand = "java -DACEC2D=\"$ACEDIR/$C2D\" -Xmx${{mem}}m -classpath \"$ACEDIR/ace.jar:$ACEDIR/inflib.jar:$ACEDIR/jdom.jar\" mark.reason.apps.BnUai08 -z {} empty.uai.evid {} > {} 2>{}.stat".format(f, seed, of, of)
                cp2command = "cp {} $HOME/CD/".format(of)
                cp3command = "cp {}.stat $HOME/CD/".format(of)
                tf.write(runcommand+" && "+cp2command+" && "+cp3command+"\n")
    if not qsub_single:
        os.system(cstr + " " + script)
