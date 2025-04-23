from typing import List, Dict, Optional, Union, Type
from .base import AnalysisComponent
from abc import ABC, abstractmethod


class Integrator(AnalysisComponent):
    """
    Base abstract class for integrators, which determine how displacement and resistance are updated
    in the nonlinear solution algorithms.
    """
    _integrators = {}  # Class-level dictionary to store integrator types
    _created_integrators = {}  # Class-level dictionary to track all created integrators
    _next_tag = 1  # Class variable to track the next tag to assign
    
    def __init__(self, integrator_type: str):
        """
        Initialize an integrator
        
        Args:
            integrator_type (str): Type of the integrator
        """
        self.tag = Integrator._next_tag
        Integrator._next_tag += 1
        self.integrator_type = integrator_type
        
        # Register this integrator in the class-level tracking dictionary
        Integrator._created_integrators[self.tag] = self
    
    @staticmethod
    def register_integrator(name: str, integrator_class: Type['Integrator']):
        """Register an integrator type"""
        Integrator._integrators[name.lower()] = integrator_class
    
    @staticmethod
    def create_integrator(integrator_type: str, **kwargs) -> 'Integrator':
        """Create an integrator of the specified type"""
        integrator_type = integrator_type.lower()
        if integrator_type not in Integrator._integrators:
            raise ValueError(f"Unknown integrator type: {integrator_type}")
        return Integrator._integrators[integrator_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available integrator types"""
        return list(Integrator._integrators.keys())
    
    @classmethod
    def get_integrator(cls, tag: int) -> 'Integrator':
        """
        Retrieve a specific integrator by its tag.
        
        Args:
            tag (int): The tag of the integrator
        
        Returns:
            Integrator: The integrator with the specified tag
        
        Raises:
            KeyError: If no integrator with the given tag exists
        """
        if tag not in cls._created_integrators:
            raise KeyError(f"No integrator found with tag {tag}")
        return cls._created_integrators[tag]

    @classmethod
    def get_all_integrators(cls) -> Dict[int, 'Integrator']:
        """
        Retrieve all created integrators.
        
        Returns:
            Dict[int, Integrator]: A dictionary of all integrators, keyed by their unique tags
        """
        return cls._created_integrators
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all integrators and reset tags.
        """
        cls._created_integrators.clear()
        cls._next_tag = 1
    
    @abstractmethod
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        pass

    @classmethod
    def _reassign_tags(cls) -> None:
        """
        Reassign tags to all integrators sequentially starting from 1.
        """
        new_integrators = {}
        for idx, integrator in enumerate(sorted(cls._created_integrators.values(), key=lambda i: i.tag), start=1):
            integrator.tag = idx
            new_integrators[idx] = integrator
        cls._created_integrators = new_integrators
        cls._next_tag = len(cls._created_integrators) + 1

    @classmethod
    def remove_integrator(cls, tag: int) -> None:
        """
        Delete an integrator by its tag and re-tag all remaining integrators sequentially.
        
        Args:
            tag (int): The tag of the integrator to delete
        """
        if tag in cls._created_integrators:
            del cls._created_integrators[tag]
            cls._reassign_tags()


class StaticIntegrator(Integrator):
    """
    Base abstract class for static integrators, used in static analysis
    """
    def __init__(self, integrator_type: str):
        super().__init__(integrator_type)
        
    @staticmethod
    def get_static_types() -> List[str]:
        """Get available static integrator types"""
        return [t for t, cls in Integrator._integrators.items() 
                if issubclass(cls, StaticIntegrator)]


class TransientIntegrator(Integrator):
    """
    Base abstract class for transient integrators, used in dynamic analysis
    """
    def __init__(self, integrator_type: str):
        super().__init__(integrator_type)
        
    @staticmethod
    def get_transient_types() -> List[str]:
        """Get available transient integrator types"""
        return [t for t, cls in Integrator._integrators.items() 
                if issubclass(cls, TransientIntegrator)]

#------------------------------------------------------
# Static Integrators
#------------------------------------------------------

class LoadControlIntegrator(StaticIntegrator):
    """
    Load control integrator for static analysis
    """
    def __init__(self, incr: float, num_iter: int = 1, min_incr: Optional[float] = None, 
                 max_incr: Optional[float] = None):
        """
        Initialize a LoadControl integrator
        
        Args:
            incr (float): Load factor increment
            num_iter (int, optional): Number of iterations user would like to occur in solution algorithm. Default is 1.
            min_incr (float, optional): Min stepsize the user will allow. Default is incr.
            max_incr (float, optional): Max stepsize the user will allow. Default is incr.
        """
        super().__init__("LoadControl")
        self.incr = incr
        self.num_iter = num_iter
        self.min_incr = min_incr if min_incr is not None else incr
        self.max_incr = max_incr if max_incr is not None else incr
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator LoadControl {self.incr} {self.num_iter} {self.min_incr} {self.max_incr}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "incr": self.incr,
            "num_iter": self.num_iter,
            "min_incr": self.min_incr,
            "max_incr": self.max_incr
        }


