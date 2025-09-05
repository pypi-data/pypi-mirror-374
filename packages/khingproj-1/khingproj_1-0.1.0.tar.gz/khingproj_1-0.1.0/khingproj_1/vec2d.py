import numpy as np
def vec_mag(x,y):
    return (x**2 + y**2)**0.5

def dot_product(a,b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a,b)

def cross_product(a,b):
    c = np.array([a[0],a[1],0])
    d = np.array([b[0],b[1],0])    
    return np.cross(c,d)
