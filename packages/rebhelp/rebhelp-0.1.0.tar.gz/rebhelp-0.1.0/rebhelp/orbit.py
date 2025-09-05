# rebhelp/orbits.py
import numpy as np

def get_primary(particles):
    """Return the most massive particle (the primary)."""
    return max(particles, key=lambda p: p.m)

def dist(p1, p2):
    """Euclidean distance between two particles."""
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def rel_vel(p1, p2):
    """Relative velocity of p2 w.r.t. p1."""
    return np.array([p2.vx - p1.vx, p2.vy - p1.vy, p2.vz - p1.vz])

def rel_speed(p1, p2):
    """Magnitude of relative velocity."""
    return np.linalg.norm(rel_vel(p1, p2))

def get_orbit(particles, obj):
    """
    Calculates an orbit based on a hierarchy tree.

    Assumptions:
    - One dominant primary body
    - S-type system: planets << star, moons << planets
    - Does not handle P-type circumbinary systems or equal-mass binaries

    Returns:
        (orbit, primary)
    """
    primary = get_primary(particles)

    # Remove primary, add object if needed
    particle_list = [p for p in particles if p != primary]
    if obj not in particle_list:
        particle_list.append(obj)

    # Hill radii relative to the primary
    hill_list = [
        p.orbit(primary).a * np.cbrt(p.m / (3*primary.m))
        for p in particle_list
    ]

    # Each particle starts as its own subsystem
    particle_subs = [[p] for p in particle_list]
    parents = particle_list[:]

    # Assign moons
    for i, p in enumerate(parents):
        if p is not None:  # not banned
            for j, q in enumerate(particle_list):
                if i != j and dist(p, q) < hill_list[i] and p.m > q.m:
                    particle_subs[i].append(q)
                    particle_subs[j] = [q]   # reset q's subsystem
                    parents[j] = None        # ban q from claiming moons

    # Case 1: obj still orbits the primary
    if obj in parents:
        return (obj.orbit(primary), primary)

    # Case 2: obj is inside a subsystem
    for sys in filter(lambda s: len(s) > 1, particle_subs):
        if obj in sys:
            return get_orbit(sys, obj)