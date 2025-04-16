from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Union, Tuple
import gc

class DampingBase:
    _dampings = {}
    def __init__(self):
        tag = self._get_next_tag()
        self.name = f"damping{tag}"
        self.tag = tag
        self._dampings[tag] = self

    @classmethod
    def _get_next_tag(cls):
        """Returns the next available tag for a new damping"""
        return len(cls._dampings) + 1
    
    @classmethod
    def remove_damping(cls, tag):
        """Removes a damping from the list of dampings"""
        if tag in cls._dampings:
            del cls._dampings[tag]
            cls._update_tags()


    @staticmethod
    def get_damping(tag):
        """Returns the damping with the given tag"""
        return DampingBase._dampings[tag]
    

    def remove(self):
        """Removes the damping from the list of dampings"""
        refrences = gc.get_referrers(self)
        tag = self.tag
        self.__class__.remove_damping(tag)
        
    

    @classmethod
    def _update_tags(cls):
        """Updates the tags of all dampings"""
        tags = cls._dampings.keys()
        tags = sorted(tags)
        new_dampings = {}
        for i, tag in enumerate(tags):
            cls._dampings[tag].tag = i + 1
            cls._dampings[tag].name = f"damping{i + 1}"
            new_dampings[i + 1] = cls._dampings[tag]
        cls._dampings = new_dampings
        
    def __str__(self) -> str:
        res = f"Damping Class:\t{self.__class__.__name__}"
        res += f"\n\tName: {self.name}"
        res += f"\n\tTag: {self.tag}"
        return res
    
    @classmethod
    def print_dampings(cls):
        """Prints all the dampings"""
        print("Printing all dampings:")
        for tag in cls._dampings:
            print(cls._dampings[tag])

   

        


    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """Returns the parameters of the damping"""
        pass

    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """Returns the notes of the damping"""
        pass
    
    @abstractmethod
    def get_values(self)-> Dict[str, Union[str, int, float, list]]:
        """Returns the values of the parameters of the damping"""
        pass

    @abstractmethod
    def update_values(self, **kwargs) -> None:
        """Updates the values of the parameters of the damping"""
        pass

    @abstractmethod
    def to_tcl(self) -> str:
        """Returns the TCL code of the damping"""
        pass
        





