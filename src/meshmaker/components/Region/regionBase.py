from meshmaker.components.Damping.dampingBase import DampingBase
import weakref 
from abc import ABC, abstractmethod
from typing import List, Dict, Type, Optional, Union

class RegionBase(ABC):
    _regions = {}  # Dictionary to hold regions
    _global_region = None  # Global region instance

    def __new__(cls, tag=None, damping: Type[DampingBase] = None):

        if tag in cls._regions:
            return cls._regions[tag]
        
        if tag == 0:
            cls._global_region = super().__new__(cls)
            cls._regions[0] = cls._global_region
            return cls._global_region

        # Create a new instance for a unique tag
        instance = super().__new__(cls)
        return instance



    def __init__(self, tag=None, damping: Type[DampingBase] = None):
        
        if tag == 0:
            # check the region is type of global region for tag 0
            if not isinstance(self, GlobalRegion):
                raise ValueError("Region with tag 0 should be of type GlobalRegion \
                                 please use GlobalRegion class to create a global region")
            self._tag = tag
            self._name = "GlobalRegion"
            self._regions[0] = self
            self.damping = damping
        elif tag is None:
            tag = self._get_next_tag()
            self._tag = tag
            self._name = f"region {tag}"
            self._regions[tag] = self
            self.damping = damping

        # Default values
        if not hasattr(self, "active"):
            self.active = True

    @property
    def tag(self):
        return self._tag
    
    @property
    def name(self):
        return self._name
    
    @property
    def damping(self):
        return self._damping() if self._damping else None

    @damping.setter
    def damping(self, value: Optional[Type[DampingBase]]):
        if value is not None and not issubclass(value.__class__, DampingBase):
            raise TypeError("damping must be a subclass of DampingBase")
        self._damping = weakref.ref(value) if value else None 

    @damping.deleter
    def damping(self):
        self._damping_ref = None 


    def __str__(self) -> str:
        type_name = self.get_type()
        res = f"Region class"
        res += f"\n\tTag: {self.tag}"
        res += f"\n\tName: {self.name}"
        res += f"\n\tType: {type_name}"
        res += f"\n\tActive: {self.active}"
        res += f"\n\tDamping: " + ("\n\t" + str(self.damping)).replace("\n", "\n\t") if self.damping else "\n\tDamping: None"
        return res

    @classmethod
    def _get_next_tag(cls):
        """Get the next available tag."""
        return len(cls._regions)

    @classmethod
    def _update_tags(cls):
        """Update tags and names of all regions except the global region."""
        tags = sorted(cls._regions.keys())
        if 0 in tags:
            tags.remove(0)  # Preserve the global region tag
        new_regions = {0: cls._regions[0]} if 0 in cls._regions else {}
        for i, old_tag in enumerate(tags, start=1):
            region = cls._regions[old_tag]
            region._tag = i
            region._name = f"region{i}"
            new_regions[i] = region
        cls._regions = new_regions

    @classmethod
    def remove_region(cls, tag):
        """Remove a region by its tag."""
        if tag == 0:
            raise ValueError("Cannot remove the global region (tag 0)")
        if tag in cls._regions:
            del cls._regions[tag]
            cls._update_tags()

    @classmethod
    def get_region(cls, tag) -> Optional["RegionBase"]:
        """Get a region by its tag."""
        return cls._regions.get(tag)

    @classmethod
    def get_all_regions(cls) -> Dict[int, "RegionBase"]:
        """Get all regions."""
        return cls._regions

    @classmethod
    def clear(cls) -> None:
        """Clear all regions, including the global region."""
        cls._regions = {}
        cls._global_region = None

    @staticmethod
    def print_regions() -> None:
        """Print all regions."""
        for tag, region in RegionBase.get_all_regions().items():
            print(region)


    @abstractmethod
    def to_tcl(self) -> str:
        """Convert the region to a TCL representation."""
        pass

    @abstractmethod
    def validate(self):
        """Validate region parameters."""
        pass

    @staticmethod
    @abstractmethod
    def get_Parameters() -> Dict[str, str]:
        """Get parameters for the region."""
        pass

    @staticmethod
    @abstractmethod
    def getNotes() -> Dict[str, list[str]]:
        """Get notes for the region."""
        pass

    @staticmethod
    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def setComponent(self, component:str, value:list[int]):
        pass


