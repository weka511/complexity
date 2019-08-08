# Copyright (C) 2019 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.

# Optimize flow through a branching network, after West et al--
# A General Model for the Origin of Allometric Scaling Laws in Biology
# http://hermes.ffn.ub.es/oscar/Biologia/Escala/Science_276_122_1997.pdf

from random import random, seed, choice, gauss
from ga import evolve,plot_fitness
from matplotlib.pyplot import plot, show, legend, xlabel, ylabel, ylim, title, figure, savefig
from numpy import mean, std
from math import sqrt

def create_branching_network(c=10,gamma0=0.1):
    gamma = [gamma0+(1-gamma0)*random() for _ in range(c)]
    n     = [choice([2,4,8,16,32])      for _ in range(c)]
    beta  = [1/sqrt(n0)                 for n0 in n]
    return (beta,gamma,n)

def get_resistance(beta,gamma,n,r_c=1,l_c=1):
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

def evaluate_branching_network(individual):
    beta, gamma,n = individual
    return 1/get_resistance(beta,gamma,n)

def mutate_branching_network(individual,probability=0.5,sigma=0.5):
    def perturb(x,sigma=0.1):
        if random()<probability:
            return max(0.05,x*gauss(1,sigma))
        return x
    
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
#    seed(1)
    
    population,statistics,indices = evolve(
        N         = 1000,
        create    = lambda :create_branching_network(c=10),
        evaluate  = evaluate_branching_network,
        mutate    = lambda individual:mutate_branching_network(individual,probability=0.1),
        crossover = lambda population:population)
    beta,gamma,n = population[indices[-1]]
    print (std(n)/mean(n), std(beta)/mean(beta), std(gamma)/mean(gamma))
    plot_fitness(statistics,name='WBE')
    
    figure(figsize=(20,10))
    plot([b/max(beta) for b in beta],'r',label='beta')
    plot([g/max(gamma) for g in gamma],'g',label='gamma')
    plot([n0/max(n) for n0 in n],'b',label='n')
    legend()
    
    show()