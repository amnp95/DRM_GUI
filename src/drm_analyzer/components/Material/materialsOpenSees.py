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

    def get_values(self, keys: List[str]) -> Dict[str, float]:
        return {key: self.params.get(key) for key in keys}

    def update_values(self, values: Dict[str, float]) -> None:
        self.params.update(values)
        print(f"Updated parameters: {self.params}")


class ManzariDafaliasMaterial(Material):
    def __init__(self, user_name: str = "Unnamed", **kwargs):
        super().__init__('nDMaterial', 'ManzariDafalias', user_name)
        self.params = kwargs if kwargs else {}

    def __str__(self):
        params_str = " ".join(str(value) for value in self.params.values())
        return f"{self.material_type} ManzariDafalias {self.tag} {params_str} # {self.user_name}"

    @classmethod 
    def get_parameters(cls) -> List[str]:
        return ['G0', 'nu', 'e_init', 'Mc', 'c',
                'lambda_c', 'e0', 'ksi', 'P_atm',
                'm', 'h0', 'ch', 'nb', 'A0',
                'nd', 'z_max', 'cz', 'Den']

    def get_values(self, keys: List[str]) -> Dict[str, float]:
        return {key: self.params.get(key) for key in keys}

    def update_values(self, values: Dict[str, float]) -> None:
        self.params.update(values)
        print(f"Updated parameters: {self.params}")


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

    def get_values(self, keys: List[str]) -> Dict[str, float]:
        return {key: self.params.get(key) for key in keys}

    def update_values(self, values: Dict[str, float]) -> None:
        self.params.update(values)
        print(f"Updated parameters: {self.params}")


# Register material types
MaterialRegistry.register_material_type('nDMaterial', 'ElasticIsotropic', ElasticIsotropicMaterial)
MaterialRegistry.register_material_type('nDMaterial', 'ManzariDafalias', ManzariDafaliasMaterial)
MaterialRegistry.register_material_type('uniaxialMaterial', 'Elastic', ElasticUniaxialMaterial)