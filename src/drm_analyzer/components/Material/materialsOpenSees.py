from typing import List, Dict

from .materialBase import Material, MaterialRegistry


class ElasticIsotropicMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('nDMaterial', 'ElasticIsotropic', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        params_str = " ".join(str(value) for value in self.params.values())
        return f"{self.material_type} ElasticIsotropic {self.tag} {params_str} # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ["E", "nu", "rho"]


class ManzariDafaliasMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('nDMaterial', 'ManzariDafalias', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        params_str = " ".join(str(value) for value in self.params.values())
        return f"{self.material_type} ManzariDafalias {self.tag} {params_str} # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ['G₀', 'ν', 'eᵢₙᵢₜ', 'Μc', 'c',
        'λc', 'e₀', 'ξ', 'Pₐₜₘ',
        'm', 'h₀', 'ch', 'nᵦ', 'Α₀',
        'nᵈ', 'zₘₐₓ', 'c𝓏', 'ρ']


class ElasticUniaxialMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('uniaxialMaterial', 'Elastic', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        params_str = " ".join(str(value) for value in self.params.values())
        return f"{self.material_type} Elastic {self.tag} {params_str} # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ["E", "eta"]




# Register material types
MaterialRegistry.register_material_type('nDMaterial', 'ElasticIsotropic', ElasticIsotropicMaterial)
MaterialRegistry.register_material_type('nDMaterial', 'ManzariDafalias', ManzariDafaliasMaterial)
MaterialRegistry.register_material_type('uniaxialMaterial', 'Elastic', ElasticUniaxialMaterial)