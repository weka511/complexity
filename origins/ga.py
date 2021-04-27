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

# Evolve a solution using a Genetic Algorithm

# References:
# [1]  Melanie Mitchell. An introduction to genetic algorithms. MIT press, 1998.
# [2]  Werner Krauth. Statistical mechanics: algorithms and computations. OUP Oxford, 2006.

from numpy import mean, std, argsort, searchsorted
from random import random, choice, sample, gauss
from matplotlib.pyplot import plot, show, legend, xlabel, ylabel, ylim, title, figure, savefig

# roulette
#
#  Implements fitness proportional selection as described in [1].
#   Parameters:
#      population   A collection of genomes
#      fitness      Fitness values assigned to each genome

def roulette(population,fitness):
    # Select one element from population using Tower Sampling [2]
    def select(T=None,breaks=[],indices=[]):
        return indices[searchsorted(breaks,T * random())]
    
    indices = argsort(fitness)              # Used to order fitnesses
    fitness = [fitness[i] for i in indices] # Organize fitness in ascending order
     
    T       = sum(fitness)                  # Normalizing value, so we can treat fitnesses as probabilities
    
    breaks  = [sum(fitness[:i]) for i in range(1,len(fitness))] # Subtotals for use in tower sampling[2].
    
    return [population[select(T=T,breaks=breaks,indices=indices)] for _ in population]   # Select new population

# mutate_bit_string
#
# Mutate a genome consisting of a bit string
#
#   Parameters:
#      genome
#      p        Probability a single bit will be mutated

def mutate_bit_string(genome,p=0.001):
    
    # flip
    #
    # flip one bit with probability p
    
    def flip(bit):
        return bit if random()>p else 1 - bit
    
    return [flip(bit) for bit in genome]

# single_point_crossover
#
# Perform Single point crossover on a genome consisting of a list.
# Randomly choose pairs of parents (without replacement) and crossover
# both members of the pair.
#
#      Parameters:
#          population  Collection of genomes
#          p           Probability of a genome being slected as a parent
def single_point_crossover(population,p=0.7):
    parents  = iter(sample(range(len(population)),int(p*len(population))))
    for i in parents:
        j       = next(parents)
        k       = choice(range(1,len(population[i])-1))
        #  Split the two genomes that have been selected
        pi_head = population[i][0:k]
        pi_tail = population[i][k:]
        pj_head = population[j][0:k]
        pj_tail = population[j][k:]
        # Recombine
        pi      = pi_head + pj_tail
        pj      = pj_head + pi_tail
    return population
 
# evolve
#
# Use a genetic algorithm to improve fitness
#
#    Parameters:
#      N           Number of generations          
#      M           Size of population
#      create      Used to create one genome
#      evaluate    Evaluate fitness
#      select      Select elements for next generation 
#      mutate      Used to mutate a genome
#      crossover   Used to perform crossover
#
#    Returns:
#         population  The population at the end of the evolution
#         statistics  A list of stats for eact generation: maximum fitness,
#                                                          average fitness, and standard deviation
#         indices     A list of indices of the population, in ascending order of fitness
#                     so population[indices[-1]] will be the most fit solution found

def evolve(N         = 100,
           M         = 100,
           create    = lambda : [],
           evaluate  = lambda individual:0.5,
           select    = roulette,
           mutate    = mutate_bit_string,
           crossover = single_point_crossover):
    
    population = [create() for i in range(M)]
    statistics = []
    
    for i in range(N):
        fitness    = [evaluate(individual) for individual in population]
        statistics.append((max(fitness),mean(fitness),std(fitness)))
        population = [mutate(individual) for individual in crossover(select(population,fitness))]
        
    fitness = [evaluate(individual) for individual in population]
    statistics.append((max(fitness),mean(fitness),std(fitness)))        
    return (population,statistics,argsort(fitness))

# plot_fitness
#
# Plot the maximum, mean, and standard deviation of fitness
#
#   Parameters:
#      statistics
#      name
def plot_fitness(statistics,name='Exercise 1'):
    maxima = [a for a,_,_ in statistics]
    plot(maxima,'r', label='Maximum Fitness')
    plot([b for _,b,_ in statistics],'g', label='Mean Fitness')
    plot([c for _,_,c in statistics],'b',label=r'$\sigma$')
    title(name)
    ylabel('Fitness')
    xlabel('Generation')
    ylim((0,max(maxima)+1))    
    legend(loc='center')
   
# Mutate a continuous value
# 
def perturb(x,
            probability = 0.5,  # Probability of mutation
            mean    = 1.0,
            sigma   = 0.1,
            minimum = 0.05,
            maximum = 0.95):
    if random()<probability:
        return min(maximum,max(minimum,x*gauss(mean,sigma)))
    return x

# Mutate a discrete value
def perturb_n(n,
               probability = 0.5,  # Probability of mutation
              min_value=1,
              max_value=32):
    if random()<probability:
        n_mutated = n + choice([-1,+1])
        if min_value<n_mutated and n_mutated<max_value:
            return n_mutated
    return n

if __name__=='__main__':    # Test, based on exercise 1 in [1]
    
    from argparse import ArgumentParser
    from matplotlib import rc
    rc('text', usetex=True)
    
    parser = ArgumentParser('Genetic Algorithm Demo')
    parser.add_argument('--pc', default=0.7,   type=float, nargs='+', help='Crossover rate')
    parser.add_argument('--pm', default=0.001, type=float, nargs='+', help='Mutation probability')
    parser.add_argument('-n',   default=20,    type=int,              help='Number of Trials')
    parser.add_argument('-N',   default=1000,  type=int,              help='Number of generations')
    args = parser.parse_args();
    
    pcs = args.pc if type(args.pc)==list else [args.pc]
    pms = args.pm if type(args.pm)==list else [args.pm]
    for pc in pcs:
        for pm in pms:
            firsts = []
            for i in range(args.n):
                _,statistics,_ = evolve(
                    N         = args.N,
                    create    = lambda : [choice([0,1]) for _ in range(20)],
                    evaluate  = lambda individual:sum(individual),
                    mutate    = lambda individual: mutate_bit_string(individual,p=pm),
                    crossover = lambda population: single_point_crossover(population,p=pc)        
                )
                maxima = [a for a,_,_ in statistics]
                try:
                    firsts.append(maxima.index(20))
                except ValueError:
                    firsts.append(args.N+1)
                    
            print('{0}, {1}, {2}, {3}'.format(pc,pm,int(mean(firsts)),int(std(firsts))))

#   Pc       Pm       Mean         Std
#   0.7      0.001    224         110
#   0.0      0.001    235          62
#   0.3      0.001    250         112
#0.0, 0.001, 285, 111
#0.0, 0.002, 196, 70
#0.0, 0.005, 109, 45
#0.1, 0.001, 267, 82
#0.1, 0.002, 164, 76
#0.1, 0.005, 111, 52
#0.3, 0.001, 250, 91
#0.3, 0.002, 190, 72
#0.3, 0.005, 107, 51
#0.7, 0.001, 217, 72
#0.7, 0.002, 171, 77
#0.7, 0.005, 98, 45
