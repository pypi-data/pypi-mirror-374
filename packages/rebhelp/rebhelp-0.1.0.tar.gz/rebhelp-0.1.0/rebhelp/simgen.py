# rebhelp/simgen.py
import rebound

def si():
    """SI units: meters, kg, seconds"""
    sim = rebound.Simulation()
    sim.units = ("m", "kg", "s")
    return sim

def si_km():
    """SI units: kilometers, kg, seconds"""
    sim = rebound.Simulation()
    sim.units = ("km", "kg", "s")
    return sim

def astro():
    """Astronomical units: AU, Msun, years"""
    sim = rebound.Simulation()
    sim.units = ("AU", "Msun", "yr")
    return sim

def astro_me():
    """Astronomical units with Earth masses: AU, Mearth, years"""
    sim = rebound.Simulation()
    sim.units = ("AU", "Mearth", "yr")
    return sim