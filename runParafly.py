import os
import sys
import random
import argparse

def walkandInvoke():
        parser = argparse.ArgumentParser(description="Walks through the data folder and triggers parafly script")
        parser.add_argument("-job", type=str, default='uai', help="dataset folder")
        parser.add_argument('-q', '--queue', type=str, default="yexiang", help="qsub queue")
        args = parser.parse_args()
        indir = "/home/ding274/CD/%sdata/%s/" % (args.job.lower(), args.job.lower())
        outdir = "/home/ding274/CD/%sdata/model/" % (args.job.lower())

        for file in sorted(os.listdir(indir)):
                command = "python parafly.py {} {} -job {} --queue {}".format(indir+file, outdir, args.job, args.queue)
                print(command)
                os.system(command)

if __name__ == "__main__":
    walkandInvoke()