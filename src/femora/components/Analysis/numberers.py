from typing import List, Dict, Type
from .base import AnalysisComponent

class Numberer(AnalysisComponent):
    """
    Base abstract class for numberer, which determines the mapping between equation numbers and DOFs
    """
    _numberers = {}  # Class-level dictionary to store numberer types
    _numberer_instances = {}  # Class-level dictionary to store created numberer instances
    
    @staticmethod
    def register_numberer(name: str, numberer_class: Type['Numberer']):
        """Register a numberer type"""
        Numberer._numberers[name.lower()] = numberer_class
    
    @staticmethod
    def create_numberer(numberer_type: str, **kwargs) -> 'Numberer':
        """Create a numberer of the specified type"""
        numberer_type = numberer_type.lower()
        if numberer_type not in Numberer._numberers:
            raise ValueError(f"Unknown numberer type: {numberer_type}")
        
        # Create the numberer instance
        numberer = Numberer._numberers[numberer_type](**kwargs)
        
        # Store in class-level instances dictionary
        Numberer._numberer_instances[numberer_type] = numberer
        
        return numberer
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available numberer types"""
        return list(Numberer._numberers.keys())
    
    @staticmethod
    def get_instances() -> Dict[str, 'Numberer']:
        """Get all created numberer instances"""
        return Numberer._numberer_instances
    
    @staticmethod
    def get_instance(numberer_type: str) -> 'Numberer':
        """Get a specific numberer instance if it exists"""
        numberer_type = numberer_type.lower()
        if numberer_type not in Numberer._numberer_instances:
            return None
        return Numberer._numberer_instances[numberer_type]
    
    @staticmethod
    def reset_instances():
        """Clear all stored numberer instances"""
        Numberer._numberer_instances.clear()


class PlainNumberer(Numberer):
    """
    Plain numberer, assigns equation numbers to DOFs based on the order in which nodes are created
    Implemented as a singleton
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlainNumberer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer Plain"


class RCMNumberer(Numberer):
    """
    Reverse Cuthill-McKee numberer, designed to reduce the bandwidth of the system matrix
    Implemented as a singleton
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RCMNumberer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer RCM"


class AMDNumberer(Numberer):
    """
    Alternate Minimum Degree numberer, designed to minimize fill-in during matrix factorization
    Implemented as a singleton
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AMDNumberer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer AMD"


class ParallelRCMNumberer(Numberer):
    """
    Parallel Reverse Cuthill-McKee numberer, a parallelized version of the RCM algorithm
    for improved performance on large systems while still reducing bandwidth
    Implemented as a singleton
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParallelRCMNumberer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer ParallelRCM"


class NumbererManager:
    """
    Manager class for handling numberer instances and operations
    Implemented as a singleton
    """
    _instance = None
    _numberer_instances = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NumbererManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Initialize by creating all three numberer instances if they don't exist
        if not NumbererManager._numberer_instances:
            self._initialize_default_numberers()
    
    def _initialize_default_numberers(self):
        """
        Automatically create instances of the default numberer types
        """
        self.get_numberer('plain')
        self.get_numberer('rcm')
        self.get_numberer('amd')
        self.get_numberer('parallelrcm')
    
    @classmethod
    def get_instance(cls) -> 'NumbererManager':
        """
        Get the singleton instance of NumbererManager
        """
        if cls._instance is None:
            cls._instance = NumbererManager()
        return cls._instance
    
    def get_numberer(self, numberer_type: str) -> Numberer:
        """
        Get a numberer instance of the specified type
        Reuses existing instances (singleton pattern)
        """
        numberer_type = numberer_type.lower()
        
        # Check if the numberer already exists in Numberer class
        existing_numberer = Numberer.get_instance(numberer_type)
        if existing_numberer:
            # Update manager's instance dictionary if needed
            NumbererManager._numberer_instances[numberer_type] = existing_numberer
            return existing_numberer
            
        # Create new numberer if not found
        if numberer_type not in NumbererManager._numberer_instances:
            NumbererManager._numberer_instances[numberer_type] = Numberer.create_numberer(numberer_type)
            
        return NumbererManager._numberer_instances[numberer_type]
    

    def create_numberer(self, numberer_type: str) -> Numberer:
        """
        Create a new numberer instance of the specified type
        """
        return self.get_numberer(numberer_type)  # Ensure the numberer is created if not already
        
    
    def get_all_numberers(self) -> Dict[str, Numberer]:
        """
        Return all available numberer instances
        """
        for numberer_type in Numberer.get_available_types():
            self.get_numberer(numberer_type)
        return NumbererManager._numberer_instances
    
    def reset(self):
        """
        Clear all cached numberer instances
        """
        NumbererManager._numberer_instances.clear()
        Numberer.reset_instances()


# Register all numberers
Numberer.register_numberer('plain', PlainNumberer)
Numberer.register_numberer('rcm', RCMNumberer)
Numberer.register_numberer('amd', AMDNumberer)
Numberer.register_numberer('parallelrcm', ParallelRCMNumberer)