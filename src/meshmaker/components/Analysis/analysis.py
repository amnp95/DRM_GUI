from typing import Optional, Dict, List, Any
from .base import AnalysisComponent
from .numberers import Numberer, NumbererManager
from .integrators import Integrator, IntegratorManager,StaticIntegrator, TransientIntegrator
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
    
    def __init__(self, name: str, analysis_type: str, constraint_handler: ConstraintHandler, 
                 numberer: Numberer, system: System, algorithm: Algorithm, 
                 test: Test, integrator: Integrator):
        """
        Initialize an Analysis with all required components.
        
        Args:
            name (str): Name of the analysis for identification
            analysis_type (str): Type of analysis (e.g., "Static", "Transient", "VariableTransient")
            constraint_handler (ConstraintHandler): The constraint handler for the analysis
            numberer (Numberer): The numberer for the analysis
            system (System): The system for the analysis
            algorithm (Algorithm): The algorithm for the analysis
            test (Test): The convergence test for the analysis
            integrator (Integrator): The integrator for the analysis
            
        Raises:
            ValueError: If integrator type is incompatible with analysis type
        """
        self.tag = Analysis._next_tag
        Analysis._next_tag += 1
        self.name = name
        self.analysis_type = analysis_type
        
        # Set all components
        self.constraint_handler = constraint_handler
        self.numberer = numberer
        self.system = system
        self.algorithm = algorithm
        self.test = test
        
        if analysis_type.lower() == "static" and not isinstance(integrator, StaticIntegrator):
            raise ValueError(f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
        
        elif analysis_type.lower() in ["transient", "variabletransient"] and not isinstance(integrator, TransientIntegrator):
            raise ValueError(f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
        
        self.integrator = integrator
        
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
        
    def run_analysis_tcl(self, num_steps: int, time_step: float = 1.0) -> str:
        """
        Generate TCL commands to run the analysis.
        
        Args:
            num_steps (int): Number of analysis steps to run
            time_step (float, optional): Time step size. Defaults to 1.0.
            
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
        commands.append(f"analyze {num_steps} {time_step}")
            
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
        }
        
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
                     test: Test, integrator: Integrator) -> Analysis:
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
        
        Returns:
            Analysis: The created analysis
            
        Raises:
            ValueError: If integrator type is incompatible with analysis type
        """
        return Analysis(name, analysis_type, constraint_handler, numberer, 
                     system, algorithm, test, integrator)
    
    def create_static_analysis(self, name: str, constraint_handler: ConstraintHandler, 
                            numberer: Numberer, system: System, algorithm: Algorithm, 
                            test: Test, integrator: Integrator) -> Analysis:
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
            
        Returns:
            Analysis: The created static analysis
            
        Raises:
            ValueError: If the integrator is not a static integrator
        """
        return Analysis(name, "Static", constraint_handler, numberer, 
                     system, algorithm, test, integrator)
    
    def create_transient_analysis(self, name: str, constraint_handler: ConstraintHandler, 
                               numberer: Numberer, system: System, algorithm: Algorithm, 
                               test: Test, integrator: Integrator) -> Analysis:
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
            
        Returns:
            Analysis: The created transient analysis
            
        Raises:
            ValueError: If the integrator is not a transient integrator
        """
        return Analysis(name, "Transient", constraint_handler, numberer, 
                     system, algorithm, test, integrator)
    
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
        Analysis.get_analysis(tag)
        
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
        if analysis.analysis_type.lower() == "static" and not isinstance(integrator, StaticIntegrator):
            raise ValueError(f"Static analysis requires a static integrator. {integrator.integrator_type} is not compatible.")
        
        elif analysis.analysis_type.lower() in ["transient", "variabletransient"] and not isinstance(integrator, TransientIntegrator):
            raise ValueError(f"Transient analysis requires a transient integrator. {integrator.integrator_type} is not compatible.")
        
        analysis.integrator = integrator