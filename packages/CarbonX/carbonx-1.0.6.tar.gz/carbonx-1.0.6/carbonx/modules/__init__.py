"""
Supporting modules for CarbonX solver
Contains kinetics solvers, particle models, and utility functions
"""

# Import all solver modules
try:
    from . import saturation_test
    from . import chemical_kinetics_solver
    from . import particle_temperature_solver
    from . import surface_kinetics_C2H2
    from . import chemical_kinetics_species_detector
    from . import sintering_models
    from . import Results_Processor
    from . import hydrogen_tracker
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")

# You can also import specific functions if you want them easily accessible
try:
    from .chemical_kinetics_solver import chemical_kinetics
    from .surface_kinetics_C2H2 import (
        Surface_Kinetics_Puretzky_etal_2005,
        Surface_Kinetics_Ma_etal_2005
    )
except ImportError:
    pass

# Define what's publicly available
__all__ = [
    'saturation_test',
    'chemical_kinetics_solver', 
    'particle_temperature_solver',
    'surface_kinetics_C2H2',
    'chemical_kinetics_species_detector',
    'sintering_models',
    'Results_Processor',
    'hydrogen_tracker',
    'chemical_kinetics',  # Convenience import
]