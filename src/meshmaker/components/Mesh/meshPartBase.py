'''
This module defines the MeshPart abstract base class and the MeshPartRegistry class for managing mesh parts in a DRM  analysis application.
Classes:
    MeshPart(ABC): An abstract base class for mesh parts with various categories and types. It includes methods for generating meshes, managing parameters, and assigning materials and actors.
    MeshPartRegistry: A registry class for managing different types of mesh parts. It allows for the registration, retrieval, and creation of mesh part instances.
    MeshPartManager: A manager class providing advanced mesh part management capabilities, including creation, retrieval, filtering, grouping, validation, and batch operations.
Modules:
    numpy (np): A package for scientific computing with Python.
    pyvista (pv): A 3D plotting and mesh analysis library for Python.
    abc: A module that provides tools for defining abstract base classes.
    typing: A module that provides runtime support for type hints.
    meshmaker.components.Element.elementBase: A module that defines the Element and ElementRegistry classes.
    meshmaker.components.Material.materialBase: A module that defines the Material class.
Usage:
    This module is intended to be used as part of a larger DRM analysis application. 
    The MeshPart class should be subclassed to create specific types of mesh parts, 
    and the MeshPartRegistry and MeshPartManager classes can be used to manage these subclasses.
'''

import numpy as np
import pyvista as pv
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Type, Union, Optional
from femora.components.Element.elementBase import Element
from femora.components.Material.materialBase import Material
from femora.components.Region.regionBase import RegionBase, GlobalRegion


