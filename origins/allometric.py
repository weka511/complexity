# Copyright (C) 2019-2020 Greenweaves Software Limited

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

from random import random, seed, choice, gauss
from ga import evolve,plot_fitness
from matplotlib.pyplot import plot, show, legend, xlabel, ylabel, ylim, title, figure, savefig
from numpy import mean, std
from math import sqrt

# create_branching_network
#
# Create a representation of flow though a network
def create_branching_network(c      = 10, #Number of levels
                             gamma0 = 0.1):
    gamma = [gamma0+(1-gamma0)*random() for _ in range(c)]
    n     = [choice([2,4,8,16,32])      for _ in range(c)]
    beta  = [1/sqrt(n0)                 for n0 in n]
    return (beta,gamma,n)

# get_resistance

def get_resistance(beta,
                   gamma,
                   n,
                   r_c=1,
                   l_c=1):
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

def mutate_branching_network(individual,
                             probability=0.5,
                             sigma=0.5):
    # Mutate a continuous value
    def perturb(x,
                mean=1.0,
                sigma=0.1,
                minimum=0.05):
        if random()<probability:
            return max(minimum,x*gauss(mean,sigma))
        return x
    
    # Mutate a discrete value
    def perturb_n(n0):
        if random()<probability:
            n1 = n0 + choice([-1,+1])
            if 1<n1 and n1<32:
                return n1
        return n0
    
    beta,gamma,n = individual
    gamma        = [perturb(g) for g in gamma]
    n            = [perturb_n(n0)  for n0 in n]
    beta         = [1/sqrt(n0) for n0 in n]
    return beta, gamma,n

if __name__=='__main__':
    import argparse
    
    from matplotlib import rc
    rc('text', usetex=True)    
    
    parser = argparse.ArgumentParser('Evolve branching network')
    parser.add_argument('--seed',  default=None, type=int,   help='Seed for random number generation')
    parser.add_argument('--N',     default=1000, type=int,   help='Number of generations')
    parser.add_argument('--M',     default=100,  type=int,   help='Population size')
    parser.add_argument('--c',     default=10,   type=int,   help='c')
    parser.add_argument('--m',     default=0.1,  type=float, help='mutation probability')
    parser.add_argument('--gamma', default=0.1,  type=float, help='Initial gamma')
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
    print (std(n)/mean(n), std(beta)/mean(beta), std(gamma)/mean(gamma))
    plot_fitness(statistics,name='WBE')
    
    figure(figsize=(20,10))
    plot([b/max(beta) for b in beta],'r',label=r'$\beta$')
    plot([g/max(gamma) for g in gamma],'g',label=r'$\gamma$')
    plot([n0/max(n) for n0 in n],'b',label='n')
    legend()
    
    show()