class RayleighDamping(DampingBase):
    def __init__(self, **kwargs):
        kwargs = self.validate(**kwargs)
        super().__init__()
        self.alphaM = kwargs["alphaM"]
        self.betaK = kwargs["betaK"]
        self.betaKInit = kwargs["betaKInit"]
        self.betaKComm = kwargs["betaKComm"]

    
    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n\talphaM: {self.alphaM}"
        res += f"\n\tbetaK: {self.betaK}"
        res += f"\n\tbetaKInit: {self.betaKInit}"
        res += f"\n\tbetaKComm: {self.betaKComm}"
        return res



    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """Returns the parameters of the damping"""
        return [
            ("alphaM", "factor applied to elements or nodes mass matrix (optional, default=0.0)"),
            ("betaK", "factor applied to elements or nodes stiffness matrix (optional, default=0.0)"),
            ("betaKInit", "factor applied to elements initial stiffness matrix (optional, default=0.0)"),
            ("betaKComm", "factor applied to elements commited stiffness matrix (optional, default=0.0)")
        ]
    
    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """Returns the notes of the damping"""
        return {
        "Notes": [
            "The damping matrix is calculated as: C = α<sub>M</sub> M + β<sub>K</sub>  K + β<sub>KInit</sub> Kinit + β<sub>KComm</sub>  Kcomm",
            "The usage of Rayleigh damping may provide incorrect result when used with Non-Linear Time History Analysis using Concentrated Plasticity Model."
            ],
        "References": [
            "https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/rayleigh.html",
            "https://opensees.berkeley.edu/wiki/index.php/Rayleigh_Damping_Command"
        ]
        }
    
    @staticmethod
    def validate(**kwargs)-> Dict[str, Union[str, list]]:
        """Validates the damping"""
        newkwargs = {
            "alphaM": 0.0,
            "betaK": 0.0,
            "betaKInit": 0.0,
            "betaKComm": 0.0
        }


        #  check if the values are floats and are between 0 and 1
        for key in newkwargs:
            try:
                newkwargs[key] = float(kwargs.get(key, 0.0))
            except ValueError:
                raise ValueError(f"{key} should be a float")


        for key in newkwargs:
            try:
                if newkwargs[key] < 0 or newkwargs[key] > 1:
                    raise ValueError
            except ValueError:
                raise ValueError(f"{key} should be a float between 0 and 1")
        
        eps = 1e-10
        res = newkwargs["alphaM"] + newkwargs["betaK"] 
        res += newkwargs["betaKInit"] + newkwargs["betaKComm"]
        # at least one of the values should be greater than 0
        if res < eps:
            raise ValueError("At least one of the damping factors should be greater than 0")
        
        return newkwargs

    def get_values(self)-> Dict[str, Union[str, int, float, list]]:
        return {
            "alphaM": self.alphaM,
            "betaK": self.betaK,
            "betaKInit": self.betaKInit,
            "betaKComm": self.betaKComm
        }
    
    def update_values(self, **kwargs) -> None:
        """Updates the values of the parameters of the damping"""
        kwargs = self.validate(**kwargs)
        self.alphaM = kwargs["alphaM"]
        self.betaK = kwargs["betaK"]
        self.betaKInit = kwargs["betaKInit"]
        self.betaKComm = kwargs["betaKComm"]

    def to_tcl(self) -> str:
        """Returns the TCL code of the damping"""
        res = f"# damping rayleigh {self.tag} {self.alphaM} {self.betaK} {self.betaKInit} {self.betaKComm}"
        return res
    
    @staticmethod
    def get_Type() -> str:
        return "Rayleigh"