class GlobalRegion(RegionBase):
    def __new__(cls, damping: Type[DampingBase] = None):
        return super().__new__(cls, tag=0)

    def __init__(self, damping: Type[DampingBase] = None):
        super().__init__(tag=0, damping=damping)
        self.elements = None
        self.element_range = None
        self.nodes = None
        self.node_range = None

    def to_tcl(self) -> str:
        """TCL representation for global region."""
        return "region 0"

    def validate(self):
        """No validation required for global region."""
        pass

    @staticmethod
    def get_Parameters() -> Dict[str, str]:
        """No parameters for global region."""
        return {}

    @staticmethod
    def getNotes() -> Dict[str, list[str]]:
        """Notes about global region."""
        # return "Global region representing entire model"
        return {
            "Notes": [
                "Global region representing entire model"
            ],
            "References": []    
        }
    @staticmethod
    def get_type() -> str:
        return "GlobalRegion"
    
    def setComponent(self, component:str, values:list[int]):
        if component == "element":
            self.elements = values
            self.element_range = None
            self.nodes = None
            self.node_range = None
        elif component == "elementRange":
            if len(values) != 2:
                raise ValueError("element_range should have 2 elements")
            self.element_range = values
            self.elements = None
            self.nodes = None
            self.node_range = None
        elif component == "node":
            self.nodes = values
            self.node_range = None
            self.elements = None
            self.element_range = None
        elif component == "nodeRange":
            if len(values) != 2:
                raise ValueError("node_range should have 2 elements")
            self.node_range = values
            self.nodes = None
            self.elements = None
            self.element_range = None
        else:
            raise ValueError(f"""Invalid component {component} for GlobalRegion
                             valid components are element, elementRange, node, nodeRange""")
        

def initialize_region_base():
    """Initialize the RegionBase with the global region."""
    GlobalRegion()


class ElementRegion(RegionBase):
    def __new__(cls, damping: Type[DampingBase] = None, **kwargs):
        return super().__new__(cls, tag=kwargs.pop("tag", None))
    
    def __init__(self, damping: Type[DampingBase] = None ,**kwargs):
        super().__init__(tag=kwargs.pop("tag", None), damping=damping)
        self.elements = []
        self.element_range = []
        self.element_only = False

        if kwargs:
            validated = self.validate(**kwargs)
            self.elements = validated["elements"]
            self.element_range = validated["element_range"]
            self.element_only = validated["element_only"]


    def to_tcl(self):
        cmd = f"eval \"region {self.tag}"
        if len(self.element_range) > 0:
            cmd += " -eleRange {} {}".format(*self.element_range)
            if self.element_only:
                cmd += "Only"
        elif len(self.elements) > 0:
            cmd += " -ele" + ("Only" if self.element_only else "")
            cmd += " " + " ".join(str(e) for e in self.elements)

        if self.damping:
            if self.damping.get_Type() in ["RayleighDamping", "Frequency Rayleigh"]:
                cmd += f" -rayleigh {self.damping.alphaM} {self.damping.betaK} {self.damping.betaKInit} {self.damping.betaKComm}"
            else:
                cmd += f" -damping {self.damping.tag}"
        cmd += "\""
        return cmd
    

    def __str__(self):
        res = super().__str__()
        res += f"\n\tNum of Elements: {len(self.elements)}"
        res += f"\n\tElement Range: {self.element_range}"
        res += f"\n\tElement Only: {self.element_only}"
        return res


    @staticmethod
    def get_Parameters():
        return {
            "elements": "lineEdit",
            "element_range": "lineEdit",
            "element_only": "checkbox"
        }
    
    @staticmethod
    def getNotes()->Dict[str, list[str]]:
        return {
            "Notes": [
                "Use elements list for specific elements: [1, 2, 3, ...]"
                "If you use GUI, use comma separated values 1, 2, 3, ...",
                "Use element_range for a range: [start, end]",
                "If you use GUI, use comma separated values start, end for range",
                "Cannot use both elements and element_range simultaneously",
                "Set element_only=True to include only elements (default is False)",
                "If you use GUI, check the checkbox to include only elements"
            ],
            "References": []
        }

    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, bool, list]]:
        # check if elements or element_range is provided
        # if "elements" not in kwargs and "element_range" not in kwargs:
        #     raise ValueError("Either elements or element_range should be provided")
        
        # check if elements and element_range are provided at the same time
        if "elements" in kwargs and "element_range" in kwargs:
            raise ValueError("Both elements and element_range cannot be provided at the same time")
        
        elements = []
        element_range = []
        element_only = False

        if "elements" in kwargs:
            elements = kwargs["elements"]
            # elements should be list of integers check that
            if not isinstance(elements, list):
                raise ValueError("elements should be a list of integers")
            for e in elements:
                if not isinstance(e, int):
                    raise ValueError("elements should be a list of integers")
                

        if "element_range" in kwargs:
            element_range = kwargs["element_range"]
            if not isinstance(element_range, list):
                raise ValueError("element_range should be a list of integers")
            if len(element_range) != 2:
                raise ValueError("element_range should have 2 elements")
            for e in element_range:
                if not isinstance(e, int):
                    raise ValueError("element_range should be a list of integers")

        if "element_only" in kwargs:
            element_only = kwargs["element_only"]
            if not isinstance(element_only, bool):
                raise ValueError("element_only should be a boolean")
            
        return {
            "elements": elements,
            "element_range": element_range,
            "element_only": element_only
        }
    
    @staticmethod
    def get_type() -> str:
        return "ElementRegion"
    
    def setComponent(self, component:str, value:list[int]):
        if component == "element":
            self.elements = value
            self.element_range = []
        elif component == "elementRange":
            if len(value) != 2:
                raise ValueError("element_range should have 2 elements")
            self.element_range = value
            self.elements = []
        else:
            raise ValueError(f"""Invalid component {component} for ElementRegion 
                             valid components are element and elementRange""")


