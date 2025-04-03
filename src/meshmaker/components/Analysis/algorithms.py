from typing import List, Dict, Optional, Union, Type
from .base import AnalysisComponent
from abc import abstractmethod

class Algorithm(AnalysisComponent):
    """
    Base abstract class for algorithms, which determine how the constraint equations are enforced
    in the system of equations
    """
    _algorithms = {}  # Class-level dictionary to store algorithm types
    _created_algorithms = {}  # Class-level dictionary to track all created algorithms
    _next_tag = 1  # Class variable to track the next tag to assign
    
    def __init__(self, algorithm_type: str):
        """
        Initialize an algorithm
        
        Args:
            algorithm_type (str): Type of the algorithm
        """
        self.tag = Algorithm._next_tag
        Algorithm._next_tag += 1
        self.algorithm_type = algorithm_type
        
        # Register this algorithm in the class-level tracking dictionary
        Algorithm._created_algorithms[self.tag] = self
    
    @staticmethod
    def register_algorithm(name: str, algorithm_class: Type['Algorithm']):
        """Register an algorithm type"""
        Algorithm._algorithms[name.lower()] = algorithm_class
    
    @staticmethod
    def create_algorithm(algorithm_type: str, **kwargs) -> 'Algorithm':
        """Create an algorithm of the specified type"""
        algorithm_type = algorithm_type.lower()
        if algorithm_type not in Algorithm._algorithms:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")
        return Algorithm._algorithms[algorithm_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available algorithm types"""
        return list(Algorithm._algorithms.keys())
    
    @classmethod
    def get_algorithm(cls, tag: int) -> 'Algorithm':
        """
        Retrieve a specific algorithm by its tag.
        
        Args:
            tag (int): The tag of the algorithm
        
        Returns:
            Algorithm: The algorithm with the specified tag
        
        Raises:
            KeyError: If no algorithm with the given tag exists
        """
        if tag not in cls._created_algorithms:
            raise KeyError(f"No algorithm found with tag {tag}")
        return cls._created_algorithms[tag]

    @classmethod
    def get_all_algorithms(cls) -> Dict[int, 'Algorithm']:
        """
        Retrieve all created algorithms.
        
        Returns:
            Dict[int, Algorithm]: A dictionary of all algorithms, keyed by their unique tags
        """
        return cls._created_algorithms
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all algorithms and reset tags.
        """
        cls._created_algorithms.clear()
        cls._next_tag = 1
    
    @abstractmethod
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        pass

    @classmethod
    def _reassign_tags(cls) -> None:
        """
        Reassign tags to all algorithms sequentially starting from 1.
        """
        new_algorithms = {}
        for idx, algorithm in enumerate(sorted(cls._created_algorithms.values(), key=lambda h: h.tag), start=1):
            algorithm.tag = idx
            new_algorithms[idx] = algorithm
        cls._created_algorithms = new_algorithms
        cls._next_tag = len(cls._created_algorithms) + 1

    @classmethod
    def remove_algorithm(cls, tag: int) -> None:
        """
        Delete an algorithm by its tag and re-tag all remaining algorithms sequentially.
        
        Args:
            tag (int): The tag of the algorithm to delete
        """
        if tag in cls._created_algorithms:
            del cls._created_algorithms[tag]
            cls._reassign_tags()


class LinearAlgorithm(Algorithm):
    """
    Linear algorithm which takes one iteration to solve the system of equations
    """
    def __init__(self, initial: bool = False, factor_once: bool = False):
        """
        Initialize a Linear algorithm
        
        Args:
            initial (bool): Flag to use initial stiffness
            factor_once (bool): Flag to only set up and factor matrix once
        """
        super().__init__("Linear")
        self.initial = initial
        self.factor_once = factor_once
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "algorithm Linear"
        if self.initial:
            cmd += " -initial"
        if self.factor_once:
            cmd += " -factorOnce"
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "initial": self.initial,
            "factor_once": self.factor_once
        }


class NewtonAlgorithm(Algorithm):
    """
    Newton algorithm uses the Newton-Raphson method to solve the nonlinear residual equation
    """
    def __init__(self, initial: bool = False, initial_then_current: bool = False):
        """
        Initialize a Newton algorithm
        
        Args:
            initial (bool): Flag to use initial stiffness
            initial_then_current (bool): Flag to use initial stiffness on first step and then current stiffness
        """
        super().__init__("Newton")
        self.initial = initial
        self.initial_then_current = initial_then_current
        
        # Check for incompatible options
        if self.initial and self.initial_then_current:
            raise ValueError("Cannot specify both -initial and -initialThenCurrent flags")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "algorithm Newton"
        if self.initial:
            cmd += " -initial"
        if self.initial_then_current:
            cmd += " -initialThenCurrent"
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "initial": self.initial,
            "initial_then_current": self.initial_then_current
        }


