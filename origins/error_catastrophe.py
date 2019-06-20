def evolve(A,replication=1.0,advantage=9,q=0.88):
    
    def grow(i,a):
        return a * replication * (advantage if i==0 else 1)

    def mutations(i):
        unmutated  = q * A1[i]
        from_lower = 0 if i==0 else A1[i-1] * (1-q) * (n-i+1) / n # n-i+1 zeroes in i-1
        from_upper = 0 if i==n else A1[i+1] * (1-q) * (i+1) / n # i+1 ones in i+1
        return from_lower + unmutated + from_upper  
    
    n     = len(A) - 1
    A1    = [grow(i,A[i]) for i in range(len(A)) ]
    A2    = [mutations(i) for i in range(len(A1))]
    total = sum(A2)
    return [a/total for a in A2]

if __name__=='__main__':
    M = 1000
    N = 20
    A = [1] + N * [0]
    for i in range(M):
        A = evolve(A)
        if (i%100==0):
            print (A)