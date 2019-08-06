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

from random import random, seed
from ga import evolve


def create_branching_network(c=10):
    beta  = [random() for i in range(c)]
    gamma = [random() for i in range(c)]
    return (beta,gamma)
 
def evaluate_branching_network(individual):
    beta, gamma = individual
    return random()

def mutate_branching_network(individual,probability=0.1):
    return individual

if __name__=='__main__':
    seed(1)
    
    population,statistics = evolve(
        create   = lambda :create_branching_network(c=10),
        evaluate = evaluate_branching_network,
        mutate   = lambda individual:mutate_branching_network(individual,probability=0.1))
    
