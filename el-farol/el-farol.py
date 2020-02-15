# el-farol.py

# Copyright (C) 2020 Greenweaves Software Limited

# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.GA

# You should have received a copy of the GNU General Public License
# along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.

import random,abc,numpy as np

history = []
 
class BarGoer(metaclass=abc.ABCMeta):
    def __init__(self):
        pass
    @abc.abstractmethod
    def predict(self):
        pass
    @abc.abstractmethod
    def review(self,threshold=60):
        pass


def past(history,k=2):
    if len(history)>k:
        return history[-k]
    elif len(history)>0:
        return history[-1]
    else:
        return 67

def average(history,k=3):
    if len(history)>k:
        return np.average(history[-k:])
    elif len(history)>0:
        return np.average(history)
    else:
        return 67
    
class Arthur(BarGoer):
    basket = [lambda history: past(history,k=2),
              lambda history: past(history,k=3),
              lambda history: past(history,k=4),
              lambda history: past(history,k=5),
              lambda history: int(average(history,k=6)),
              ]
    def __init__(self,nstrategies=3):
        super().__init__()
        self.strategies = [Arthur.basket[i] for i in random.sample(range(len(Arthur.basket)),nstrategies)]
        self.favourite  = 0
        self.prediction = None
        
    def predict(self):
        self.prediction = self.strategies[self.favourite](history)   
        return self.prediction
    
    def review(self,threshold=60):
        if self.prediction<=threshold and history[-1]<=threshold:
            return
        if self.prediction>threshold and history[-1]>threshold:
            return
        predictions = [strategy(history) for strategy in self.strategies]
        matches     = [i for i in range(len(self.strategies)) if self.match(predictions[i],threshold)]
        if len(matches)>0:
            self.favourite = random.choice(matches)
            
    def match(self,prediction,threshold=60):
        if self.prediction<=threshold and prediction>threshold:
            return True
        if self.prediction>threshold and prediction<=threshold:
            return True
        return False
       
class GA(BarGoer):
    def __init__(self):
        super().__init__()

def step_week(bargoers,init=False,threshold=60,I=10):
    predictions = [b.predict() for b in bargoers]
    attendance  = sum(1 for p in predictions if p<=threshold)
    history.append(attendance)
    if len(history)>I:
        history.pop(0)
    for b in bargoers:
        b.review(threshold)    
    print (history)    
    
def run(bargoers,N=100,L=10,I=10,threshold=60):
    for i in range(L):
        step_week(bargoers,init=True,threshold=threshold,I=I)
    for i in range(N):
        step_week(bargoers,threshold=threshold,I=I)

if __name__=='__main__':
    import argparse
    
    parser = argparse.ArgumentParser('El Farol simulation')
    parser.add_argument('--I',           type=int, default=10,   help='Length of history')
    parser.add_argument('--L',           type=int, default=100,  help='Number of generations for initialization')
    parser.add_argument('--N',           type=int, default=100,  help='Number of generations')
    parser.add_argument('--NA',          type=int, default=100,  help='Number of Arthurian Players')
    parser.add_argument('--NGA',         type=int, default=0,    help='Number of Generic Algorithm Players')
    parser.add_argument('--threshold',   type=int, default=60,   help='Threshold for comfort')
    parser.add_argument('--seed',        type=int, default=None, help='Random number seed')
    parser.add_argument('--nstrategies', type=int, default=5,    help='Number of strategies')
    args   = parser.parse_args();
    if args.seed!=None:
        random.seed(args.seed)
        print ('Random number generator initialized with seed={0}'.format(args.seed))
    else:
        print ('Random number generator initialized with random seed')
    bargoers = [Arthur(nstrategies=args.nstrategies) for i in range(args.NA)] + [GA() for i in range(args.NGA)]
    run(bargoers, N=args.N, L=args.L, I=args.I, threshold=args.threshold)
