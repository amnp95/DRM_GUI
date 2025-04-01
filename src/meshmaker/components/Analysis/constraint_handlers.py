from typing import List, Dict, Optional, Union, Type
from .base import AnalysisComponent

class ConstraintHandler(AnalysisComponent):
    """
    Base abstract class for constraint handlers, which determine how the constraint equations are enforced
    in the system of equations
    """
    _handlers = {}  # Class-level dictionary to store handler types
    
    @staticmethod
    def register_handler(name: str, handler_class: Type['ConstraintHandler']):
        """Register a constraint handler type"""
        ConstraintHandler._handlers[name.lower()] = handler_class
    
    @staticmethod
    def create_handler(handler_type: str, **kwargs) -> 'ConstraintHandler':
        """Create a constraint handler of the specified type"""
        handler_type = handler_type.lower()
        if handler_type not in ConstraintHandler._handlers:
            raise ValueError(f"Unknown constraint handler type: {handler_type}")
        return ConstraintHandler._handlers[handler_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available constraint handler types"""
        return list(ConstraintHandler._handlers.keys())


class PlainConstraintHandler(ConstraintHandler):
    """
    Plain constraint handler, does not follow the constraint definitions across the model evolution
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "constraints Plain"


class TransformationConstraintHandler(ConstraintHandler):
    """
    Transformation constraint handler, performs static condensation of the constraint degrees of freedom
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "constraints Transformation"


class PenaltyConstraintHandler(ConstraintHandler):
    """
    Penalty constraint handler, uses penalty numbers to enforce constraints
    """
    def __init__(self, alpha_s: float, alpha_m: float):
        self.alpha_s = alpha_s
        self.alpha_m = alpha_m
    
    def to_tcl(self) -> str:
        return f"constraints Penalty {self.alpha_s} {self.alpha_m}"


class LagrangeConstraintHandler(ConstraintHandler):
    """
    Lagrange multipliers constraint handler, uses Lagrange multipliers to enforce constraints
    """
    def __init__(self, alpha_s: float = 1.0, alpha_m: float = 1.0):
        self.alpha_s = alpha_s
        self.alpha_m = alpha_m
    
    def to_tcl(self) -> str:
        return f"constraints Lagrange {self.alpha_s} {self.alpha_m}"


class AutoConstraintHandler(ConstraintHandler):
    """
    Automatic constraint handler, automatically selects the penalty value for compatibility constraints
    """
    def __init__(self, verbose: bool = False, auto_penalty: Optional[float] = None, 
                 user_penalty: Optional[float] = None):
        self.verbose = verbose
        self.auto_penalty = auto_penalty
        self.user_penalty = user_penalty
    
    def to_tcl(self) -> str:
        cmd = "constraints Auto"
        if self.verbose:
            cmd += " -verbose"
        if self.auto_penalty is not None:
            cmd += f" -autoPenalty {self.auto_penalty}"
        if self.user_penalty is not None:
            cmd += f" -userPenalty {self.user_penalty}"
        return cmd


# Register all constraint handlers
ConstraintHandler.register_handler('plain', PlainConstraintHandler)
ConstraintHandler.register_handler('transformation', TransformationConstraintHandler)
ConstraintHandler.register_handler('penalty', PenaltyConstraintHandler)
ConstraintHandler.register_handler('lagrange', LagrangeConstraintHandler)
ConstraintHandler.register_handler('auto', AutoConstraintHandler)