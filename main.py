# import torch
# import torch.nn as nn
# from torch.autograd import Variable
# import torch.optim as optim
import numpy as np
from scipy import stats
from numpy.linalg import inv
import scipy.io as scio
import scipy.stats as st
import argparse
import copy
import math
import os 
import sys
from pyGM.messagepass import LBP
from pyGM.graphmodel import GraphModel, eliminationOrder
from pyGM.factor import Factor
from AceSample import log10partition
from mrf import MRF
from loaduai import readUai, writeUai

NUM_EPOCHS = 100
NUM_SAMPLES = 100
LAMDA = 10

def SampleUai(filename, n_samples):  # use Ace #######
	factors, dims = readUai(filename)
	a = np.ones([n_samples, dims], dtype=int)
	for sam in range(n_samples):
		logZ = log10partition(filename)
		model = MRF(factors, dims)
		for xi in range(dims):
			for f in model.factors:
				f.t[np.where(f.t==0)] = 1e-5
			model1 = GraphModel(model.factors)
			model1.condition2([xi], [1])
			for f in model1.factors:
				f.t[np.where(f.t==0)] = 1e-5
			writeUai('%spartition1.uai' % (filename[:-4]), model1.factors)
			logZ1 = log10partition('%spartition1.uai' % (filename[:-4]))
			# print('sam:[%d],xi:[%d]' % (sam,xi))
			# print('logZ:',logZ)
			# print('logZ1:',logZ1)
			p1 = np.clip(np.power(10, logZ1-logZ), 0, 1)
			v = np.random.binomial(1, p1, 1)[0]
			# print('v:',v)
			a[sam][xi] = v
			if (v == 1):
				logZ = logZ1
				model = model1
			elif (v == 0):
				logZ = np.log10(1-p1) + logZ
				model0 = GraphModel(model.factors)
				model0.condition2([xi], [0])
				model = model0
	return a

def isSolution(model, sample):
	vars_list = [factor.v.labels for factor in model.factors]
	for vars in vars_list:
		if sample[vars].sum() != 3:
			return False
	return True

def SampleSeq(model, n_samples, dims):
	term = []
	vars_list = [factor.v.labels for factor in model.factors]
	vars_list.sort()
	for _ in range(n_samples):
		sample = np.zeros(dims, dtype=int)
		for i, vars in enumerate(vars_list):
			if i == 0:
				idx = np.random.choice(vars, 3, replace=False)
				sample[idx] = 1
			else:
				n = sample[vars[:3]].sum()
				idx = np.random.choice(vars[3:], 3-n, replace=False)
				sample[idx] = 1
		term.append(sample.tolist())
	a = np.asarray(term, dtype=int)
	return a

def SampleSeqq(model, n_samples, dims):
	term = []
	vars_list = [factor.v.labels for factor in model.factors]
	vars_list.sort()
	for _ in range(n_samples):
		sample = np.zeros(dims, dtype=int)
		for i, vars in enumerate(vars_list):
			idx = np.random.choice(vars, 3, replace=False)
			sample[idx] = 1
		term.append(sample.tolist())
	a = np.asarray(term, dtype=int)
	return a

def Loglikelihood(model, data, logZ=None):      
    LL = 0.0
    if logZ is None: 
        tmp = GraphModel(model.factors)  # copy the graphical model and do VE
        sumElim = lambda F,Xlist: F.sum(Xlist)
        tmp.eliminate( eliminationOrder(model,'wtminfill') , sumElim )
        logZ = tmp.logValue([])
    for s in range(len(data)):
        LL += model.logValue(data[s])
        LL -= logZ
    LL /= len(data)
    return LL

