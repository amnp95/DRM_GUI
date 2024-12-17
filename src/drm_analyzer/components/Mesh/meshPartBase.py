'''
This module defines the MeshPart abstract base class and the MeshPartRegistry class for managing mesh parts in a DRM  analysis application.
Classes:
    MeshPart(ABC): An abstract base class for mesh parts with various categories and types. It includes methods for generating meshes, managing parameters, and assigning materials and actors.
    MeshPartRegistry: A registry class for managing different types of mesh parts. It allows for the registration, retrieval, and creation of mesh part instances.
Modules:
    numpy (np): A package for scientific computing with Python.
    pyvista (pv): A 3D plotting and mesh analysis library for Python.
    abc: A module that provides tools for defining abstract base classes.
    typing: A module that provides runtime support for type hints.
    drm_analyzer.components.Element.elementBase: A module that defines the Element and ElementRegistry classes.
    drm_analyzer.components.Material.materialBase: A module that defines the Material class.
Usage:
    This module is intended to be used as part of a larger DRM analysis application. 
    The MeshPart class should be subclassed to create specific types of mesh parts, 
    and the MeshPartRegistry class can be used to manage these subclasses.
'''

import numpy as np
import pyvista as pv
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Type, Union
from drm_analyzer.components.Element.elementBase import Element, ElementRegistry
from drm_analyzer.components.Material.materialBase import Material


class MeshPart(ABC):
    """
    Abstract base class for mesh parts with various categories and types
    """
    # Class-level tracking of mesh part names to ensure uniqueness
    _mesh_parts = {}

    def __init__(self, category: str, mesh_type: str, user_name: str, element: Element):
        """
        Initialize a MeshPart instance

        Args:
            category (str): Mesh part category 
            mesh_type (str): Specific type within the category
            user_name (str): User-defined unique name for the mesh part
            element (Optional[Element]): Associated element 
        """
        # Validate unique user name
        if user_name in self._mesh_parts:
            raise ValueError(f"Mesh part with name '{user_name}' already exists")

        self.category = category
        self.mesh_type = mesh_type
        self.user_name = user_name
        self.element = element
        
        # Generate mesh based on type and kwargs
        self.mesh = None
        
        # Optional pyvista actor (initially None)
        self.actor = None

        # Register the mesh part
        self._mesh_parts[user_name] = self

    @abstractmethod
    def generate_mesh(self) -> None:
        """
        Abstract method to generate a pyvista mesh
        
        Args:
            **kwargs: Keyword arguments specific to mesh generation
        
        Returns:
            pv.UnstructuredGrid: Generated mesh
        """
        pass

    @classmethod
    def get_mesh_parts(cls) -> Dict[str, 'MeshPart']:
        """
        Get all registered mesh parts
        
        Returns:
            Dict[str, MeshPart]: Dictionary of mesh parts by user name
        """
        return cls._mesh_parts

    @classmethod
    def delete_mesh_part(cls, user_name: str):
        """
        Delete a mesh part by its user name
        
        Args:
            user_name (str): User name of the mesh part to delete
        """
        if user_name in cls._mesh_parts:
            del cls._mesh_parts[user_name]

    @classmethod
    @abstractmethod
    def get_parameters(cls) -> List[Tuple[str, str]]:
        """
        Get the list of parameters for this mesh part type.
        
        Returns:
            List[(str,str)]: List of parameter names
        """
        pass

    @classmethod
    @abstractmethod
    def validate_parameters(cls, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the mesh part input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        pass

    @classmethod
    @abstractmethod
    def get_compatible_elements(cls) -> List[str]:
        """
        Get the list of compatible element types

        Returns:
            List[str]: List of compatible element types
        """
        pass

    @abstractmethod
    def update_parameters(self, **kwargs) -> None:
        """
        Update mesh part parameters
        
        Args:
            **kwargs: Keyword arguments to update
        """
        pass

    
    def assign_material(self, material: Material) -> None:
        """
        Assign a material to the mesh part

        Args:
            material (Material): Material to assign
        """
        if self.element.material is not None:
            self.element.assign_material(material)
        else:
            raise ValueError("No material to assign to the element")
        
    def assign_actor(self, actor) -> None:
        """
        Assign a pyvista actor to the mesh part
        
        Args:
            actor: Pyvista actor to assign
        """
        self.actor = actor



# Optional: Add to registry if needed
class MeshPartRegistry:
    _mesh_part_types = {
        "Volume mesh" : {},
        "Surface mesh" : {},
        "Line mesh" : {},
        "Point mesh" : {}
    }
    
    @classmethod
    def register_mesh_part_type(cls, category: str ,name: str, mesh_part_class: Type[MeshPart]):
        if category not in cls._mesh_part_types.keys():
            raise KeyError(f"Mesh part category {category} not registered")
        if name in cls._mesh_part_types[category]:
            raise KeyError(f"Mesh part type {name} already registered in {category}")
        if not issubclass(mesh_part_class, MeshPart):
            raise TypeError("Mesh part class must be a subclass of MeshPart")
        
        cls._mesh_part_types[category][name] = mesh_part_class
    
    @classmethod
    def get_mesh_part_types(cls, category: str):
        return list(cls._mesh_part_types.get(category, {}).keys())
    
    @classmethod
    def get_mesh_part_categories(cls):
        return list(cls._mesh_part_types.keys())
    
    @classmethod
    def create_mesh_part(cls, category: str, mesh_part_type: str, user_name: str, element: Element, **kwargs) -> MeshPart:
        if mesh_part_type not in cls._mesh_part_types.get(category, {}):
            raise KeyError(f"Mesh part type {mesh_part_type} not registered in {category}")
        
        return cls._mesh_part_types[mesh_part_type](user_name, element, **kwargs)
