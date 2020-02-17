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

import random,numpy as np,sys,plot

# past
#
# Predict that attendance will be the same as 'k' weeks ago

def past(history,k=2,NN=None):
    if len(history)>k:
        return history[-k]
    elif len(history)>0:
        return history[-1]
    else:
        return random.randint(0,NN)

# average
#
# Predicts that attendance will be the average of previous 'k' weeks 

def average(history,k=3,NN=None):
    if len(history)>k:
        return np.average(history[-k:])
    elif len(history)>0:
        return np.average(history)
    else:
        return random.randint(0,NN)

# trend
#
# Predict attendance using trend line

def trend(history,k=3,NN=None):
    if len(history)>k:
        coeff = np.polyfit(range(k),history[-k:],1)
        return max(0,min(NN,coeff[0]+k*coeff[1]))
    elif len(history)>0:
        return history[-1]
    else:
        return random.randint(0,NN)

# mirror
#
# Predict that attendance will be mirror image of previous week

def mirror(history,NN=None):
    if len(history)>0:
        return NN-history[-1]
    else:
        return random.randint(0,NN)

# Bargoer
#
# This class represents a person who decides whther or not to go to the bar

class BarGoer():
    def __init__(self,I=None):
        self.prediction = None
        self.scores     = []
        self.I          = I
        
    def predict(self,history = []):
        raise Exception('Not implemented')
    
    def get_score(self,prediction,attendance,weight_miss=10,weight_uncomfortable=2,tolerance_miss=0,tolerance_discomfort=0):
        error = prediction - attendance
        if prediction>60 and attendance<=60:
            return weight_miss
        if prediction<=60 and attendance>60:
            return weight_uncomfortable        
        if error>tolerance_miss: # prediction too high
            return 1
        if error<0 and abs(error)>tolerance_discomfort: #too low
            return 1
        return 0
    
    def score(self,attendance,weight_miss=10,weight_uncomfortable=1):
        self.scores.append(self.get_score(self.prediction,attendance,weight_miss=weight_miss,weight_uncomfortable=weight_uncomfortable))
        if len(self.scores)>self.I:
            self.scores.pop(0)

            
    def review(self,attendance,threshold=5,history = []):
        raise Exception('Not implemented')

# Arthur
#
# Use Arthurian strategies for making decisions

class Arthur(BarGoer):
    basket=None     # Basket of starategies used to populate individual instances
    @classmethod
    def createBasket(dummy,NN=None):
        Arthur.basket = [
            lambda history: past(history,k=1,NN=NN),
            lambda history: past(history,k=2,NN=NN),
            lambda history: past(history,k=3,NN=NN),
            lambda history: past(history,k=4,NN=NN),
            lambda history: past(history,k=5,NN=NN),
            lambda history: past(history,k=6,NN=NN),            
            lambda history: trend(history,k=2,NN=NN),
            lambda history: trend(history,k=4,NN=NN),
            lambda history: trend(history,k=8,NN=NN),
            lambda history: trend(history,k=3,NN=NN),
            lambda history: trend(history,k=5,NN=NN),
            lambda history: trend(history,k=9,NN=NN),            
            lambda history: int(average(history,k=2,NN=NN)),
            lambda history: int(average(history,k=3,NN=NN)),
            lambda history: int(average(history,k=4,NN=NN)),
            lambda history: int(average(history,k=5,NN=NN)),
            lambda history: int(average(history,k=6,NN=NN)),            
            lambda history: int(average(history,k=8,NN=NN)),
            lambda history: mirror(history,NN=NN)
        ]
        
    def __init__(self,nstrategies=3,I=None):
        super().__init__(I=I)
        self.strategies = [Arthur.basket[i] for i in random.sample(range(len(Arthur.basket)),nstrategies)]
        self.favourite  = 0 # OK to initialize to 0 as selection of strategies is random
        #self.grace = 10
        
    def predict(self,history = []):
        self.prediction = self.strategies[self.favourite](history)   
        return self.prediction
    
    def get_gap(self,strategy,history): 
        prediction = strategy(history[:-1])
        return self.get_score(prediction,history[-1])
        
    def review(self,attendance,threshold=25,history = []):
        #self.grace-=1
        #if self.grace>0: return
        LH    = 10
        LL    = 10
        score = sum(self.scores)
        tol   = 0
        if score>threshold and len(history)> LL+LH:
            for i in range(len(self.strategies)):
                scores        = [self.get_gap(self.strategies[i],history[:-j] if j>0 else history) for j in range(LL)]
                if sum(scores)<score-tol:
                    #print ('{0}->{1} {2} {3}'.format(i,self.favourite, score, sum(scores)))
                    score          = sum(scores)
                    self.favourite = i
                    #self.grace     = 10
             
    def match(self,prediction,threshold=60):
        if self.prediction<=threshold and prediction>threshold:
            return True
        if self.prediction>threshold and prediction<=threshold:
            return True
        return False
 
 # GA
 #
 # Use a Gnettic Algorithm for making decisions
 
