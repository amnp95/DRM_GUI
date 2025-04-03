from typing import List, Dict, Optional, Union, Type
from .base import AnalysisComponent

class Test(AnalysisComponent):
    """
    Base abstract class for convergence test, which determines if convergence has been achieved
    in nonlinear solution algorithms.
    """
    _tests = {}  # Class-level dictionary to store test types
    _created_tests = {}  # Class-level dictionary to track all created tests
    _next_tag = 1  # Class variable to track the next tag to assign
    
    def __init__(self, test_type: str):
        """
        Initialize a test
        
        Args:
            test_type (str): Type of the test
        """
        self.tag = Test._next_tag
        Test._next_tag += 1
        self.test_type = test_type
        
        # Register this test in the class-level tracking dictionary
        Test._created_tests[self.tag] = self
    
    @staticmethod
    def register_test(name: str, test_class: Type['Test']):
        """
        Register a test type
        
        Args:
            name (str): The name of the test type
            test_class (Type['Test']): The class for the test
        """
        Test._tests[name.lower()] = test_class
    
    @staticmethod
    def create_test(test_type: str, **kwargs) -> 'Test':
        """
        Create a test of the specified type
        
        Args:
            test_type (str): The type of test to create
            **kwargs: Arguments for the test constructor
            
        Returns:
            Test: An instance of the specified test type
            
        Raises:
            ValueError: If the test type is unknown
        """
        test_type = test_type.lower()
        if test_type not in Test._tests:
            raise ValueError(f"Unknown test type: {test_type}")
        return Test._tests[test_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """
        Get available test types
        
        Returns:
            List[str]: List of available test types
        """
        return list(Test._tests.keys())
    
    @classmethod
    def get_test(cls, tag: int) -> 'Test':
        """
        Retrieve a specific test by its tag.
        
        Args:
            tag (int): The tag of the test
        
        Returns:
            Test: The test with the specified tag
        
        Raises:
            KeyError: If no test with the given tag exists
        """
        if tag not in cls._created_tests:
            raise KeyError(f"No test found with tag {tag}")
        return cls._created_tests[tag]

    @classmethod
    def get_all_tests(cls) -> Dict[int, 'Test']:
        """
        Retrieve all created tests.
        
        Returns:
            Dict[int, Test]: A dictionary of all tests, keyed by their unique tags
        """
        return cls._created_tests
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all tests and reset tags.
        """
        cls._created_tests.clear()
        cls._next_tag = 1
    
    def get_values(self) -> Dict[str, Union[str, int, float, bool]]:
        """
        Get the parameters defining this test
        
        Returns:
            Dict[str, Union[str, int, float, bool]]: Dictionary of parameter values
        """
        return {k: v for k, v in self.__dict__.items() if k != 'tag' and k != 'test_type'}

    @classmethod
    def _reassign_tags(cls) -> None:
        """
        Reassign tags to all tests sequentially starting from 1.
        """
        new_tests = {}
        for idx, test in enumerate(sorted(cls._created_tests.values(), key=lambda t: t.tag), start=1):
            test.tag = idx
            new_tests[idx] = test
        cls._created_tests = new_tests
        cls._next_tag = len(cls._created_tests) + 1

    @classmethod
    def remove_test(cls, tag: int) -> None:
        """
        Delete a test by its tag and re-tag all remaining tests sequentially.
        
        Args:
            tag (int): The tag of the test to delete
        """
        if tag in cls._created_tests:
            del cls._created_tests[tag]
            cls._reassign_tags()


class NormUnbalanceTest(Test):
    """
    Norm unbalance test, checks the norm of the residual (unbalanced forces) vector 
    against a tolerance.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        """
        Initialize a NormUnbalance test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
        """
        super().__init__("NormUnbalance")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test NormUnbalance {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class NormDispIncrTest(Test):
    """
    Norm displacement increment test, checks the norm of the displacement 
    increment vector against a tolerance.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        """
        Initialize a NormDispIncr test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
        """
        super().__init__("NormDispIncr")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test NormDispIncr {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class EnergyIncrTest(Test):
    """
    Energy increment test, checks the energy increment (0.5 * x^T * b) against a tolerance.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0):
        """
        Initialize an EnergyIncr test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
        """
        super().__init__("EnergyIncr")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test EnergyIncr {self.tol} {self.max_iter} {self.print_flag}"


class RelativeNormUnbalanceTest(Test):
    """
    Relative norm unbalance test, compares current unbalance to initial unbalance.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        """
        Initialize a RelativeNormUnbalance test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
        """
        super().__init__("RelativeNormUnbalance")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test RelativeNormUnbalance {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class RelativeNormDispIncrTest(Test):
    """
    Relative norm displacement increment test, tracks relative changes in displacement.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        """
        Initialize a RelativeNormDispIncr test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
        """
        super().__init__("RelativeNormDispIncr")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test RelativeNormDispIncr {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class RelativeTotalNormDispIncrTest(Test):
    """
    Relative total norm displacement increment test, tracks cumulative displacement changes.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        """
        Initialize a RelativeTotalNormDispIncr test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
        """
        super().__init__("RelativeTotalNormDispIncr")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test RelativeTotalNormDispIncr {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class RelativeEnergyIncrTest(Test):
    """
    Relative energy increment test, compares energy increment relative to first iteration.
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0):
        """
        Initialize a RelativeEnergyIncr test.
        
        Args:
            tol (float): Tolerance criteria for convergence
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
        """
        super().__init__("RelativeEnergyIncr")
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test RelativeEnergyIncr {self.tol} {self.max_iter} {self.print_flag}"


class FixedNumIterTest(Test):
    """
    Fixed number iterations test, runs a fixed number of iterations without checking convergence.
    """
    def __init__(self, num_iter: int):
        """
        Initialize a FixedNumIter test.
        
        Args:
            num_iter (int): Number of iterations to perform
        """
        super().__init__("FixedNumIter")
        self.num_iter = num_iter
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test FixedNumIter {self.num_iter}"


class NormDispAndUnbalanceTest(Test):
    """
    Norm displacement and unbalance test, requires both displacement and unbalance norms to converge.
    """
    def __init__(self, tol_incr: float, tol_r: float, max_iter: int, 
                 print_flag: int = 0, norm_type: int = 2, max_incr: int = -1):
        """
        Initialize a NormDispAndUnbalance test.
        
        Args:
            tol_incr (float): Tolerance for left-hand solution increments
            tol_r (float): Tolerance for right-hand residual
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
            max_incr (int, optional): Maximum times error can increase 
                                     (-1 for default behavior)
        """
        super().__init__("NormDispAndUnbalance")
        self.tol_incr = tol_incr
        self.tol_r = tol_r
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
        self.max_incr = max_incr
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test NormDispAndUnbalance {self.tol_incr} {self.tol_r} {self.max_iter} {self.print_flag} {self.norm_type} {self.max_incr}"


class NormDispOrUnbalanceTest(Test):
    """
    Norm displacement or unbalance test, convergence achieved if either displacement 
    or unbalance norm criterion is met.
    """
    def __init__(self, tol_incr: float, tol_r: float, max_iter: int, 
                 print_flag: int = 0, norm_type: int = 2, max_incr: int = -1):
        """
        Initialize a NormDispOrUnbalance test.
        
        Args:
            tol_incr (float): Tolerance for left-hand solution increments
            tol_r (float): Tolerance for right-hand residual
            max_iter (int): Maximum iterations before failure
            print_flag (int, optional): Print control flag:
                0: Print nothing (default)
                1: Print norm information each iteration
                2: Print norms and iterations at successful test end
                4: Print norms, displacement vector, and residual vector
                5: Print error message but return successful test
            norm_type (int, optional): Norm type to use:
                0: Max-norm
                1: 1-norm
                2: 2-norm (default)
            max_incr (int, optional): Maximum times error can increase 
                                     (-1 for default behavior)
        """
        super().__init__("NormDispOrUnbalance")
        self.tol_incr = tol_incr
        self.tol_r = tol_r
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
        self.max_incr = max_incr
    
    def to_tcl(self) -> str:
        """
        Convert the test to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        return f"test NormDispOrUnbalance {self.tol_incr} {self.tol_r} {self.max_iter} {self.print_flag} {self.norm_type} {self.max_incr}"


class TestManager:
    """
    Singleton class for managing convergence tests
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TestManager, cls).__new__(cls)
        return cls._instance

    def create_test(self, test_type: str, **kwargs) -> Test:
        """Create a new test"""
        return Test.create_test(test_type, **kwargs)

    def get_test(self, tag: int) -> Test:
        """Get test by tag"""
        return Test.get_test(tag)

    def remove_test(self, tag: int) -> None:
        """Remove test by tag"""
        Test.remove_test(tag)

    def get_all_tests(self) -> Dict[int, Test]:
        """Get all tests"""
        return Test.get_all_tests()

    def get_available_types(self) -> List[str]:
        """Get list of available test types"""
        return Test.get_available_types()
    
    def clear_all(self):
        """Clear all tests"""  
        Test.clear_all()


# Register all tests
Test.register_test('normunbalance', NormUnbalanceTest)
Test.register_test('normdispincr', NormDispIncrTest)
Test.register_test('energyincr', EnergyIncrTest)
Test.register_test('relativenormunbalance', RelativeNormUnbalanceTest)
Test.register_test('relativenormdispincr', RelativeNormDispIncrTest)
Test.register_test('relativetotalnormdispincr', RelativeTotalNormDispIncrTest)
Test.register_test('relativeenergyincr', RelativeEnergyIncrTest)
Test.register_test('fixednumiter', FixedNumIterTest)
Test.register_test('normdispandunbalance', NormDispAndUnbalanceTest)
Test.register_test('normdisporunbalance', NormDispOrUnbalanceTest)