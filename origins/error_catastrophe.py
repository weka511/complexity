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
    from argparse import ArgumentParser
    
    parser = ArgumentParser('Plot error catastrophe')
    parser.add_argument('-L','--Length',default=10,type=int,help='Length of genome in bits')
    parser.add_argument('-n','--nu',default=0.01,type=float,help='Mutation rate per bit')
    parser.add_argument('-s','--advantage',default=[0.8,0.6,0.4, 0.3,0.2,0.1,0.09,0.07,0.0],
                        nargs='+',type=float,help='Advantage for optimal genome')
    args    = parser.parse_args()
   
    index   = 0
    colours = ['r','g','b','y','c','m']
    patterns = ['','/'] 
    line_styles = ['-','--','-.',':']
    Ss      = sorted(args.advantage,reverse=True)
    plt.figure(figsize=(20,20))
    
    Populations =[[] for i in range(args.Length+1)]
    
    for s in Ss:
        A = evolve([1] + args.Length * [0],s=s,nu=args.nu,N=10000)
        for i in range(len(Populations)):
            Populations[i].append(A[i])
        x = [i + index/len(Ss) for i in range(len(A))]
        plt.bar(x,A,width=1/len(Ss),color=colours[index%len(colours)],ecolor='face',
                hatch=patterns[index//len(colours)],label='{0:.2f}'.format(s))
        index += 1
        
    plt.title('L={0}, nu={1:.2}'.format(args.Length,args.nu))
    plt.xlim(0,len(A))
    plt.xlabel('Hamming Distance from optimum')
    plt.ylabel('Frequency')
    plt.legend(title='s')
    
    plt.figure(figsize=(20,20))
    for i in range(len(Populations)):
        plt.plot(Ss,Populations[i],color=colours[i%len(colours)],
                ls=line_styles[i//len(colours)],label='{0}'.format(i))
    
    plt.legend(title='Length') 
    plt.xlim(min(Ss),max(Ss))
    plt.xlabel('s')
    plt.ylabel('Frequency')
    plt.title('Error catastrophe')
    plt.show()
