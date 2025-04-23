from typing import List, Dict, Union, Optional
import weakref

# Import your existing component classes
from femora.components.Constraint.mpConstraint import mpConstraint
from femora.components.Constraint.spConstraint import SPConstraint
from femora.components.Pattern.patternBase import Pattern
from femora.components.Recorder.recorderBase import Recorder
from femora.components.Analysis.analysis import Analysis

# Define a union type for all components that can be used in the process
ProcessComponent = Union[SPConstraint, mpConstraint, Pattern, Recorder, Analysis]

class ProcessManager:
    """
    Singleton class to manage the sequence of operations in the structural analysis process.
    
    This class maintains a list of steps as weak references to component objects.
    Each step has only the object reference and an optional description.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProcessManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.steps = []
            self.current_step = -1
            self._initialized = True


    def __iter__(self):
        return iter(self.steps)
    

    def __len__(self):
        return len(self.steps)

    def add_step(self, component: ProcessComponent, description: str = "") -> int:
        """
        Add a step to the process
        
        Args:
            component: The component object to use in this step (must be one of the allowed component types)
            description: Description of the step
            
        Returns:
            int: Index of the added step
        """
        # Store a weak reference to the component
        component_ref = weakref.ref(component)
        # component_ref = component
        
        step = {
            "component": component_ref,
            "description": description
        }
        
        self.steps.append(step)
        return len(self.steps) - 1

    def insert_step(self, index: int, component: ProcessComponent, description: str = "") -> bool:
        """
        Insert a step at a specific position
        
        Args:
            index: Position to insert the step
            component: The component object to use in this step (must be one of the allowed component types)
            description: Description of the step
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 0 <= index <= len(self.steps):
            # Store a weak reference to the component
            component_ref = weakref.ref(component)
            
            step = {
                "component": component_ref,
                "description": description
            }
            
            self.steps.insert(index, step)
            
            # Adjust current step if needed
            if index <= self.current_step:
                self.current_step += 1
                
            return True
        return False

    def remove_step(self, index: int) -> bool:
        """
        Remove a step at a specific position
        
        Args:
            index: Position of the step to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        if 0 <= index < len(self.steps):
            del self.steps[index]
            
            # Adjust current step if needed
            if index <= self.current_step:
                self.current_step -= 1
                
            return True
        return False

    def clear_steps(self) -> None:
        """Clear all steps"""
        self.steps.clear()
        self.current_step = -1

    def get_steps(self) -> List[Dict]:
        """Get all steps in the process"""
        return self.steps

    def get_step(self, index: int) -> Optional[Dict]:
        """
        Get a step at a specific position
        
        Args:
            index: Position of the step
            
        Returns:
            Optional[Dict]: The step or None if index is invalid
        """
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None
    
    def to_tcl(self):
        """Convert the process to a TCL script"""
        tcl_script = ""
        for step in self.steps:
            component = step["component"]
            component = component() if component else None
            description = step["description"]
            tcl_script += f"# {description} ======================================\n\n"
            tcl_script += f"{component.to_tcl()}\n\n\n"
        return tcl_script