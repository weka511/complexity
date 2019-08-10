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

import numpy as np
import matplotlib.pyplot as plt
import math

def flux(c,yC,D=1):
    return 4*math.pi * c *yC /(c**3)

def  plot_flux():
    cell_sizes = np.linspace(0,1,21)
    yCs        = np.linspace(0.1,10,21)
    z = np.array([flux(c,yC) for yC in yCs for c in cell_sizes])

    X, Y = np.meshgrid(cell_sizes, yCs)
    Z = z.reshape(21, 21)
    
    plt.contourf(X, Y, Z)
    plt.xlabel('Cell size')
    plt.ylabel('yCs')
    plt.title('Energy Yield')
    plt.show()
    
if __name__=='__main__':
    plot_flux()