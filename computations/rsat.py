import random

k     = 3
n     = 100
alpha = 0.01
N     = 100              # trials

def create_environment(n=n):
    return [random.choice([0,1]) for i in range(n)]

def  create_clauses(n=n,m=int(alpha*n),k=k):
    def create_one_clause():
        indices = sorted([random.randrange(1,n+1) for i in range(k)])
        return [i * random.choice([-1,1]) for i in indices]
    return [create_one_clause() for i in range(m)]

def evaluate(clauses,environment):
    def isTrue(var):
        assert(var != 0)
        index = abs(var)-1
        value = environment[index]
        if var < 0 and value==0:
            return True
        elif var>0 and value==1:
            return True
        else:
            return False
        
    def isFalse(clause):
        for var in clause:
            if isTrue(var):
                return True
        return False
    
    for clause in clauses:
        if isFalse(clause):
            return False
    return True

if __name__=='__main__':
    import matplotlib.pyplot as plt
    random.seed(1)
    alphas =[0.01,0.02,0.05,0.1,0.2]
    ys = []
    for alpha in alphas:
        count = sum([1 for i in range(N) if evaluate(create_clauses(m=int(alpha*n)),create_environment())])
        ys.append(count/N)
    plt.plot(alphas,ys)
    plt.show()