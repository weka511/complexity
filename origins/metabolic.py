#!/usr/bin/env python

# Copyright (C) 2019-2023 Simon Crase

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

import numpy as np
from matplotlib.pyplot import figure, show

def flux(c,yC,D=1):
    return 4*np.pi * c *yC /(c**3)

def  plot_flux(M=21,N=25):
    cell_sizes = np.linspace(0.1,1,M)
    yCs        = np.linspace(1.0,10,N)
    X, Y       = np.meshgrid(cell_sizes, yCs)
    Z          = flux(X,Y)

    fig = figure()
    ax = fig.add_subplot(1,1,1)
    mappable = ax.contourf(X, Y, Z)
    ax.set_xlabel('Cell size')
    ax.set_ylabel('yCs')
    ax.set_title('Energy Yield')
    fig.colorbar(mappable)
    show()

if __name__=='__main__':
    plot_flux()
