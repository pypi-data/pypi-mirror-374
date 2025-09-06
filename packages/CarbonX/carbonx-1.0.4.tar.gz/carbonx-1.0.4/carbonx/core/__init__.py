"""
Core modules for CarbonX solver
Contains the main reactor models and wrapper classes
"""

# Import core classes
try:
    from .main_flow_reactor_SPBM_V5_2 import MovingSectionalModel
    from .mapping_wrapper_CarbonX import Mapping_Wrapper
    from . import cythonization_module
  
    
  
except ImportError as e:
    print(f"Warning: Could not import core modules: {e}")
    # Set to None if import fails
    MovingSectionalModel = None
    Mapping_Wrapper = None

# Define public API
__all__ = [
    'MovingSectionalModel',
    'Mapping_Wrapper',
    'cythonization_module'
]


