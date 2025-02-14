from meshmaker.components.Constraint.mpConstraint import mpConstraintManager

class Constraint:
    """
    This module defines the Constraint class, which is a singleton that manages constraints using the mpConstraintManager.

    Classes:
        Constraint: A singleton class that initializes and manages constraints.

    Usage:
        constraint_instance = Constraint()

    Attributes:
        _instance (Constraint): A class-level attribute that holds the singleton instance of the Constraint class.
        initialized (bool): An instance-level attribute that indicates whether the instance has been initialized.
        mp (mpConstraintManager): An instance of mpConstraintManager used to manage constraints.

    Methods:
        __new__(cls, *args, **kwargs): Ensures that only one instance of the Constraint class is created.
        __init__(self): Initializes the singleton instance and sets up the mpConstraintManager.
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