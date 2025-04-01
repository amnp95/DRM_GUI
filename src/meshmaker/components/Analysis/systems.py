from typing import List, Dict, Optional, Union, Type
from .base import AnalysisComponent
from abc import abstractmethod

class System(AnalysisComponent):
    """
    Base abstract class for system, which handles the system of linear equations
    """
    _systems = {}  # Class-level dictionary to store system types
    _created_systems = {}  # Class-level dictionary to track all created systems
    _next_tag = 1  # Class variable to track the next tag to assign
    
    def __init__(self, system_type: str):
        """
        Initialize a system
        
        Args:
            system_type (str): Type of the system
        """
        self.tag = System._next_tag
        System._next_tag += 1
        self.system_type = system_type
        
        # Register this system in the class-level tracking dictionary
        System._created_systems[self.tag] = self
    
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
    
    @classmethod
    def get_system(cls, tag: int) -> 'System':
        """
        Retrieve a specific system by its tag.
        
        Args:
            tag (int): The tag of the system
        
        Returns:
            System: The system with the specified tag
        
        Raises:
            KeyError: If no system with the given tag exists
        """
        if tag not in cls._created_systems:
            raise KeyError(f"No system found with tag {tag}")
        return cls._created_systems[tag]

    @classmethod
    def get_all_systems(cls) -> Dict[int, 'System']:
        """
        Retrieve all created systems.
        
        Returns:
            Dict[int, System]: A dictionary of all systems, keyed by their unique tags
        """
        return cls._created_systems
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all systems and reset tags.
        """
        cls._created_systems.clear()
        cls._next_tag = 1
    
    @abstractmethod
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this system
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        pass

    @classmethod
    def _reassign_tags(cls) -> None:
        """
        Reassign tags to all systems sequentially starting from 1.
        """
        new_systems = {}
        for idx, system in enumerate(sorted(cls._created_systems.values(), key=lambda s: s.tag), start=1):
            system.tag = idx
            new_systems[idx] = system
        cls._created_systems = new_systems
        cls._next_tag = len(cls._created_systems) + 1

    @classmethod
    def remove_system(cls, tag: int) -> None:
        """
        Delete a system by its tag and re-tag all remaining systems sequentially.
        
        Args:
            tag (int): The tag of the system to delete
        """
        if tag in cls._created_systems:
            del cls._created_systems[tag]
            cls._reassign_tags()


class FullGeneralSystem(System):
    """
    Full general system, is NOT optimized, uses all the matrix
    """
    def __init__(self):
        super().__init__("FullGeneral")
    
    def to_tcl(self) -> str:
        return "system FullGeneral"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {}


class BandGeneralSystem(System):
    """
    Band general system, uses banded matrix storage
    """
    def __init__(self):
        super().__init__("BandGeneral")
    
    def to_tcl(self) -> str:
        return "system BandGeneral"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {}


class BandSPDSystem(System):
    """
    Band SPD system, for symmetric positive definite matrices, uses banded profile storage
    """
    def __init__(self):
        super().__init__("BandSPD")
    
    def to_tcl(self) -> str:
        return "system BandSPD"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {}


class ProfileSPDSystem(System):
    """
    Profile SPD system, for symmetric positive definite matrices, uses skyline storage
    """
    def __init__(self):
        super().__init__("ProfileSPD")
    
    def to_tcl(self) -> str:
        return "system ProfileSPD"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {}


class SuperLUSystem(System):
    """
    SuperLU system, sparse system solver
    """
    def __init__(self):
        super().__init__("SuperLU")
    
    def to_tcl(self) -> str:
        return "system SuperLU"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {}


class UmfpackSystem(System):
    """
    Umfpack system, sparse system solver
    """
    def __init__(self, lvalue_fact: Optional[float] = None):
        super().__init__("Umfpack")
        self.lvalue_fact = lvalue_fact
    
    def to_tcl(self) -> str:
        cmd = "system Umfpack"
        if self.lvalue_fact is not None:
            cmd += f" -lvalueFact {self.lvalue_fact}"
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {
            "lvalue_fact": self.lvalue_fact
        }


class MumpsSystem(System):
    """
    Mumps system, sparse direct solver
    """
    def __init__(self, icntl14: Optional[float] = None, icntl7: Optional[int] = None):
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
        super().__init__("Mumps")
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
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        return {
            "icntl14": self.icntl14,
            "icntl7": self.icntl7
        }


class SystemManager:
    """
    Singleton class for managing systems
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemManager, cls).__new__(cls)
        return cls._instance

    def create_system(self, system_type: str, **kwargs) -> System:
        """Create a new system"""
        return System.create_system(system_type, **kwargs)

    def get_system(self, tag: int) -> System:
        """Get system by tag"""
        return System.get_system(tag)

    def remove_system(self, tag: int) -> None:
        """Remove system by tag"""
        System.remove_system(tag)

    def get_all_systems(self) -> Dict[int, System]:
        """Get all systems"""
        return System.get_all_systems()

    def get_available_types(self) -> List[str]:
        """Get list of available system types"""
        return System.get_available_types()
    
    def clear_all(self):
        """Clear all systems"""  
        System.clear_all()


# Register all systems
System.register_system('fullgeneral', FullGeneralSystem)
System.register_system('bandgeneral', BandGeneralSystem)
System.register_system('bandspd', BandSPDSystem)
System.register_system('profilespd', ProfileSPDSystem)
System.register_system('superlu', SuperLUSystem)
System.register_system('umfpack', UmfpackSystem)
System.register_system('mumps', MumpsSystem)