class NodeRegion(RegionBase):
    def __new__(cls, damping: Type[DampingBase] = None, **kwargs):
        return super().__new__(cls, tag=kwargs.pop("tag", None))
    
    def __init__(self, damping: Type[DampingBase] = None, **kwargs):
        super().__init__(tag=kwargs.pop("tag", None), damping=damping)
        self.nodes = []
        self.node_range = []
        self.node_only = False
        
        if kwargs:
            validated = self.validate(**kwargs)
            self.nodes = validated["nodes"]
            self.node_range = validated["node_range"]
            self.node_only = validated["node_only"]


    def to_tcl(self):
        cmd = f"region {self.tag}"
        if len(self.node_range) > 0:
            cmd += " -node" + ("Only" if self.node_only else "") + "Range"
            cmd += " {} {}".format(*self.node_range)
        elif len(self.nodes) > 0:
            cmd += " -node" + ("Only" if self.node_only else "")
            cmd += " " + " ".join(str(n) for n in self.nodes)

        if self.damping:
            if self.damping.get_Type() in ["RayleighDamping", "Frequency Rayleigh"]:
                cmd += F"-rayleigh {self.damping.alphaM} {self.damping.betaK} {self.damping.betaKInit} {self.damping.betaKComm}"
            else:
                cmd += f"-damping {self.damping.tag}"
        return cmd
    


    def __str__(self):
        res = super().__str__()
        res += f"\n\tNum of Nodes: {len(self.nodes)}"
        res += f"\n\tNode Range: {self.node_range}"
        return res

    @staticmethod
    def get_Parameters():
        return {
            "nodes": "lineEdit",
            "node_range": "lineEdit"
        }

    @staticmethod
    def getNotes()->Dict[str, list[str]]:
        return {
            "Notes": [
                "Use nodes list for specific nodes: [1, 2, 3, ...]",
                "If you use GUI, use comma separated values 1, 2, 3, ...",
                "Use node_range for a range: [start, end]",
                "If you use GUI, use comma separated values start, end for range",
                "Cannot use both nodes and node_range simultaneously",
                "Set node_only=True to include only nodes (default is False)",
                "If you use GUI, check the checkbox to include only nodes",
            ],
            "References": []
        }

    @staticmethod
    def validate(**kwargs) -> Dict[str, Union[str, list]]:
        # if "nodes" not in kwargs and "node_range" not in kwargs:
        #     raise ValueError("Either nodes or node_range should be provided")
        
        if "nodes" in kwargs and "node_range" in kwargs:
            raise ValueError("Both nodes and node_range cannot be provided at the same time")
        
        nodes = []
        node_range = []
        node_only = False

        if "nodes" in kwargs:
            nodes = kwargs["nodes"]
            if not isinstance(nodes, list):
                raise ValueError("nodes should be a list of integers")
            for n in nodes:
                if not isinstance(n, int):
                    raise ValueError("nodes should be a list of integers")

        if "node_range" in kwargs:
            node_range = kwargs["node_range"]
            if not isinstance(node_range, list):
                raise ValueError("node_range should be a list of integers")
            if len(node_range) != 2:
                raise ValueError("node_range should have 2 elements")
            for n in node_range:
                if not isinstance(n, int):
                    raise ValueError("node_range should be a list of integers")
                
        if "node_only" in kwargs:
            node_only = kwargs["node_only"]
            if not isinstance(node_only, bool):
                raise ValueError("node_only should be a boolean")
            
        return {
            "nodes": nodes,
            "node_range": node_range,
            "node_only": node_only
        }

    @staticmethod
    def get_type() -> str:
        return "NodeRegion"
    
    def setComponent(self, component:str, value:list[int]):
        if component == "node":
            self.nodes = value
            self.node_range = []
        elif component == "nodeRange":
            if len(value) != 2:
                raise ValueError("node_range should have 2 elements")
            self.node_range = value
            self.nodes = []
        else:
            raise ValueError(f"""Invalid component {component} for NodeRegion
                             valid components are node and nodeRange""")

