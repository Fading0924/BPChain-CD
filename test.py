import os
import math
import numpy as np
import sys
from loaduai import readUai
from mrf import MRF
from pyGM.messagepass import LBP
from pyGM.graphmodel import GraphModel, eliminationOrder
from pyGM.factor import Factor
from AceSample import log10partition
from main import SampleUai, isSolution

def count():
	app_set = [[0,0],[0,1],[1,0],[1,1]]
	solution_set = []
	dim = tuple(2 for i in range(5))
	filename = "seqdata/seq/seqvar_5.uai"
	print(filename)
	factors, dims = readUai(filename)
	mrf = MRF(factors, dims)
	for idx in range(np.power(2, 5)):
		binary = np.unravel_index(idx, dim)
		if isSolution(mrf, np.array(binary)):
			solution_set.append(list(binary))
	print('\tnumber:', len(solution_set))
	print('\tProb:', len(solution_set)/np.power(2,dims))
	for num in range(7, 33, 2):
		filename = "seqdata/seq/seqvar_%d.uai" % (num)
		print(filename)
		count = 0
		factors, dims = readUai(filename)
		mrf = MRF(factors, dims)
		tmp_set = []
		for pre in solution_set:
			for app in app_set:
				binary = pre + app
				if isSolution(mrf, np.array(binary)):
					tmp_set.append(list(binary))
		
		solution_set = tmp_set
		print('\tnumber:', len(solution_set))
		print('\tProb:', len(solution_set)/np.power(2,dims))


if __name__ == '__main__':
	count()
	sys.exit(0)
	
	filename = 'uaidata/uai2.uai'
	
	factors, dims = readUai(filename)
	mrf = MRF(factors, dims)

	for f in mrf.factors:
		f.t[np.where(f.t==0)] = 1e-5
	
	print([f.t for f in mrf.factors])
	print('Smaple UAI initial:\n')
	init_smaples = SampleUai(filename, 100)
	np.set_printoptions(threshold=np.inf)
	print(init_smaples)
	print('P:\n')
	print(init_smaples.sum(0))

	# print('CBP sample:\n')
	# cbp_samples = mrf.Conditional_Belief_Propagation()
	# np.set_printoptions(threshold=np.inf)
	# print(cbp_samples)
	# print('P:\n')
	# print(cbp_samples.sum(0))

	