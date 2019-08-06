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

# Evolve a solution using a Genetic Algorithm

from numpy import mean,std,argsort
from random import random,choice
from matplotlib.pyplot import plot, show, legend, xlabel, ylabel, ylim, title, figure, savefig

def roulette(population,fitness):
    def f():
        r       = T * random()
        i       = 0
        for i in range(len(breaks)-1):
            if r < breaks[i+1]:
                return i
        return -1
    indices = [len(fitness)-1- index for index in argsort(fitness)]
    T       = sum(fitness)
    breaks  = [sum(fitness[:i]) for i in range(len(fitness))]
    return [population[f()] for dummy in population]

def mutate_bit_string(individual,p=0.001):
    def flip(bit):
        return bit if random()>p else 1 - bit
    
    return [flip(bit) for bit in individual]

def simple_crossover(population,p=0.7):
    if random() < p:
        i       = choice(range(len(population)))
        j       = (i + choice(range(1,len(population))))%len(population)
        k       = choice(range(1,len(population[i])-1))
        pi_head = population[i][0:k]
        pi_tail = population[i][k:]
        pj_head = population[j][0:k]
        pj_tail = population[j][k:]
        pi      = pi_head + pj_tail
        pj      = pj_head + pi_tail
    return population
    
def evolve(N         = 100,
           M         = 100,
           create    = lambda : [],
           evaluate  = lambda individual:0.5,
           select    = roulette,
           mutate    = mutate_bit_string,
           crossover = simple_crossover):
    population = [create() for i in range(M)]
    statistics = []
    
    for i in range(N):
        fitness    = [evaluate(individual) for individual in population]
        statistics.append((max(fitness),mean(fitness),std(fitness)))
        population = crossover([mutate(individual) for individual in select(population,fitness)])
        
    fitness = [evaluate(individual) for individual in population]
    statistics.append((max(fitness),mean(fitness),std(fitness)))        
    return (population,statistics)

def plot_fitness(statistics,name='Exercise 1'):
    maxs = [a for a,_,_ in statistics]
    plot(maxs,'r', label='Maximum Fitness')
    plot([b for _,b,_ in statistics],'g', label='Mean Fitness')
    plot([c for _,_,c in statistics],'b',label='Standard Deviation')
    title(name)
    ylabel('Fitness')
    xlabel('Generation')
    ylim((0,max(maxs)+1))    
    legend(loc='center')
   

if __name__=='__main__':
    
    p_mutations = [0.001, 0.0005, 0.002]
    p_crossovers = [0, 0.1, 0.3, 0.7]
    
    index = 0
    for p1 in p_mutations:
        for p2 in p_crossovers:
            population,statistics = evolve(
                N         = 1000,
                create    = lambda : [choice([0,1]) for i in range(20)],
                evaluate  = lambda individual:sum(individual),
                mutate    = lambda individual: mutate_bit_string(individual,p=p1),
                crossover = lambda population: simple_crossover(population,p=p2)        
            )
            figure(figsize=(20,10)) 
            plot_fitness(statistics,name='P(mutation)={0}, P(crossover)={1}'.format(p1,p2))
            index += 1
            savefig('{0}'.format(index))
    show() 