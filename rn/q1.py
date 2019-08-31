import math

pp = {
    'a': 0.0777093, 'b': 0.01694125, 'c': 0.02509587, 'd': 0.0415729,
    'e': 0.1293273, 'f': 0.02237207, 'g': 0.01869932, 'h': 0.063514,
    'i': 0.0705279, 'j': 0.00162383, 'k': 0.00598080, 'l': 0.04025481,
    'm': 0.0275251, 'n': 0.0702613, 'o': 0.0746462, 'p': 0.01533419,
    'q': 0.001168940, 'r': 0.0602125, 's': 0.0617264, 't': 0.0869565,
    'u': 0.02793712, 'v': 0.01067520, 'w': 0.0229406, 'x': 0.001564180,
    'y': 0.02368643, 'z': 0.001745021
}

def get_entropy(ps,coarse=lambda l: True):
    def get_entropy_contribution(p):
        return - p * math.log2(p)
    
    return sum([get_entropy_contribution(ps[letter]) for letter in ps.keys() if coarse(letter)])

def vowel(c):
    return c in ['a','e','i','o','u']

if __name__=='__main__':
    print (get_entropy(pp))
    