if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Discrete MRF')
	parser.add_argument('--filename',default='uai1.uai', help='name must be specified')
	parser.add_argument('--job',default='none', help='name must be specified')
	args = parser.parse_args()
	filename = args.filename
	print(filename)

	# jobdir = "%sdata/%s/" % (args.job.lower(), args.job.lower())
	# joblist = os.listdir(jobdir)
	# for a_file in joblist:
	# 	filename = jobdir + a_file
	# 	print(filename)

	factors, dims = readUai(filename)
	mrf = MRF(factors, dims)
	mrf_gibbs = MRF(factors, dims)
	for f in mrf_gibbs.factors:
		f.randIP() 
	mrf_bp = MRF(factors, dims)
	for f in mrf_bp.factors:
		f.randIP()
	mrf_cbp = MRF(factors, dims)
	for f in mrf_cbp.factors:
		f.randIP()
	mrf_xor = MRF(factors, dims)
	for f in mrf_xor.factors:
		f.randIP()

	if args.job == 'SEQ':
		initials = SampleSeq(mrf, NUM_SAMPLES, dims)
		test = SampleSeq(mrf, NUM_SAMPLES, dims)
	elif args.job == 'SEQQ':
		initials = SampleSeqq(mrf, NUM_SAMPLES, dims)
		test = SampleSeqq(mrf, NUM_SAMPLES, dims)
	else:
		initials = SampleUai(filename, NUM_SAMPLES)
		test = SampleUai(filename, NUM_SAMPLES)
		# np.set_printoptions(threshold=np.inf)
		# print('initials:',initials)
		# print(initials.sum(0))
	np.savetxt('initials.txt', initials)
	np.savetxt('test.txt', test)
		
	for epoch in range(NUM_EPOCHS):
		print('epoch [{}/{}]'.format(epoch, NUM_EPOCHS))
		if epoch > 50:
			lamda = LAMDA / 100
		elif epoch > 20:
			lamda = LAMDA / 10
		else:
			lamda = LAMDA
		print('[gibbs]:')
		mrf_gibbs.CD(initials, 'gibbs', lamda=lamda)
		print('[bp]:')
		mrf_bp.CD(initials, 'bp', lamda=lamda)
		print('[cbp]:')
		mrf_cbp.CD(initials, 'cbp', lamda=lamda)

		if epoch % 10 == 9:
			writeUai('{}gibbs.uai'.format(filename[:-4]), mrf_gibbs.factors)
			writeUai('{}bp.uai'.format(filename[:-4]), mrf_bp.factors)
			writeUai('{}cbp.uai'.format(filename[:-4]), mrf_cbp.factors)

			## Compare likelihood of initials
			f_gibbs = mrf_gibbs.joint().table
			f_bp    = mrf_bp.joint().table
			f_cbp   = mrf_cbp.joint().table
			Z_gibbs = log10partition('{}gibbs.uai'.format(filename[:-4]))  # 
			Z_bp    = log10partition('{}bp.uai'.format(filename[:-4]))     # 
			Z_cbp   = log10partition('{}cbp.uai'.format(filename[:-4]))    # 
			os.system('touch %s.ILOGLUE.uai.LOG' % (filename[:-4]))
			os.system('touch %s_results' % (filename[:-4]))
			os.system('mv %s.ILOGLUE.uai.LOG %s.ILOGLUE' % (filename[:-4], filename[:-4]))
			try:
				f = open("%s.ILOGLUE.uai.LOG" % (filename[:-4]), 'w')
				f.write('Loglikelihood [epoch %d]: \n' % (epoch))
				for i in range(NUM_SAMPLES):
					f.write('initial sample [{}/{}]:\n'.format(i, NUM_SAMPLES))
					f.write('\t gibbs: {:.10f}'.format(math.log10(f_gibbs[tuple(initials[i])]) - Z_gibbs))
					f.write('\t bp: {:.10}'.format(math.log10(f_bp[tuple(initials[i])]) - Z_bp))
					f.write('\t cbp: {:.10}\n'.format(math.log10(f_cbp[tuple(initials[i])]) - Z_cbp))
				for i in range(NUM_SAMPLES):
					f.write('\ntest sample [{}/{}]:\n'.format(i, NUM_SAMPLES))
					f.write('\t gibbs: {:.10f}'.format(math.log10(f_gibbs[tuple(test[i])]) - Z_gibbs))
					f.write('\t bp: {:.10}'.format(math.log10(f_bp[tuple(test[i])]) - Z_bp))
					f.write('\t cbp: {:.10}\n'.format(math.log10(f_cbp[tuple(test[i])]) - Z_cbp))
				f.close()
			except:
				os.system('mv %s.ILOGLUE %s.ILOGLUE.uai.LOG' % (filename[:-4], filename[:-4]))

			if args.job == 'SEQ' or args.job == 'SEQQ':
				samples_gibbs = SampleUai('{}gibbs.uai'.format(filename[:-4]), NUM_SAMPLES)
				samples_bp = SampleUai('{}bp.uai'.format(filename[:-4]), NUM_SAMPLES)
				samples_cbp = SampleUai('{}cbp.uai'.format(filename[:-4]), NUM_SAMPLES)
				solutions_gibbs = 0
				solutions_bp = 0
				solutions_cbp = 0

				for i in range(10 * NUM_SAMPLES):
					if (isSolution(mrf_gibbs, samples_gibbs[i])):
						solutions_gibbs += 1
					if (isSolution(mrf_bp, samples_bp[i])):
						solutions_bp += 1
					if (isSolution(mrf_cbp, samples_cbp[i])):
						solutions_cbp += 1

				os.system('mv %s_results %s_results_tmp' % (filename[:-4], filename[:-4]))
				try:
					with open('%s_results' % (filename[:-4]), 'w') as f:
						f.write('Accuracy in epoch %d\n' % (epoch))
						f.write('\tGibbs:\t{:2f}\n'.format(solutions_gibbs/NUM_SAMPLES))
						f.write('\tBP:\t{:2f}\n'.format(solutions_bp/NUM_SAMPLES))
						f.write('\tCBP:\t{:2f}\n'.format(solutions_cbp/NUM_SAMPLES))
				except:
					print('write results wrong!')
					os.system('mv %s_results_tmp %s_results' % (filename[:-4], filename[:-4]))








