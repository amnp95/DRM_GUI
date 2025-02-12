"""
This module defines various mesh part instances with the base class of MeshPart.
It includes the StructuredRectangular3D class, which represents a 3D 
structured rectangular mesh part.It provides functionality to 
initialize, generate, and validate a structured rectangular mesh grid using 
the PyVista library.

Classes:
    StructuredRectangular3D: A class representing a 3D structured rectangular mesh part.

Functions:
    generate_mesh: Generates a structured rectangular mesh.
    get_parameters: Returns a list of parameters for the mesh part type.
    validate_parameters: Validates the input parameters for the mesh part.
    get_compatible_elements: Returns a list of compatible element types.
    update_parameters: Updates the mesh part parameters.

Usage:
    This module is intended to be used as part of the DRM Analyzer application for 
    defining and manipulating 3D structured rectangular mesh parts.
"""
from typing import Dict, List, Tuple, Union
from abc import ABC, abstractmethod
import numpy as np
import pyvista as pv
from meshmaker.components.Mesh.meshPartBase import MeshPart, MeshPartRegistry
from meshmaker.components.Element.elementBase import Element
from meshmaker.components.Region.regionBase import RegionBase



class StructuredRectangular3D(MeshPart):
    """
    Structured Rectangular 3D Mesh Part
    """
    def __init__(self, user_name: str, element: Element, region: RegionBase=None,**kwargs):
        """
        Initialize a 3D Structured Rectangular Mesh Part
        
        Args:
            user_name (str): Unique user name for the mesh part
            element (Optional[Element]): Associated element
        """
        super().__init__(
            category='volume mesh',
            mesh_type='Rectangular Grid',
            user_name=user_name,
            element=element,
            region=region
        )
        kwargs = self.validate_parameters(**kwargs)
        self.params = kwargs if kwargs else {}
        self.generate_mesh()


    def generate_mesh(self) -> pv.UnstructuredGrid:
        """
        Generate a structured rectangular mesh
        
        Returns:
            pv.UnstructuredGrid: Generated mesh
        """
        
        # Extract parameters
        x_min = self.params.get('X Min', 0)
        x_max = self.params.get('X Max', 1)
        y_min = self.params.get('Y Min', 0)
        y_max = self.params.get('Y Max', 1)
        z_min = self.params.get('Z Min', 0)
        z_max = self.params.get('Z Max', 1)
        nx = self.params.get('Nx Cells', 10)
        ny = self.params.get('Ny Cells', 10)
        nz = self.params.get('Nz Cells', 10)
        X = np.linspace(x_min, x_max, nx + 1)
        Y = np.linspace(y_min, y_max, ny + 1)
        Z = np.linspace(z_min, z_max, nz + 1)
        X, Y, Z = np.meshgrid(X, Y, Z, indexing='ij')
        self.mesh = pv.StructuredGrid(X, Y, Z)
        return self.mesh


    @classmethod
    def get_parameters(cls) -> List[Tuple[str, str]]:
        """
        Get the list of parameters for this mesh part type.
        
        Returns:
            List[str]: List of parameter names
        """
        return [
            ("X Min", "Minimum X coordinate (float)"),
            ("X Max", "Maximum X coordinate (float)"),
            ("Y Min", "Minimum Y coordinate (float)"),
            ("Y Max", "Maximum Y coordinate (float)"),
            ("Z Min", "Minimum Z coordinate (float)"),
            ("Z Max", "Maximum Z coordinate (float)"),
            ("Nx Cells", "Number of cells in X direction (integer)"),
            ("Ny Cells", "Number of cells in Y direction (integer)"),
            ("Nz Cells", "Number of cells in Z direction (integer)")
        ]
    

    @classmethod
    def validate_parameters(cls, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the mesh part input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        valid_params = {}
        for param_name in ['X Min', 'X Max', 'Y Min', 'Y Max', 'Z Min', 'Z Max']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = float(kwargs[param_name])
                except ValueError:
                    raise ValueError(f"{param_name} must be a float number")
            else:
                raise ValueError(f"{param_name} parameter is required")
        
        for param_name in ['Nx Cells', 'Ny Cells', 'Nz Cells']:
            if param_name in kwargs:
                try:
                    valid_params[param_name] = int(kwargs[param_name])
                except ValueError:
                    raise ValueError(f"{param_name} must be an integer number")
            else:
                raise ValueError(f"{param_name} parameter is required")
            
        if valid_params['X Min'] >= valid_params['X Max']:
            raise ValueError("X Min must be less than X Max")
        if valid_params['Y Min'] >= valid_params['Y Max']:
            raise ValueError("Y Min must be less than Y Max")
        if valid_params['Z Min'] >= valid_params['Z Max']:
            raise ValueError("Z Min must be less than Z Max")
        
        if valid_params['Nx Cells'] <= 0:
            raise ValueError("Nx Cells must be greater than 0")
        if valid_params['Ny Cells'] <= 0:
            raise ValueError("Ny Cells must be greater than 0")
        if valid_params['Nz Cells'] <= 0:
            raise ValueError("Nz Cells must be greater than 0")
        
        return valid_params
    
    @classmethod
    def get_compatible_elements(cls) -> List[str]:
        """
        Get the list of compatible element types
        Returns:
            List[str]: List of compatible element types
        """
        return ["stdBrick", "bbarBrick", "SSPbrick", "PML3D"]
    


    def update_parameters(self, **kwargs) -> None:
        """
        Update mesh part parameters
        
        Args:
            **kwargs: Keyword arguments to update
        """
        validated_params = self.validate_parameters(**kwargs)
        self.params = validated_params


# Register the 3D Structured Rectangular mesh part type
MeshPartRegistry.register_mesh_part_type('Volume mesh', 'Rectangular Grid', StructuredRectangular3D)
