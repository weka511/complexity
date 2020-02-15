# el-farol.py

# Copyright (C) 2020 Greenweaves Software Limited

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

history = []
    
def step_week():
    history.append(1)

def run(N=100,L=10,I=10):
    for i in range(L):
        step_week()
    print (history)
    for i in range(N):
        step_week()

if __name__=='__main__':
    import argparse
    
    parser = argparse.ArgumentParser('El Farol simulation')
    parser.add_argument('--I',type=int,default=10,help='Length of history')
    parser.add_argument('--L',type=int,default=100,help='Number of generations for initialization')
    parser.add_argument('--N',type=int,default=100,help='Number of generations')
    args   = parser.parse_args();
    
    run(N=args.N,L=args.L,I=args.I)
