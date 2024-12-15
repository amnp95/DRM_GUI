from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Union
from ..Material.materialBase import Material

class ElementTagManager:
    """
    Singleton class for generating sequential integer tags for elements
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


class Element(ABC):
    """
    Base abstract class for all elements with material association
    """
    _elements = {}  # Class-level dictionary to track all elements
    _elementTags = {}  # Class-level dictionary to track element tags
    _class_tag_manager = ElementTagManager()

    def __init__(self, element_type: str, ndof: int, material: Material):
        """
        Initialize a new element with a unique integer tag, material, and DOF.

        Args:
            element_type (str): The type of element (e.g., 'quad', 'truss')
            ndof (int): Number of degrees of freedom for the element
            material (Material): Material to assign to this element
        """
        # Generate a unique integer tag
        self.tag = self._class_tag_manager.generate_tag()

        self.element_type = element_type
        self._ndof = ndof  # Assign ndof directly

        # Assign and validate the material
        if not self._is_material_compatible(material):
            raise ValueError(f"Material {material} is not compatible with {self.element_type} element")
        self._material = material

        # Register this element in the class-level tracking dictionary
        self._elements[self.tag] = self
        self._elementTags[self] = self.tag

    def assign_material(self, material: Material):
        """
        Assign a material to the element
        
        Args:
            material (Material): The material to assign to this element
        """
        # Validate material type compatibility 
        if not self._is_material_compatible(material):
            raise ValueError(f"Material {material} is not compatible with {self.element_type} element")
        
        self._material = material

    def assign_ndof(self, ndof: int):
        """
        Assign the number of DOFs for the element
        
        Args:
            ndof (int): Number of DOFs for the element
        """
        self._ndof = ndof


    def get_material(self) -> Optional[Material]:
        """
        Retrieve the assigned material
        
        Returns:
            Optional[Material]: The material assigned to this element, or None
        """
        return self._material

    @classmethod
    @abstractmethod
    def _is_material_compatible(self, material: Material) -> bool:
        """
        Check if the given material is compatible with this element type
        
        Args:
            material (Material): Material to check for compatibility
        
        Returns:
            bool: Whether the material is compatible
        """
        pass

    @classmethod
    def set_tag_start(cls, start_number: int):
        """
        Set the starting number for element tags globally
        
        Args:
            start_number (int): The first tag number to use
        """
        cls._class_tag_manager.set_start_tag(start_number)

    @classmethod
    def get_all_elements(cls) -> Dict[int, 'Element']:
        """
        Retrieve all created elements.
        
        Returns:
            Dict[int, Element]: A dictionary of all elements, keyed by their unique tags
        """
        return cls._elements

    @classmethod
    def delete_element(cls, tag: int) -> None:
        """
        Delete an element by its tag.
        
        Args:
            tag (int): The tag of the element to delete
        """
        if tag in cls._elements:
            cls._elementTags.pop(cls._elements[tag])
            cls._elements.pop(tag)
            cls._class_tag_manager.release_tag(tag)
    
    @classmethod  
    @abstractmethod
    def get_parameters(cls) -> List[str]:
        """
        Get the list of parameters for this element type.
        
        Returns:
            List[str]: List of parameter names
        """
        pass

    @classmethod
    @abstractmethod
    def get_possible_dofs(cls) -> List[str]:
        """
        Get the list of possible DOFs for this element type.
        
        Returns:
            List[str]: List of possible DOFs
        """
        pass

    @classmethod
    @abstractmethod
    def get_description(cls) -> List[str]:
        """
        Get the list of parameter descriptions for this element type.
        
        Returns:
            List[str]: List of parameter descriptions
        """
        pass

    @classmethod
    @abstractmethod
    def get_parameters_type(cls) -> List[str]:
        """
        Get the list of parameter types for this element type.
        
        Returns:
            List[str]: List of parameter types
        """
        pass

    @classmethod
    @abstractmethod
    def validate_element_parameters(self, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the element input parameters are valid.
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        pass

    @abstractmethod
    def get_values(self, keys: List[str]) -> Dict[str,  Union[int, float, str]]:
        """
        Retrieve values for specific parameters.
        
        Args:
            keys (List[str]): List of parameter names to retrieve
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parameter values
        """
        pass

    @abstractmethod
    def update_values(self, values: Dict[str, Union[int, float, str]]) -> None:
        """
        Update element parameters.
        
        Args:
            values (Dict[str, Union[int, float, str]]): Dictionary of parameter names and values to update
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        String representation of the element for OpenSees or other purposes.
        
        Returns:
            str: Formatted element definition string
        """
        pass



class ElementRegistry:
    """
    A registry to manage element types and their creation.
    """
    _element_types = {}

    @classmethod
    def register_element_type(cls, name: str, element_class: Type[Element]):
        """
        Register a new element type for easy creation.
        
        Args:
            name (str): The name of the element type
            element_class (Type[Element]): The class of the element
        """
        cls._element_types[name] = element_class

    @classmethod
    def get_element_types(cls):
        """
        Get available element types.
        
        Returns:
            List[str]: Available element types
        """
        return list(cls._element_types.keys())

    @classmethod
    def create_element(cls, element_type: str, ndof: int, material: Material, **kwargs) -> Element:
        """
        Create a new element of a specific type.

        Args:
            element_type (str): Type of element to create
            ndof (int): Number of degrees of freedom for the element
            material (Material): Material to assign to the element
            **kwargs: Parameters for element initialization

        Returns:
            Element: A new element instance

        Raises:
            KeyError: If the element type is not registered
        """

        if element_type not in cls._element_types:
            raise KeyError(f"Element type {element_type} not registered")
        
        return cls._element_types[element_type](ndof, material, **kwargs)





