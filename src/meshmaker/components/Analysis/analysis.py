from typing import Optional, Dict, List, Any
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
            num_steps (Optional[int]): Number of analysis steps (either this or final_time must be provided)
            final_time (Optional[float]): Final time for analysis (either this or num_steps must be provided)
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
        if num_steps is None and final_time is None:
            raise ValueError("Either num_steps or final_time must be provided.")
        
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
        
        return "\n".join(commands)
        
    def run_analysis_tcl(self) -> str:
        """
        Generate TCL commands to run the analysis.
        
        Returns:
            str: TCL command string to run the analysis
            
        Raises:
            ValueError: If any required component is missing
        """
        if not self.validate():
            missing = self.get_missing_components()
            raise ValueError(f"Cannot run analysis. Missing components: {', '.join(missing)}")
            
        # Setup analysis
        commands = [self.to_tcl()]
        
        # Run analysis
        commands.append(f"# Run {self.analysis_type.lower()} analysis - {self.name}")
        
        # Construct the analyze command based on analysis type and parameters
        analyze_cmd = "analyze"
        
        if self.analysis_type == "Static":
            if self.num_steps is not None:
                analyze_cmd += f" {self.num_steps}"
            else:
                analyze_cmd += f" 0 {self.final_time}"
        
        elif self.analysis_type == "Transient":
            if self.num_steps is not None:
                analyze_cmd += f" {self.num_steps} {self.dt}"
            else:
                analyze_cmd += f" 0 {self.dt} {self.final_time}"
                
            # Add optional sublevel parameters if provided
            if self.num_sublevels is not None and self.num_substeps is not None:
                analyze_cmd += f" {self.num_sublevels} {self.num_substeps}"
        
        elif self.analysis_type == "VariableTransient":
            if self.num_steps is not None:
                analyze_cmd += f" {self.num_steps} {self.dt} {self.dt_min} {self.dt_max} {self.jd}"
            else:
                analyze_cmd += f" 0 {self.dt} {self.final_time} {self.dt_min} {self.dt_max} {self.jd}"
        
        commands.append(analyze_cmd)
            
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
        return cls._instance
    
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
            num_steps (Optional[int]): Number of analysis steps (either this or final_time must be provided)
            final_time (Optional[float]): Final time for analysis (either this or num_steps must be provided)
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
    
    def create_static_analysis(self, name: str, constraint_handler: ConstraintHandler, 
                            numberer: Numberer, system: System, algorithm: Algorithm, 
                            test: Test, integrator: Integrator, num_steps: Optional[int] = None,
                            final_time: Optional[float] = None) -> Analysis:
        """
        Create a static analysis with the specified components.
        
        Args:
            name (str): Name of the analysis
            constraint_handler (ConstraintHandler): The constraint handler for the analysis
            numberer (Numberer): The numberer for the analysis
            system (System): The system for the analysis
            algorithm (Algorithm): The algorithm for the analysis
            test (Test): The convergence test for the analysis
            integrator (Integrator): The integrator for the analysis (must be a static integrator)
            num_steps (Optional[int]): Number of analysis steps (either this or final_time must be provided)
            final_time (Optional[float]): Final time for analysis (either this or num_steps must be provided)
            
        Returns:
            Analysis: The created static analysis
            
        Raises:
            ValueError: If the integrator is not a static integrator
            ValueError: If neither num_steps nor final_time is provided, or if both are provided
        """
        return Analysis(name, "Static", constraint_handler, numberer, 
                      system, algorithm, test, integrator, 
                      num_steps=num_steps, final_time=final_time)
    
    def create_transient_analysis(self, name: str, constraint_handler: ConstraintHandler, 
                               numberer: Numberer, system: System, algorithm: Algorithm, 
                               test: Test, integrator: Integrator, dt: float,
                               num_steps: Optional[int] = None, final_time: Optional[float] = None,
                               num_sublevels: Optional[int] = None, 
                               num_substeps: Optional[int] = None) -> Analysis:
        """
        Create a transient analysis with the specified components.
        
        Args:
            name (str): Name of the analysis
            constraint_handler (ConstraintHandler): The constraint handler for the analysis
            numberer (Numberer): The numberer for the analysis
            system (System): The system for the analysis
            algorithm (Algorithm): The algorithm for the analysis
            test (Test): The convergence test for the analysis
            integrator (Integrator): The integrator for the analysis (must be a transient integrator)
            dt (float): Time step increment
            num_steps (Optional[int]): Number of analysis steps (either this or final_time must be provided)
            final_time (Optional[float]): Final time for analysis (either this or num_steps must be provided)
            num_sublevels (Optional[int]): Number of sublevels in case of analysis failure (optional)
            num_substeps (Optional[int]): Number of substeps to try at each sublevel (optional)
            
        Returns:
            Analysis: The created transient analysis
            
        Raises:
            ValueError: If the integrator is not a transient integrator
            ValueError: If dt is not provided
            ValueError: If neither num_steps nor final_time is provided, or if both are provided
        """
        return Analysis(name, "Transient", constraint_handler, numberer, 
                      system, algorithm, test, integrator, 
                      num_steps=num_steps, final_time=final_time, dt=dt,
                      num_sublevels=num_sublevels, num_substeps=num_substeps)
    
    def create_variable_transient_analysis(self, name: str, constraint_handler: ConstraintHandler, 
                                        numberer: Numberer, system: System, algorithm: Algorithm, 
                                        test: Test, integrator: Integrator, dt: float,
                                        dt_min: float, dt_max: float, jd: int,
                                        num_steps: Optional[int] = None, 
                                        final_time: Optional[float] = None) -> Analysis:
        """
        Create a variable transient analysis with the specified components.
        
        Args:
            name (str): Name of the analysis
            constraint_handler (ConstraintHandler): The constraint handler for the analysis
            numberer (Numberer): The numberer for the analysis
            system (System): The system for the analysis
            algorithm (Algorithm): The algorithm for the analysis
            test (Test): The convergence test for the analysis
            integrator (Integrator): The integrator for the analysis (must be a transient integrator)
            dt (float): Time step increment
            dt_min (float): Minimum time step
            dt_max (float): Maximum time step
            jd (int): Number of iterations desired at each step
            num_steps (Optional[int]): Number of analysis steps (either this or final_time must be provided)
            final_time (Optional[float]): Final time for analysis (either this or num_steps must be provided)
            
        Returns:
            Analysis: The created variable transient analysis
            
        Raises:
            ValueError: If the integrator is not a transient integrator
            ValueError: If dt, dt_min, dt_max, or jd is not provided
            ValueError: If neither num_steps nor final_time is provided, or if both are provided
        """
        return Analysis(name, "VariableTransient", constraint_handler, numberer, 
                      system, algorithm, test, integrator, 
                      num_steps=num_steps, final_time=final_time, dt=dt,
                      dt_min=dt_min, dt_max=dt_max, jd=jd)
    
    def get_analysis(self, tag: int) -> Analysis:
        """
        Get analysis by tag.
        
        Args:
            tag (int): Tag of the analysis to retrieve
        
        Returns:
            Analysis: The analysis with the specified tag
        """
        return Analysis.get_analysis(tag)
    
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
    
    def remove_analysis(self, tag: int) -> None:
        """
        Remove an analysis by its tag.
        
        Args:
            tag (int): Tag of the analysis to remove
            
        Raises:
            KeyError: If no analysis with the given tag exists
        """
        # Check if analysis exists
        analysis = Analysis.get_analysis(tag)
        
        # Remove from name set
        Analysis._names.remove(analysis.name)
        
        # Remove from instances dictionary
        if tag in Analysis._instances:
            del Analysis._instances[tag]
    
    def remove_analysis_by_name(self, name: str) -> bool:
        """
        Remove an analysis by its name.
        
        Args:
            name (str): Name of the analysis to remove
            
        Returns:
            bool: True if an analysis was removed, False if not found
        """
        analysis = self.find_analysis_by_name(name)
        if analysis:
            self.remove_analysis(analysis.tag)
            return True
        return False
    
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
    
    def update_constraint_handler(self, analysis: Analysis, constraint_handler: ConstraintHandler) -> None:
        """
        Update the constraint handler for an analysis.
        
        Args:
            analysis: The analysis to modify
            constraint_handler: The new constraint handler
        """
        analysis.constraint_handler = constraint_handler
    
    def update_numberer(self, analysis: Analysis, numberer: Numberer) -> None:
        """
        Update the numberer for an analysis.
        
        Args:
            analysis: The analysis to modify
            numberer: The new numberer
        """
        analysis.numberer = numberer
    
    def update_system(self, analysis: Analysis, system: System) -> None:
        """
        Update the system for an analysis.
        
        Args:
            analysis: The analysis to modify
            system: The new system
        """
        analysis.system = system
    
    def update_algorithm(self, analysis: Analysis, algorithm: Algorithm) -> None:
        """
        Update the algorithm for an analysis.
        
        Args:
            analysis: The analysis to modify
            algorithm: The new algorithm
        """
        analysis.algorithm = algorithm
    
    def update_test(self, analysis: Analysis, test: Test) -> None:
        """
        Update the test for an analysis.
        
        Args:
            analysis: The analysis to modify
            test: The new test
        """
        analysis.test = test
    
    def update_integrator(self, analysis: Analysis, integrator: Integrator) -> None:
        """
        Update the integrator for an analysis.
        
        Args:
            analysis: The analysis to modify
            integrator: The new integrator
        """
        if analysis.analysis_type == "Static" and not isinstance(integrator, StaticIntegrator):
            raise ValueError(f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
        
        elif analysis.analysis_type in ["Transient", "VariableTransient"] and not isinstance(integrator, TransientIntegrator):
            raise ValueError(f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
        
        analysis.integrator = integrator
    
    def rename_analysis(self, analysis: Analysis, new_name: str) -> None:
        """
        Rename an analysis.
        
        Args:
            analysis: The analysis to rename
            new_name: The new name for the analysis
            
        Raises:
            ValueError: If the new name is already in use
        """
        if new_name in Analysis._names:
            raise ValueError(f"Analysis name '{new_name}' is already in use. Names must be unique.")
        
        # Remove old name and add new name
        Analysis._names.remove(analysis.name)
        analysis.name = new_name
        Analysis._names.add(new_name)