from typing import Dict, List, Optional, Any
from .materialBase import Material, MaterialRegistry

class MaterialManager:
    """
    Singleton class for managing mesh materials and properties
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MaterialManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance


    def _initialize(self):
        """Initialize the singleton instance"""
        pass


    def create_material(self, 
                       material_category: str, 
                       material_type: str, 
                       user_name: str, 
                       **material_params) -> Material:
        """
        Create a new material with the given parameters
        
        Args:
            material_category (str): Category of material (e.g., 'nDMaterial')
            material_type (str): Type of material (e.g., 'Concrete')
            user_name (str): Unique name for the material
            **material_params: Material-specific parameters
            
        Returns:
            Material: The created material instance
            
        Raises:
            KeyError: If material category or type doesn't exist
            ValueError: If material name already exists
        """
        return MaterialRegistry.create_material(
            material_category=material_category,
            material_type=material_type,
            user_name=user_name,
            **material_params
        )


    def get_material(self, identifier: Any) -> Material:
        """
        Get material by either tag or name
        
        Args:
            identifier: Either material tag (int) or user_name (str)
            
        Returns:
            Material: The requested material
            
        Raises:
            KeyError: If material not found
            TypeError: If identifier type is invalid
        """
        if isinstance(identifier, int):
            return Material.get_material_by_tag(identifier)
        elif isinstance(identifier, str):
            return Material.get_material_by_name(identifier)
        else:
            raise TypeError("Identifier must be either tag (int) or name (str)")


    def update_material_params(self, 
                             identifier: Any, 
                             new_params: Dict[str, float]) -> None:
        """
        Update parameters of an existing material
        
        Args:
            identifier: Either material tag (int) or user_name (str)
            new_params: Dictionary of parameter names and new values
            
        Raises:
            KeyError: If material not found
        """
        material = self.get_material(identifier)
        material.update_values(new_params)


    def delete_material(self, identifier: Any) -> None:
        """
        Delete a material by its identifier
        
        Args:
            identifier: Either material tag (int) or user_name (str)
            
        Raises:
            KeyError: If material not found
        """
        if isinstance(identifier, str):
            material = Material.get_material_by_name(identifier)
            Material.delete_material(material.tag)
        elif isinstance(identifier, int):
            Material.delete_material(identifier)
        else:
            raise TypeError("Identifier must be either tag (int) or name (str)")


    def get_all_materials(self) -> Dict[int, Material]:
        """
        Get all registered materials
        
        Returns:
            Dict[int, Material]: Dictionary of all materials keyed by their tags
        """
        return Material.get_all_materials()


    def get_available_material_types(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get available material types, optionally filtered by category
        
        Args:
            category (str, optional): Specific category to get types for
            
        Returns:
            Dict[str, List[str]]: Dictionary of categories and their material types
        """
        if category:
            return {category: MaterialRegistry.get_material_types(category)}
        
        return {
            cat: MaterialRegistry.get_material_types(cat)
            for cat in MaterialRegistry.get_material_categories()
        }


    def set_material_tag_start(self, start_number: int) -> None:
        """
        Set the starting number for material tags
        
        Args:
            start_number (int): Starting tag number (must be > 0)
            
        Raises:
            ValueError: If start_number < 1
        """
        Material.set_tag_start(start_number)


    def clear_all_materials(self) -> None:
        """Clear all registered materials and reset tags"""
        Material.clear_all()


    @classmethod
    def get_instance(cls, **kwargs):
        """
        Get the singleton instance of MaterialManager
        
        Args:
            **kwargs: Keyword arguments to pass to the constructor
            
        Returns:
            MaterialManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance