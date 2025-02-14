from typing import List, Dict
from abc import ABC, abstractmethod

class mpConstraint(ABC):
    """Base class for OpenSees multi-point constraints"""
    
    # Class variable to store all MP constraints
    _constraints: Dict[int, 'mpConstraint'] = {}
    

    def __init__(self, master_node: int, slave_nodes: List[int]):
        """
        Initialize the base MP constraint
        
        Args:
            master_node: Tag of the master/retained node
            slave_nodes: List of slave/constrained node tags
        """
        self.master_node = master_node
        self.slave_nodes = slave_nodes
        self.tag = mpConstraint._next_tag()
        mpConstraint._constraints[self.tag] = self
        
    
    @classmethod
    def _next_tag(cls) -> int:
        """Get the next available tag"""
        return len(cls._constraints) + 1
    
    @classmethod
    def get_constraint(cls, tag: int) -> 'mpConstraint':
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





class equalDOF(mpConstraint):
    """Equal DOF constraint"""
    
    def __init__(self, master_node: int, slave_nodes: List[int], dofs: List[int]):
        """
        Initialize EqualDOF constraint
        
        Args:
            master_node: Retained node tag
            slave_node: Constrained node tag
            dofs: List of DOFs to be constrained
        """
        super().__init__(master_node, slave_nodes)
        self.dofs = dofs
    
    def to_tcl(self) -> str:
        tcl_str = ""
        for slave in self.slave_nodes:
            dofs_str = " ".join(str(dof) for dof in self.dofs)
            tcl_str += f"equalDOF {self.master_node} {slave} {dofs_str}\n"
        return tcl_str







class rigidLink(mpConstraint):
    """Rigid link constraint"""
    
    def __init__(self, type_str: str, master_node: int, slave_nodes: List[int]):
        """
        Initialize RigidLink constraint
        
        Args:
            type_str: Type of rigid link ('bar' or 'beam')
            master_node: Retained node tag
            slave_node: Constrained node tag
        """
        super().__init__(master_node, slave_nodes)
        if type_str not in ['bar', 'beam']:
            raise ValueError("RigidLink type must be 'bar' or 'beam'")
        self.type = type_str
    
    def to_tcl(self) -> str:
        tcl_str = ""
        for slave in self.slave_nodes:
            tcl_str += f"rigidLink {self.type} {self.master_node} {slave}\n"
        # return f"rigidLink {self.type} {self.master_node} {self.slave_nodes[0]}"






class rigidDiaphragm(mpConstraint):
    """Rigid diaphragm constraint"""
    
    def __init__(self, direction: int, master_node: int, slave_nodes: List[int]):
        """
        Initialize RigidDiaphragm constraint
        
        Args:
            direction: Direction perpendicular to rigid plane (3D) or direction of motion (2D)
            master_node: Retained node tag
            slave_nodes: List of constrained node tags
        """
        super().__init__(master_node, slave_nodes)
        self.direction = direction
    
    def to_tcl(self) -> str:
        slaves_str = " ".join(str(node) for node in self.slave_nodes)
        return f"rigidDiaphragm {self.direction} {self.master_node} {slaves_str}"
    






class mpConstraintManager:
    """
    Singleton class to manage MP constraints.
    This class provides methods to create and manage different types of constraints
    such as EqualDOF, RigidLink, and RigidDiaphragm. It ensures that only one instance
    of the class exists and provides a global point of access to it.
    """   
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(mpConstraintManager, cls).__new__(cls)
        return cls._instance

    def create_equal_dof(self, master_node: int, slave_nodes: List[int], dofs: List[int]) -> equalDOF:
        """
        Create an EqualDOF constraint.

        Parameters:
        master_node (int): The master node ID.
        slave_nodes (List[int]): A list of slave node IDs.
        dofs (List[int]): A list of degrees of freedom to be constrained.

        Returns:
        equalDOF: An instance of the equalDOF constraint.
        """
        """Create an EqualDOF constraint"""
        return equalDOF(master_node, slave_nodes, dofs)


    def create_rigid_link(self, type_str: str, master_node: int, slave_nodes: List[int]) -> rigidLink:
        """
        Create a RigidLink constraint.

        Args:
            type_str (str): The type of the rigid link.
            master_node (int): The master node ID.
            slave_nodes (List[int]): A list of slave node IDs.

        Returns:
            rigidLink: An instance of the rigidLink class representing the constraint.
        """
        return rigidLink(type_str, master_node, slave_nodes)


    def create_rigid_diaphragm(self, direction: int, master_node: int, slave_nodes: List[int]) -> rigidDiaphragm:
        """
        Create a RigidDiaphragm constraint.

        Parameters:
        direction (int): The direction of the rigid diaphragm constraint.
        master_node (int): The master node ID for the rigid diaphragm.
        slave_nodes (List[int]): A list of slave node IDs that will be constrained by the rigid diaphragm.

        Returns:
        rigidDiaphragm: An instance of the rigidDiaphragm class representing the created constraint.
        """
        return rigidDiaphragm(direction, master_node, slave_nodes)
    


    def create_constraint(self, constraint_type: str, *args) -> mpConstraint:
        """
        Create a constraint based on the specified type.

        Parameters:
        constraint_type (str): The type of constraint to create. 
                       Supported types are "equalDOF", "rigidLink", and "rigidDiaphragm".
        *args: Additional arguments required for creating the specific type of constraint.

        Returns:
        mpConstraint: An instance of the created constraint.

        Raises:
        ValueError: If an unknown constraint type is provided.
        """
        if constraint_type == "equalDOF":
            return self.create_equal_dof(*args)
        elif constraint_type == "rigidLink":
            return self.create_rigid_link(*args)
        elif constraint_type == "rigidDiaphragm":
            return self.create_rigid_diaphragm(*args)
        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")


    def get_constraint(self, tag: int) -> mpConstraint:
        """
        Retrieve a constraint by its tag.

        Args:
            tag (int): The tag identifier of the constraint.

        Returns:
            mpConstraint: The constraint object associated with the given tag.
        """
        """Get a constraint by its tag"""
        return mpConstraint.get_constraint(tag)


    def remove_constraint(self, tag: int) -> None:
        """
        Remove a constraint by its tag.

        Parameters:
        tag (int): The tag of the constraint to be removed.

        Returns:
        None
        """
        """Remove a constraint by its tag"""
        mpConstraint.remove_constraint(tag)


    def to_tcl(self) -> str:
        """
        Convert all constraints to TCL commands.

        This method iterates over all constraints stored in the class variable
        `_constraints` of `mpConstraint` and converts each constraint to its
        corresponding TCL command string. The resulting TCL command strings are
        concatenated into a single string.

        Returns:
            str: A string containing all the TCL commands for the constraints.
        """
        """Convert all constraints to TCL commands"""
        tcl_str = ""
        for constraint in mpConstraint._constraints.values():
            tcl_str += constraint.to_tcl()
        return tcl_str