class DisplacementControlIntegrator(StaticIntegrator):
    """
    Displacement control integrator for static analysis
    """
    def __init__(self, node_tag: int, dof: int, incr: float, num_iter: int = 1, 
                 min_incr: Optional[float] = None, max_incr: Optional[float] = None):
        """
        Initialize a DisplacementControl integrator
        
        Args:
            node_tag (int): Tag of node whose response controls solution
            dof (int): Degree of freedom at the node, 1 through ndf
            incr (float): First displacement increment
            num_iter (int, optional): Number of iterations user would like to occur. Default is 1.
            min_incr (float, optional): Min stepsize the user will allow. Default is incr.
            max_incr (float, optional): Max stepsize the user will allow. Default is incr.
        """
        super().__init__("DisplacementControl")
        self.node_tag = node_tag
        self.dof = dof
        self.incr = incr
        self.num_iter = num_iter
        self.min_incr = min_incr if min_incr is not None else incr
        self.max_incr = max_incr if max_incr is not None else incr
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator DisplacementControl {self.node_tag} {self.dof} {self.incr} {self.num_iter} {self.min_incr} {self.max_incr}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "node_tag": self.node_tag,
            "dof": self.dof,
            "incr": self.incr,
            "num_iter": self.num_iter,
            "min_incr": self.min_incr,
            "max_incr": self.max_incr
        }


class ParallelDisplacementControlIntegrator(StaticIntegrator):
    """
    Parallel displacement control integrator for static analysis in parallel processing
    """
    def __init__(self, node_tag: int, dof: int, incr: float, num_iter: int = 1, 
                 min_incr: Optional[float] = None, max_incr: Optional[float] = None):
        """
        Initialize a ParallelDisplacementControl integrator
        
        Args:
            node_tag (int): Tag of node whose response controls solution
            dof (int): Degree of freedom at the node, 1 through ndf
            incr (float): First displacement increment
            num_iter (int, optional): Number of iterations user would like to occur. Default is 1.
            min_incr (float, optional): Min stepsize the user will allow. Default is incr.
            max_incr (float, optional): Max stepsize the user will allow. Default is incr.
        """
        super().__init__("ParallelDisplacementControl")
        self.node_tag = node_tag
        self.dof = dof
        self.incr = incr
        self.num_iter = num_iter
        self.min_incr = min_incr if min_incr is not None else incr
        self.max_incr = max_incr if max_incr is not None else incr
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator ParallelDisplacementControl {self.node_tag} {self.dof} {self.incr} {self.num_iter} {self.min_incr} {self.max_incr}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "node_tag": self.node_tag,
            "dof": self.dof,
            "incr": self.incr,
            "num_iter": self.num_iter,
            "min_incr": self.min_incr,
            "max_incr": self.max_incr
        }