class ModifiedNewtonAlgorithm(Algorithm):
    """
    Modified Newton algorithm uses the modified Newton-Raphson algorithm to solve the nonlinear residual equation
    """
    def __init__(self, initial: bool = False, factor_once: bool = False):
        """
        Initialize a Modified Newton algorithm
        
        Args:
            initial (bool): Flag to use initial stiffness iterations
            factor_once (bool): Flag to factor matrix only once
        """
        super().__init__("ModifiedNewton")
        self.initial = initial
        self.factor_once = factor_once
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "algorithm ModifiedNewton"
        if self.initial:
            cmd += " -initial"
        if self.factor_once:
            cmd += " -factorOnce"
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "initial": self.initial,
            "factor_once": self.factor_once
        }


class NewtonLineSearchAlgorithm(Algorithm):
    """
    Newton Line Search algorithm introduces line search to the Newton-Raphson algorithm
    """
    def __init__(self, type_search: str = "InitialInterpolated", tol: float = 0.8, 
                 max_iter: int = 10, min_eta: float = 0.1, max_eta: float = 10.0):
        """
        Initialize a Newton Line Search algorithm
        
        Args:
            type_search (str): Line search algorithm type
            tol (float): Tolerance for search
            max_iter (int): Maximum number of iterations to try
            min_eta (float): Minimum η value
            max_eta (float): Maximum η value
        """
        super().__init__("NewtonLineSearch")
        self.type_search = type_search
        self.tol = tol
        self.max_iter = max_iter
        self.min_eta = min_eta
        self.max_eta = max_eta
        
        # Validate search type
        valid_search_types = ["Bisection", "Secant", "RegulaFalsi", "InitialInterpolated"]
        if self.type_search not in valid_search_types:
            raise ValueError(f"Invalid search type: {self.type_search}. "
                           f"Valid types are: {', '.join(valid_search_types)}")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = f"algorithm NewtonLineSearch -type {self.type_search}"
        
        # Add other parameters if they're not default values
        if self.tol != 0.8:
            cmd += f" -tol {self.tol}"
        if self.max_iter != 10:
            cmd += f" -maxIter {self.max_iter}"
        if self.min_eta != 0.1:
            cmd += f" -minEta {self.min_eta}"
        if self.max_eta != 10.0:
            cmd += f" -maxEta {self.max_eta}"
            
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "type_search": self.type_search,
            "tol": self.tol,
            "max_iter": self.max_iter,
            "min_eta": self.min_eta,
            "max_eta": self.max_eta
        }


class KrylovNewtonAlgorithm(Algorithm):
    """
    Krylov-Newton algorithm uses a modified Newton method with Krylov subspace acceleration
    """
    def __init__(self, tang_iter: str = "current", tang_incr: str = "current", max_dim: int = 3):
        """
        Initialize a Krylov-Newton algorithm
        
        Args:
            tang_iter (str): Tangent to iterate on
            tang_incr (str): Tangent to increment on
            max_dim (int): Max number of iterations until tangent is reformed
        """
        super().__init__("KrylovNewton")
        self.tang_iter = tang_iter
        self.tang_incr = tang_incr
        self.max_dim = max_dim
        
        # Validate tangent options
        valid_tangent_options = ["current", "initial", "noTangent"]
        if self.tang_iter not in valid_tangent_options:
            raise ValueError(f"Invalid tangent iteration type: {self.tang_iter}. "
                           f"Valid types are: {', '.join(valid_tangent_options)}")
        if self.tang_incr not in valid_tangent_options:
            raise ValueError(f"Invalid tangent increment type: {self.tang_incr}. "
                           f"Valid types are: {', '.join(valid_tangent_options)}")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "algorithm KrylovNewton"
        
        # Add parameters if they're not default values
        if self.tang_iter != "current":
            cmd += f" -iterate {self.tang_iter}"
        if self.tang_incr != "current":
            cmd += f" -increment {self.tang_incr}"
        if self.max_dim != 3:
            cmd += f" -maxDim {self.max_dim}"
            
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "tang_iter": self.tang_iter,
            "tang_incr": self.tang_incr,
            "max_dim": self.max_dim
        }


class SecantNewtonAlgorithm(Algorithm):
    """
    Secant Newton algorithm uses the two-term update to accelerate convergence
    """
    def __init__(self, tang_iter: str = "current", tang_incr: str = "current", max_dim: int = 3):
        """
        Initialize a Secant Newton algorithm
        
        Args:
            tang_iter (str): Tangent to iterate on
            tang_incr (str): Tangent to increment on
            max_dim (int): Max number of iterations until tangent is reformed
        """
        super().__init__("SecantNewton")
        self.tang_iter = tang_iter
        self.tang_incr = tang_incr
        self.max_dim = max_dim
        
        # Validate tangent options
        valid_tangent_options = ["current", "initial", "noTangent"]
        if self.tang_iter not in valid_tangent_options:
            raise ValueError(f"Invalid tangent iteration type: {self.tang_iter}. "
                           f"Valid types are: {', '.join(valid_tangent_options)}")
        if self.tang_incr not in valid_tangent_options:
            raise ValueError(f"Invalid tangent increment type: {self.tang_incr}. "
                           f"Valid types are: {', '.join(valid_tangent_options)}")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "algorithm SecantNewton"
        
        # Add parameters if they're not default values
        if self.tang_iter != "current":
            cmd += f" -iterate {self.tang_iter}"
        if self.tang_incr != "current":
            cmd += f" -increment {self.tang_incr}"
        if self.max_dim != 3:
            cmd += f" -maxDim {self.max_dim}"
            
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "tang_iter": self.tang_iter,
            "tang_incr": self.tang_incr,
            "max_dim": self.max_dim
        }


