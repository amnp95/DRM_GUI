from femora.components.Constraint.mpConstraint import mpConstraintManager
from femora.components.Constraint.spConstraint import SPConstraintManager

class Constraint:
    """
    This module defines the Constraint class, which is a singleton that manages constraints using both
    mpConstraintManager and SPConstraintManager.

    The Constraint class provides a unified interface for applying boundary conditions and constraints
    to your MeshMaker models. It manages two types of constraints:
    
    1. MP (Multi-Point) Constraints: Create relationships between multiple nodes
    2. SP (Single-Point) Constraints: Fix or control degrees of freedom at specific nodes

    SP constraints should typically be created after assembling the whole mesh, as they are applied
    directly to nodes in the assembled mesh.

    Classes:
        Constraint: A singleton class that initializes and manages constraints.

    Usage:
        # Direct access to the Constraint manager
        from femora.components.Constraint.constraint import Constraint
        constraint_instance = Constraint()
        
        # Access through MeshMaker (recommended approach)
        from femora.components.MeshMaker import MeshMaker
        mk = MeshMaker()
        constraint_manager = mk.constraint
        
        # Using the SP constraint manager
        sp_manager = constraint_manager.sp
        
        # Add a fixed constraint to node 10, DOF 1 (X-direction)
        sp_manager.add_constraint(node_id=10, dof=1, value=0.0, constraint_type="fix")
        
        # Available SP constraint types include:
        # - "fix": Fix a degree of freedom to a specified value
        # - "disp": Apply a prescribed displacement
        # - "vel": Apply a prescribed velocity
        # - "accel": Apply a prescribed acceleration

    Attributes:
        _instance (Constraint): A class-level attribute that holds the singleton instance of the Constraint class.
        initialized (bool): An instance-level attribute that indicates whether the instance has been initialized.
        mp (mpConstraintManager): An instance of mpConstraintManager used to manage multi-point constraints.
        sp (SPConstraintManager): An instance of SPConstraintManager used to manage single-point constraints.

    Methods:
        __new__(cls, *args, **kwargs): Ensures that only one instance of the Constraint class is created.
        __init__(self): Initializes the singleton instance and sets up the managers.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Constraint, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # Initialize your singleton class here
            self.mp = mpConstraintManager()
            self.sp = SPConstraintManager()