class MinUnbalDispNormIntegrator(StaticIntegrator):
    """
    Minimum Unbalanced Displacement Norm integrator for static analysis
    """
    def __init__(self, dlambda1: float, jd: int = 1, min_lambda: Optional[float] = None, 
                 max_lambda: Optional[float] = None, det: bool = False):
        """
        Initialize a MinUnbalDispNorm integrator
        
        Args:
            dlambda1 (float): First load increment (pseudo-time step)
            jd (int, optional): Factor relating first load increment at subsequent time steps. Default is 1.
            min_lambda (float, optional): Min load increment. Default is dlambda1.
            max_lambda (float, optional): Max load increment. Default is dlambda1.
            det (bool, optional): Flag to use determinant of tangent. Default is False.
        """
        super().__init__("MinUnbalDispNorm")
        self.dlambda1 = dlambda1
        self.jd = jd
        self.min_lambda = min_lambda if min_lambda is not None else dlambda1
        self.max_lambda = max_lambda if max_lambda is not None else dlambda1
        self.det = det
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        det_str = " -det" if self.det else ""
        return f"integrator MinUnbalDispNorm {self.dlambda1} {self.jd} {self.min_lambda} {self.max_lambda}{det_str}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "dlambda1": self.dlambda1,
            "jd": self.jd,
            "min_lambda": self.min_lambda,
            "max_lambda": self.max_lambda,
            "det": self.det
        }


class ArcLengthIntegrator(StaticIntegrator):
    """
    Arc-Length Control integrator for static analysis
    """
    def __init__(self, s: float, alpha: float):
        """
        Initialize an ArcLength integrator
        
        Args:
            s (float): The arcLength
            alpha (float): A scaling factor on the reference loads
        """
        super().__init__("ArcLength")
        self.s = s
        self.alpha = alpha
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator ArcLength {self.s} {self.alpha}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "s": self.s,
            "alpha": self.alpha
        }


#------------------------------------------------------
# Transient Integrators
#------------------------------------------------------

class CentralDifferenceIntegrator(TransientIntegrator):
    """
    Central Difference integrator for dynamic analysis
    """
    def __init__(self):
        """
        Initialize a CentralDifference integrator
        """
        super().__init__("CentralDifference")
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return "integrator CentralDifference"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {}


class NewmarkIntegrator(TransientIntegrator):
    """
    Newmark Method integrator for dynamic analysis
    """
    def __init__(self, gamma: float, beta: float, form: str = "D"):
        """
        Initialize a Newmark integrator
        
        Args:
            gamma (float): Gamma factor
            beta (float): Beta factor
            form (str, optional): Flag to indicate primary variable: 'D' (displacement, default), 
                                'V' (velocity), or 'A' (acceleration)
        """
        super().__init__("Newmark")
        self.gamma = gamma
        self.beta = beta
        if form not in ["D", "V", "A"]:
            raise ValueError("form must be one of 'D', 'V', or 'A'")
        self.form = form
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        if self.form == "D":
            return f"integrator Newmark {self.gamma} {self.beta}"
        else:
            return f"integrator Newmark {self.gamma} {self.beta} -form {self.form}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "gamma": self.gamma,
            "beta": self.beta,
            "form": self.form
        }


class HHTIntegrator(TransientIntegrator):
    """
    Hilber-Hughes-Taylor Method integrator for dynamic analysis
    """
    def __init__(self, alpha: float, gamma: Optional[float] = None, beta: Optional[float] = None):
        """
        Initialize a HHT integrator
        
        Args:
            alpha (float): Alpha factor
            gamma (float, optional): Gamma factor. Default is 1.5 - alpha.
            beta (float, optional): Beta factor. Default is (2-alpha)^2/4.
        """
        super().__init__("HHT")
        self.alpha = alpha
        # Default values if not provided
        if gamma is None:
            self.gamma = 1.5 - alpha
        else:
            self.gamma = gamma
            
        if beta is None:
            self.beta = ((2.0 - alpha) ** 2) / 4.0
        else:
            self.beta = beta
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator HHT {self.alpha} {self.gamma} {self.beta}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "beta": self.beta
        }


class GeneralizedAlphaIntegrator(TransientIntegrator):
    """
    Generalized Alpha Method integrator for dynamic analysis
    """
    def __init__(self, alpha_m: float, alpha_f: float, gamma: Optional[float] = None, 
                 beta: Optional[float] = None):
        """
        Initialize a GeneralizedAlpha integrator
        
        Args:
            alpha_m (float): Alpha_m factor
            alpha_f (float): Alpha_f factor
            gamma (float, optional): Gamma factor. Default is 0.5 + alpha_m - alpha_f.
            beta (float, optional): Beta factor. Default is (1 + alpha_m - alpha_f)^2/4.
        """
        super().__init__("GeneralizedAlpha")
        self.alpha_m = alpha_m
        self.alpha_f = alpha_f
        
        # Default values if not provided
        if gamma is None:
            self.gamma = 0.5 + alpha_m - alpha_f
        else:
            self.gamma = gamma
            
        if beta is None:
            self.beta = ((1.0 + alpha_m - alpha_f) ** 2) / 4.0
        else:
            self.beta = beta
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator GeneralizedAlpha {self.alpha_m} {self.alpha_f} {self.gamma} {self.beta}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "alpha_m": self.alpha_m,
            "alpha_f": self.alpha_f,
            "gamma": self.gamma,
            "beta": self.beta
        }


