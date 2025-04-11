from typing import List, Dict
from .materialBase import Material, MaterialRegistry
from typing import Union


class ElasticIsotropicMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        # validate the parameters
        kwargs = self.validate(**kwargs)
        super().__init__('nDMaterial', 'ElasticIsotropic', user_name)
        self.params = kwargs if kwargs else {}

    
    def to_tcl(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)

        return f"{self.material_type} ElasticIsotropic {self.tag} {params_str}; # {self.user_name}"
    
    @staticmethod
    def validate(**params) -> Dict[str, Union[float, int, str, None]]:
        # Extract and validate E
        E = params.get("E")
        if E is None:
            raise ValueError("ElasticIsotropicMaterial requires the 'E' parameter.")
        try:
            E = float(E)
            if E <= 0:
                raise ValueError("Elastic modulus 'E' must be positive.")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'E'. It must be a positive number.")

        # Extract and validate nu
        nu = params.get("nu")
        if nu is None:
            raise ValueError("ElasticIsotropicMaterial requires the 'nu' parameter.")
        try:
            nu = float(nu)
            if not (0 <= nu < 0.5):
                raise ValueError("Poisson's ratio 'nu' must be in the range [0, 0.5).")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'nu'. It must be a number in range [0, 0.5).")

        # Extract and validate rho
        rho = params.get("rho", 0.0)
        try:
            rho = float(rho)
            if rho < 0:
                raise ValueError("Density 'rho' must be non-negative.")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'rho'. It must be a non-negative number.")

        return {"E": E, "nu": nu, "rho": rho}
        
    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ["E", "nu", "rho"]
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Young\'s modulus', 
                'Poisson\'s ratio', 
                'Mass density of the material']
    


class ElasticUniaxialMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        # validate the parameters
        kwargs = self.validate(**kwargs)
        super().__init__('uniaxialMaterial', 'Elastic', user_name)
        self.params = kwargs if kwargs else {}

    def to_tcl(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)
        return f"{self.material_type} Elastic {self.tag} {params_str}; # {self.user_name}"
    
    @staticmethod
    def validate(**params) -> Dict[str, Union[float, int, str, None]]:
        # Extract and validate E
        E = params.get("E")
        if E is None:
            raise ValueError("ElasticUniaxialMaterial requires the 'E' parameter.")
        try:
            E = float(E)
            if E <= 0:
                raise ValueError("Elastic modulus 'E' must be positive.")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'E'. It must be a positive number.")

        # Extract and validate eta
        eta = params.get("eta", 0.0)
        try:
            eta = float(eta)
            if eta < 0:
                raise ValueError("Damping ratio 'eta' must be non-negative.")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'eta'. It must be a non-negative number.")

        # Extract and validate Eneg
        Eneg = params.get("Eneg", E)
        try:
            Eneg = float(Eneg)
            if Eneg <= 0:
                raise ValueError("Negative elastic modulus 'Eneg' must be positive.")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'Eneg'. It must be a positive number.")

        return {"E": E, "eta": eta, "Eneg": Eneg}
        
    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ["E", "eta", "Eneg"]
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Tangent', 
                'Damping tangent (optional, default=0.0)',
                'Tangent in compression (optional, default=E)']
    




class J2CyclicBoundingSurfaceMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        # validate parameters
        kwargs = self.validate(**kwargs)
        super().__init__('nDMaterial', 'J2CyclicBoundingSurface', user_name)
        self.params = kwargs if kwargs else {}

    def to_tcl(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)
        return f"{self.material_type} J2CyclicBoundingSurface {self.tag} {params_str}; # {self.user_name}"
    
    @staticmethod
    def validate(**params) -> Dict[str, Union[float, int, str, None]]:
        required_params = ['G', 'K', 'Su', 'Den', 'h', 'm', 'h0', 'chi']
        validated_params = {}
        
        # Check required parameters
        for param in required_params:
            value = params.get(param)
            if value is None:
                raise ValueError(f"J2CyclicBoundingSurfaceMaterial requires the '{param}' parameter.")
            
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for '{param}'. It must be a number.")
            
            # Specific validations
            if param in ['G', 'K', 'Su'] and value <= 0:
                raise ValueError(f"'{param}' must be positive.")
            if param == 'Den' and value < 0:
                raise ValueError("Mass density 'Den' must be non-negative.")
            
            validated_params[param] = value
            
        # Optional parameter
        beta = params.get('beta', 0.5)  # Default value
        try:
            beta = float(beta)
            if not (0 <= beta <= 1):
                raise ValueError("Integration variable 'beta' must be in range [0, 1].")
        except (ValueError, TypeError):
            raise ValueError("Invalid value for 'beta'. It must be a number in range [0, 1].")
        
        validated_params['beta'] = beta
        
        return validated_params
    
    @classmethod
    def get_parameters(cls) -> List[str]:
        return ['G', 'K', 'Su', 'Den', 'h', 'm', 'h0', 'chi', 'beta']
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Shear modulus', 
                'Bulk modulus',
                'Undrained shear strength',
                'Mass density',
                'Hardening parameter',
                'Hardening exponent',
                'Initial hardening parameter',
                'Initial damping (viscous). chi = 2*dr_o/omega (dr_o = damping ratio at zero strain, omega = angular frequency)',
                'Integration variable (0 = explicit, 1 = implicit, 0.5 = midpoint rule)']
    

    def updateMaterialStage(self, state: str)-> str:
        if state.lower() == 'elastic':
            return "updateMaterialStage -material {self.tag} -stage 0"
        elif state.lower() == 'plastic':
            return "updateMaterialStage -material {self.tag} -stage 1"
        else:
            return ""


class DruckerPragerMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        # validate parameters
        kwargs = self.validate(**kwargs)
        super().__init__('nDMaterial', 'DruckerPrager', user_name)
        self.params = kwargs if kwargs else {}

    def to_tcl(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)
        return f"{self.material_type} DruckerPrager {self.tag} {params_str}; # {self.user_name}"
    
    @staticmethod
    def validate(**params) -> Dict[str, Union[float, int, str, None]]:
        required_params = ['k', 'G', 'sigmaY', 'rho']
        validated_params = {}
        
        # Check required parameters
        for param in required_params:
            value = params.get(param)
            if value is None:
                raise ValueError(f"DruckerPragerMaterial requires the '{param}' parameter.")
            
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for '{param}'. It must be a number.")
            
            # Specific validations
            if param in ['k', 'G', 'sigmaY'] and value <= 0:
                raise ValueError(f"'{param}' must be positive.")
            
            validated_params[param] = value
        
        # Optional parameters with specific validations
        optional_params = {
            'rhoBar': {'default': validated_params['rho'], 'min': 0, 'max': validated_params['rho'], 
                      'message': "rhoBar must be in the range [0, rho]"},
            'Kinf': {'default': 0.0, 'min': 0, 'message': "Kinf must be non-negative"},
            'Ko': {'default': 0.0, 'min': 0, 'message': "Ko must be non-negative"},
            'delta1': {'default': 0.0, 'min': 0, 'message': "delta1 must be non-negative"},
            'delta2': {'default': 0.0, 'min': 0, 'message': "delta2 must be non-negative"},
            'H': {'default': 0.0, 'min': 0, 'message': "H must be non-negative"},
            'theta': {'default': 0.0, 'min': 0, 'max': 1, 'message': "theta must be in range [0, 1]"},
            'density': {'default': 0.0, 'min': 0, 'message': "density must be non-negative"},
            'atmPressure': {'default': 101.0, 'min': 0, 'message': "atmPressure must be non-negative"}
        }
        
        for param, constraints in optional_params.items():
            value = params.get(param, constraints['default'])
            try:
                value = float(value)
                if 'min' in constraints and value < constraints['min']:
                    raise ValueError(constraints['message'])
                if 'max' in constraints and value > constraints['max']:
                    raise ValueError(constraints['message'])
            except (ValueError, TypeError):
                raise ValueError(f"Invalid value for '{param}'. It must be a number.")
            
            validated_params[param] = value
        
        return validated_params

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ['k', 'G', 'sigmaY', 'rho', 'rhoBar', 'Kinf', 'Ko', 'delta1', 'delta2', 'H', 'theta', 'density', 'atmPressure']
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Bulk modulus', 
                'Shear modulus',
                'Yield stress',
                'Frictional strength parameter',
                'Controls evolution of plastic volume change: 0 ≤ rhoBar ≤ rho',
                'Nonlinear isotropic strain hardening parameter: Kinf ≥ 0',
                'Nonlinear isotropic strain hardening parameter: Ko ≥ 0',
                'Nonlinear isotropic strain hardening parameter: delta1 ≥ 0',
                'Tension softening parameter: delta2 ≥ 0',
                'Linear strain hardening parameter: H ≥ 0',
                'Controls relative proportions of isotropic and kinematic hardening: 0 ≤ theta ≤ 1',
                'Mass density of the material',
                'Optional atmospheric pressure for update of elastic bulk and shear moduli (default = 101 kPa)']





# Register material types
MaterialRegistry.register_material_type('nDMaterial', 'ElasticIsotropic', ElasticIsotropicMaterial)
MaterialRegistry.register_material_type('uniaxialMaterial', 'Elastic', ElasticUniaxialMaterial)
MaterialRegistry.register_material_type('nDMaterial', 'J2CyclicBoundingSurface', J2CyclicBoundingSurfaceMaterial)
MaterialRegistry.register_material_type('nDMaterial', 'DruckerPrager', DruckerPragerMaterial)