from typing import Optional, List

class mpConstraint:
    """
    Base class representing a multipoint constraint in a finite element model.

    Attributes:
        _tag (Optional[int]): A unique identifier for the constraint.
    """

    def __init__(self):
        """Initializes the constraint with no assigned tag."""
        self._tag: Optional[int] = None

    def setTag(self, tag: int):
        """
        Assigns a unique identifier to the constraint.

        Args:
            tag (int): The unique identifier for this constraint.
        """
        self._tag = tag

    def isMaster(self) -> bool:
        """
        Determines whether this constraint is a master node.

        Returns:
            bool: True if the constraint is a master node, False otherwise.
        """
        return False  # Subclasses should override this


class equalDOF(mpConstraint):
    """
    Represents an equal degree-of-freedom (DOF) constraint between two nodes.

    Attributes:
        masterNode (Optional[mpConstraint]): The master node to which the DOFs are constrained.
        dofs (List[int]): The list of degrees of freedom to be constrained.
    """

    def __init__(self, masterNode: Optional[mpConstraint] = None, dofs: Optional[List[int]] = None):
        """
        Initializes the equalDOF constraint.

        Args:
            masterNode (Optional[mpConstraint]): The master node. If None, this constraint acts as a master.
            dofs (Optional[List[int]]): List of DOFs to constrain.
        """
        super().__init__()
        self.masterNode = masterNode
        self.dofs = dofs or []

    def isMaster(self) -> bool:
        """
        Checks if this node is a master.

        Returns:
            bool: True if this constraint is a master node, False otherwise.
        """
        return self.masterNode is None

    def to_tcl(self) -> str:
        """
        Generates the TCL command for the equalDOF constraint.

        Returns:
            str: The corresponding OpenSees TCL command.
        """
        return "" if self.isMaster() else f"equalDOF {self.masterNode._tag} {self._tag} {' '.join(map(str, self.dofs))}\n"


class rigidLink(mpConstraint):
    """
    Represents a rigid link constraint between two nodes.

    Attributes:
        masterNode (Optional[mpConstraint]): The master node to which the rigid link is applied.
        type (str): The type of rigid link ('bar' or 'beam').
    """

    def __init__(self, masterNode: Optional[mpConstraint] = None, type: str = "bar"):
        """
        Initializes the rigidLink constraint.

        Args:
            masterNode (Optional[mpConstraint]): The master node to which the rigid link is applied.
            type (str): The type of rigid link, either 'bar' or 'beam'.

        Raises:
            ValueError: If type is not 'bar' or 'beam'.
        """
        if type not in {"bar", "beam"}:
            raise ValueError("type must be 'bar' or 'beam'")
        super().__init__()
        self.masterNode = masterNode
        self.type = type  # Just store the string directly

    def isMaster(self) -> bool:
        """
        Checks if this node is a master.

        Returns:
            bool: True if this constraint is a master node, False otherwise.
        """
        return self.masterNode is None

    def to_tcl(self) -> str:
        """
        Generates the TCL command for the rigidLink constraint.

        Returns:
            str: The corresponding OpenSees TCL command.
        """
        return "" if self.isMaster() else f"rigidLink {self.type} {self.masterNode._tag} {self._tag}\n"



class rigidDiaphragm(mpConstraint):
    """
    Represents a rigid diaphragm constraint, enforcing plane motion.

    Attributes:
        masterNode (Optional[mpConstraint]): The master node for the diaphragm constraint.
        direction (int): The axis of constraint (1 for X, 2 for Y, 3 for Z).
    """

    def __init__(self, masterNode: Optional[mpConstraint] = None, direction: int = 1):
        """
        Initializes the rigidDiaphragm constraint.

        Args:
            masterNode (Optional[mpConstraint]): The master node for the diaphragm constraint.
            direction (int): The axis of constraint (1 for perpendicular to y-z plane, 2 for perpendicular to x-z plane, 3 for perpendicular to x-y plane).

        Raises:
            ValueError: If direction is not 1, 2, or 3.
        """
        if direction not in {1, 2, 3}:
            raise ValueError("direction must be 1, 2, or 3")
        super().__init__()
        self.masterNode = masterNode
        self.direction = direction  # Just store the integer directly

    def isMaster(self) -> bool:
        """
        Checks if this node is a master.

        Returns:
            bool: True if this constraint is a master node, False otherwise.
        """
        return self.masterNode is None

    def to_tcl(self) -> str:
        """
        Generates the TCL command for the rigidDiaphragm constraint.

        Returns:
            str: The corresponding OpenSees TCL command.
        """
        return "" if self.isMaster() else f"rigidDiaphragm {self.direction} {self.masterNode._tag} {self._tag}\n"




# Test Cases
if __name__ == "__main__":
    # Create master and slave nodes
    master = mpConstraint()
    master.setTag(1)

    slave = mpConstraint()
    slave.setTag(2)

    # Test equalDOF
    eq_dof = equalDOF(masterNode=master, dofs=[1, 2, 3])
    eq_dof.setTag(2)
    print("equalDOF Test:", eq_dof.to_tcl())  # Expected: "equalDOF 1 2 1 2 3\n"

    # Test rigidLink
    try:
        invalid_link = rigidLink(masterNode=master, type="invalid")
    except ValueError as e:
        print("Caught expected error:", e)

    rl = rigidLink(masterNode=master, type="beam")
    rl.setTag(2)
    print("rigidLink Test:", rl.to_tcl())  # Expected: "rigidLink beam 1 2\n"

    # Test rigidDiaphragm
    try:
        invalid_rd = rigidDiaphragm(masterNode=master, direction=4)
    except ValueError as e:
        print("Caught expected error:", e)

    rd = rigidDiaphragm(masterNode=master, direction=2)
    rd.setTag(2)
    print("rigidDiaphragm Test:", rd.to_tcl())  # Expected: "rigidDiaphragm 2 1 2\n"