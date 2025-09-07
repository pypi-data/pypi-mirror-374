import math as m
def sp_volume(r):
    v = (4/3)*m.pi*r**3
    return v
    

def sp_surface(r):
    sur = 4*m.pi*r**2
    return sur
    

def sp_cap(r,h):
    capv = (1/3)*(m.pi*h**2)*((3*r)-h)
    return capv
  