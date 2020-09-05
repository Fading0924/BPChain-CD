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
from loaduai import readUai, writeUai

NUM_SAMPLES = 100

class MRF(GraphModel):
	def __init__(self, factors, dims):
		super(MRF, self).__init__(factorList=factors)
		# self.factors = factors
		self.dims = dims
	
	def SampleUaipaws(self, filename, n_samples):
		nbauxv = 15
		os.system('./paws {} -paritylevel 1 -samples {} -nbauxv {} -b 1 -alpha 1 -pivot 4 > tmp.txt'.format(filename, 3*n_samples, nbauxv))
		term = []
		with open('forsample.txt', 'r') as f:
			while(True):
				line=f.readline()
				if(len(line)==0 or len(term)==n_samples):
					break
				line = line[:-nbauxv-1]
				term.append(list(line))
		a=np.asarray(term, dtype=int)
		return a

	def Gibbs_Sampling(self, initials=None, stopSamples=1):
		"""Gibbs sampling procedure for discrete graphical model "model"
		"""
		# state = state if state is not None else [np.random.randint(Xi.states) for Xi in self.X]
		# TODO: timing check
		term = copy.deepcopy(initials)
		for sam in range(NUM_SAMPLES):
			for j in range(stopSamples):
				# TODO if out of time, break
				for Xi in self.X:
					p = Factor([],1.0)
					for f in self.factorsWith(Xi,False):
						cvar = f.vars - [Xi]
						p *= f.condition2( cvar, [term[sam][v] for v in cvar] )
					p /= p.sum()
					term[sam][Xi] = p.sample()[0]
		return term
	
	def Belief_Propagation(self):
		term = np.ones((NUM_SAMPLES, self.dims), dtype=int)
		belief_V = LBP(self, maxIter=10, verbose=False)
		for sam in range(NUM_SAMPLES):
			for i, x_p in enumerate(belief_V):
				term[sam][i] = x_p.sample()[0]
		return term

	def Conditional_Belief_Propagation(self):
		term = np.ones((NUM_SAMPLES, self.dims), dtype=int)
		for sam in range(NUM_SAMPLES):
			modelA = GraphModel(self.factors)
			for i in range(self.dims):
				belief_V = LBP(modelA, maxIter=10, verbose=False)
				# print('belief_V:', [f.t for f in belief_V])
				one_sample = belief_V[self.dims-1-i].sample()[0]
				# print('[dim %d]_sample:' % (i), one_sample)
				term[sam][self.dims-1-i] = one_sample
				modelA.condition2([self.dims-1-i], [one_sample])
				modelA.removeFactors(modelA.factorsWith(self.dims-1-i))
				modelA = GraphModel(modelA.factors)
				for f in modelA.factors:
					f.t[np.where(f.t==0)] = 1e-5
				# print('modelA:', modelA.X)
				# print([(f.v, f.t) for f in modelA.factors])
		return term

	def XOR_Sampling(self):
		writeUai('./forsample.uai', self.factors)
		term = self.SampleUaipaws('forsample.uai', NUM_SAMPLES)
		# print('term shape:', term.shape)
		return term

	def CD(self, initials, method, lamda):
		if method == 'gibbs':
			samples = self.Gibbs_Sampling(initials)
		elif method == 'bp':
			samples = self.Belief_Propagation()
		elif method == 'cbp':
			samples = self.Conditional_Belief_Propagation()
		elif method == 'xor':
			samples = self.XOR_Sampling()
		else:
			print("WRONG TO SAMPLE!")
		for i in range(len(self.factors)):
			var = self.factors[i].v
			for sam in range(NUM_SAMPLES):
				sample_v = tuple([int(samples[sam][v.label]) for v in var])
				initial_v = tuple([int(initials[sam][v.label]) for v in var])
				self.factors[i][sample_v]  /= np.exp(lamda/NUM_SAMPLES)
				self.factors[i][initial_v] *= np.exp(lamda/NUM_SAMPLES)