class TRBDF2Integrator(TransientIntegrator):
    """
    TRBDF2 integrator for dynamic analysis
    """
    def __init__(self):
        """
        Initialize a TRBDF2 integrator
        """
        super().__init__("TRBDF2")
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return "integrator TRBDF2"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {}


class ExplicitDifferenceIntegrator(TransientIntegrator):
    """
    Explicit Difference integrator for dynamic analysis
    """
    def __init__(self):
        """
        Initialize an ExplicitDifference integrator
        """
        super().__init__("ExplicitDifference")
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return "integrator ExplicitDifference"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {}


class PFEMIntegrator(TransientIntegrator):
    """
    PFEM integrator for fluid-structure interaction analysis
    """
    def __init__(self, gamma: float = 0.5, beta: float = 0.25):
        """
        Initialize a PFEM integrator
        
        Args:
            gamma (float, optional): Gamma factor. Default is 0.5.
            beta (float, optional): Beta factor. Default is 0.25.
        """
        super().__init__("PFEM")
        self.gamma = gamma
        self.beta = beta
    
    def to_tcl(self) -> str:
        """
        Convert the integrator to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"integrator PFEM {self.gamma} {self.beta}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool, list]]:
        """
        Get the parameters defining this integrator
        
        Returns:
            Dict[str, Union[str, int, float, bool, list]]: Dictionary of parameter values
        """
        return {
            "gamma": self.gamma,
            "beta": self.beta
        }


class IntegratorManager:
    """
    Singleton class for managing integrators
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IntegratorManager, cls).__new__(cls)
        return cls._instance

    def create_integrator(self, integrator_type: str, **kwargs) -> Integrator:
        """Create a new integrator"""
        return Integrator.create_integrator(integrator_type, **kwargs)

    def get_integrator(self, tag: int) -> Integrator:
        """Get integrator by tag"""
        return Integrator.get_integrator(tag)

    def remove_integrator(self, tag: int) -> None:
        """Remove integrator by tag"""
        Integrator.remove_integrator(tag)

    def get_all_integrators(self) -> Dict[int, Integrator]:
        """Get all integrators"""
        return Integrator.get_all_integrators()

    def get_available_types(self) -> List[str]:
        """Get list of available integrator types"""
        return Integrator.get_available_types()
    
    def get_static_types(self) -> List[str]:
        """Get list of available static integrator types"""
        return StaticIntegrator.get_static_types()
    
    def get_transient_types(self) -> List[str]:
        """Get list of available transient integrator types"""
        return TransientIntegrator.get_transient_types()
    
    def clear_all(self):
        """Clear all integrators"""  
        Integrator.clear_all()


# Register all integrators
Integrator.register_integrator('loadcontrol', LoadControlIntegrator)
Integrator.register_integrator('displacementcontrol', DisplacementControlIntegrator)
Integrator.register_integrator('paralleldisplacementcontrol', ParallelDisplacementControlIntegrator)
Integrator.register_integrator('minunbaldispnorm', MinUnbalDispNormIntegrator)
Integrator.register_integrator('arclength', ArcLengthIntegrator)
Integrator.register_integrator('centraldifference', CentralDifferenceIntegrator)
Integrator.register_integrator('newmark', NewmarkIntegrator)
Integrator.register_integrator('hht', HHTIntegrator)
Integrator.register_integrator('generalizedalpha', GeneralizedAlphaIntegrator)
Integrator.register_integrator('trbdf2', TRBDF2Integrator)
Integrator.register_integrator('explicitdifference', ExplicitDifferenceIntegrator)
Integrator.register_integrator('pfem', PFEMIntegrator)





