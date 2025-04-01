from typing import List, Dict, Optional, Type
from .base import AnalysisComponent

class System(AnalysisComponent):
    """
    Base abstract class for system, which handles the system of linear equations
    """
    _systems = {}  # Class-level dictionary to store system types
    
    @staticmethod
    def register_system(name: str, system_class: Type['System']):
        """Register a system type"""
        System._systems[name.lower()] = system_class
    
    @staticmethod
    def create_system(system_type: str, **kwargs) -> 'System':
        """Create a system of the specified type"""
        system_type = system_type.lower()
        if system_type not in System._systems:
            raise ValueError(f"Unknown system type: {system_type}")
        return System._systems[system_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available system types"""
        return list(System._systems.keys())


class FullGeneralSystem(System):
    """
    Full general system, is NOT optimized, uses all the matrix
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "system FullGeneral"


class BandGeneralSystem(System):
    """
    Band general system, uses banded matrix storage
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "system BandGeneral"


class BandSPDSystem(System):
    """
    Band SPD system, for symmetric positive definite matrices, uses banded profile storage
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "system BandSPD"


class ProfileSPDSystem(System):
    """
    Profile SPD system, for symmetric positive definite matrices, uses skyline storage
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "system ProfileSPD"


class SuperLUSystem(System):
    """
    SuperLU system, sparse system solver
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "system SuperLU"


class UmfpackSystem(System):
    """
    Umfpack system, sparse system solver
    """
    def __init__(self, lvalue_fact: Optional[float] = None):
        self.lvalue_fact = lvalue_fact
    
    def to_tcl(self) -> str:
        cmd = "system Umfpack"
        if self.lvalue_fact is not None:
            cmd += f" -lvalueFact {self.lvalue_fact}"
        return cmd


class MumpsSystem(System):
    """
    Mumps system, sparse direct solver
    """
    def __init__(self, icntl14=None, icntl7=None):
        """
        Initialize a Mumps System

        Args:
            icntl14 (float, optional): Controls the percentage increase in the estimated working space
            icntl7 (int, optional): Computes a symmetric permutation (ordering) for factorization
                0: AMD
                1: set by user
                2: AMF
                3: SCOTCH
                4: PORD
                5: Metis
                6: AMD with QADM
                7: automatic
        """
        self.icntl14 = icntl14
        self.icntl7 = icntl7
    
    def to_tcl(self) -> str:
        """
        Convert the system to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "system Mumps"
        if self.icntl14 is not None:
            cmd += f" -ICNTL14 {self.icntl14}"
        if self.icntl7 is not None:
            cmd += f" -ICNTL7 {self.icntl7}"
        return cmd


# Register all systems
System.register_system('fullgeneral', FullGeneralSystem)
System.register_system('bandgeneral', BandGeneralSystem)
System.register_system('bandspd', BandSPDSystem)
System.register_system('profilespd', ProfileSPDSystem)
System.register_system('superlu', SuperLUSystem)
System.register_system('umfpack', UmfpackSystem)
System.register_system('mumps', MumpsSystem)