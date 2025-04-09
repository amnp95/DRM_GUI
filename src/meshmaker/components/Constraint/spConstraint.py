from typing import List, Dict, Optional, Union
from abc import ABC, abstractmethod
import numpy as np

# Ensure this module is part of the Constraint package
__all__ = ['SPConstraint', 'FixConstraint', 'FixXConstraint', 'FixYConstraint', 'FixZConstraint', 'SPConstraintManager']

class SPConstraint(ABC):
    """Base class for OpenSees single-point constraints
    
    Single-point constraints (SP_Constraints) are constraints that define the 
    response of a single degree-of-freedom at a node. These constraints can be 
    homogeneous (=0.0) or non-homogeneous.
    
    Types of SP constraints:
    - fix: Fix specific DOFs at a node
    - fixX: Fix specific DOFs at all nodes with a specified X coordinate
    - fixY: Fix specific DOFs at all nodes with a specified Y coordinate
    - fixZ: Fix specific DOFs at all nodes with a specified Z coordinate
    """
    
    # Class variable to store all SP constraints
    _constraints: Dict[int, 'SPConstraint'] = {}
    
    def __init__(self, node_tag: int, dofs: List[int]):
        """
        Initialize the base SP constraint
        
        Args:
            node_tag: Tag of the node to constrain
            dofs: List of DOFs to be constrained (1 = fixed, 0 = free)
        """
        self.node_tag = node_tag
        self.dofs = dofs
        self.tag = SPConstraint._next_tag()
        SPConstraint._constraints[self.tag] = self
    
    @classmethod
    def _next_tag(cls) -> int:
        """Get the next available tag"""
        return len(cls._constraints) + 1
    
    @classmethod
    def get_constraint(cls, tag: int) -> Optional['SPConstraint']:
        """Get a constraint by its tag"""
        return cls._constraints.get(tag)
    
    @classmethod
    def remove_constraint(cls, tag: int) -> None:
        """Remove a constraint and reorder remaining tags"""
        if tag in cls._constraints:
            del cls._constraints[tag]
            # Reorder remaining constraints
            constraints = sorted(cls._constraints.items())
            cls._constraints.clear()
            for new_tag, (_, constraint) in enumerate(constraints, 1):
                constraint.tag = new_tag
                cls._constraints[new_tag] = constraint
    
    @abstractmethod
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        pass


class FixConstraint(SPConstraint):
    """Fix constraint"""
    
    def __init__(self, node_tag: int, dofs: List[int]):
        """
        Initialize Fix constraint
        
        Args:
            node_tag: Tag of the node to be fixed
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
        """
        super().__init__(node_tag, dofs)
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fix {self.node_tag} {' '.join(map(str, self.dofs))};"