class ModalDamping(DampingBase):
    def __init__(self, **kwargs):
        kwargs = self.validate(**kwargs)
        super().__init__()
        self.numberofModes = kwargs["numberofModes"]
        self.dampingFactors = kwargs["dampingFactors"]
    
    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n\tNumber of Modes: {self.numberofModes}"
        res += f"\n\tDamping Factors: {self.dampingFactors}"
        return res
    
    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """Returns the parameters of the damping"""
        return [
            ("numberofModes", "number of modes to consider for modal damping (integer greater than 0)"),
            ("dampingFactors", "damping factors for each mode (list of comma separated floats between 0 and 1)"),
        ]
    
    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """Returns the notes of the damping"""
        return {
        "References": ["https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/modalDamping.html",
                       "https://portwooddigital.com/2019/09/12/be-careful-with-modal-damping/",
                       "https://portwooddigital.com/2023/01/25/modal-and-stiffness-proportional-damping/",
                    ]
        }

    @staticmethod
    def validate(**kwargs)-> Dict[str, Union[str, list]]:
        """Validates the damping"""
        numberofModes = 0
        dampingFactors = []

        if "numberofModes" in kwargs:
            numberofModes = kwargs["numberofModes"]
            try :
                numberofModes = int(numberofModes)
            except ValueError:
                raise ValueError("numberofModes should be an integer")
            if numberofModes <= 0:
                raise ValueError("numberofModes should be greater than 0")
        else:
            raise ValueError("numberofModes is required")
        
        if "dampingFactors" in kwargs:
            dampingFactors = kwargs["dampingFactors"]
            try:
                dampingFactors = dampingFactors.split(",")
            except :
                pass
            if not isinstance(dampingFactors, list):
                raise ValueError("dampingFactors should be a list")
            if len(dampingFactors) != numberofModes:
                raise ValueError("dampingFactors should have the same length as numberofModes")
            for i, factor in enumerate(dampingFactors):
                try:
                    dampingFactors[i] = float(factor)
                    if dampingFactors[i] < 0 or dampingFactors[i] > 1:
                        raise ValueError("dampingFactors should be greater than or equal to 0 and less than or equal to 1")
                except ValueError:
                    raise ValueError("dampingFactors should be a list of floats")
        else:
            raise ValueError("dampingFactors is required")
        
        return {
            "numberofModes": numberofModes,
            "dampingFactors": dampingFactors
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        return {
            "numberofModes": self.numberofModes,
            "dampingFactors": ",".join([str(x) for x in self.dampingFactors])
        }
    
    def update_values(self, **kwargs) -> None:
        """Updates the values of the parameters of the damping"""
        kwargs = self.validate(**kwargs)
        self.numberofModes = kwargs["numberofModes"]
        self.dampingFactors = kwargs["dampingFactors"]
    
    def to_tcl(self) -> str:
        """Returns the TCL code of the damping"""
        res = f"-modalDamping {' '.join([str(x) for x in self.dampingFactors])}"
        return res
    
    @staticmethod
    def get_Type() -> str:
        return "Modal"
                

class FrequencyRayleighDamping(RayleighDamping):
    def __init__(self, **kwargs):
        kwargs = self.validate(**kwargs)
        super().__init__(**kwargs)
        self.f1 = kwargs["f1"]
        self.f2 = kwargs["f2"]
        self.dampingFactor = kwargs["dampingFactor"]
        kwargs = {
            "alphaM": 0.0,
            "betaK": 0.0,
            "betaKInit": 0.0,
            "betaKComm": 0.0,
        }

    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n\tf1: {self.f1}"
        res += f"\n\tf2: {self.f2}"
        res += f"\n\tDamping Factor: {self.dampingFactor}"
        return res
    
    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """Returns the parameters of the damping"""
        return [
            ("dampingFactor", "damping factor for the frequency range (float between 0 and 1) (required)"),
            ("f1", "lower bound Target Frequency (float greater than 0) (optional, default=0.2)"),
            ("f2", "upper bound Target Frequency (float greater than 0) (optional, default=20)")
        ]
    
    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """Returns the notes of the damping"""
        return {
        "Notes": [
            '''
                <b>Mathematical Formulation:</b>
                <p style="text-indent: 30px;">ω₁ = 2π f₁,  ω₂ = 2π f₂</p>
                <p style="text-indent: 30px;">α<sub>M</sub> = 2ω₁ω₂ / (ω₁ + ω₂)</p>
                <p style="text-indent: 30px;">β<sub>K</sub> = 2 / (ω₁ + ω₂)</p>
                <p style="text-indent: 30px;">β<sub>KInit</sub> = 0,  β<sub>KComm</sub> = 0</p>
              ''', 
            "The damping matrix is calculated as: C = α<sub>M</sub> M + β<sub>K</sub>  K",
            ],
        "References": []
    }

    @staticmethod
    def validate(**kwargs)-> Dict[str, Union[str, list]]:
        """Validates the damping"""
        f1 = 0.2 # Hz 
        f2 = 20  # Hz
        dampingFactor = 0

        if "f1" in kwargs:
            f1 = kwargs["f1"]
            try :
                f1 = float(f1)
            except ValueError:
                raise ValueError("f1 should be a float")
            if f1 <= 0:
                raise ValueError("f1 should be greater than 0")
        
        if "f2" in kwargs:
            f2 = kwargs["f2"]
            try :
                f2 = float(f2)
            except ValueError:
                raise ValueError("f2 should be a float")
            if f2 <= 0:
                raise ValueError("f2 should be greater than 0")
        
        if "dampingFactor" in kwargs:
            dampingFactor = kwargs["dampingFactor"]
            try:
                dampingFactor = float(dampingFactor)
            except ValueError:
                raise ValueError("dampingFactor should be a float")
            
            if dampingFactor < 0 or dampingFactor > 1:
                raise ValueError("dampingFactor should be greater than or equal to 0 and less than or equal to 1")
        else:
            raise ValueError("dampingFactor is required")
        
        # calculating the damping factors
        omega1 = 2 * 3.141592653589 * f1
        omega2 = 2 * 3.141592653589 * f2
        alphaM = 2 * dampingFactor * omega1 * omega2 / (omega1 + omega2)
        betaK  = (2 * dampingFactor) / (omega1 + omega2)

        return {
            "f1": f1,
            "f2": f2,
            "dampingFactor": dampingFactor,
            "alphaM": alphaM,
            "betaK": betaK,
            "betaKInit": 0,
            "betaKComm": 0
        }
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        return {
            "dampingFactor": self.dampingFactor,
            "f1": self.f1,
            "f2": self.f2,
        }
    

    def update_values(self, **kwargs) -> None:
        """Updates the values of the parameters of the damping"""
        kwargs = self.validate(**kwargs)
        self.f1 = kwargs["f1"]
        self.f2 = kwargs["f2"]
        self.dampingFactor = kwargs["dampingFactor"]    
        self.alphaM = kwargs["alphaM"]
        self.betaK = kwargs["betaK"]
        self.betaKInit = kwargs["betaKInit"]
        self.betaKComm = kwargs["betaKComm"]

    @staticmethod
    def get_Type() -> str:
        return "Frequency Rayleigh"



class UniformDamping(DampingBase):
    def __init__(self, **kwargs):
        kwargs = self.validate(**kwargs)
        super().__init__()
        self.dampingRatio = kwargs["dampingRatio"]
        self.freql = kwargs["freql"]
        self.freq2 = kwargs["freq2"]
        self.Ta    = kwargs.get("Ta", None)
        self.Td    = kwargs.get("Td", None)
        self.tsTagScaleFactorVsTime = kwargs.get("tsTagScaleFactorVsTime", None)

    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n\tDamping Ratio: {self.dampingRatio}"
        res += f"\n\tLower Frequency: {self.freql}"
        res += f"\n\tUpper Frequency: {self.freq2}"
        res += f"\n\tTa: {self.Ta if self.Ta is not None else 'default'}"
        res += f"\n\tTd: {self.Td if self.Td is not None else 'default'}"
        res += f"\n\ttsTagScaleFactorVsTime: {self.tsTagScaleFactorVsTime if self.tsTagScaleFactorVsTime is not None else 'No time series'}"
        return res
    

    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """Returns the parameters of the damping"""
        return [
            ("dampingRatio", "target equivalent viscous damping ratio (float between 0 and 1) (required)"),
            ("freql", "lower bound of the frequency range (in units of T^-1) (float greater than 0) (required)"),
            ("freq2", "upper bound of the frequency range (in units of T^-1) (float greater than 0) (required)"),
            ("Ta", "time when the damping is activated (float)"),
            ("Td", "time when the damping is deactivated (float) (optional)"),
            ("tsTagScaleFactorVsTime", "time series tag identifying the scale factor of the damping versus time (int) (optional)")
        ]
    
    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """Returns the notes of the damping"""
        return {
            "References": [
                "https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/elementalDamping/UniformDamping.html",
            ]
        }
    
    @staticmethod
    def validate(**kwargs)-> Dict[str, Union[str, list]]:
        """Validates the damping"""

        # make them float
        try :
            for key in ["dampingRatio", "freql", "freq2", "Ta", "Td"]:
                res = kwargs.get(key, None)
                if res is not None and res != "":
                    kwargs[key] = float(kwargs[key])
        except ValueError:
            raise ValueError(f"{key} should be a float")
        
        # check if the values are between 0 and 1
        for key in ["dampingRatio", "freql", "freq2"]:
            if key not in kwargs:
                raise ValueError(f"{key} is required")
            
        if kwargs["dampingRatio"] < 0 or kwargs["dampingRatio"] > 1:
            raise ValueError("dampingRatio should be greater than or equal to 0 and less than or equal to 1")
        
        if kwargs["freql"] <= 0:
            raise ValueError("freql should be greater than 0")
        
        if kwargs["freq2"] <= 0 or kwargs["freq2"] <= kwargs["freql"]:
            raise ValueError("freq2 should be greater than 0 and greater than freql")
        
        if "tsTagScaleFactorVsTime" in kwargs and kwargs["tsTagScaleFactorVsTime"] != "":
            try:
                kwargs["tsTagScaleFactorVsTime"] = int(kwargs["tsTagScaleFactorVsTime"])
            except ValueError:
                raise ValueError("tsTagScaleFactorVsTime should be an integer")

        
        return kwargs
        
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        return {
            "dampingRatio": self.dampingRatio,
            "freql": self.freql,
            "freq2": self.freq2,
            **{k: v for k, v in {
            "Ta": self.Ta,
            "Td": self.Td,
            "tsTagScaleFactorVsTime": self.tsTagScaleFactorVsTime
            }.items() if v is not None}
        }
    
    def update_values(self, **kwargs) -> None:
        """Updates the values of the parameters of the damping"""
        kwargs = self.validate(**kwargs)
        self.dampingRatio = kwargs["dampingRatio"]
        self.freql = kwargs["freql"]
        self.freq2 = kwargs["freq2"]
        
        # Handle optional parameters if they are present
        self.Ta = kwargs.get("Ta", None) # Ta is optional so we use get
        self.Td = kwargs.get("Td", None) # Td is optional so we use get
        self.tsTagScaleFactorVsTime = kwargs.get("tsTagScaleFactorVsTime", None) # tsTagScaleFactorVsTime is optional so we use get

    def to_tcl(self) -> str:
        """Returns the TCL code of the damping"""
        res = f"damping Uniform {self.tag} {self.dampingRatio} {self.freql} {self.freq2}"
        if self.Ta is not None:
            res += f" -activateTime  {self.Ta}"
        if self.Td is not None:
            res += f" -deactivateTime {self.Td}"
        if self.tsTagScaleFactorVsTime is not None:
            res += f" -fact {self.tsTagScaleFactorVsTime}"

        return res
    
    @staticmethod
    def get_Type() -> str:
        return "Uniform"





class SecantStiffnessProportional (DampingBase):
    def __init__(self, **kwargs):
        kwargs = self.validate(**kwargs)
        super().__init__()
        self.dampingFactor = kwargs["dampingFactor"]
        self.Ta = kwargs.get("Ta", None)
        self.Td = kwargs.get("Td", None)
        self.tsTagScaleFactorVsTime = kwargs.get("tsTagScaleFactorVsTime", None)
    
    def __str__(self) -> str:
        res = super().__str__()
        res += f"\n\tDamping Factor: {self.dampingFactor}"
        res += f"\n\tTa: {self.Ta if self.Ta is not None else 'default'}"
        res += f"\n\tTd: {self.Td if self.Td is not None else 'default'}"
        res += f"\n\ttsTagScaleFactorVsTime: {self.tsTagScaleFactorVsTime if self.tsTagScaleFactorVsTime is not None else 'No time series'}"
        return res
    
    @staticmethod
    def get_Parameters() -> List[Tuple[str, str]]:
        """Returns the parameters of the damping"""
        return [
            ("dampingFactor", "coefficient used in the secant stiffness-proportional damping (float between 0 and 1) (required)"),
            ("Ta", "time when the damping is activated (float) (optional)"),
            ("Td", "time when the damping is deactivated (float) (optional)"),
            ("tsTagScaleFactorVsTime", "time series tag identifying the scale factor of the damping versus time (int) (optional)")
        ]
    
    @staticmethod
    def get_Notes() -> Dict[str, Union[str, list]]:
        """Returns the notes of the damping"""
        return {
            "Notes": [
                """The formulation of the damping matrix is:
                <p style="text-indent: 30px;"> f <sub> damping </sub> = dampingFactor * K<sub> secant </sub> * u&#775; </p>
                """,
            ],

            "References": [
                "https://opensees.github.io/OpenSeesDocumentation/user/manual/model/damping/elementalDamping/SecStifDamping.html"
                ]
        }
    
    @staticmethod
    def validate(**kwargs)-> Dict[str, Union[str, list]]:
        """Validates the damping"""
        # make them float
        try :
            for key in ["dampingFactor", "Ta", "Td"]:
                res = kwargs.get(key, None)
                if res is not None and res != "":
                    kwargs[key] = float(kwargs[key])
        except ValueError:
            raise ValueError(f"{key} should be a float")
        
        # check if the values are between 0 and 1
        if "dampingFactor" not in kwargs:
            raise ValueError("dampingFactor is required")
        
        if kwargs["dampingFactor"] < 0 or kwargs["dampingFactor"] > 1:
            raise ValueError("dampingFactor should be greater than or equal to 0 and less than or equal to 1")
        
        if "tsTagScaleFactorVsTime" in kwargs and kwargs["tsTagScaleFactorVsTime"] != "":
            try:
                kwargs["tsTagScaleFactorVsTime"] = int(kwargs["tsTagScaleFactorVsTime"])
            except ValueError:
                raise ValueError("tsTagScaleFactorVsTime should be an integer")

        return kwargs
    
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        return {
            "dampingFactor": self.dampingFactor,
            **{k: v for k, v in {
            "Ta": self.Ta,
            "Td": self.Td,
            "tsTagScaleFactorVsTime": self.tsTagScaleFactorVsTime
            }.items() if v is not None}
        }
    
    def update_values(self, **kwargs) -> None:
        """Updates the values of the parameters of the damping"""
        kwargs = self.validate(**kwargs)
        self.dampingFactor = kwargs["dampingFactor"]

        # Handle optional parameters if they are present
        self.Ta = kwargs.get("Ta", None)
        self.Td = kwargs.get("Td", None)
        self.tsTagScaleFactorVsTime = kwargs.get("tsTagScaleFactorVsTime", None)
    
    def to_tcl(self) -> str:
        """Returns the TCL code of the damping"""
        res = f"damping SecStiff {self.tag} {self.dampingFactor}"
        if self.Ta is not None:
            res += f" -activateTime  {self.Ta}"
        if self.Td is not None:
            res += f" -deactivateTime {self.Td}"
        if self.tsTagScaleFactorVsTime is not None:
            res += f" -fact {self.tsTagScaleFactorVsTime}"

        return res
    
    @staticmethod
    def get_Type() -> str:
        return "Secant Stiffness Proportional"



class DampingManager:
    """
    A centralized manager for all damping instances in MeshMaker.
    
    The DampingManager implements the Singleton pattern to ensure a single, consistent
    point of damping management across the entire application. It provides methods for
    creating, retrieving, and managing damping objects used in dynamic structural analysis.
    
    All damping objects created through this manager are automatically tracked and tagged,
    simplifying the process of creating models with appropriate energy dissipation mechanisms.
    
    Usage:
        # Direct access
        from meshmaker.components.Damping import DampingManager
        damping_manager = DampingManager()
        
        # Through MeshMaker (recommended)
        from meshmaker.components.MeshMaker import MeshMaker
        mk = MeshMaker()
        damping_manager = mk.damping
        
        # Creating a damping instance
        rayleigh_damping = damping_manager.create_damping('rayleigh', alphaM=0.05, betaK=0.001)
    """
    _instance = None
    
    def __new__(cls):
        """
        Create a new DampingManager instance or return the existing one if already created.
        
        Returns:
            DampingManager: The singleton instance of the DampingManager
        """
        if cls._instance is None:
            cls._instance = super(DampingManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of the DampingManager.
        
        This method ensures that only one instance of DampingManager exists throughout
        the application, following the Singleton design pattern.
        
        Returns:
            DampingManager: The singleton instance of the DampingManager
        """
        return cls._instance

    def create_damping(self, damping_type: str, **kwargs) -> DampingBase:
        """
        Create a new damping instance of the specified type.
        
        This method delegates the damping creation to the DampingRegistry, which
        maintains a dictionary of available damping types and their corresponding classes.
        
        Args:
            damping_type (str): The type of damping to create. Available types include:
                - 'rayleigh': Classical Rayleigh damping
                - 'modal': Modal damping for specific modes
                - 'frequency rayleigh': Rayleigh damping specified by target frequencies
                - 'uniform': Uniform damping across a frequency range
                - 'secant stiffness proportional': Damping proportional to secant stiffness
            **kwargs: Specific parameters for the damping type being created
                      (see documentation for each damping type for details)
        
        Returns:
            DampingBase: A new instance of the requested damping type
            
        Raises:
            ValueError: If the damping type is unknown or if required parameters are missing or invalid
        """
        return DampingRegistry.create_damping(damping_type, **kwargs)

    def get_damping(self, tag: int) -> DampingBase:
        """
        Get a damping instance by its tag.
        
        Args:
            tag (int): The unique identifier of the damping instance
            
        Returns:
            DampingBase: The damping instance with the specified tag
            
        Raises:
            KeyError: If no damping with the given tag exists
        """
        return DampingBase.get_damping(tag)

    def remove_damping(self, tag: int) -> None:
        """
        Remove a damping instance by its tag.
        
        This method removes the specified damping instance and automatically
        updates the tags of the remaining damping instances to maintain sequential numbering.
        
        Args:
            tag (int): The unique identifier of the damping instance to remove
        """
        DampingBase.remove_damping(tag)

    def get_all_dampings(self) -> Dict[int, DampingBase]:
        """
        Get all damping instances currently managed by this DampingManager.
        
        Returns:
            Dict[int, DampingBase]: A dictionary mapping tags to damping instances
        """
        return DampingBase._dampings

    def clear_all_dampings(self) -> None:
        """
        Remove all damping instances managed by this DampingManager.
        
        This method clears all damping instances from the manager, effectively
        resetting the damping system.
        """
        DampingBase._dampings.clear()

    def get_available_types(self) -> List[str]:
        """
        Get a list of available damping types that can be created.
        
        Returns:
            List[str]: A list of damping type names that can be used with create_damping()
        """
        return DampingRegistry.get_available_types()
    


class DampingRegistry:
    _damping_types = {
        'frequency rayleigh': FrequencyRayleighDamping,
        'rayleigh': RayleighDamping,
        'modal': ModalDamping,
        'uniform': UniformDamping,
        'secant stiffness proportional': SecantStiffnessProportional
    }

    @classmethod
    def create_damping(cls, damping_type: str, **kwargs) -> DampingBase:
        if damping_type.lower() not in cls._damping_types:
            raise ValueError(f"Unknown damping type: {damping_type}")
        return cls._damping_types[damping_type.lower()](**kwargs)

    @classmethod
    def get_available_types(cls) -> List[str]:
        return list(cls._damping_types.keys())

    @classmethod
    def register_damping_type(cls, name: str, damping_class: Type[DampingBase]):
        cls._damping_types[name.lower()] = damping_class

    @classmethod
    def remove_damping_type(cls, name: str):
        if name.lower() in cls._damping_types:
            del cls._damping_types[name.lower()]

 



if __name__ == "__main__":
    # test the DampingBase class
    damping1 = DampingBase()
    damping2 = DampingBase()
    damping3 = DampingBase()

    RayleighDamping1 = RayleighDamping(alphaM=0.1, betaK=0.2, betaKInit=0.3, betaKComm=0.4)
    RayleighDamping2 = RayleighDamping(alphaM=0.5, betaK=0.6, betaKInit=0.7, betaKComm=0.8)
    ModalDamping1 = ModalDamping(numberofModes=2, dampingFactors="0.1,0.2")
    ModalDamping2 = ModalDamping(numberofModes=3, dampingFactors="0.3,0.4,0.5")



    DampingBase.print_dampings()

    print(10*"*"+"\nRemoving damping 2\n"+10*"*")

    DampingBase.remove_damping(2)
    DampingBase.print_dampings()

