from typing import Dict, List, Union
from ..Material.materialBase import Material
from .elementBase import Element, ElementRegistry



class SSPQuadElement(Element):
    def __init__(self, ndof: int, material: Material, **kwargs):
        super().__init__('SSPQuad', ndof, material)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        """
        Generate the OpenSees element string representation
        
        Example: element SSPquad $type $thick $b1 $b2
        """
        keys = self.get_parameters()
        params_str = " ".join(str(self.params[key]) for key in keys if key in self.params)

        return f"{self._material.tag} {params_str}"
    
    def toString(self, tag :int ,nodes: List[int]) -> str:
        """
        Generate the OpenSees element string representation
        
        Example: element SSPquad $tag $nodes $matTag $type $thick $b1 $b2
        """
        if len(nodes) != 4:
            raise ValueError("SSPQuad element requires 4 nodes")
        keys = self.get_parameters()
        params_str = " ".join(str(self.params[key]) for key in keys if key in self.params)
        nodes_str = " ".join(str(node) for node in nodes)
        tag = str(tag)
        return f"element SSPquad {tag} {nodes_str} {self._material.tag} {params_str}"
    

    @classmethod 
    def get_parameters(cls) -> List[str]:
        """
        Specific parameters for SSPQuadElement
        
        Returns:
            List[str]: Parameters for SSPQuad element
        """
        return ["Type", "Thickness", "b1", "b2"]


    def get_values(self, keys: List[str]) -> Dict[str, Union[int, float, str]]:
        """
        Retrieve values for specific parameters
        
        Args:
            keys (List[str]): List of parameter names to retrieve
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parameter values
        """
        return {key: self.params.get(key) for key in keys}

    def update_values(self, values: Dict[str, Union[int, float, str]]) -> None:
        """
        Update element parameters
        
        Args:
            values (Dict[str, Union[int, float, str]]): Dictionary of parameter names and values to update
        """
        self.params.clear()
        self.params.update(values)
        print(f"Updated parameters: {self.params} \nmaterial:{self._material} \nndof:{self._ndof}  ")

    @classmethod
    def _is_material_compatible(self, material: Material) -> bool:
        """
        Check material compatibility for SSP Quad Element
        
        Returns:
            bool: True if material is a 2D (nDMaterial) type
        """
        return material.material_type == 'nDMaterial'
    
    @classmethod
    def get_possible_dofs(cls) -> List[str]:
        """
        Get the number of possible DOFs for this element type.
        
        Returns:
            List[str]: List of number of possible DOFs
        """
        return ['2']
    
    @classmethod
    def get_description(cls) -> List[str]:
        """
        Get the list of parameter descriptions for this element type.
        
        Returns:
            List[str]: List of parameter descriptions
        """
        return ['Type of element can be either "PlaneStrain" or "PlaneStress" ', 
                'Thickness of the element in out-of-plane direction ',
                'Constant body forces in global x direction',
                'Constant body forces in global y direction'] 
    
    @classmethod
    def validate_element_parameters(self, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the element input parameters are valid.

        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        if 'Type' not in kwargs:
            raise ValueError("Type of element must be specified")
        elif kwargs['Type'] not in ['PlaneStrain', 'PlaneStress']:
            raise ValueError("Element type must be either 'PlaneStrain' or 'PlaneStress'")
        
        if "Thickness" not in kwargs:
            raise ValueError("Thickness must be specified")
        else:
            try:
                kwargs['Thickness'] = float(kwargs['Thickness'])
            except ValueError:
                raise ValueError("Thickness must be a float number")
        
        if "b1" in kwargs:
            try:
                kwargs['b1'] = float(kwargs['b1'])
            except ValueError:
                raise ValueError("b1 must be a float number")
        
        if "b2" in kwargs:
            try:
                kwargs['b2'] = float(kwargs['b2'])
            except ValueError:
                raise ValueError("b2 must be a float number")
            
        return kwargs
        
        


class stdBrickElement(Element):
    def __init__(self, ndof: int, material: Material, **kwargs):
        super().__init__('stdBrick', ndof, material)
        self.params = kwargs if kwargs else {}
        
    def toString(self, tag :int ,nodes: List[int]) -> str:
        """
        Generate the OpenSees element string representation
        
        Example: element stdBrick tag nodes matTag b1 b2 b3

        """
        if len(nodes) != 8:
            raise ValueError("stdBrick element requires 8 nodes")
        keys = self.get_parameters()
        params_str = " ".join(str(self.params[key]) for key in keys if key in self.params)
        nodes_str = " ".join(str(node) for node in nodes)
        tag = str(tag)
        return f"element stdBrick {tag} {nodes_str} {self._material.tag} {params_str}"


    
    @classmethod
    def get_parameters(cls) -> List[str]:
        """
        Specific parameters for stdBrickElement
        
        Returns:
            List[str]: Parameters for stdBrick element
        """
        return ["b1", "b2", "b3"]
    
    def get_values(self, keys: List[str]) -> Dict[str, Union[int, float, str]]:
        """
        Retrieve values for specific parameters
        
        Args:
            keys (List[str]): List of parameter names to retrieve
        
        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parameter values
        """
        return {key: self.params.get(key) for key in keys}
    
    def update_values(self, values: Dict[str, Union[int, float, str]]) -> None:
        """
        Update element parameters
        
        Args:
            values (Dict[str, Union[int, float, str]]): Dictionary of parameter names and values to update
        """
        self.params.clear()
        self.params.update(values)

    @classmethod
    def _is_material_compatible(self, material: Material) -> bool:
        """
        Check material compatibility for stdBrick Element
        
        Returns:
            bool: True if material is a 3D (nDMaterial) type
        """
        return material.material_type == 'nDMaterial'
    
    @classmethod
    def get_possible_dofs(cls) -> List[str]:
        """
        Get the number of possible DOFs for this element type.
        
        Returns:
            List[str]: List of number of possible DOFs
        """
        return ['3']
    
    @classmethod
    def get_description(cls) -> List[str]:
        """
        Get the list of parameter descriptions for this element type.
        
        Returns:
            List[str]: List of parameter descriptions
        """
        return ['Constant body forces in global x direction',
                'Constant body forces in global y direction',
                'Constant body forces in global z direction']
    
    @classmethod
    def validate_element_parameters(self, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the element input parameters are valid.

        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        if "b1" in kwargs:
            try:
                kwargs['b1'] = float(kwargs['b1'])
            except ValueError:
                raise ValueError("b1 must be a float number")
        
        if "b2" in kwargs:
            try:
                kwargs['b2'] = float(kwargs['b2'])
            except ValueError:
                raise ValueError("b2 must be a float number")
        
        if "b3" in kwargs:
            try:
                kwargs['b3'] = float(kwargs['b3'])
            except ValueError:
                raise ValueError("b3 must be a float number")
            
        return kwargs

    
    


        


# =================================================================================================
# Register element types
# =================================================================================================
ElementRegistry.register_element_type('SSPQuad', SSPQuadElement)
ElementRegistry.register_element_type('stdBrick', stdBrickElement)
