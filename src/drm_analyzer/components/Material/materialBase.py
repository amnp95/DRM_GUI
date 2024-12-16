from abc import ABC, abstractmethod
from typing import List, Dict, Type

class MaterialTagManager:
    """
    Singleton class for generating sequential integer tags
    """
    _instance = None

    def __new__(cls):
        """
        Override __new__ to ensure only one instance is created
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # Initialize the singleton's attributes
            cls._instance._current_tag = 1
            cls._instance._used_tags = set()
        return cls._instance

    def generate_tag(self) -> int:
        """
        Generate a new unique integer tag
        
        Returns:
            int: A unique integer tag
        """
        # Find the next available tag
        while self._current_tag in self._used_tags:
            self._current_tag += 1
        
        # Mark the tag as used
        self._used_tags.add(self._current_tag)
        
        # Return and increment
        tag = self._current_tag
        self._current_tag += 1
        return tag

    def release_tag(self, tag: int):
        """
        Release a previously used tag, making it available again
        
        Args:
            tag (int): The tag to release
        """
        if tag in self._used_tags:
            self._used_tags.remove(tag)

    def set_start_tag(self, start_number: int):
        """
        Set the starting tag number
        
        Args:
            start_number (int): The first tag number to use
        """
        # Only set if no tags have been used yet
        if not self._used_tags:
            self._current_tag = start_number

    def reset(self):
        """
        Reset the tag manager to its initial state
        Useful for testing or restarting tag generation
        """
        self._current_tag = 1
        self._used_tags.clear()


class Material(ABC):
    """
    Base abstract class for all materials with integer-based tagging
    """
    _materials = {}  # Class-level dictionary to track all materials
    _matTags = {}    # Class-level dictionary to track material tags
    _names = {}      # Class-level dictionary to track material names

    def __init__(self, material_type: str, material_name: str, user_name: str, tag_manager=None):
        """
        Initialize a new material with a unique integer tag
        
        Args:
            material_type (str): The type of material (e.g., 'nDMaterial', 'uniaxialMaterial')
            material_name (str): The specific material name (e.g., 'ElasticIsotropic')
            user_name (str): User-specified name for the material
            tag_manager (MaterialTagManager, optional): Custom tag manager to use
        """
        # Use the provided tag manager or the global one
        tag_manager = MaterialTagManager()
        
        # Generate a unique integer tag
        self.tag = tag_manager.generate_tag()

        if user_name in self._names:
            raise ValueError(f"Material name '{user_name}' already exists")
        
        self.material_type = material_type
        self.material_name = material_name
        self.user_name = user_name
        
        # Register this material in the class-level tracking dictionary
        self._materials[self.tag] = self
        self._matTags[self] = self.tag
        self._names[user_name] = self

    @classmethod
    def set_tag_start(cls, start_number: int):
        """
        Set the starting number for material tags globally
        
        Args:
            start_number (int): The first tag number to use
        """
        global _global_tag_manager
        _global_tag_manager = MaterialTagManager(start_number)

    @classmethod
    def get_all_materials(cls) -> Dict[int, 'Material']:
        """
        Retrieve all created materials.
        
        Returns:
            Dict[int, Material]: A dictionary of all materials, keyed by their unique tags
        """
        return cls._materials

    @classmethod
    def delete_material(cls, tag: int) -> None:
        """
        Delete a material by its tag.
        
        Args:
            tag (int): The tag of the material to delete
        """
        if tag in cls._materials:
            cls._names.pop(cls._materials[tag].user_name)
            cls._matTags.pop(cls._materials[tag])
            cls._materials.pop(tag)
            _global_tag_manager.release_tag(tag)
    
    @classmethod
    def get_material_by_name(cls, name: str) -> 'Material':
        """
        Retrieve a specific material by its user-specified name.
        
        Args:
            name (str): The user-specified name of the material
        
        Returns:
            Material: The material with the specified name
        
        Raises:
            KeyError: If no material with the given name exists
        """
        tag = cls._names[name]
        return cls._materials[tag]
    
    @classmethod  
    @abstractmethod
    def get_parameters(cls) -> List[str]:
        """
        Get the list of parameters for this material type.
        
        Returns:
            List[str]: List of parameter names
        """
        pass

    @classmethod  
    @abstractmethod
    def get_description(cls) -> List[str]:
        """
        Get the list of descriptions for the parameters of this material type.
        
        Returns:
            List[str]: List of parameter descriptions
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        String representation of the material for OpenSees or other purposes.
        
        Returns:
            str: Formatted material definition string
        """
        pass

    def get_values(self, keys: List[str]) -> Dict[str, float]:
        """
        Default implementation to retrieve values for specific parameters.
        
        Args:
            keys (List[str]): List of parameter names to retrieve
        
        Returns:
            Dict[str, float]: Dictionary of parameter values
        """
        return {key: self.params.get(key) for key in keys}
    

    def update_values(self, values: Dict[str, float]) -> None:
        """
        Default implementation to update material parameters.
        
        Args:
            values (Dict[str, float]): Dictionary of parameter names and values to update
        """
        self.params.clear()
        self.params.update(values)
        print(f"Updated parameters: {self.params}")


class MaterialRegistry:
    """
    A registry to manage material types and their creation.
    """
    _material_types = {}

    @classmethod
    def register_material_type(cls, material_category: str, name: str, material_class: Type[Material]):
        """
        Register a new material type for easy creation.
        
        Args:
            material_category (str): The category of material (nDMaterial, uniaxialMaterial)
            name (str): The name of the material type
            material_class (Type[Material]): The class of the material
        """
        if material_category not in cls._material_types:
            cls._material_types[material_category] = {}
        cls._material_types[material_category][name] = material_class

    @classmethod
    def get_material_categories(cls):
        """
        Get available material categories.
        
        Returns:
            List[str]: Available material categories
        """
        return list(cls._material_types.keys())

    @classmethod
    def get_material_types(cls, category: str):
        """
        Get available material types for a given category.
        
        Args:
            category (str): Material category
        
        Returns:
            List[str]: Available material types for the category
        """
        return list(cls._material_types.get(category, {}).keys())

    @classmethod
    def create_material(cls, material_category: str, material_type: str, user_name: str = "Unnamed", **kwargs) -> Material:
        """
        Create a new material of a specific type.
        
        Args:
            material_category (str): Category of material (nDMaterial, uniaxialMaterial)
            material_type (str): Type of material to create
            user_name (str): User-specified name for the material
            **kwargs: Parameters for material initialization
        
        Returns:
            Material: A new material instance
        
        Raises:
            KeyError: If the material category or type is not registered
        """
        if material_category not in cls._material_types:
            raise KeyError(f"Material category {material_category} not registered")
        
        if material_type not in cls._material_types[material_category]:
            raise KeyError(f"Material type {material_type} not registered in {material_category}")
        
        return cls._material_types[material_category][material_type](user_name=user_name, **kwargs)