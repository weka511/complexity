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

import random

# create_environment
#
# Create one set of variables.
# We will represent the variables x1, x2, ... as successive elements in a Python list, so x1 is the zeroth element, and so on.
# We represent True by +1, False by -1. So x1=True, x2=False, x3=True, x4=True,... would be [+1,-1, +1, +1, ...]
#
# Parameters:
#      n        Number of variables
#
# Returns:
#     An array of n variables, set either to +1 (True) or -1 (False)

def create_environment(n=100):
    return [random.choice([-1,1]) for i in range(n)]

# create_clauses
#
# Create one set of clauses
# A single clause is a list of values, e.g. 
# [x1, not x5, x17] would be represented [+1, -5, +17]
#
# Parameters:
#
#    n    Number of variables
#    m    Number of clauses in a set
#    k    Number of terms (including negated terms) in a clause
#
#    Returns:
#        a List containing m clauses

def  create_clauses(n=100,m=100,k=3):
    # create_one_clause
    #
    # Create one clause with k terms
    def create_one_clause():
        return [i * random.choice([-1,1]) for i in sorted(random.sample(range(1,n+1),k))]
    
    return [create_one_clause() for i in range(m)]

# evaluate
#
# Evaluate a set of clauses in specified environment
#
# Returns True iff all clauses satisified in specified environment

def evaluate(clauses=[],environment=[]):
    # isTrue
    #
    # Test one term to see whether or not it is satisfied. 
    # From the description of the enviornmant and clauses given above,
    # both variable and term will have the same sign if term is satisfied
    # i.e. if x5 is False, environment[4]==-1, and this will satisfy the term -5 (Not x5).
    def isTrue(term):
        assert(term != 0)
        return term * environment[abs(term)-1]>0
    
    # isSatisfied
    #
    # Returns true if any term in clause is satisfied
    def isSatisfied(clause):
        for term in clause:
            if isTrue(term):
                return True
        return False
    
    for clause in clauses:
        if not isSatisfied(clause):
            return False
    return True

# solve
#
# Try to satisfy a set of clauses
#
# Parameters:
#      clauses List of clauses to be satisified
#      M       Number of attempts to satisfy clauses, each with a defferent assignmnet to variables
#      n       Number of varaibles to be set
# Returns:
#      True iff the clauses are satisfied for at least one assignment of values

def solve(clauses,M=100,n=100):
    for i in range(M):
        if evaluate(clauses=clauses,environment=create_environment(n=n)):
            return True
    return False    

# coerce_list
#
# Used with a command line parameter that has nargs='*' to force the argument to be a list
def coerce_list(x):
    return x if type(x)==list else [x]

# estimate_solvability
#
# Work out which fraction of clauses is solveable
#
# Parameters:
#     m   Number of clauses in each set
#     k   Number of terms in each clause: default to 3-SAT
#     n   Number of variables
#     M   Number of attempts to solve for each set
#     N   Number of sets of clauses to solve for
#
# Returns: fraction of clauses that can be solved. Generate N sets of clauses, 
#          and make up to M attempts to solve, with a new set of variables each time.

def estimate_solvability(m=10,k=3,n=100,M=100,N=25):
    return sum(
        [solve(clauses=create_clauses(m = m, k = k, n = n),
               M = M,
               n = n)
         for i in range(N)]
        )/N

if __name__=='__main__':
    import matplotlib.pyplot as plt, matplotlib as mpl, argparse
    plt.rcParams.update({
        "text.usetex": True
    }) 
    
    parser = argparse.ArgumentParser('Investigate dependence of satisfiability on alpha')
    parser.add_argument('--seed',   type=int,                             help='Seed for random number generator')
    parser.add_argument('--dalpha', type=float,            default=0.01,  help='Stepsize for iterating alpha')
    parser.add_argument('--k',      type=int,              default=3,     help='Number of terms in each clause: default to 3-SAT')
    parser.add_argument('--N',      type=int,              default=100,   help='Number of sets of clauses to solve for')
    parser.add_argument('--M',      type=int,              default=100,   help='Number of attempts to solve for each set')
    parser.add_argument('--n',      type=int,  nargs='*',  default=100,   help='Number of variables')
    parser.add_argument('--show', action='store_true',     default=False, help='Show plot')
    args = parser.parse_args();
    
    random.seed(args.seed) # Uses system time if no seed specified through command line
    
    alphas = [args.dalpha*i for i in range(int(1.0/args.dalpha))]
    
    for n in coerce_list(args.n):
        plt.plot(alphas, 
                 [estimate_solvability(m = int(alpha*n),
                                       k = args.k,
                                       n = n,
                                       M = args.M,
                                       N = args.N) for alpha in alphas],
                 label=f'{n}')
     
    plt.title(f'{args.k}-SAT: N={args.N}, M={args.M}')
    plt.xlabel(r'$\alpha$')
    plt.ylabel('Satisfiability')
    plt.legend(title='Number of variables')
    plt.savefig(f'{args.k}-SAT')
    
    if args.show:
        plt.show()