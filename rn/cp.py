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
from matplotlib import rc

betas = np.linspace(0,1,50)
Ss    = [3*math.log(math.cosh(4*beta))/8 for beta in betas]

plt.plot(betas,Ss,'b',betas,betas,'r')
plt.xlabel(r'$\beta$')
plt.ylabel(r'$\frac{3}{8} \log{\cosh{4\beta}}$')
plt.savefig('figs/beta.jpg')
plt.show()