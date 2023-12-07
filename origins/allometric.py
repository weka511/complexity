#!/usr/bin/env python

# Copyright (C) 2019-2023 Simon Crase

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Optimize flow through a branching network, after West et al--
# A General Model for the Origin of Allometric Scaling Laws in Biology
# http://hermes.ffn.ub.es/oscar/Biologia/Escala/Science_276_122_1997.pdf

import argparse
from random import random, seed, choice
from ga import evolve,plot_fitness, perturb, perturb_n
from matplotlib.pyplot import show,  figure
from matplotlib import rc
import numpy as np

# create_branching_network
#
# Create a representation of flow though a network
#

def create_branching_network(c      = 10, #Number of levels
                             gamma0 = 0.1):
    gamma = [gamma0+(1-gamma0)*random() for _ in range(c)] # scale factor for branching - lengths
    n     = [choice([2,4,8,16,32])      for _ in range(c)] # number of branches at each level
    beta  = [1/np.sqrt(n0)                 for n0 in n]       # scale factor for branching - radii
    return (beta,gamma,n)

# get_resistance
#
# Calculate resistance using West et al equation (6)
def get_resistance(beta,     # scale factor for branching - radii
                   gamma,    # scale factor for branching - lengths
                   n,        # number of branches at each level
                   r_c=1,    # initial radius at root of tree
                   l_c=1):   # initial length at root of tree
    r = r_c
    l = l_c
    R = []
    for k in range(len(beta),0,-1):
        r /= beta[k-1]
        l /= gamma[k-1]
        R.append(l * r**-4)

    Z = 0
    N = 1

    for k in range(len(beta)):
        Z += R[k]/N
        N *= n[k]

    return Z

# evaluate_branching_network
#
# The score is 1/resiatnce, as we want a network that minimizes resistance.

def evaluate_branching_network(individual):
    beta, gamma,n = individual
    return 1/get_resistance(beta,gamma,n)

# mutate_branching_network

def mutate_branching_network(individual,       # Individual to be mutated
                             probability = 0.5,  # Probability of mutation
                             sigma       = 0.5):       # standard deviation for mutating continuous values


    beta,gamma,n = individual
    gamma        = [perturb(g,probability=probability) for g in gamma]
    n            = [perturb_n(n0,probability=probability)  for n0 in n]
    beta         = [1/np.sqrt(n0) for n0 in n]
    return beta, gamma,n

if __name__=='__main__':
    rc('text', usetex=True)

    parser = argparse.ArgumentParser('Evolve branching network')
    parser.add_argument('--seed',   default=None, type=int,   help='Seed for random number generation')
    parser.add_argument('--N',      default=1000, type=int,   help='Number of generations')
    parser.add_argument('--M',      default=100,  type=int,   help='Population size')
    parser.add_argument('--c',      default=10,   type=int,   help='c')
    parser.add_argument('--m',      default=0.1,  type=float, help='mutation probability')
    parser.add_argument('--gamma',  default=0.1,  type=float, help='Initial gamma')
    parser.add_argument('--savefig', default=None,             help='File name for saving plots')
    args = parser.parse_args()
    seed(args.seed)

    population,statistics,indices = evolve(
        N         = args.N,
        M         = args.M,
        create    = lambda :create_branching_network(c=args.c, gamma0=args.gamma),
        evaluate  = evaluate_branching_network,
        mutate    = lambda individual:mutate_branching_network(individual,probability=args.m),
        crossover = lambda population:population)
    beta,gamma,n = population[indices[-1]]
    print (np.std(n)/np.mean(n), np.std(beta)/np.mean(beta), np.std(gamma)/np.mean(gamma))

    fig = figure(figsize=(10,10))
    fig.tight_layout()
    ax1 = fig.add_subplot(2,1,1)
    plot_fitness(statistics,name='Fitness',ax=ax1)
    ax2= fig.add_subplot(2,1,2)
    ax2.set_title('Evolution of Parameters')
    ax2.plot([b/max(beta) for b in beta],   'r', label=r'$\beta$')
    ax2.plot([g/max(gamma) for g in gamma], 'g', label=r'$\gamma$')
    ax2.plot([n0/max(n) for n0 in n],       'b', label='n')
    ax2.legend()
    if args.savefig!=None:
        fig.savefig(args.savefig)
    show()
