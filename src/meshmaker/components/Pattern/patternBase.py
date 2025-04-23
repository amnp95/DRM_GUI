from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union, Type
import numpy as np
from femora.components.TimeSeries.timeSeriesBase import TimeSeries

class Pattern(ABC):
    """
    Base abstract class for all load patterns
    """
    _patterns = {}  # Class-level dictionary to track all patterns
    _next_tag = 1   # Class variable to track the next tag to assign

    def __init__(self, pattern_type: str):
        """
        Initialize a new pattern with a sequential tag
        
        Args:
            pattern_type (str): The type of pattern (e.g., 'UniformExcitation', 'H5DRM')
        """
        self.tag = Pattern._next_tag
        Pattern._next_tag += 1
        
        self.pattern_type = pattern_type
        
        # Register this pattern in the class-level tracking dictionary
        Pattern._patterns[self.tag] = self

    @classmethod
    def get_pattern(cls, tag: int) -> 'Pattern':
        """
        Retrieve a specific pattern by its tag.
        
        Args:
            tag (int): The tag of the pattern
        
        Returns:
            Pattern: The pattern with the specified tag
        
        Raises:
            KeyError: If no pattern with the given tag exists
        """
        if tag not in cls._patterns:
            raise KeyError(f"No pattern found with tag {tag}")
        return cls._patterns[tag]

    @classmethod
    def remove_pattern(cls, tag: int) -> None:
        """
        Delete a pattern by its tag.
        
        Args:
            tag (int): The tag of the pattern to delete
        """
        if tag in cls._patterns:
            del cls._patterns[tag]
            # Recalculate _next_tag if needed
            if cls._patterns:
                cls._next_tag = max(cls._patterns.keys()) + 1
            else:
                cls._next_tag = 1

    @classmethod
    def get_all_patterns(cls) -> Dict[int, 'Pattern']:
        """
        Retrieve all created patterns.
        
        Returns:
            Dict[int, Pattern]: A dictionary of all patterns, keyed by their unique tags
        """
        return cls._patterns
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all patterns and reset tags.
        """
        cls._patterns.clear()
        cls._next_tag = 1

    @abstractmethod
    def to_tcl(self) -> str:
        """
        Convert the pattern to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        pass

    @staticmethod
    def get_parameters() -> List[tuple]:
        """
        Get the parameters defining this pattern
        
        Returns:
            List[tuple]: List of (parameter name, description) tuples
        """
        pass

    @abstractmethod
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this pattern
        
        Returns:
            Dict[str, Union[str, int, float, list]]: Dictionary of parameter values
        """
        pass

    @abstractmethod
    def update_values(self, **kwargs) -> None:
        """
        Update the values of the pattern
        
        Args:
            **kwargs: Parameters for pattern update
        """
        pass


class UniformExcitation(Pattern):
    """
    UniformExcitation pattern allows applying a uniform excitation to a model
    acting in a certain direction.
    """
    def __init__(self, **kwargs):
        """
        Initialize a UniformExcitation pattern
        
        Args:
            dof (int): DOF direction the ground motion acts
            time_series (TimeSeries): TimeSeries defining the acceleration history
            vel0 (float, optional): Initial velocity (default=0.0)
            factor (float, optional): Constant factor (default=1.0)
        """
        super().__init__("UniformExcitation")
        validated_params = self.validate(**kwargs)
        self.dof = validated_params["dof"]
        self.time_series = validated_params["time_series"]
        self.vel0 = validated_params.get("vel0", 0.0)
        self.factor = validated_params.get("factor", 1.0)

    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[int, float, TimeSeries]]:
        """
        Validate parameters for UniformExcitation pattern
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Dict[str, Union[int, float, TimeSeries]]: Validated parameters
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        if "dof" not in kwargs:
            raise ValueError("DOF direction must be specified")
        
        try:
            dof = int(kwargs["dof"])
            if dof < 1:
                raise ValueError("DOF must be a positive integer")
        except ValueError:
            raise ValueError("DOF must be an integer")
        
        if "time_series" not in kwargs:
            raise ValueError("TimeSeries must be specified")
        
        time_series = kwargs["time_series"]
        if not isinstance(time_series, TimeSeries):
            raise ValueError("time_series must be a TimeSeries object")
        
        # Optional parameters
        validated = {"dof": dof, "time_series": time_series}
        
        if "vel0" in kwargs:
            try:
                vel0 = float(kwargs["vel0"])
                validated["vel0"] = vel0
            except ValueError:
                raise ValueError("Initial velocity (vel0) must be a number")
        
        if "factor" in kwargs:
            try:
                factor = float(kwargs["factor"])
                validated["factor"] = factor
            except ValueError:
                raise ValueError("Constant factor must be a number")
        
        return validated

    def to_tcl(self) -> str:
        """
        Convert the UniformExcitation pattern to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = f"pattern UniformExcitation {self.tag} {self.dof} -accel {self.time_series.tag}"
        
        if self.vel0 != 0.0:
            cmd += f" -vel0 {self.vel0}"
        
        if self.factor != 1.0:
            cmd += f" -fact {self.factor}"
            
        return cmd

    @staticmethod
    def get_parameters() -> List[tuple]:
        """
        Get the parameters defining this pattern
        
        Returns:
            List[tuple]: List of (parameter name, description) tuples
        """
        return [
            ("dof", "DOF direction the ground motion acts"),
            ("time_series", "TimeSeries defining the acceleration history"),
            ("vel0", "Initial velocity (optional, default=0.0)"),
            ("factor", "Constant factor (optional, default=1.0)")
        ]

    def get_values(self) -> Dict[str, Union[str, int, float, TimeSeries]]:
        """
        Get the parameters defining this pattern
        
        Returns:
            Dict[str, Union[str, int, float, TimeSeries]]: Dictionary of parameter values
        """
        return {
            "dof": self.dof,
            "time_series": self.time_series,
            "vel0": self.vel0,
            "factor": self.factor
        }

    def update_values(self, **kwargs) -> None:
        """
        Update the values of the pattern
        
        Args:
            **kwargs: Parameters for pattern update
        """
        validated_params = self.validate(**kwargs)
        if "dof" in validated_params:
            self.dof = validated_params["dof"]
        if "time_series" in validated_params:
            self.time_series = validated_params["time_series"]
        if "vel0" in validated_params:
            self.vel0 = validated_params["vel0"]
        if "factor" in validated_params:
            self.factor = validated_params["factor"]


class H5DRMPattern(Pattern):
    """
    H5DRM pattern implements the Domain Reduction Method (DRM) 
    using the H5DRM data format for seismic analysis.
    """
    def __init__(self, **kwargs):
        """
        Initialize a H5DRM pattern
        
        Args:
            filepath (str): Path to the H5DRM dataset
            factor (float): Scale factor for DRM forces and displacements
            crd_scale (float): Scale factor for dataset coordinates
            distance_tolerance (float): Tolerance for DRM point to FE mesh matching
            do_coordinate_transformation (int): Whether to apply coordinate transformation
            transform_matrix (list): 3x3 transformation matrix [T00, T01, T02, T10, T11, T12, T20, T21, T22]
            origin (list): Origin location after transformation [x00, x01, x02]
        """
        super().__init__("H5DRM")
        validated_params = self.validate(**kwargs)
        self.filepath = validated_params["filepath"]
        self.factor = validated_params["factor"]
        self.crd_scale = validated_params["crd_scale"]
        self.distance_tolerance = validated_params["distance_tolerance"]
        self.do_coordinate_transformation = validated_params["do_coordinate_transformation"]
        self.transform_matrix = validated_params["transform_matrix"]
        self.origin = validated_params["origin"]

    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, float, int, list]]:
        """
        Validate parameters for H5DRM pattern
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Dict[str, Union[str, float, int, list]]: Validated parameters
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        required_params = [
            "filepath", "factor", "crd_scale", "distance_tolerance", 
            "do_coordinate_transformation"
        ]
        
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Required parameter '{param}' is missing")
        
        validated = {}
        
        # Validate filepath
        validated["filepath"] = str(kwargs["filepath"])
        
        # Validate numeric parameters
        numeric_params = ["factor", "crd_scale", "distance_tolerance"]
        for param in numeric_params:
            try:
                validated[param] = float(kwargs[param])
            except ValueError:
                raise ValueError(f"Parameter '{param}' must be a number")
        
        # Validate coordinate transformation flag
        try:
            do_transform = int(kwargs["do_coordinate_transformation"])
            if do_transform not in [0, 1]:
                raise ValueError("do_coordinate_transformation must be 0 or 1")
            validated["do_coordinate_transformation"] = do_transform
        except ValueError:
            raise ValueError("do_coordinate_transformation must be an integer (0 or 1)")
        
        # Validate transformation matrix
        transform_keys = ["T00", "T01", "T02", "T10", "T11", "T12", "T20", "T21", "T22"]
        if "transform_matrix" in kwargs:
            transform_matrix = kwargs["transform_matrix"]
            if len(transform_matrix) != 9:
                raise ValueError("transform_matrix must be a list of 9 values")
            validated["transform_matrix"] = transform_matrix
        else:
            # Check for individual transformation parameters
            transform_matrix = []
            for key in transform_keys:
                if key not in kwargs:
                    raise ValueError(f"Required transformation parameter '{key}' is missing")
                try:
                    transform_matrix.append(float(kwargs[key]))
                except ValueError:
                    raise ValueError(f"Transformation parameter '{key}' must be a number")
            validated["transform_matrix"] = transform_matrix
        
        # Validate origin
        origin_keys = ["x00", "x01", "x02"]
        if "origin" in kwargs:
            origin = kwargs["origin"]
            if len(origin) != 3:
                raise ValueError("origin must be a list of 3 values")
            validated["origin"] = origin
        else:
            # Check for individual origin parameters
            origin = []
            for key in origin_keys:
                if key not in kwargs:
                    raise ValueError(f"Required origin parameter '{key}' is missing")
                try:
                    origin.append(float(kwargs[key]))
                except ValueError:
                    raise ValueError(f"Origin parameter '{key}' must be a number")
            validated["origin"] = origin
        
        return validated

    def to_tcl(self) -> str:
        """
        Convert the H5DRM pattern to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        # Extract transformation matrix and origin values
        T00, T01, T02, T10, T11, T12, T20, T21, T22 = self.transform_matrix
        x00, x01, x02 = self.origin
        
        cmd = f'pattern H5DRM {self.tag} "{self.filepath}" {self.factor} {self.crd_scale} '
        cmd += f'{self.distance_tolerance} {self.do_coordinate_transformation} '
        cmd += f'{T00} {T01} {T02} {T10} {T11} {T12} {T20} {T21} {T22} '
        cmd += f'{x00} {x01} {x02}'
        
        return cmd

    @staticmethod
    def get_parameters() -> List[tuple]:
        """
        Get the parameters defining this pattern
        
        Returns:
            List[tuple]: List of (parameter name, description) tuples
        """
        return [
            ("filepath", "Path to the H5DRM dataset"),
            ("factor", "Scale factor for DRM forces and displacements"),
            ("crd_scale", "Scale factor for dataset coordinates"),
            ("distance_tolerance", "Tolerance for DRM point to FE mesh matching"),
            ("do_coordinate_transformation", "Whether to apply coordinate transformation (0/1)"),
            ("transform_matrix", "3x3 transformation matrix [T00, T01, T02, T10, T11, T12, T20, T21, T22]"),
            ("origin", "Origin location after transformation [x00, x01, x02]")
        ]

    def get_values(self) -> Dict[str, Union[str, float, int, list]]:
        """
        Get the parameters defining this pattern
        
        Returns:
            Dict[str, Union[str, float, int, list]]: Dictionary of parameter values
        """
        return {
            "filepath": self.filepath,
            "factor": self.factor,
            "crd_scale": self.crd_scale,
            "distance_tolerance": self.distance_tolerance,
            "do_coordinate_transformation": self.do_coordinate_transformation,
            "transform_matrix": self.transform_matrix,
            "origin": self.origin
        }

    def update_values(self, **kwargs) -> None:
        """
        Update the values of the pattern
        
        Args:
            **kwargs: Parameters for pattern update
        """
        validated_params = self.validate(**kwargs)
        for key, value in validated_params.items():
            setattr(self, key, value)


class PatternRegistry:
    """
    A registry to manage pattern types and their creation.
    """
    _pattern_types = {
        'uniformexcitation': UniformExcitation,
        'h5drm': H5DRMPattern
    }

    @classmethod
    def register_pattern_type(cls, name: str, pattern_class: Type[Pattern]):
        """
        Register a new pattern type for easy creation.
        
        Args:
            name (str): The name of the pattern type
            pattern_class (Type[Pattern]): The class of the pattern
        """
        cls._pattern_types[name.lower()] = pattern_class

    @classmethod
    def get_pattern_types(cls):
        """
        Get available pattern types.
        
        Returns:
            List[str]: Available pattern types
        """
        return list(cls._pattern_types.keys())

    @classmethod
    def create_pattern(cls, pattern_type: str, **kwargs) -> Pattern:
        """
        Create a new pattern of a specific type.
        
        Args:
            pattern_type (str): Type of pattern to create
            **kwargs: Parameters for pattern initialization
        
        Returns:
            Pattern: A new pattern instance
        
        Raises:
            KeyError: If the pattern type is not registered
        """
        if pattern_type.lower() not in cls._pattern_types:
            raise KeyError(f"Pattern type {pattern_type} not registered")
        
        return cls._pattern_types[pattern_type.lower()](**kwargs)


class PatternManager:
    """
    Singleton class for managing load patterns
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PatternManager, cls).__new__(cls)
        return cls._instance

    def create_pattern(self, pattern_type: str, **kwargs) -> Pattern:
        """Create a new pattern"""
        return PatternRegistry.create_pattern(pattern_type, **kwargs)

    def get_pattern(self, tag: int) -> Pattern:
        """Get pattern by tag"""
        return Pattern.get_pattern(tag)

    def remove_pattern(self, tag: int) -> None:
        """Remove pattern by tag"""
        Pattern.remove_pattern(tag)

    def get_all_patterns(self) -> Dict[int, Pattern]:
        """Get all patterns"""
        return Pattern.get_all_patterns()

    def get_available_types(self) -> List[str]:
        """Get list of available pattern types"""
        return PatternRegistry.get_pattern_types()
    
    def clear_all(self):
        """Clear all patterns"""  
        Pattern.clear_all()