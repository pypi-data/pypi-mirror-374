# rebhelp/units.py

# Constants
__M_EARTH = 5.9722e24
__M_MOON  = 7.3477e22
__M_SUN   = 1.9885e30

# Mass converters
def etkg(m):
    """Earth masses to kg"""
    return m * __M_EARTH

def mtkg(m):
    """Lunar masses to kg"""
    return m * __M_MOON

def stkg(m):
    """Solar masses to kg"""
    return m * __M_SUN

def mte(m):
    """Lunar masses to Earth masses"""
    return m * __M_MOON / __M_EARTH

def ets(m):
    """Earth masses to Solar masses"""
    return m * __M_EARTH / __M_SUN

def mts(m):
    """Lunar masses to Solar masses"""
    return m * __M_MOON / __M_SUN

def ste(m):
    """Solar masses to Earth masses"""
    return m * __M_SUN / __M_EARTH

# Velocity converters
def sikm_astro(v):
    """km/s to AU/yr"""
    return v * 365.25 * 86400 / 149597870.7

def astro_sikm(v):
    """AU/yr to km/s"""
    return v * 149597870.7 / (365.25 * 86400)