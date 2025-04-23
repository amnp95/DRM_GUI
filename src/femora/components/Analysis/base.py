from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union, Type, Any

class AnalysisComponent(ABC):
    """
    Base abstract class for all analysis components.
    """
    @abstractmethod
    def to_tcl(self) -> str:
        """
        Convert the component to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        pass