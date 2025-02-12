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
    
    def to_tcl(self, tag :int ,nodes: List[int]) -> str:
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
        
    def to_tcl(self, tag :int ,nodes: List[int]) -> str:
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
    

class PML3DElement(Element):
    def __init__(self, ndof: int, material: Material, **kwargs):
        super().__init__('PML3D', ndof, material)
        self.params = kwargs if kwargs else {}

    def to_tcl(self, tag :int ,nodes: List[int]) -> str:
        """
        Generate the OpenSees element string representation
        """
        if len(nodes) != 8:
            raise ValueError("PML3D element requires 8 nodes")
        keys = self.get_parameters()
        eta = self.params.get('eta')
        gamma = self.params.get('gamma')
        beta = self.params.get('beta')
        thickness = self.params.get('PML Thickness')
        m = self.params.get('m')
        R = self.params.get('R')
        RD_half_width_x = self.params.get('RD_half_width_x')
        RD_half_width_y = self.params.get('RD_half_width_y')
        RD_Depth = self.params.get('RD_Depth')
        E = self._material.get_param('E')
        nu = self._material.get_param('nu')
        rho = self._material.get_param('rho')
        elestr = f"element PML {tag} "
        elestr += " ".join(str(node) for node in nodes)
        elestr += f" {eta} {beta} {gamma}"
        elestr += f" {E} {nu} {rho} 6 {thickness} {m} {R} {RD_half_width_x} {RD_half_width_y} {RD_Depth} 0.0 0.0"
        return elestr
    
    @classmethod
    def create_string(cls, tag :int ,nodes: List[int], material: Material, **kwargs) -> str:
        """
        Generate the OpenSees element string representation from class method and parameters.

        This method creates an element string directly without instantiating the class.
        Primarily used for automated absorbing layer generation in the GUI, where creating 
        individual instances for each element would be inefficient.

        Args:
            tag (int): Element tag number
            nodes (List[int]): List of node numbers defining the element
            material (Material): Material properties for the element
            **kwargs: Additional parameters required for PML element

        Returns:
            str: OpenSees element string representation
        """
        if len(nodes) != 8:
            raise ValueError("PML3D element requires 8 nodes")
        # validate parameters first
        kwargs = cls.validate_element_parameters(**kwargs)
        eta = kwargs.get('eta')
        gamma = kwargs.get('gamma')
        beta = kwargs.get('beta')
        thickness = kwargs.get('PML Thickness')
        m = kwargs.get('m')
        R = kwargs.get('R')
        RD_half_width_x = kwargs.get('RD_half_width_x')
        RD_half_width_y = kwargs.get('RD_half_width_y')
        RD_Depth = kwargs.get('RD_Depth')
        E = material.get_param('E')
        nu = material.get_param('nu')
        rho = material.get_param('rho')
        elestr = f"element PML {tag} "
        elestr += " ".join(str(node) for node in nodes)
        elestr += f" {eta} {beta} {gamma}"
        elestr += f" {E} {nu} {rho} 6 {thickness} {m} {R} {RD_half_width_x} {RD_half_width_y} {RD_Depth} 0.0 0.0"


    @classmethod
    def get_parameters(cls) -> List[str]:
        """
        Specific parameters for PML3D
        
        Returns:
            List[str]: Parameters for stdBrick element
        """
        return ["gamma", "beta", "eta", "PML Thickness", "m", "R", "RD_half_width_x", "RD_half_width_y", "RD_Depth"]

    @classmethod
    def get_description(cls) -> List[str]:
        """
        Get the list of parameter descriptions for this element type.
        
        Returns:
            List[str]: List of parameter descriptions
        """
        return ['Newmark gamma parameter',
                'Newmark beta parameter',
                'Newmark eta parameter',
                'Thickness of the PML around regular domain',
                'PML parameter (m=2 is recommended)',
                'PML parameter (R=1e-8 is recommended)',
                'Distance from the PML-regular domain border to the origin along the x-axis',
                'Distance from the PML-regular domain border to the origin along the y-axis',
                'Distance from the PML-regular domain border to the origin along the z-axis']
    
    @classmethod
    def get_possible_dofs(cls) -> List[str]:
        """
        Get the number of possible DOFs for this element type.
        
        Returns:
            List[str]: List of number of possible DOFs
        """
        return ['9']
    
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
        Check material compatibility for PML3D Element
        
        Returns:
            bool: True if material is a 3D (nDMaterial) type and ElasticIsotropicMaterial
        """
        check = (material.material_type == 'nDMaterial') and  (material.__class__.__name__ == 'ElasticIsotropicMaterial')
        return check
    
    @classmethod
    def validate_element_parameters(self, **kwargs) -> Dict[str, Union[int, float, str]]:
        """
        Check if the element input parameters are valid.

        Returns:
            Dict[str, Union[int, float, str]]: Dictionary of parmaeters with valid values
        """
        if "gamma" in kwargs:
            try:
                kwargs['gamma'] = float(kwargs['gamma'])
            except ValueError:
                raise ValueError("gamma must be a float number")
        else:
            raise ValueError("gamma must be specified")
        
        if "beta" in kwargs:
            try:
                kwargs['beta'] = float(kwargs['beta'])
            except ValueError:
                raise ValueError("beta must be a float number")
        else:
            raise ValueError("beta must be specified")
        
        if "eta" in kwargs:
            try:
                kwargs['eta'] = float(kwargs['eta'])
            except ValueError:
                raise ValueError("eta must be a float number")
        else:
            raise ValueError("eta must be specified")
        
        if "PML Thickness" in kwargs:
            try:
                kwargs['PML Thickness'] = float(kwargs['PML Thickness'])
            except ValueError:
                raise ValueError("PML Thickness must be a float number")
        else:
            raise ValueError("PML Thickness must be specified")
        
        if "m" in kwargs:
            try:
                kwargs['m'] = float(kwargs['m'])
            except ValueError:
                raise ValueError("m must be a float number")
        else:
            raise ValueError("m must be specified")
        
        if "R" in kwargs:
            try:
                kwargs['R'] = float(kwargs['R'])
            except ValueError:
                raise ValueError("R must be a float number")
        else:
            raise ValueError("R must be specified")
        
        if "RD_half_width_x" in kwargs:
            try:
                kwargs['RD_half_width_x'] = float(kwargs['RD_half_width_x'])
            except ValueError:
                raise ValueError("RD_half_width_x must be a float number")
        else:
            raise ValueError("RD_half_width_x must be specified")
        
        if "RD_half_width_y" in kwargs:
            try:
                kwargs['RD_half_width_y'] = float(kwargs['RD_half_width_y'])
            except ValueError:
                raise ValueError("RD_half_width_y must be a float number")
        else:
            raise ValueError("RD_half_width_y must be specified")
    
        if "RD_Depth" in kwargs:
            try:
                kwargs['RD_Depth'] = float(kwargs['RD_Depth'])
            except ValueError:
                raise ValueError("RD_Depth must be a float number")
        else:
            raise ValueError("RD_Depth must be specified")
        
        return kwargs
    

    
        
        
    
    

    
    


        


# =================================================================================================
# Register element types
# =================================================================================================
ElementRegistry.register_element_type('SSPQuad', SSPQuadElement)
ElementRegistry.register_element_type('stdBrick', stdBrickElement)
ElementRegistry.register_element_type('PML3D', PML3DElement)