class BFGSAlgorithm(Algorithm):
    """
    BFGS algorithm performs successive rank-two updates of the tangent (for symmetric systems)
    """
    def __init__(self, count: int):
        """
        Initialize a BFGS algorithm
        
        Args:
            count (int): Number of iterations before reforming tangent
        """
        super().__init__("BFGS")
        self.count = count
        
        # Validate count
        if not isinstance(self.count, int) or self.count < 1:
            raise ValueError("Count must be a positive integer")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"algorithm BFGS {self.count}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "count": self.count
        }


class BroydenAlgorithm(Algorithm):
    """
    Broyden algorithm performs successive rank-one updates of the tangent (for general unsymmetric systems)
    """
    def __init__(self, count: int):
        """
        Initialize a Broyden algorithm
        
        Args:
            count (int): Number of iterations before reforming tangent
        """
        super().__init__("Broyden")
        self.count = count
        
        # Validate count
        if not isinstance(self.count, int) or self.count < 1:
            raise ValueError("Count must be a positive integer")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"algorithm Broyden {self.count}"
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "count": self.count
        }


class ExpressNewtonAlgorithm(Algorithm):
    """
    ExpressNewton algorithm accepts the solution after a constant number of iterations
    """
    def __init__(self, iter_count: int = 2, k_multiplier: float = 1.0, 
                 initial_tangent: bool = False, current_tangent: bool = True, 
                 factor_once: bool = False):
        """
        Initialize an ExpressNewton algorithm
        
        Args:
            iter_count (int): Constant number of iterations
            k_multiplier (float): Multiplier to system stiffness
            initial_tangent (bool): Flag to use initial stiffness
            current_tangent (bool): Flag to use current stiffness
            factor_once (bool): Flag to factorize system matrix only once
        """
        super().__init__("ExpressNewton")
        self.iter_count = iter_count
        self.k_multiplier = k_multiplier
        self.initial_tangent = initial_tangent
        self.current_tangent = current_tangent
        self.factor_once = factor_once
        
        # Validate iter_count
        if not isinstance(self.iter_count, int) or self.iter_count < 1:
            raise ValueError("Iteration count must be a positive integer")
        
        # Check for incompatible options
        if self.initial_tangent and self.current_tangent:
            raise ValueError("Cannot specify both -initialTangent and -currentTangent flags")
    
    def to_tcl(self) -> str:
        """
        Convert the algorithm to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = f"algorithm ExpressNewton {self.iter_count} {self.k_multiplier}"
        
        # Add optional flags
        if self.initial_tangent:
            cmd += " -initialTangent"
        if self.current_tangent and not self.initial_tangent:
            cmd += " -currentTangent"
        if self.factor_once:
            cmd += " -factorOnce"
            
        return cmd
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this algorithm
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {
            "iter_count": self.iter_count,
            "k_multiplier": self.k_multiplier,
            "initial_tangent": self.initial_tangent,
            "current_tangent": self.current_tangent,
            "factor_once": self.factor_once
        }


class AlgorithmManager:
    """
    Singleton class for managing algorithms
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlgorithmManager, cls).__new__(cls)
        return cls._instance

    def create_algorithm(self, algorithm_type: str, **kwargs) -> Algorithm:
        """Create a new algorithm"""
        return Algorithm.create_algorithm(algorithm_type, **kwargs)

    def get_algorithm(self, tag: int) -> Algorithm:
        """Get algorithm by tag"""
        return Algorithm.get_algorithm(tag)

    def remove_algorithm(self, tag: int) -> None:
        """Remove algorithm by tag"""
        Algorithm.remove_algorithm(tag)

    def get_all_algorithms(self) -> Dict[int, Algorithm]:
        """Get all algorithms"""
        return Algorithm.get_all_algorithms()

    def get_available_types(self) -> List[str]:
        """Get list of available algorithm types"""
        return Algorithm.get_available_types()
    
    def clear_all(self):
        """Clear all algorithms"""  
        Algorithm.clear_all()


# Register all algorithms
Algorithm.register_algorithm('linear', LinearAlgorithm)
Algorithm.register_algorithm('newton', NewtonAlgorithm)
Algorithm.register_algorithm('modifiednewton', ModifiedNewtonAlgorithm)
Algorithm.register_algorithm('newtonlinesearch', NewtonLineSearchAlgorithm)
Algorithm.register_algorithm('krylovnewton', KrylovNewtonAlgorithm)
Algorithm.register_algorithm('secantnewton', SecantNewtonAlgorithm)
Algorithm.register_algorithm('bfgs', BFGSAlgorithm)
Algorithm.register_algorithm('broyden', BroydenAlgorithm)
Algorithm.register_algorithm('expressnewton', ExpressNewtonAlgorithm)