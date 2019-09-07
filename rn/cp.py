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

import matplotlib.pyplot as plt, numpy as np,math

def S(beta):
    return 3*math.log(math.cosh(4*beta))/8

def plot(beta,S_beta):
    betas = np.linspace(0,1,100)
    plt.plot(betas,[S(beta) for beta in betas],'b',label=r'$\frac{3}{8} \log(\cosh(4\beta))$')
    plt.plot(betas,betas,'r',label=r'$\beta$')
    plt.plot(betas,[3*math.tanh(4*beta)/2 for beta in betas],'k',ls='-.',label=r'Derivative: $\frac{3}{2} \tanh(4\beta)$')
    plt.scatter(beta,S_beta)
    plt.text(beta+0.01,S_beta+0.01,'Critical point {0:.6f}'.format(beta))
    plt.xlabel(r'$\beta$')
    plt.legend(loc='lower right')
    plt.savefig('figs/beta.jpg')

def solve(eps=0.1):
    beta0  = 0
    S0     = S(beta0)
    beta1  = 1
    S1     = S(beta1)
    beta   = 0.5* (beta0+beta1)
    S_beta = S(beta)    
    while beta1-beta0>eps:
        if S_beta<beta:
            beta0 = beta
            S0    = S_beta
        else:
            beta1 = beta
            S1    = S_beta
        beta   = 0.5* (beta0+beta1)
        S_beta = S(beta)
        
    return (beta,S_beta)

if __name__=='__main__':
    beta,S_beta = solve(eps=1e-6)
    plot(beta,S_beta)
    
    plt.show()