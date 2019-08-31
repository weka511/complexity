def freqs(r):
    result={}
    total=0
    for c in r:
        if c.isalpha():
            if c.isupper():
                c=c.lower()
            if c in result:
                result[c]+=1
            else:
                result[c]=1
            total+=1
    return {c:result[c]/total for c in result.keys()}

if __name__=='__main__':
    import requests   
    url = 'https://www.gutenberg.org/files/1342/1342-0.txt'
    r = requests.get(url)
    ps = freqs(r.text)
    for l in sorted(ps.keys()):
        print (l,ps[l])