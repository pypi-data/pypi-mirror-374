"""CarbonX Solver Package"""

__version__ = '1.0.0'

# Import main classes for easy access
from .core.main_flow_reactor_SPBM_V5_2 import MovingSectionalModel
from .core.mapping_wrapper_CarbonX import Mapping_Wrapper

__all__ = ['MovingSectionalModel', 'Mapping_Wrapper']