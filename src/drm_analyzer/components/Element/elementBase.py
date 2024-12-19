from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Union
from drm_analyzer.components.Material.materialBase import Material

class Element(ABC):
    """
    Base abstract class for all elements with material association
    """
    _elements = {}  # Dictionary mapping tags to elements
    _element_to_tag = {}  # Dictionary mapping elements to their tags
    _next_tag = 1  # Track the next available tag

    def __init__(self, element_type: str, ndof: int, material: Material):
        """
        Initialize a new element with a unique integer tag, material, and DOF.

        Args:
            element_type (str): The type of element (e.g., 'quad', 'truss')
            ndof (int): Number of degrees of freedom for the element
            material (Material): Material to assign to this element
        """
        self.element_type = element_type
        self._ndof = ndof

        # Assign and validate the material
        if not self._is_material_compatible(material):
            raise ValueError(f"Material {material} is not compatible with {self.element_type} element")
        self._material = material

        # Assign the next available tag
        self.tag = self._next_tag
        Element._next_tag += 1

        # Register this element in both mapping dictionaries
        Element._elements[self.tag] = self
        Element._element_to_tag[self] = self.tag

    @classmethod
    def _retag_elements(cls):
        """
        Retag all elements sequentially from 1 to n based on their current order.
        Updates both mapping dictionaries.
        """
        # Get all current elements sorted by their tags
        sorted_elements = sorted(cls._elements.items(), key=lambda x: x[0])
        
        # Clear existing mappings
        cls._elements.clear()
        cls._element_to_tag.clear()
        
        # Reassign tags sequentially
        for new_tag, (old_tag, element) in enumerate(sorted_elements, start=1):
            element.tag = new_tag
            cls._elements[new_tag] = element
            cls._element_to_tag[element] = new_tag
        
        # Update next available tag
        cls._next_tag = len(sorted_elements) + 1

    @classmethod
    def delete_element(cls, tag: int) -> None:
        """
        Delete an element by its tag and retag remaining elements.
        
        Args:
            tag (int): The tag of the element to delete
        """
        if tag in cls._elements:
            element = cls._elements[tag]
            # Remove from both dictionaries
            del cls._elements[tag]
            del cls._element_to_tag[element]
            # Retag remaining elements
            cls._retag_elements()

    @classmethod
    def get_element_by_tag(cls, tag: int) -> Optional['Element']:
        """
        Get an element by its tag.
        
        Args:
            tag (int): The tag to look up
            
        Returns:
            Optional[Element]: The element with the given tag, or None if not found
        """
        return cls._elements.get(tag)

    @classmethod
    def get_tag_by_element(cls, element: 'Element') -> Optional[int]:
        """
        Get an element's tag.
        
        Args:
            element (Element): The element to look up
            
        Returns:
            Optional[int]: The tag for the given element, or None if not found
        """
        return cls._element_to_tag.get(element)

    @classmethod
    def set_tag_start(cls, start_number: int):
        """
        Set the starting number for element tags and retag all existing elements.
        
        Args:
            start_number (int): The first tag number to use
        """
        if not cls._elements:
            cls._next_tag = start_number
        else:
            offset = start_number - 1
            # Create new mappings with offset tags
            new_elements = {(tag + offset): element for tag, element in cls._elements.items()}
            new_element_to_tag = {element: (tag + offset) for element, tag in cls._element_to_tag.items()}
            
            # Update all element tags
            for element in cls._elements.values():
                element.tag += offset
            
            # Replace the mappings
            cls._elements = new_elements
            cls._element_to_tag = new_element_to_tag
            cls._next_tag = max(cls._elements.keys()) + 1

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