class RegionManager:
    """
    A centralized manager for all region instances in MeshMaker.
    
    The RegionManager implements the Singleton pattern to ensure a single, consistent
    point of region management across the entire application. It provides methods for
    creating, retrieving, and managing region objects used to define specific parts
    of structural models for analysis and damping assignments.
    
    All region objects created through this manager are automatically tracked and tagged,
    simplifying the process of defining and managing model regions. A special GlobalRegion
    with tag 0 is automatically created when the RegionManager is initialized.
    
    """
    _instance = None
    def __new__(cls):
        """
        Create a new RegionManager instance or return the existing one if already created.
        
        Returns:
            RegionManager: The singleton instance of the RegionManager
        """
        if cls._instance is None:
            cls._instance = super(RegionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the RegionManager and create the GlobalRegion.
        
        This method ensures that the global region (tag 0) is automatically created
        when the RegionManager is initialized. The initialization only happens once
        due to the singleton pattern.
        """
        if not self._initialized:
            self._initialized = True
            initialize_region_base()

    @property
    def regions(self):
        """
        Get all regions as a dictionary mapping tags to region instances.
        
        Returns:
            Dict[int, RegionBase]: A dictionary mapping tags to region instances
        """
        return RegionBase.get_all_regions()

    def get_region(self, tag):
        """
        Get a region by its tag.
        
        Args:
            tag (int): The unique identifier of the region instance
            
        Returns:
            RegionBase: The region instance with the specified tag, or None if not found
        """
        return RegionBase.get_region(tag)
    
    def create_region(self, regionType: str, damping=None, **kwargs):
        """
        Create a new region instance of the specified type.
        
        This method creates and returns a new region object based on the provided type
        and parameters. The region is automatically registered and tracked.
        
        Args:
            regionType (str): The type of region to create. Available types include:
                'ElementRegion': A region defined by a set of elements or element range
                'NodeRegion': A region defined by a set of nodes or node range
                'GlobalRegion': The global region representing the entire model
            damping: Optional damping instance to associate with the region
            **kwargs: Specific parameters for the region type being created
                (e.g., elements, element_range for ElementRegion,
                nodes, node_range for NodeRegion)
        
        Returns:
            RegionBase: A new instance of the requested region type
            
        Raises:
            ValueError: If the region type is unknown or if required parameters are missing or invalid
        """
        if regionType.lower() == "elementregion":
            return ElementRegion(damping=damping, **kwargs)
        elif regionType.lower() == "noderegion":
            return NodeRegion(damping=damping, **kwargs)
        elif regionType.lower() == "globalregion":
            return GlobalRegion(damping=damping)
        else:
            raise ValueError(f"""Invalid region type {regionType}
                             valid region types are ElementRegion, NodeRegion, GlobalRegion""")

    def remove_region(self, tag):
        """
        Remove a region by its tag.
        
        This method removes the specified region instance and automatically
        updates the tags of the remaining region instances to maintain sequential numbering.
        The GlobalRegion (tag 0) cannot be removed.
        
        Args:
            tag (int): The unique identifier of the region instance to remove
            
        Raises:
            ValueError: If attempting to remove the GlobalRegion (tag 0)
        """
        RegionBase.remove_region(tag)

    def clear_regions(self):
        """
        Remove all regions and reinitialize the GlobalRegion.
        
        This method clears all region instances, including the GlobalRegion,
        and then recreates the GlobalRegion with tag 0.
        """
        RegionBase.clear()
        initialize_region_base()

    def print_regions(self):
        """
        Print information about all regions.
        
        This method prints detailed information about all region instances
        including their tags, types, elements/nodes, and damping assignments.
        """
        RegionBase.print_regions()

if __name__ == "__main__":
    from meshmaker.components.Damping.dampingBase import RayleighDamping, ModalDamping
    # ---- Test Global Region ----
    # test the DampingBase class
    damping1 = DampingBase()
    damping2 = DampingBase()
    damping3 = DampingBase()

    RayleighDamping1 = RayleighDamping(alphaM=0.1, betaK=0.2, betaKInit=0.3, betaKComm=0.4)
    RayleighDamping2 = RayleighDamping(alphaM=0.5, betaK=0.6, betaKInit=0.7, betaKComm=0.8)
    ModalDamping1 = ModalDamping(numberofModes=2, dampingFactors="0.1,0.2")
    ModalDamping2 = ModalDamping(numberofModes=3, dampingFactors="0.3,0.4,0.5")

    initialize_region_base()
    global_region = RegionBase.get_region(0)
    global_region2 = GlobalRegion()
    global_region3 = GlobalRegion()



    assert global_region == global_region2, "Global regions should be equal"
    assert global_region is global_region3, "Global regions should be the same instance"
    assert global_region is not None, "Global region should exist"
    assert global_region.tag == 0, "Global region tag should be 0"
    assert global_region.name == "GlobalRegion", "Global region name incorrect"
    global_region.damping = DampingBase.get_damping(4)


    eleregion1 = ElementRegion(elements=[1, 2, 3])
    print("Global Region tests passed")



    eleregion1 = ElementRegion(elements=[1, 2, 3])
    eleregion2 = ElementRegion(element_range=[4, 10])
    eleregion4 = ElementRegion()
    eleregion5 = ElementRegion(tag=0)

    # Test Element Regions
    assert eleregion1.tag == 2, "Element region 1 tag should be 1"
    assert eleregion2.tag == 3, "Element region 2 tag should be 2"
    assert len(eleregion1.elements) == 3, "Element region 1 should have 3 elements"
    assert eleregion2.element_range == [4, 10], "Element region 2 range incorrect"
    eleregion3 = ElementRegion(tag=2)
    assert eleregion3.tag == 2, "Element region 3 tag should be 2"
    assert len(eleregion3.elements) == 0, "Element region 3 should have 0 elements"
    print("Element Region tests passed")

    # Test Node Regions
    noderegion1 = NodeRegion(nodes=[1, 2, 3])
    noderegion2 = NodeRegion(node_range=[4, 10])

    assert noderegion1.tag == 5, "Node region 1 tag should be 3"
    assert noderegion2.tag == 6, "Node region 2 tag should be 4"
    assert len(noderegion1.nodes) == 3, "Node region 1 should have 3 nodes"
    assert noderegion2.node_range == [4, 10], "Node region 2 range incorrect"
    noderegion3 = NodeRegion(tag=5)
    assert noderegion3.tag == 5, "Node region 3 tag should be 3"
    print("Node Region tests passed")

    # Test region removal and tag updates
    # Test removing global region (should raise ValueError)
    try:
        RegionBase.remove_region(0)
        assert False, "Should have raised ValueError"
    except ValueError:
        assert True

    # assign with damping 
    eleDamping = ElementRegion(elements=[1, 2, 4], damping=RayleighDamping1)
    nodeDamping = NodeRegion(nodes=[1, 2, 4], damping=ModalDamping1)
    baseDamping = GlobalRegion(damping=RayleighDamping1)
    # print(eleDamping)
    # print(nodeDamping)
    # print(baseDamping)

    print("Region assignment with damping passed")
    
    # Test damping assignment
    noderegion1.damping = RayleighDamping2
    assert noderegion1.damping is not None, "Damping should be assigned"
    print("Damping assignment test passed")

    print("\nAll tests passed successfully!")


