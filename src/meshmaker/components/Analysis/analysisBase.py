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


class Numberer(AnalysisComponent):
    """
    Base abstract class for numberer, which determines the mapping between equation numbers and DOFs
    """
    _numberers = {}  # Class-level dictionary to store numberer types
    
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
        return Numberer._numberers[numberer_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available numberer types"""
        return list(Numberer._numberers.keys())


class PlainNumberer(Numberer):
    """
    Plain numberer, assigns equation numbers to DOFs based on the order in which nodes are created
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer Plain"


class RCMNumberer(Numberer):
    """
    Reverse Cuthill-McKee numberer, designed to reduce the bandwidth of the system matrix
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer RCM"


class AMDNumberer(Numberer):
    """
    Alternate Minimum Degree numberer, designed to minimize fill-in during matrix factorization
    """
    def __init__(self):
        pass
    
    def to_tcl(self) -> str:
        return "numberer AMD"


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


class Test(AnalysisComponent):
    """
    Base abstract class for convergence test, which determines if convergence has been achieved
    """
    _tests = {}  # Class-level dictionary to store test types
    
    @staticmethod
    def register_test(name: str, test_class: Type['Test']):
        """Register a test type"""
        Test._tests[name.lower()] = test_class
    
    @staticmethod
    def create_test(test_type: str, **kwargs) -> 'Test':
        """Create a test of the specified type"""
        test_type = test_type.lower()
        if test_type not in Test._tests:
            raise ValueError(f"Unknown test type: {test_type}")
        return Test._tests[test_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available test types"""
        return list(Test._tests.keys())


class NormUnbalanceTest(Test):
    """
    Norm unbalance test, checks the norm of the residual vector against a tolerance
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        return f"test NormUnbalance {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class NormDispIncrTest(Test):
    """
    Norm displacement increment test, checks the norm of the displacement increment vector against a tolerance
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        return f"test NormDispIncr {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class Algorithm(AnalysisComponent):
    """
    Base abstract class for algorithm, which determines the sequence of steps taken to solve the nonlinear equation
    """
    _algorithms = {}  # Class-level dictionary to store algorithm types
    
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


class LinearAlgorithm(Algorithm):
    """
    Linear algorithm, takes one iteration to solve the system
    """
    def __init__(self, initial: bool = False, factor_once: bool = False):
        self.initial = initial
        self.factor_once = factor_once
    
    def to_tcl(self) -> str:
        cmd = "algorithm Linear"
        if self.initial:
            cmd += " -initial"
        if self.factor_once:
            cmd += " -factorOnce"
        return cmd


class NewtonAlgorithm(Algorithm):
    """
    Newton-Raphson algorithm, uses tangent stiffness in each iteration
    """
    def __init__(self, initial: bool = False, initial_then_current: bool = False):
        self.initial = initial
        self.initial_then_current = initial_then_current
        
        if self.initial and self.initial_then_current:
            raise ValueError("Cannot use both -initial and -initialThenCurrent with Newton algorithm")
    
    def to_tcl(self) -> str:
        cmd = "algorithm Newton"
        if self.initial:
            cmd += " -initial"
        if self.initial_then_current:
            cmd += " -initialThenCurrent"
        return cmd


class ModifiedNewtonAlgorithm(Algorithm):
    """
    Modified Newton algorithm, uses the initial stiffness for all iterations
    """
    def __init__(self, initial: bool = False):
        self.initial = initial
    
    def to_tcl(self) -> str:
        cmd = "algorithm ModifiedNewton"
        if self.initial:
            cmd += " -initial"
        return cmd


class Integrator(AnalysisComponent):
    """
    Base abstract class for integrator, which determines the meaning of the terms in the system of equation
    """
    _integrators = {}  # Class-level dictionary to store integrator types
    
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


class LoadControlIntegrator(Integrator):
    """
    Load control integrator, specifies the load increment directly
    """
    def __init__(self, lambda_val: float, num_iter: Optional[int] = None, 
                 min_lambda: Optional[float] = None, max_lambda: Optional[float] = None):
        self.lambda_val = lambda_val
        self.num_iter = num_iter
        self.min_lambda = min_lambda
        self.max_lambda = max_lambda
    
    def to_tcl(self) -> str:
        cmd = f"integrator LoadControl {self.lambda_val}"
        if self.num_iter is not None:
            cmd += f" {self.num_iter}"
            if self.min_lambda is not None:
                cmd += f" {self.min_lambda}"
                if self.max_lambda is not None:
                    cmd += f" {self.max_lambda}"
        return cmd


class DisplacementControlIntegrator(Integrator):
    """
    Displacement control integrator, specifies the displacement increment directly
    """
    def __init__(self, node: int, dof: int, incr: float, num_iter: Optional[int] = None,
                 min_incr: Optional[float] = None, max_incr: Optional[float] = None):
        self.node = node
        self.dof = dof
        self.incr = incr
        self.num_iter = num_iter
        self.min_incr = min_incr
        self.max_incr = max_incr
    
    def to_tcl(self) -> str:
        cmd = f"integrator DisplacementControl {self.node} {self.dof} {self.incr}"
        if self.num_iter is not None:
            cmd += f" {self.num_iter}"
            if self.min_incr is not None:
                cmd += f" {self.min_incr}"
                if self.max_incr is not None:
                    cmd += f" {self.max_incr}"
        return cmd


class NewmarkIntegrator(Integrator):
    """
    Newmark integrator, for transient analysis, uses Newmark's method
    """
    def __init__(self, gamma: float, beta: float):
        self.gamma = gamma
        self.beta = beta
    
    def to_tcl(self) -> str:
        return f"integrator Newmark {self.gamma} {self.beta}"


class GeneralizedAlphaIntegrator(Integrator):
    """
    Generalized alpha integrator, for transient analysis, uses the generalized alpha method
    """
    def __init__(self, alpha_m: float, alpha_f: float, gamma: Optional[float] = None, 
                 beta: Optional[float] = None):
        self.alpha_m = alpha_m
        self.alpha_f = alpha_f
        self.gamma = gamma
        self.beta = beta
    
    def to_tcl(self) -> str:
        cmd = f"integrator GeneralizedAlpha {self.alpha_m} {self.alpha_f}"
        if self.gamma is not None:
            cmd += f" {self.gamma}"
            if self.beta is not None:
                cmd += f" {self.beta}"
        return cmd


class Analysis:
    """
    Analysis class that combines all components and performs the analysis
    """
    _analyses = {}  # Class-level dictionary to store analysis objects
    _next_tag = 1   # Class variable to track the next tag to assign
    
    def __init__(self, name: str = None, analysis_type: str = None, constraint_handler: ConstraintHandler = None,
                 numberer: Numberer = None, system: System = None, test: Test = None,
                 algorithm: Algorithm = None, integrator: Integrator = None):
        """
        Initialize a new Analysis
        
        Args:
            name (str, optional): Name of the analysis
            analysis_type (str, optional): Type of analysis (Static, Transient, VariableTransient)
            constraint_handler (ConstraintHandler, optional): Constraint handler to use
            numberer (Numberer, optional): Numberer to use
            system (System, optional): System to use
            test (Test, optional): Test to use
            algorithm (Algorithm, optional): Algorithm to use
            integrator (Integrator, optional): Integrator to use
        """
        self.tag = Analysis._next_tag
        Analysis._next_tag += 1
        
        self.name = name or f"Analysis_{self.tag}"
        
        self.analysis_type = analysis_type
        self.constraint_handler = constraint_handler
        self.numberer = numberer
        self.system = system
        self.test = test
        self.algorithm = algorithm
        self.integrator = integrator
        
        Analysis._analyses[self.tag] = self
    
    @classmethod
    def get_analysis(cls, tag: int) -> 'Analysis':
        """
        Get an analysis by its tag
        
        Args:
            tag (int): The tag of the analysis
        
        Returns:
            Analysis: The analysis with the specified tag
        
        Raises:
            KeyError: If no analysis with the given tag exists
        """
        if tag not in cls._analyses:
            raise KeyError(f"No analysis found with tag {tag}")
        return cls._analyses[tag]
    
    @classmethod
    def get_all_analyses(cls) -> Dict[int, 'Analysis']:
        """
        Get all analyses
        
        Returns:
            Dict[int, Analysis]: A dictionary of all analyses, keyed by their tags
        """
        return cls._analyses
    
    @classmethod
    def remove_analysis(cls, tag: int) -> None:
        """
        Remove an analysis by its tag
        
        Args:
            tag (int): The tag of the analysis to remove
        """
        if tag in cls._analyses:
            del cls._analyses[tag]
    
    def set_type(self, analysis_type: str) -> None:
        """
        Set the analysis type
        
        Args:
            analysis_type (str): The analysis type (Static, Transient, VariableTransient)
        """
        if analysis_type not in ['Static', 'Transient', 'VariableTransient']:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        self.analysis_type = analysis_type
    
    def set_constraint_handler(self, handler_type: str, **kwargs) -> None:
        """
        Set the constraint handler
        
        Args:
            handler_type (str): The type of constraint handler
            **kwargs: Additional arguments for the constraint handler
        """
        self.constraint_handler = ConstraintHandler.create_handler(handler_type, **kwargs)
    
    def set_numberer(self, numberer_type: str, **kwargs) -> None:
        """
        Set the numberer
        
        Args:
            numberer_type (str): The type of numberer
            **kwargs: Additional arguments for the numberer
        """
        self.numberer = Numberer.create_numberer(numberer_type, **kwargs)
    
    def set_system(self, system_type: str, **kwargs) -> None:
        """
        Set the system
        
        Args:
            system_type (str): The type of system
            **kwargs: Additional arguments for the system
        """
        self.system = System.create_system(system_type, **kwargs)
    
    def set_test(self, test_type: str, *args, **kwargs) -> None:
        """
        Set the convergence test
        
        Args:
            test_type (str): The type of test
            *args: Positional arguments for the test
            **kwargs: Additional arguments for the test
        """
        # For convenience, handle common positional arguments for tests
        if test_type.lower() in ['normunbalance', 'normdispincr']:
            if len(args) >= 2:  # At minimum, we need tolerance and max iterations
                tol, max_iter = args[0:2]
                print_flag = args[2] if len(args) > 2 else kwargs.get('print_flag', 0)
                norm_type = args[3] if len(args) > 3 else kwargs.get('norm_type', 2)
                
                kwargs = {
                    'tol': tol,
                    'max_iter': max_iter,
                    'print_flag': print_flag,
                    'norm_type': norm_type
                }
            
        self.test = Test.create_test(test_type, **kwargs)
    
    def set_algorithm(self, algorithm_type: str, *args, **kwargs) -> None:
        """
        Set the algorithm
        
        Args:
            algorithm_type (str): The type of algorithm
            *args: Positional arguments representing flags
            **kwargs: Additional arguments for the algorithm
        """
        # Handle flags for algorithms that are often passed as strings
        if algorithm_type.lower() in ['linear', 'newton', 'modifiednewton']:
            for arg in args:
                if arg == '-initial':
                    kwargs['initial'] = True
                elif arg == '-factorOnce':
                    kwargs['factor_once'] = True
                elif arg == '-initialThenCurrent':
                    kwargs['initial_then_current'] = True
        
        self.algorithm = Algorithm.create_algorithm(algorithm_type, **kwargs)
    
    def set_integrator(self, integrator_type: str, *args, **kwargs) -> None:
        """
        Set the integrator
        
        Args:
            integrator_type (str): The type of integrator
            *args: Positional arguments for the integrator
            **kwargs: Additional arguments for the integrator
        """
        # For convenience, handle common positional arguments for integrators
        if integrator_type.lower() == 'loadcontrol':
            if len(args) >= 1:
                lambda_val = args[0]
                num_iter = args[1] if len(args) > 1 else None
                min_lambda = args[2] if len(args) > 2 else None
                max_lambda = args[3] if len(args) > 3 else None
                
                kwargs = {
                    'lambda_val': lambda_val,
                    'num_iter': num_iter,
                    'min_lambda': min_lambda,
                    'max_lambda': max_lambda
                }
                
        elif integrator_type.lower() == 'displacementcontrol':
            if len(args) >= 3:
                node = args[0]
                dof = args[1]
                incr = args[2]
                num_iter = args[3] if len(args) > 3 else None
                min_incr = args[4] if len(args) > 4 else None
                max_incr = args[5] if len(args) > 5 else None
                
                kwargs = {
                    'node': node,
                    'dof': dof,
                    'incr': incr,
                    'num_iter': num_iter,
                    'min_incr': min_incr,
                    'max_incr': max_incr
                }
                
        elif integrator_type.lower() == 'newmark':
            if len(args) >= 2:
                gamma = args[0]
                beta = args[1]
                
                kwargs = {
                    'gamma': gamma,
                    'beta': beta
                }
                
        elif integrator_type.lower() == 'generalizedalpha':
            if len(args) >= 2:
                alpha_m = args[0]
                alpha_f = args[1]
                gamma = args[2] if len(args) > 2 else None
                beta = args[3] if len(args) > 3 else None
                
                kwargs = {
                    'alpha_m': alpha_m,
                    'alpha_f': alpha_f,
                    'gamma': gamma,
                    'beta': beta
                }
        
        self.integrator = Integrator.create_integrator(integrator_type, **kwargs)
    
    def analyze(self, num_steps: int, dt: Optional[float] = None, num_sublevels: Optional[int] = None, 
                num_substeps: Optional[int] = None) -> bool:
        """
        Perform the analysis
        
        Args:
            num_steps (int): Number of analysis steps to perform
            dt (float, optional): Time step for transient analysis
            num_sublevels (int, optional): Number of sublevels for transient analysis
            num_substeps (int, optional): Number of substeps for transient analysis
        
        Returns:
            bool: True if the analysis was successful, False otherwise
        """
        # Validate that all components are set
        if not self.analysis_type:
            raise ValueError("Analysis type must be set")
        if not self.constraint_handler:
            raise ValueError("Constraint handler must be set")
        if not self.numberer:
            raise ValueError("Numberer must be set")
        if not self.system:
            raise ValueError("System must be set")
        if not self.test:
            raise ValueError("Test must be set")
        if not self.algorithm:
            raise ValueError("Algorithm must be set")
        if not self.integrator:
            raise ValueError("Integrator must be set")
        
        # Build the analysis commands
        commands = []
        
        # Add the components
        commands.append(self.constraint_handler.to_tcl())
        commands.append(self.numberer.to_tcl())
        commands.append(self.system.to_tcl())
        commands.append(self.test.to_tcl())
        commands.append(self.algorithm.to_tcl())
        commands.append(self.integrator.to_tcl())
        
        # Add the analysis command
        analysis_cmd = f"analysis {self.analysis_type}"
        if num_sublevels is not None:
            analysis_cmd += f" -numSublevels {num_sublevels}"
        if num_substeps is not None:
            analysis_cmd += f" -numSubSteps {num_substeps}"
        commands.append(analysis_cmd)
        
        # Add the analyze command
        if self.analysis_type == 'Static':
            commands.append(f"analyze {num_steps}")
        else:  # Transient or VariableTransient
            if dt is None:
                raise ValueError("Time step (dt) must be provided for transient analysis")
            commands.append(f"analyze {num_steps} {dt}")
        
        # TODO: Execute the commands (this would depend on how your application executes TCL commands)
        print("Analysis commands:")
        for cmd in commands:
            print(f"  {cmd}")
        
        return True  # Assuming success for now
    
    def __str__(self) -> str:
        """
        String representation of the analysis
        
        Returns:
            str: String representation
        """
        components = []
        if self.analysis_type:
            components.append(f"Type: {self.analysis_type}")
        if self.constraint_handler:
            components.append(f"Constraint Handler: {type(self.constraint_handler).__name__}")
        if self.numberer:
            components.append(f"Numberer: {type(self.numberer).__name__}")
        if self.system:
            components.append(f"System: {type(self.system).__name__}")
        if self.test:
            components.append(f"Test: {type(self.test).__name__}")
        if self.algorithm:
            components.append(f"Algorithm: {type(self.algorithm).__name__}")
        if self.integrator:
            components.append(f"Integrator: {type(self.integrator).__name__}")
        
        return f"Analysis '{self.name}' (Tag: {self.tag}):\n  " + "\n  ".join(components)


# Register all constraint handlers
ConstraintHandler.register_handler('plain', PlainConstraintHandler)
ConstraintHandler.register_handler('transformation', TransformationConstraintHandler)
ConstraintHandler.register_handler('penalty', PenaltyConstraintHandler)
ConstraintHandler.register_handler('lagrange', LagrangeConstraintHandler)
ConstraintHandler.register_handler('auto', AutoConstraintHandler)

# Register all numberers
Numberer.register_numberer('plain', PlainNumberer)
Numberer.register_numberer('rcm', RCMNumberer)
Numberer.register_numberer('amd', AMDNumberer)

# Register all systems
System.register_system('fullgeneral', FullGeneralSystem)
System.register_system('bandgeneral', BandGeneralSystem)
System.register_system('bandspd', BandSPDSystem)
System.register_system('profilespd', ProfileSPDSystem)
System.register_system('superlu', SuperLUSystem)
System.register_system('umfpack', UmfpackSystem)

# Register all tests
Test.register_test('normunbalance', NormUnbalanceTest)
Test.register_test('normdispincr', NormDispIncrTest)

# Register all algorithms
Algorithm.register_algorithm('linear', LinearAlgorithm)
Algorithm.register_algorithm('newton', NewtonAlgorithm)
Algorithm.register_algorithm('modifiednewton', ModifiedNewtonAlgorithm)

# Register all integrators
Integrator.register_integrator('loadcontrol', LoadControlIntegrator)
Integrator.register_integrator('displacementcontrol', DisplacementControlIntegrator)
Integrator.register_integrator('newmark', NewmarkIntegrator)
Integrator.register_integrator('generalizedalpha', GeneralizedAlphaIntegrator)


class AnalysisManager:
    """
    Singleton class for managing analyses
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalysisManager, cls).__new__(cls)
        return cls._instance

    def create_analysis(self, name: str = None, analysis_type: str = None, **kwargs) -> Analysis:
        """Create a new analysis"""
        return Analysis(name=name, analysis_type=analysis_type, **kwargs)

    def get_analysis(self, tag: int) -> Analysis:
        """Get analysis by tag"""
        return Analysis.get_analysis(tag)

    def remove_analysis(self, tag: int) -> None:
        """Remove analysis by tag"""
        Analysis.remove_analysis(tag)

    def get_all_analyses(self) -> Dict[int, Analysis]:
        """Get all analyses"""
        return Analysis.get_all_analyses()

    def get_available_constraint_handlers(self) -> List[str]:
        """Get list of available constraint handler types"""
        return ConstraintHandler.get_available_types()

    def get_available_numberers(self) -> List[str]:
        """Get list of available numberer types"""
        return Numberer.get_available_types()

    def get_available_systems(self) -> List[str]:
        """Get list of available system types"""
        return System.get_available_types()

    def get_available_tests(self) -> List[str]:
        """Get list of available test types"""
        return Test.get_available_types()

    def get_available_algorithms(self) -> List[str]:
        """Get list of available algorithm types"""
        return Algorithm.get_available_types()

    def get_available_integrators(self) -> List[str]:
        """Get list of available integrator types"""
        return Integrator.get_available_types()
    
    def clear_all(self):
        """Clear all analyses"""  
        Analysis._analyses.clear()
        Analysis._next_tag = 1