class GA(BarGoer):
    def __init__(self):
        super().__init__()

# step_week
#
# Simulate decision making process for one week

def step_week(bargoers,init=False,threshold=60,history = []):
    predictions = [b.predict(history) for b in bargoers]
    attendance  = sum(1 for p in predictions if p<=threshold)
    
    for b in bargoers:
        b.score(attendance)
        
    if not init:
        for b in bargoers:
            b.review(attendance,threshold,history) 
        
    history.append(attendance)

# run
#
# Simulate decision making process for entire time period

def run(bargoers,N=100,L=10,threshold=5):
    history = []
    for i in range(L):
        step_week(bargoers,init=True,threshold=threshold,history = history)

    for i in range(N):
        step_week(bargoers,threshold=threshold,history = history)

    return history

# log_history
#
# Write parameters and history to logfile

def log_history(history,out='log.txt'):
   
    with open(plot.get_logfile_name(out),'w') as f:
        f.write('I={0},L={1},N={2},NA={3},NGA={4},threshold={5},seed={6},nstrategies={7}\n'.
                format(args.I,
                       args.L,
                       args.N,
                       args.NA,
                       args.NGA,
                       args.threshold,
                       args.seed,
                       args.nstrategies))
        
        for attendance in history:
            f.write('{0}\n'.format(attendance))
            
        f.write('Completed\n')
            
if __name__=='__main__':
    import argparse
    
    parser = argparse.ArgumentParser('El Farol simulation')
    parser.add_argument('--I',           type=int, default=10,    help='Length of history')
    parser.add_argument('--L',           type=int, default=100,   help='Number of generations for initialization')
    parser.add_argument('--N',           type=int, default=100,   help='Number of generations')
    parser.add_argument('--NA',          type=int, default=100,   help='Number of Arthurian Players')
    parser.add_argument('--NGA',         type=int, default=0,     help='Number of Genetic Algorithm Players')
    parser.add_argument('--threshold',   type=int, default=60,    help='Threshold for comfort')
    parser.add_argument('--seed',        type=int, default=None,  help='Random number seed')
    parser.add_argument('--nstrategies', type=int, default=5,     help='Number of strategies')
    parser.add_argument('--out',                   default='log', help='File for logging histories')
    
    args   = parser.parse_args();
    
    if args.seed!=None:
        random.seed(args.seed)
        print ('Random number generator initialized with seed={0}'.format(args.seed))
    else:
        print ('Random number generator initialized with random seed')

    #try:
    Arthur.createBasket(NN=args.NA + args.NGA)
    
    history = run([Arthur(nstrategies=args.nstrategies,I=args.I) for i in range(args.NA)] + [GA() for i in range(args.NGA)],
                  N         = args.N,
                  L         = args.L,
                  threshold = args.threshold)
    
    log_history(history,out=args.out)

    mu    = np.mean(history[args.L:])
    sigma = np.std(history[args.L:])
    print ('Mean Attendance={0:.1f}, Standard deviation={1:.1f}, Sharpe={2:.1f}'.format(mu,sigma,mu/sigma))    
    #except Exception as e:
        #sys.exit('{0} {1}'.format(type(e),e.args))