class MeshPart(ABC):
    """
    Abstract base class for mesh parts with various categories and types
    """
    # Class-level tracking of mesh part names to ensure uniqueness
    _mesh_parts = {}

    def __init__(self, category: str, mesh_type: str, user_name: str, element: Element, region: RegionBase=None):
        """
        Initialize a MeshPart instance

        Args:
            category (str): Mesh part category 
            mesh_type (str): Specific type within the category
            user_name (str): User-defined unique name for the mesh part
            element (Optional[Element]): Associated element 
            region (RegionBase): Region to which the mesh part belongs
        """
        # Validate unique user name
        if user_name in self._mesh_parts:
            raise ValueError(f"Mesh part with name '{user_name}' already exists")

        self.category = category
        self.mesh_type = mesh_type
        self.user_name = user_name
        self.element = element
        self.region = region if region is not None else GlobalRegion()
        
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
    def clear_all_mesh_parts(cls) -> None:
        """
        Delete all mesh parts from the registry
        """
        # Create a copy of the keys to avoid modifying dictionary during iteration
        mesh_part_names = list(cls._mesh_parts.keys())
        for user_name in mesh_part_names:
            cls.delete_mesh_part(user_name)

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
    _instance = None
    _mesh_part_types = {
        "Volume mesh" : {},
        "Surface mesh" : {},
        "Line mesh" : {},
        "Point mesh" : {}
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MeshPartRegistry, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
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
    def create_mesh_part(cls, category: str, mesh_part_type: str, user_name: str, element: Element, region: RegionBase , **kwargs) -> MeshPart:
        if mesh_part_type not in cls._mesh_part_types.get(category, {}):
            raise KeyError(f"Mesh part type {mesh_part_type} not registered in {category}")
        
        return cls._mesh_part_types[category][mesh_part_type](user_name, element, region,**kwargs)
    
    @staticmethod
    def get_mesh_part(user_name: str) -> MeshPart:
        return MeshPart._mesh_parts.get(user_name, None)


class MeshPartManager:
    """
    Advanced manager class for mesh parts with extended functionality beyond the registry.
    
    This class provides comprehensive mesh part management capabilities, including creation,
    retrieval, filtering, grouping, validation, and batch operations. It works with the
    MeshPartRegistry to offer a higher-level API for mesh part operations.

    """
    _instance = None
    
    def __new__(cls):
        """Singleton implementation to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(MeshPartManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the MeshPartManager if not already initialized."""
        if not self._initialized:
            self._registry = MeshPartRegistry()
            self._last_operation_status = {"success": True, "message": ""}
            self._initialized = True
    
    def create_mesh_part(self, category: str, mesh_part_type: str, user_name: str, 
                        element: Element, region: RegionBase=None, **kwargs) -> MeshPart:
        """
        Creates a new mesh part with specified parameters.
        
        Args:
            category (str): Mesh part category (e.g., 'Volume mesh', 'Surface mesh')
            mesh_part_type (str): Specific type within the category
            user_name (str): Unique user-defined name for the mesh part
            element (Element): Element to associate with this mesh part
            region (RegionBase, optional): Region to associate with this mesh part
            **kwargs: Type-specific parameters for mesh part generation
            
        Returns:
            MeshPart: The newly created mesh part
            
        Raises:
            KeyError: If the category or mesh part type is not registered
            ValueError: If a mesh part with the provided user_name already exists
        """
        try:
            mesh_part = self._registry.create_mesh_part(category, mesh_part_type, 
                                                      user_name, element, region, **kwargs)
            self._last_operation_status = {
                "success": True, 
                "message": f"Successfully created {category} mesh part '{user_name}'"
            }
            return mesh_part
        except Exception as e:
            self._last_operation_status = {"success": False, "message": str(e)}
            raise
    
    def get_mesh_part(self, user_name: str) -> Optional[MeshPart]:
        """
        Retrieves a mesh part by its user name.
        
        Args:
            user_name (str): User-defined name of the mesh part
            
        Returns:
            Optional[MeshPart]: The requested mesh part or None if not found
        """
        mesh_part = self._registry.get_mesh_part(user_name)
        if mesh_part:
            self._last_operation_status = {
                "success": True, 
                "message": f"Retrieved mesh part '{user_name}'"
            }
        else:
            self._last_operation_status = {
                "success": False, 
                "message": f"Mesh part '{user_name}' not found"
            }
        return mesh_part
    
    def get_all_mesh_parts(self) -> Dict[str, MeshPart]:
        """
        Gets all registered mesh parts.
        
        Returns:
            Dict[str, MeshPart]: Dictionary of all mesh parts by their user names
        """
        mesh_parts = MeshPart.get_mesh_parts()
        self._last_operation_status = {
            "success": True, 
            "message": f"Retrieved {len(mesh_parts)} mesh parts"
        }
        return mesh_parts
    
    def get_mesh_parts_by_category(self, category: str) -> Dict[str, MeshPart]:
        """
        Retrieves mesh parts filtered by category.
        
        Args:
            category (str): Category to filter by (e.g., 'Volume mesh')
            
        Returns:
            Dict[str, MeshPart]: Dictionary of filtered mesh parts by their user names
        """
        mesh_parts = {name: part for name, part in MeshPart.get_mesh_parts().items() 
                     if part.category.lower() == category.lower()}
        self._last_operation_status = {
            "success": True, 
            "message": f"Retrieved {len(mesh_parts)} mesh parts in category '{category}'"
        }
        return mesh_parts
    
    def get_mesh_parts_by_region(self, region: Union[RegionBase, int]) -> Dict[str, MeshPart]:
        """
        Retrieves mesh parts filtered by region.
        
        Args:
            region (Union[RegionBase, int]): Region object or region tag
            
        Returns:
            Dict[str, MeshPart]: Dictionary of filtered mesh parts by their user names
        """
        # Handle case where region is provided as tag number
        if isinstance(region, int):
            region_tag = region
            region = RegionBase.get_region(region_tag)
            if not region:
                self._last_operation_status = {
                    "success": False, 
                    "message": f"Region with tag {region_tag} not found"
                }
                return {}
        
        mesh_parts = {name: part for name, part in MeshPart.get_mesh_parts().items() 
                     if part.region == region}
        self._last_operation_status = {
            "success": True, 
            "message": f"Retrieved {len(mesh_parts)} mesh parts in region '{region.name}'"
        }
        return mesh_parts
    
    def get_mesh_parts_by_element_type(self, element_type: str) -> Dict[str, MeshPart]:
        """
        Retrieves mesh parts filtered by element type.
        
        Args:
            element_type (str): Element type name (e.g., 'stdBrick')
            
        Returns:
            Dict[str, MeshPart]: Dictionary of filtered mesh parts by their user names
        """
        mesh_parts = {name: part for name, part in MeshPart.get_mesh_parts().items() 
                     if part.element and part.element.element_type == element_type}
        self._last_operation_status = {
            "success": True, 
            "message": f"Retrieved {len(mesh_parts)} mesh parts with element type '{element_type}'"
        }
        return mesh_parts
    
    def delete_mesh_part(self, user_name: str) -> bool:
        """
        Deletes a mesh part by its user name.
        
        Args:
            user_name (str): User-defined name of the mesh part to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if user_name in MeshPart.get_mesh_parts():
            MeshPart.delete_mesh_part(user_name)
            self._last_operation_status = {
                "success": True, 
                "message": f"Deleted mesh part '{user_name}'"
            }
            return True
        else:
            self._last_operation_status = {
                "success": False, 
                "message": f"Mesh part '{user_name}' not found"
            }
            return False
    
    def clear_all_mesh_parts(self) -> None:
        """
        Deletes all mesh parts from the registry.
        """
        count = len(MeshPart.get_mesh_parts())
        MeshPart.clear_all_mesh_parts()
        self._last_operation_status = {
            "success": True, 
            "message": f"Cleared {count} mesh parts"
        }
    

    
