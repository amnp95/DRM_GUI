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
        elestr = f"element PML {tag} "
        elestr += " ".join(str(node) for node in nodes)
        elestr += f" {self._material.tag} {self.params.get('PML_Thickness')} {self.params.get('meshType')} "
        elestr += " ".join(str(val) for val in self.params.get('meshTypeParameters', []))
        elestr += f" -Newmark {self.params.get('gamma')} {self.params.get('beta')} {self.params.get('eta')} {self.params.get('ksi')}"
        
        alpha0 = self.params.get("alpha0", None)
        beta0 = self.params.get("beta0", None)
        if alpha0 is not None and beta0 is not None:
            elestr += f" -alphabeta {alpha0} {beta0}"
        else:
            elestr += f" -m {self.params['m']} -R {self.params['R']}"
            if self.params.get('Cp', None) is not None:
                elestr += f" -Cp {self.params['Cp']}"
        return elestr



    @classmethod
    def get_parameters(cls) -> List[str]:
        """
        Specific parameters for PML3D
        
        Returns:
            List[str]: Parameters for stdBrick element
        """
        return ["PML_Thickness", 
                "meshType", "meshTypeParameters",
                "gamma", "beta", "eta", "ksi", 
                "m", "R", "Cp", 
                "alpha0", "beta0"]

    @classmethod
    def get_description(cls) -> List[str]:
        """
        Get the list of parameter descriptions for this element type.
        
        Returns:
            List[str]: List of parameter descriptions
        """
        return ['Thickness of the PML layer',
            'Type of mesh for the PML layer (put 1:"General", 2:"Box")',
            'Parameters for the mesh type (comma separated)',
            "<html>&gamma; parameter for Newmark integration (optional, default=1./2.)",
            "<html>&beta; parameter for Newmark integration (optional, default=1./4.)",
            "<html>&eta; parameter for Newmark integration (optional, default=1./12.)",
            "<html>&xi; parameter for Newmark integration (optional, default=1./48.)",
            'm parameter for Newmark integration (optional, default=2.0)',
            'R parameter for Newmark integration (optional, default=1e-8)',
            'Cp parameter for Newmark integration (optional, calculated from material properties)',
            "&alpha;<sub>0</sub> PML parameter (optional, default=Calculated from m, R, Cp)",
            "&beta;<sub>0</sub> PML parameter (optional, default=Calculated from m, R, Cp)"]
    
    
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
        
        vals = {key: self.params.get(key) for key in keys}
        vals['meshTypeParameters'] = ", ".join(str(val) for val in vals['meshTypeParameters'])
        return vals
    
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

        if 'PML_Thickness' not in kwargs:
            raise ValueError("PML_Thickness must be specified")
        try:
            kwargs['PML_Thickness'] = float(kwargs['PML_Thickness'])
        except (ValueError, TypeError):
            raise ValueError("PML_Thickness must be a float number")
        
        kwargs['meshType'] = kwargs.get('meshType', None)   
        if kwargs['meshType'] is None:
            raise ValueError("meshType must be specified")
        if kwargs['meshType'].lower() not in ["box", "general"]:    
            raise ValueError("meshType must be either 'box' or 'general'")
                   

        try:
            kwargs['meshTypeParameters'] = kwargs.get('meshTypeParameters', None)
            if kwargs['meshTypeParameters'] is None:
                raise ValueError("meshTypeParameters must be specified")
            else:
                values = kwargs['meshTypeParameters'].split(",")
                # delete the space from the end of beginning and end of the string
                values = [value.strip() for value in values]
                
                if kwargs['meshType'].lower() in ["box", "general"]:
                    if len(values) < 6:
                        raise ValueError("meshTypeParameters must be a list of 6 comma separated float numbers")
                    values = values[:6]
                    for i in range(6):
                        values[i] = float(values[i])
                
                kwargs['meshTypeParameters'] = values
        except ValueError:
            raise ValueError("meshTypeParameters must be a list of  6 comma separated float numbers")
        

        try:
            kwargs['gamma'] = float(kwargs.get('gamma', 1./2.))
        except ValueError:
            raise ValueError("gamma must be a float number")
        
        try:
            kwargs['beta'] = float(kwargs.get('beta', 1./4.))
        except ValueError:
            raise ValueError("beta must be a float number")
        
        try:
            kwargs['eta'] = float(kwargs.get('eta', 1./12.))
        except ValueError:
            raise ValueError("eta must be a float number")
        
        try:
            kwargs['ksi'] = float(kwargs.get('ksi', 1./48.))
        except ValueError:
            raise ValueError("ksi must be a float number")
        
        try:
            kwargs['m'] = float(kwargs.get('m', 2.0))
        except ValueError:
            raise ValueError("m must be a float number")
        
        try:
            kwargs['R'] = float(kwargs.get('R', 1e-8))
        except ValueError:
            raise ValueError("R must be a float number")
        

        if "Cp" in kwargs:
            try:
                kwargs['Cp'] = float(kwargs['Cp'])
            except ValueError:
                raise ValueError("Cp must be a float number")
        
        
        
        
        if "alpha0" in kwargs or "beta0" in kwargs:
            if "alpha0" not in kwargs or "beta0" not in kwargs:
                raise ValueError("Both alpha0 and beta0 must be specified together")
            try:
                kwargs["alpha0"] = float(kwargs["alpha0"])
                kwargs["beta0"] = float(kwargs["beta0"])
            except ValueError:
                raise ValueError("alpha0 and beta0 must be float numbers")
        return kwargs
    

    
        
        
    
    

    
    


        


# =================================================================================================
# Register element types
# =================================================================================================
ElementRegistry.register_element_type('SSPQuad', SSPQuadElement)
ElementRegistry.register_element_type('stdBrick', stdBrickElement)
ElementRegistry.register_element_type('PML3D', PML3DElement)
