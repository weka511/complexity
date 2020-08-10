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



def create_environment(n=100):
    return [random.choice([-1,1]) for i in range(n)]

def  create_clauses(n=100,m=5,k=3):
    def create_one_clause():
        return [i * random.choice([-1,1]) for i in sorted(random.sample(range(1,n+1),k))]
    
    return [create_one_clause() for i in range(m)]

def evaluate(clauses,environment):
    def isTrue(var):
        assert(var != 0)
        return var * environment[abs(var)-1]>0
        
    def isFalse(clause):
        for var in clause:
            if isTrue(var):
                return True
        return False
    
    for clause in clauses:
        if isFalse(clause):
            return False
    return True

if __name__=='__main__':
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import argparse
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Palatino"],
    }) 
    
    parser = argparse.ArgumentParser('Investigate dependence of satisfaibility on alpha')
    parser.add_argument('--seed', type=int)
    parser.add_argument('--k',    type=int, default=3)
    parser.add_argument('--N',    type=int, default=100)
    parser.add_argument('--n',    type=int, default=100)
    args = parser.parse_args();
    
    random.seed(args.seed)
    alphas =[0.005*i for i in range(100)]
    for n in [100,200,500]:
        plt.plot(alphas,
                 [sum([evaluate(create_clauses(m=int(alpha*n),k=args.k,n=n),
                                create_environment(n=n)) for i in range(args.N)])/args.N for alpha in alphas],
                 label=f'n={n}')
    plt.title(f'k={args.k}, N={args.N}')
    plt.xlabel(r'$\alpha$')
    plt.ylabel('Satisfiability')
    plt.legend()
    plt.savefig(f'{args.k}-SAT')
    plt.show()