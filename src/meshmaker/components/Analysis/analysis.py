from typing import Optional, Dict, List, Any, Union
from .base import AnalysisComponent
from .numberers import Numberer, NumbererManager
from .integrators import Integrator, IntegratorManager, StaticIntegrator, TransientIntegrator
from .algorithms import Algorithm, AlgorithmManager
from .systems import System, SystemManager
from .constraint_handlers import ConstraintHandler, ConstraintHandlerManager
from .convergenceTests import Test, TestManager


class Analysis(AnalysisComponent):
    """
    Main class for managing an OpenSees analysis.
    
    An Analysis object combines constraint handler, test, numberer, system, algorithm, and integrator
    to define how the analysis is performed.
    """
    _instances = {}  # Class-level dictionary to track all created analyses
    _next_tag = 1    # Class variable to track the next tag to assign
    _names = set()   # Class-level set to track used names
    
    def __init__(self, name: str, analysis_type: str, constraint_handler: ConstraintHandler, 
                 numberer: Numberer, system: System, algorithm: Algorithm, 
                 test: Test, integrator: Integrator, num_steps: Optional[int] = None,
                 final_time: Optional[float] = None, dt: Optional[float] = None,
                 dt_min: Optional[float] = None, dt_max: Optional[float] = None,
                 jd: Optional[int] = None, num_sublevels: Optional[int] = None,
                 num_substeps: Optional[int] = None):
        """
        Initialize an Analysis with all required components.
        
        Args:
            name (str): Name of the analysis for identification (must be unique)
            analysis_type (str): Type of analysis ("Static", "Transient", "VariableTransient")
            constraint_handler (ConstraintHandler): The constraint handler for the analysis
            numberer (Numberer): The numberer for the analysis
            system (System): The system for the analysis
            algorithm (Algorithm): The algorithm for the analysis
            test (Test): The convergence test for the analysis
            integrator (Integrator): The integrator for the analysis
            num_steps (Optional[int]): Number of analysis steps (required for Static, optional for others)
            final_time (Optional[float]): Final time for analysis (optional for Transient/VariableTransient)
            dt (Optional[float]): Time step increment (required for Transient or VariableTransient analysis)
            dt_min (Optional[float]): Minimum time step (required for VariableTransient analysis)
            dt_max (Optional[float]): Maximum time step (required for VariableTransient analysis)
            jd (Optional[int]): Number of iterations desired at each step (required for VariableTransient analysis)
            num_sublevels (Optional[int]): Number of sublevels in case of analysis failure (optional)
            num_substeps (Optional[int]): Number of substeps to try at each sublevel (optional)
            
        Raises:
            ValueError: If integrator type is incompatible with analysis type
            ValueError: If analysis parameters are inconsistent with analysis type
            ValueError: If analysis name is not unique
        """
        # Check if name is unique
        if name in Analysis._names:
            raise ValueError(f"Analysis name '{name}' is already in use. Names must be unique.")
        
        self.tag = Analysis._next_tag
        Analysis._next_tag += 1
        self.name = name
        Analysis._names.add(name)
        
        self.analysis_type = analysis_type
        
        # Validate analysis type
        if analysis_type not in ["Static", "Transient", "VariableTransient"]:
            raise ValueError(f"Unknown analysis type: {analysis_type}. Must be 'Static', 'Transient', or 'VariableTransient'.")
        
        # Set all components
        self.constraint_handler = constraint_handler
        self.numberer = numberer
        self.system = system
        self.algorithm = algorithm
        self.test = test
        
        # Validate integrator compatibility
        if analysis_type == "Static" and not isinstance(integrator, StaticIntegrator):
            raise ValueError(f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
        
        elif analysis_type in ["Transient", "VariableTransient"] and not isinstance(integrator, TransientIntegrator):
            raise ValueError(f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
        
        self.integrator = integrator
        
        # Validate and set analysis parameters
        if analysis_type == "Static":
            if num_steps is None:
                raise ValueError("Static analysis requires num_steps parameter.")
            if final_time is not None:
                raise ValueError("Static analysis does not use final_time parameter.")
        else:  # Transient or VariableTransient
            if num_steps is None and final_time is None:
                raise ValueError("Transient analysis requires either num_steps or final_time parameter.")
            if num_steps is not None and final_time is not None:
                raise ValueError("Only one of num_steps or final_time should be provided, not both.")
        
        self.num_steps = num_steps
        self.final_time = final_time
        
        # Time step parameters
        if analysis_type in ["Transient", "VariableTransient"] and dt is None:
            raise ValueError(f"{analysis_type} analysis requires a time step (dt).")
        
        self.dt = dt
        
        # VariableTransient specific parameters
        if analysis_type == "VariableTransient":
            if dt_min is None or dt_max is None:
                raise ValueError("VariableTransient analysis requires dt_min and dt_max parameters.")
            
            if jd is None:
                raise ValueError("VariableTransient analysis requires jd parameter (desired iterations per step).")
        
        self.dt_min = dt_min
        self.dt_max = dt_max
        self.jd = jd
        
        # Optional sublevel parameters (only applicable to Transient analyses)
        if analysis_type == "Static" and (num_sublevels is not None or num_substeps is not None):
            raise ValueError("num_sublevels and num_substeps are only applicable to Transient analysis.")
        
        if (num_sublevels is not None and num_substeps is None) or (num_sublevels is None and num_substeps is not None):
            raise ValueError("Both num_sublevels and num_substeps must be provided if either is specified.")
        
        self.num_sublevels = num_sublevels
        self.num_substeps = num_substeps
        
        # Register this analysis in the class-level tracking dictionary
        Analysis._instances[self.tag] = self
    
    @classmethod
    def get_analysis(cls, tag: int) -> 'Analysis':
        """
        Retrieve a specific analysis by its tag.
        
        Args:
            tag (int): The tag of the analysis
        
        Returns:
            Analysis: The analysis with the specified tag
        
        Raises:
            KeyError: If no analysis with the given tag exists
        """
        if tag not in cls._instances:
            raise KeyError(f"No analysis found with tag {tag}")
        return cls._instances[tag]
    
    @classmethod
    def get_all_analyses(cls) -> Dict[int, 'Analysis']:
        """
        Retrieve all created analyses.
        
        Returns:
            Dict[int, Analysis]: A dictionary of all analyses, keyed by their unique tags
        """
        return cls._instances
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all analyses and reset tags.
        """
        cls._instances.clear()
        cls._names.clear()
        cls._next_tag = 1
    
    def validate(self) -> bool:
        """
        Validate that all required components are set.
        
        Returns:
            bool: True if all components are set, False otherwise
        """
        return (
            self.constraint_handler is not None and
            self.numberer is not None and
            self.system is not None and
            self.algorithm is not None and
            self.test is not None and
            self.integrator is not None
        )
    
    def get_missing_components(self) -> List[str]:
        """
        Get a list of missing components.
        
        Returns:
            List[str]: Names of missing components
        """
        missing = []
        if self.constraint_handler is None:
            missing.append("constraint handler")
        if self.numberer is None:
            missing.append("numberer")
        if self.system is None:
            missing.append("system")
        if self.algorithm is None:
            missing.append("algorithm")
        if self.test is None:
            missing.append("test")
        if self.integrator is None:
            missing.append("integrator")
        return missing
    
    def to_tcl(self) -> str:
        """
        Convert the analysis to a TCL command string for OpenSees.
        
        Returns:
            str: The TCL command string for all components and the analysis
        
        Raises:
            ValueError: If any required component is missing
        """
        if not self.validate():
            missing = self.get_missing_components()
            raise ValueError(f"Cannot create analysis. Missing components: {', '.join(missing)}")
        
        # Generate TCL commands for each component
        commands = []
        commands.append(self.constraint_handler.to_tcl())
        commands.append(self.numberer.to_tcl())
        commands.append(self.system.to_tcl())
        commands.append(self.algorithm.to_tcl())
        commands.append(self.test.to_tcl())
        commands.append(self.integrator.to_tcl())
        
        # Add analysis command
        commands.append(f"analysis {self.analysis_type}")
        
        # add analyze command with parameters
        if self.analysis_type == "Static":
            commands.append(f"analyze {self.num_steps}")
        elif self.analysis_type in ["Transient", "VariableTransient"]:
            if self.final_time is not None:
                commands.append("while {[getTime] < %f} {" % self.final_time)
                commands.append(f"\tset Ok [analyze 1 {self.dt}]\n")
                commands.append("}")
            else:
                commands.append(f"set AnalysisStep 0")
                commands.append("while {"+f" $AnalysisStep < {self.num_steps}"+"} {")
                commands.append(f"\tset Ok [analyze  {self.dt}]")   
                commands.append(f"\tincr $AnalysisStep 1")
                commands.append("}")

        # wipe analysis command
        commands.append("wipeAnalysis")

                
                                
        
        return "\n".join(commands)
    
    def get_values(self) -> Dict[str, Any]:
        """
        Get the parameters defining this analysis.
        
        Returns:
            Dict[str, Any]: Dictionary of parameter values
        """
        values = {
            "name": self.name,
            "analysis_type": self.analysis_type,
            "num_steps": self.num_steps,
            "final_time": self.final_time,
            "dt": self.dt
        }
        
        # Add VariableTransient specific parameters if applicable
        if self.analysis_type == "VariableTransient":
            values.update({
                "dt_min": self.dt_min,
                "dt_max": self.dt_max,
                "jd": self.jd
            })
        
        # Add sublevel parameters if provided
        if self.num_sublevels is not None:
            values.update({
                "num_sublevels": self.num_sublevels,
                "num_substeps": self.num_substeps
            })
        
        # Add component info if set
        if self.constraint_handler:
            values["constraint_handler"] = {
                "tag": self.constraint_handler.tag,
                "type": self.constraint_handler.handler_type
            }
        
        if self.numberer:
            values["numberer"] = {
                "type": self.numberer.to_tcl().split()[1]  # Extract type from TCL command
            }
        
        if self.system:
            values["system"] = {
                "tag": self.system.tag,
                "type": self.system.system_type
            }
        
        if self.algorithm:
            values["algorithm"] = {
                "tag": self.algorithm.tag,
                "type": self.algorithm.algorithm_type
            }
        
        if self.test:
            values["test"] = {
                "tag": self.test.tag,
                "type": self.test.test_type
            }
        
        if self.integrator:
            values["integrator"] = {
                "tag": self.integrator.tag,
                "type": self.integrator.integrator_type
            }
        
        return values


class AnalysisManager:
    """
    Manager class for creating and managing analyses
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalysisManager, cls).__new__(cls)
            # Initialize instance variables in __new__ since it's a singleton
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Only initialize the managers once
        if not self._initialized:
            self.test = TestManager()
            self.constraint = ConstraintHandlerManager()
            self.numberer = NumbererManager()
            self.system = SystemManager()
            self.algorithm = AlgorithmManager()
            self.integrator = IntegratorManager()
            self._initialized = True
    
    def create_default_transient_analysis(self, username: str, dt: float, num_steps: int = None, 
                                         final_time: float = None) -> Analysis:
        """
        Create a default transient analysis with predefined components:
        - ParallelRCM numberer
        - Newmark integrator with gamma=0.5 and beta=0.25
        - Mumps system with ICNTL14=100 and ICNTL7=7
        - EnergyIncr test with tol=1e-3, max_iter=20, print_flag=2
        - ModifiedNewton algorithm with factoronce
        - Transformation constraint handler
        
        Args:
            username (str): Username for the analysis name
            dt (float): Time step increment
            num_steps (int, optional): Number of analysis steps (either this or final_time must be provided)
            final_time (float, optional): Final time for analysis (either this or num_steps must be provided)
            
        Returns:
            Analysis: The created transient analysis
            
        Raises:
            ValueError: If neither num_steps nor final_time is provided or if both are provided
        """
        # Validate inputs
        if (num_steps is None and final_time is None) or (num_steps is not None and final_time is not None):
            raise ValueError("Exactly one of num_steps or final_time must be provided")
            
        # Create analysis name
        analysis_name = f"defualtTransient_{username}"
        
        # Create components
        numberer = self.numberer.create_numberer("parallelrcm")
        integrator = self.integrator.create_integrator("newmark", gamma=0.5, beta=0.25)
        system = self.system.create_system("mumps", icntl14=100, icntl7=7)
        test = self.test.create_test("energyincr", tol=1e-3, max_iter=20, print_flag=2)
        algorithm = self.algorithm.create_algorithm("modifiednewton", factor_once=True)
        constraint_handler = self.constraint.create_handler("transformation")
        
        # Create and return the analysis
        return self.create_analysis(
            name=analysis_name,
            analysis_type="Transient",
            constraint_handler=constraint_handler,
            numberer=numberer,
            system=system,
            algorithm=algorithm,
            test=test,
            integrator=integrator,
            num_steps=num_steps,
            final_time=final_time,
            dt=dt
        )
    
    def create_analysis(self, name: str, analysis_type: str, constraint_handler: ConstraintHandler, 
                     numberer: Numberer, system: System, algorithm: Algorithm, 
                     test: Test, integrator: Integrator, num_steps: Optional[int] = None, 
                     final_time: Optional[float] = None, dt: Optional[float] = None,
                     dt_min: Optional[float] = None, dt_max: Optional[float] = None,
                     jd: Optional[int] = None, num_sublevels: Optional[int] = None,
                     num_substeps: Optional[int] = None) -> Analysis:
        """
        Create a new analysis with all required components.
        
        Args:
            name (str): Name of the analysis
            analysis_type (str): Type of analysis ("Static", "Transient", "VariableTransient")
            constraint_handler (ConstraintHandler): The constraint handler for the analysis
            numberer (Numberer): The numberer for the analysis
            system (System): The system for the analysis
            algorithm (Algorithm): The algorithm for the analysis
            test (Test): The convergence test for the analysis
            integrator (Integrator): The integrator for the analysis
            num_steps (Optional[int]): Number of analysis steps (required for Static, optional for others)
            final_time (Optional[float]): Final time for analysis (optional for Transient/VariableTransient)
            dt (Optional[float]): Time step increment (required for Transient or VariableTransient analysis)
            dt_min (Optional[float]): Minimum time step (required for VariableTransient analysis)
            dt_max (Optional[float]): Maximum time step (required for VariableTransient analysis)
            jd (Optional[int]): Number of iterations desired at each step (required for VariableTransient analysis)
            num_sublevels (Optional[int]): Number of sublevels in case of analysis failure (optional)
            num_substeps (Optional[int]): Number of substeps to try at each sublevel (optional)
        
        Returns:
            Analysis: The created analysis
            
        Raises:
            ValueError: If analysis parameters are inconsistent with analysis type
        """
        return Analysis(name, analysis_type, constraint_handler, numberer, system, algorithm, 
                      test, integrator, num_steps, final_time, dt, dt_min, dt_max, jd,
                      num_sublevels, num_substeps)
    
    def get_analysis(self, identifier: Union[int, str, Analysis]) -> Analysis:
        """
        Get analysis by tag, name, or instance.
        
        Args:
            identifier: Tag, name, or instance of the analysis to retrieve
        
        Returns:
            Analysis: The analysis
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        if isinstance(identifier, int):
            return Analysis.get_analysis(identifier)
        elif isinstance(identifier, str):
            analysis = self.find_analysis_by_name(identifier)
            if analysis is None:
                raise KeyError(f"No analysis found with name '{identifier}'")
            return analysis
        elif isinstance(identifier, Analysis):
            return identifier
        else:
            raise TypeError(f"Identifier must be an int (tag), str (name), or Analysis instance, not {type(identifier)}")
    
    def find_analysis_by_name(self, name: str) -> Optional[Analysis]:
        """
        Find an analysis by its name.
        
        Args:
            name (str): Name of the analysis to find
            
        Returns:
            Optional[Analysis]: The analysis with the given name, or None if not found
        """
        for analysis in Analysis.get_all_analyses().values():
            if analysis.name.lower() == name.lower():
                return analysis
        return None
    
    def remove_analysis(self, identifier: Union[int, str, Analysis]) -> None:
        """
        Remove an analysis by its tag, name, or instance.
        
        Args:
            identifier: Tag, name, or instance of the analysis to remove
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        analysis = self.get_analysis(identifier)
        
        # Remove from name set
        Analysis._names.remove(analysis.name)
        
        # Remove from instances dictionary
        if analysis.tag in Analysis._instances:
            del Analysis._instances[analysis.tag]
    
    def get_all_analyses(self) -> Dict[int, Analysis]:
        """
        Get all analyses.
        
        Returns:
            Dict[int, Analysis]: Dictionary of all analyses
        """
        return Analysis.get_all_analyses()
    
    def clear_all(self) -> None:
        """
        Clear all analyses.
        """
        Analysis.clear_all()
    
    def update_constraint_handler(self, identifier: Union[int, str, Analysis], 
                                constraint_handler: ConstraintHandler) -> None:
        """
        Update the constraint handler for an analysis.
        
        Args:
            identifier: Tag, name, or instance of the analysis to modify
            constraint_handler: The new constraint handler
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        analysis = self.get_analysis(identifier)
        analysis.constraint_handler = constraint_handler
    
    def update_numberer(self, identifier: Union[int, str, Analysis], 
                      numberer: Numberer) -> None:
        """
        Update the numberer for an analysis.
        
        Args:
            identifier: Tag, name, or instance of the analysis to modify
            numberer: The new numberer
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        analysis = self.get_analysis(identifier)
        analysis.numberer = numberer
    
    def update_system(self, identifier: Union[int, str, Analysis], 
                    system: System) -> None:
        """
        Update the system for an analysis.
        
        Args:
            identifier: Tag, name, or instance of the analysis to modify
            system: The new system
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        analysis = self.get_analysis(identifier)
        analysis.system = system
    
    def update_algorithm(self, identifier: Union[int, str, Analysis], 
                       algorithm: Algorithm) -> None:
        """
        Update the algorithm for an analysis.
        
        Args:
            identifier: Tag, name, or instance of the analysis to modify
            algorithm: The new algorithm
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        analysis = self.get_analysis(identifier)
        analysis.algorithm = algorithm
    
    def update_test(self, identifier: Union[int, str, Analysis], 
                  test: Test) -> None:
        """
        Update the test for an analysis.
        
        Args:
            identifier: Tag, name, or instance of the analysis to modify
            test: The new test
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
        """
        analysis = self.get_analysis(identifier)
        analysis.test = test
    
    def update_integrator(self, identifier: Union[int, str, Analysis], 
                        integrator: Integrator) -> None:
        """
        Update the integrator for an analysis.
        
        Args:
            identifier: Tag, name, or instance of the analysis to modify
            integrator: The new integrator
            
        Raises:
            KeyError: If no analysis with the given tag or name exists
            TypeError: If identifier is not a valid type
            ValueError: If integrator type is incompatible with analysis type
        """
        analysis = self.get_analysis(identifier)
        
        if analysis.analysis_type == "Static" and not isinstance(integrator, StaticIntegrator):
            raise ValueError(f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
        
        elif analysis.analysis_type in ["Transient", "VariableTransient"] and not isinstance(integrator, TransientIntegrator):
            raise ValueError(f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
        
        analysis.integrator = integrator