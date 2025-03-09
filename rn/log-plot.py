#!/usr/bin/env python

# Copyright (C) 2025 Greenweaves Software Limited

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
    Used to generate figure: modification of classical electrodynamics that
    comes from this background of charges
'''

from matplotlib.pyplot import figure, rcParams, show
import numpy as np

if __name__=='__main__':
    rcParams['text.usetex'] = True
    ln_r = np.linspace(0,5,num=100)
    a = 0.1
    ln_phi = 1 + a - ln_r - a* np.exp(ln_r)
    fig = figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)
    ax.plot(ln_r,1 - ln_r,c='b',label=r'No plasma: $\Phi\propto\frac{1}{r}$')
    ax.plot(ln_r,ln_phi,c='r',label='With plasma')
    ax.set_xlabel(r'$\log{r}$')
    ax.set_ylabel(r'$\log{\Phi}$')
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_yticks([])
    ax.set_xticks([])
    ax.legend()
    fig.savefig('figs/log-plot.jpg',bbox_inches='tight')
    show()
