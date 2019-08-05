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

from numpy import mean,std,argsort
from random import random, seed
def create():
    pass
 
def evaluate(individual):
    return 0.5

def roulette(population,fitness):
    def f():
        r       = T * random()
        i       = 0
        for i in range(len(breaks)):
            if r < breaks[i]:
                return population[i]
        return population[-1]
    indices = [len(fitness)-1- index for index in argsort(fitness)]
    T       = sum(fitness)
    breaks  = [sum(fitness[:i]) for i in range(len(fitness))]
    return [f() for dummy in population]

def mutate(individual,probability=0.1):
    return individual

def crossover(population):
    pass

def evolve(N=10,M=100,mutation_probability=0.1,create=create,evaluate=evaluate,select=roulette,mutate=mutate,crossover=crossover):
    population = [create() for i in range(M)]
    statistics = []
    for i in range(N):
        fitness    = [evaluate(individual) for individual in population]
        statistics.append((max(fitness),mean(fitness),std(fitness)))
        population = [mutate(individual,probability=mutation_probability) for individual in select(population,fitness)]
        crossover(population)
        
    return (population,statistics)

if __name__=='__main__':
    seed(1)
    evolve()