class FixXConstraint(SPConstraint):
    """FixX constraint"""
    
    def __init__(self, xCoordinate: float, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixX constraint
        
        Args:
            xCoordinate: x-coordinate of nodes to be constrained
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.xCoordinate = xCoordinate
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixX {self.xCoordinate} {' '.join(map(str, self.dofs))} -tol {self.tol};"


class FixYConstraint(SPConstraint):
    """FixY constraint"""
    
    def __init__(self, yCoordinate: float, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixY constraint
        
        Args:
            yCoordinate: y-coordinate of nodes to be constrained
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.yCoordinate = yCoordinate
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixY {self.yCoordinate} {' '.join(map(str, self.dofs))} -tol {self.tol};"


class FixZConstraint(SPConstraint):
    """FixZ constraint"""
    
    def __init__(self, zCoordinate: float, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixZ constraint
        
        Args:
            zCoordinate: z-coordinate of nodes to be constrained
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.zCoordinate = zCoordinate
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixZ {self.zCoordinate} {' '.join(map(str, self.dofs))} -tol {self.tol};"
    

class FixMacroX_max(SPConstraint):
    """
    FixX constraint for maximum X coordinate which is 
    defined as macro with name X_MAX in the TCL file
    """
    def __init__(self, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixX constraint
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixX $X_MAX {' '.join(map(str, self.dofs))} -tol {self.tol};"
    
class FixMacroY_max(SPConstraint):
    """
    FixY constraint for maximum Y coordinate which is 
    defined as macro with name Y_MAX in the TCL file
    """
    def __init__(self, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixY constraint
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixY $Y_MAX {' '.join(map(str, self.dofs))} -tol {self.tol};"
    
class FixMacroZ_max(SPConstraint):
    """
    FixZ constraint for maximum Z coordinate which is 
    defined as macro with name Z_MAX in the TCL file
    """
    def __init__(self, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixZ constraint
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixZ $Z_MAX {' '.join(map(str, self.dofs))} -tol {self.tol};"


class FixMacroX_min(SPConstraint):
    """
    FixX constraint for minimum X coordinate which is 
    defined as macro with name X_MIN in the TCL file
    """
    def __init__(self, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixX constraint
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixX $X_MIN {' '.join(map(str, self.dofs))} -tol {self.tol};"
    

class FixMacroY_min(SPConstraint):
    """
    FixY constraint for minimum Y coordinate which is 
    defined as macro with name Y_MIN in the TCL file
    """
    def __init__(self, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixY constraint
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixY $Y_MIN {' '.join(map(str, self.dofs))} -tol {self.tol};"
    

class FixMacroZ_min(SPConstraint):
    """
    FixZ constraint for minimum Z coordinate which is 
    defined as macro with name Z_MIN in the TCL file
    """
    def __init__(self, dofs: List[int], tol: float = 1e-10):
        """
        Initialize FixZ constraint
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        """
        # Use -1 as a placeholder for node tag since it applies to multiple nodes
        super().__init__(-1, dofs)
        self.tol = tol
    
    def to_tcl(self) -> str:
        """Convert constraint to TCL command for OpenSees"""
        return f"fixZ $Z_MIN {' '.join(map(str, self.dofs))} -tol {self.tol};"
    



class SPConstraintManager:
    """
    Singleton class to manage SP constraints.
    This class provides methods to create and manage different types of constraints
    such as fix, fixX, fixY, and fixZ. It ensures that only one instance
    of the class exists and provides a global point of access to it.
    
    Methods:
        fix(node_tag, dofs): Create a fix constraint for a specific node
        fixX(xCoordinate, dofs, tol): Create a fixX constraint for nodes at specific X coordinate
        fixY(yCoordinate, dofs, tol): Create a fixY constraint for nodes at specific Y coordinate
        fixZ(zCoordinate, dofs, tol): Create a fixZ constraint for nodes at specific Z coordinate
        create_constraint(constraint_type, *args): Create a constraint based on specified type
        get_constraint(tag): Get a constraint by its tag
        remove_constraint(tag): Remove a constraint by its tag
        to_tcl(): Generate TCL commands for all constraints
    """   
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SPConstraintManager, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not self._initialized:
            self._initialized = True

    def fix(self, node_tag: int, dofs: List[int]) -> FixConstraint:
        """
        Create a fix constraint.
        
        Args:
            node_tag: Tag of the node to be fixed
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
        
        Returns:
            FixConstraint: The created fix constraint
        """
        return FixConstraint(node_tag, dofs)

    def fixX(self, xCoordinate: float, dofs: List[int], tol: float = 1e-10) -> FixXConstraint:
        """
        Create a fixX constraint.
        
        Args:
            xCoordinate: x-coordinate of nodes to be constrained
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixXConstraint: The created fixX constraint
        """
        return FixXConstraint(xCoordinate, dofs, tol)

    def fixY(self, yCoordinate: float, dofs: List[int], tol: float = 1e-10) -> FixYConstraint:
        """
        Create a fixY constraint.
        
        Args:
            yCoordinate: y-coordinate of nodes to be constrained
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixYConstraint: The created fixY constraint
        """
        return FixYConstraint(yCoordinate, dofs, tol)

    def fixZ(self, zCoordinate: float, dofs: List[int], tol: float = 1e-10) -> FixZConstraint:
        """
        Create a fixZ constraint.
        
        Args:
            zCoordinate: z-coordinate of nodes to be constrained
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixZConstraint: The created fixZ constraint
        """
        return FixZConstraint(zCoordinate, dofs, tol)
    

    def fixMacroXmin(self, dofs: List[int], tol: float = 1e-10) -> FixMacroX_min:
        """
        Create a fixX constraint for the minimum X coordinate defined as a macro.
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixMacroX_min: The created fixX constraint for X_MIN macro
        """
        return FixMacroX_min(dofs, tol)

    def fixMacroXmax(self, dofs: List[int], tol: float = 1e-10) -> FixMacroX_max:
        """
        Create a fixX constraint for the maximum X coordinate defined as a macro.
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixMacroX_max: The created fixX constraint for X_MAX macro
        """
        return FixMacroX_max(dofs, tol)

    def fixMacroYmin(self, dofs: List[int], tol: float = 1e-10) -> FixMacroY_min:
        """
        Create a fixY constraint for the minimum Y coordinate defined as a macro.
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixMacroY_min: The created fixY constraint for Y_MIN macro
        """
        return FixMacroY_min(dofs, tol)

    def fixMacroYmax(self, dofs: List[int], tol: float = 1e-10) -> FixMacroY_max:
        """
        Create a fixY constraint for the maximum Y coordinate defined as a macro.
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixMacroY_max: The created fixY constraint for Y_MAX macro
        """
        return FixMacroY_max(dofs, tol)

    def fixMacroZmin(self, dofs: List[int], tol: float = 1e-10) -> FixMacroZ_min:
        """
        Create a fixZ constraint for the minimum Z coordinate defined as a macro.
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixMacroZ_min: The created fixZ constraint for Z_MIN macro
        """
        return FixMacroZ_min(dofs, tol)

    def fixMacroZmax(self, dofs: List[int], tol: float = 1e-10) -> FixMacroZ_max:
        """
        Create a fixZ constraint for the maximum Z coordinate defined as a macro.
        
        Args:
            dofs: List of DOF constraint values (0 or 1)
                  0 unconstrained (or free)
                  1 constrained (or fixed)
            tol: Tolerance for coordinate comparison (default: 1e-10)
        
        Returns:
            FixMacroZ_max: The created fixZ constraint for Z_MAX macro
        """
        return FixMacroZ_max(dofs, tol)

    def create_constraint(self, constraint_type: str, *args) -> SPConstraint:
        """
        Create a constraint based on the specified type.
        
        Args:
            constraint_type: Type of constraint to create.
                             Supported types are "fix", "fixX", "fixY", and "fixZ".
            *args: Additional arguments required for creating the specific type of constraint.
        
        Returns:
            SPConstraint: The created constraint
        
        Raises:
            ValueError: If an unknown constraint type is provided
        """
        if constraint_type.lower() == "fix":
            return self.fix(*args)
        elif constraint_type.lower() == "fixx":
            return self.fixX(*args)
        elif constraint_type.lower() == "fixy":
            return self.fixY(*args)
        elif constraint_type.lower() == "fixz":
            return self.fixZ(*args)
        elif constraint_type.lower() == "fixmacroxmin":
            return self.fixMacroXmin(*args)
        elif constraint_type.lower() == "fixmacroxmax":
            return self.fixMacroXmax(*args)
        elif constraint_type.lower() == "fixmacroymin":
            return self.fixMacroYmin(*args)
        elif constraint_type.lower() == "fixmacroymax":
            return self.fixMacroYmax(*args)
        elif constraint_type.lower() == "fixmacrozmin":
            return self.fixMacroZmin(*args)
        elif constraint_type.lower() == "fixmacrozmax":
            return self.fixMacroZmax(*args)
        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

    def get_constraint(self, tag: int) -> Optional[SPConstraint]:
        """
        Retrieve a constraint by its tag.
        
        Args:
            tag: The tag identifier of the constraint.
        
        Returns:
            SPConstraint: The constraint object associated with the given tag.
        """
        return SPConstraint.get_constraint(tag)

    def remove_constraint(self, tag: int) -> None:
        """
        Remove a constraint by its tag.
        
        Args:
            tag: The tag of the constraint to be removed.
        """
        SPConstraint.remove_constraint(tag)

    def __iter__(self):
        """
        Iterate over all constraints.
        
        Yields:
            SPConstraint: Each constraint object in the order of their tags.
        """
        return iter(SPConstraint._constraints.values())
    

    def to_tcl(self) -> str:
        """
        Convert all constraints to TCL commands.
        
        Returns:
            str: A string containing all the TCL commands for the constraints.
        """
        tcl_commands = []
        
        # Group constraints by type for better organization
        fix_constraints = []
        fix_x_constraints = []
        fix_y_constraints = []
        fix_z_constraints = []
        
        for constraint in SPConstraint._constraints.values():
            if isinstance(constraint, FixConstraint):
                fix_constraints.append(constraint)
            elif isinstance(constraint, FixXConstraint):
                fix_x_constraints.append(constraint)
            elif isinstance(constraint, FixYConstraint):
                fix_y_constraints.append(constraint)
            elif isinstance(constraint, FixZConstraint):
                fix_z_constraints.append(constraint)
        
        # Add comments and constraints for each type
        if fix_constraints:
            tcl_commands.append("# Node-specific constraints")
            for constraint in fix_constraints:
                tcl_commands.append(constraint.to_tcl())
        
        if fix_x_constraints:
            tcl_commands.append("\n# X-coordinate constraints")
            for constraint in fix_x_constraints:
                tcl_commands.append(constraint.to_tcl())
        
        if fix_y_constraints:
            tcl_commands.append("\n# Y-coordinate constraints")
            for constraint in fix_y_constraints:
                tcl_commands.append(constraint.to_tcl())
        
        if fix_z_constraints:
            tcl_commands.append("\n# Z-coordinate constraints")
            for constraint in fix_z_constraints:
                tcl_commands.append(constraint.to_tcl())
        
        return "\n".join(tcl_commands)