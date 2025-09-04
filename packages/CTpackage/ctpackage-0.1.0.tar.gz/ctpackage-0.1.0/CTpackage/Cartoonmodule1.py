import math as m
def Area_circle(r):
    return m.pi*r**2
 
def length_circle(r):
    return 2*m.pi*r

def Area_sector(zeta,r):
    s=m.radians(zeta)
    return (s/2)*r**2