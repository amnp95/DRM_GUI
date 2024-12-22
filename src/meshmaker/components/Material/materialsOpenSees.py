from typing import List, Dict

from .materialBase import Material, MaterialRegistry


class ElasticIsotropicMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('nDMaterial', 'ElasticIsotropic', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)

        return f"{self.material_type} ElasticIsotropic {self.tag} {params_str}; # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ["E", "ν", "ρ"]
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Young\'s modulus', 
                'Poisson\'s ratio', 
                'Mass density of the material']



class ManzariDafaliasMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('nDMaterial', 'ManzariDafalias', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)
        return f"{self.material_type} ManzariDafalias {self.tag} {params_str} # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ['G₀', 'ν', 'eᵢₙᵢₜ', 'Μc', 'c',
        'λc', 'e₀', 'ξ', 'Pₐₜₘ',
        'm', 'h₀', 'ch', 'nᵦ', 'Α₀',
        'nᵈ', 'zₘₐₓ', 'c𝓏', 'ρ']
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Shear modulus', 
                'Poisson\'s ratio',
                'Initial void ratio',
                'Critical state stress ratio',
                'Ratio of critical state stress ratio in extension and compression',
                'Critical state line constant',
                'Critical void ratio at p = 0',
                'Critical state line constant',
                'Atmospheric pressure',
                'Yield surface constant',
                'Constant parameter',   
                'Constant parameter',
                'Bounding surface parameter',
                'Dilatancy parameter',
                'Dilatancy surface parameter',
                'Fabric-dilatancy tensor parameter',
                'Fabric-dilatancy tensor parameter',
                'Mass density of the material'
                ]


class ElasticUniaxialMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('uniaxialMaterial', 'Elastic', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        param_order = self.get_parameters()
        params_str = " ".join(str(self.params[param]) for param in param_order if param in self.params)
        return f"{self.material_type} Elastic {self.tag} {params_str}; # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ["E", "η", "E<sub>neg</sub>"]
    
    @classmethod
    def get_description(cls) -> List[str]:
        return ['Tangent', 
                'Damping tangent (optional, default=0.0)',
                'Tangent in compression (optional, default=E)']




# Register material types
MaterialRegistry.register_material_type('nDMaterial', 'ElasticIsotropic', ElasticIsotropicMaterial)
MaterialRegistry.register_material_type('nDMaterial', 'ManzariDafalias', ManzariDafaliasMaterial)
MaterialRegistry.register_material_type('uniaxialMaterial', 'Elastic', ElasticUniaxialMaterial)