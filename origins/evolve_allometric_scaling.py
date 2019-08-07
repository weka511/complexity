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
from matplotlib.pyplot import show

def create_branching_network(c=10,beta0=0.1,gamma0=0.1):
    beta  = [beta0+random()  for _ in range(c)]
    gamma = [gamma0+random() for _ in range(c)]
    n     = [choice([2,10])  for _ in range(c)]
    return (beta,gamma,n)

def get_resistance(beta,gamma,n,r_c=1,l_c=1):
    r = r_c
    l = l_c
    Z = 0
    for k in range(len(beta),0,-1):
        r /= beta[k-1]
        l /= gamma[k-1]
        R = l * r**-4
        Z += R/n[k-1]
    return Z

def evaluate_branching_network(individual):
    beta, gamma,n = individual
    return 1/get_resistance(beta,gamma,n)

def mutate_branching_network(individual,probability=0.1):
    def perturb(x,sigma=0.1):
        if random()<probability:
            return x*gauss(1,0.01)
        return x
    
    def get_n(n0):
        if random()<probability:
            n1 = n0 + choice([-1,+1])
            if 1<n1 and n1 <11:
                return n1
        return n0
    beta, gamma,n = individual
    beta =  [perturb(b) for b in beta]
    gamma = [perturb(g) for g in gamma]
    n     = [get_n(n0) for n0 in n]
    return beta, gamma,n

if __name__=='__main__':
#    seed(1)
    
    population,statistics,indices = evolve(
        N=10000,
        create   = lambda :create_branching_network(c=10),
        evaluate = evaluate_branching_network,
        mutate   = lambda individual:mutate_branching_network(individual,probability=0.1),
        crossover= lambda population:population)
    print (population[indices[-1]])
    plot_fitness(statistics,name='WBE')
    show()