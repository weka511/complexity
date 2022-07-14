# Copyright (C) 2019, 2022 Greenweaves Software Limited

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

'''
Critical temperature of Ising mode: used to generate a figure in renormalization.tex
- see video Renormalization: Finding Fixed Points from course
'''

from matplotlib.pyplot import plot, scatter, text, xlabel, legend, savefig, show, title
from numpy             import log, cosh, linspace, tanh

def S(beta):
    ''' '''
    return (3/8)*log(cosh(4*beta))

def plot_results(beta,S_beta):
    '''
    Plot the solution of beta = S(bata)
    '''
    betas = linspace(0,1,100)
    plot(betas,[S(beta) for beta in betas],'b',
         label = r'$\frac{3}{8} \log(\cosh(4\beta))$')
    plot(betas,betas,'r',
         label = r'$\beta$')
    plot(betas,[3*tanh(4*beta)/2 for beta in betas],'k',
         ls    = '-.',
         label = r'Derivative: $\frac{3}{2} \tanh(4\beta)$')
    scatter(beta,S_beta)
    text(beta+0.01,S_beta+0.01,f'Critical point {beta:.6f}')
    xlabel(r'$\beta$')
    legend(loc = 'lower right')
    title(__doc__)
    savefig('figs/beta.jpg')

def solve(atol = 1e-6):
    '''
    Solve the equation S(beta)==beta by binary search
    Parameters:
        atol        Tolerance
    '''
    beta0  = 0
    S0     = S(beta0)
    beta1  = 1
    S1     = S(beta1)
    while beta1-beta0>atol:
        beta   = 0.5* (beta0+beta1)
        S_beta = S(beta)
        if S_beta<beta:
            beta0 = beta
            S0    = S_beta
        else:
            beta1 = beta
            S1    = S_beta

    return (beta,S_beta)

if __name__=='__main__':
    beta,S_beta = solve()
    plot_results(beta,S_beta)
    show()
