from typing import List, Dict, Type
from .base import AnalysisComponent

class Test(AnalysisComponent):
    """
    Base abstract class for convergence test, which determines if convergence has been achieved
    """
    _tests = {}  # Class-level dictionary to store test types
    
    @staticmethod
    def register_test(name: str, test_class: Type['Test']):
        """Register a test type"""
        Test._tests[name.lower()] = test_class
    
    @staticmethod
    def create_test(test_type: str, **kwargs) -> 'Test':
        """Create a test of the specified type"""
        test_type = test_type.lower()
        if test_type not in Test._tests:
            raise ValueError(f"Unknown test type: {test_type}")
        return Test._tests[test_type](**kwargs)
    
    @staticmethod
    def get_available_types() -> List[str]:
        """Get available test types"""
        return list(Test._tests.keys())


class NormUnbalanceTest(Test):
    """
    Norm unbalance test, checks the norm of the residual vector against a tolerance
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        return f"test NormUnbalance {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


class NormDispIncrTest(Test):
    """
    Norm displacement increment test, checks the norm of the displacement increment vector against a tolerance
    """
    def __init__(self, tol: float, max_iter: int, print_flag: int = 0, norm_type: int = 2):
        self.tol = tol
        self.max_iter = max_iter
        self.print_flag = print_flag
        self.norm_type = norm_type
    
    def to_tcl(self) -> str:
        return f"test NormDispIncr {self.tol} {self.max_iter} {self.print_flag} {self.norm_type}"


# Register all tests
Test.register_test('normunbalance', NormUnbalanceTest)
Test.register_test('normdispincr', NormDispIncrTest)