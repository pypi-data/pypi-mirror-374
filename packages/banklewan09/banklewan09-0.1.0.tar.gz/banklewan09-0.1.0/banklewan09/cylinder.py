import math

def volume(r, h):
    r = float(r)
    h = float(h)
    return math.pi * r * r * h

def lateral_area(r, h):
    r = float(r)
    h = float(h)
    return 2 * math.pi * r * h

def surface_area(r, h) :
    r = float(r)
    h = float(h)
    return 2 * math.pi * r * (r + h)