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

from numpy import isclose

def step(A,s=0.01,nu=0.01):
    
    def grow(i,a):
        return a * (1+s) if i ==0 else a
    
    L     = len(A) - 1
    A1    = [grow(i,A[i]) for i in range(len(A)) ]
    A2    = (len(A)) * [0]
    for i in range(len(A1)):
        A2[i]     += (1 - L * nu) * A1[i]
        if i>0:
            A2[i-1] += i * nu  * A1[i]
        if i<len(A1)-1:
            A2[i+1] += (L-i) * nu  * A1[i]
         
    total = sum(A2)
    return [a/total for a in A2]

def evolve(A,s=0.01,nu=0.01, rtol=1e-05, atol=1e-08,N=100):
    for i in range(N):
        A1 = step(A,s=s,nu=nu)
        if all(isclose(A,A1,rtol=rtol,atol=atol)):
            return A1
        A = [a for a in A1]
 
    
if __name__=='__main__':
    import matplotlib.pyplot as plt
    
    L       = 10
    w       = 0.2
    nu      = 0.01
    index   = 0
    colours = ['r','g','b','y','c','m','k']
    
    plt.figure(figsize=(20,20))
    for s in [0.3,0.2,0.1,0.09,0.07]:
        A = evolve([1] + L * [0],s=s,nu=nu,N=10000)
        x = [i + w*index for i in range(len(A))]
        plt.bar(x,A,width=w,color=colours[index%len(colours)],label='{0:.2f}'.format(s))
        index += 1
        
    plt.title('L={0}, nu={1:.2}'.format(L,nu)) 
    plt.xlabel('Hamming Distance from optimum')
    plt.ylabel('Population')
    plt.legend(title='s')
    plt.show()
