from abc import ABC, abstractmethod
from femora.components.Material.materialBase import MaterialManager

class Action(ABC):
    """
    Abstract base class for all actions in the DRM_GUI.

    This class serves as a blueprint for creating specific actions
    that can be converted into a TCL script representation.
    """

    @abstractmethod
    def to_tcl(self) -> str:
        """
        Convert the action to its TCL script representation.

        This method must be implemented by all subclasses to define
        how the action is represented in TCL script format.

        Returns:
            str: A string containing the TCL script representation of the action.
        """
        raise NotImplementedError("Subclasses must implement the 'to_tcl' method.")



class wipe(Action):
    """
    Action to wipe the current mesh.

    This action clears the current mesh and prepares the system for a new mesh.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(wipe, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def to_tcl(self) -> str:
        return "wipe"
    

class wipeAnalysis(Action):
    """
    Action to wipe the current analysis.

    This action clears the current analysis and prepares the system for a new analysis.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(wipeAnalysis, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def to_tcl(self) -> str:
        return "wipeAnalysis"
    

class updateMaterialStageToElastic(Action):
    """
    Action to update all materials to elastic stage.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(updateMaterialStageToElastic, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def to_tcl(self) -> str:
        cmd = ""
        for mat in MaterialManager.get_all_materials().values():
            tmp = mat.updateMaterialStage("Elastic")
            if tmp != "":
                cmd += tmp + "\n"
        return cmd
    
class updateMaterialStageToPlastic(Action):
        """
        Action to update all materials to plastic stage.
        """
        _instance = None

        def __new__(cls, *args, **kwargs):
            if cls._instance is None:
                cls._instance = super(updateMaterialStageToPlastic, cls).__new__(cls, *args, **kwargs)
            return cls._instance

        def to_tcl(self) -> str:
            cmd = ""
            for mat in MaterialManager.get_all_materials().values():
                tmp = mat.updateMaterialStage("Plastic")
                if tmp != "":
                    cmd += tmp + "\n"
            return cmd
        
class reset(Action):
    """
    Action to reset the mesh to its initial state.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(reset, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def to_tcl(self) -> str:
        return "reset"
    
class loadConst(Action):
    """
    Action to load a constant.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(loadConst, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def to_tcl(self) -> str:
        return "loadConst"
    

class seTime(Action):
    """
    Action to set the time.
    """

    def __init__(self, pseudo_time: float):
        """
        Initialize the seTime action with a pseudo time.

        Args:
            pseudo_time (float): The pseudo time to set.
        """
        self.pseudo_time = pseudo_time

    def to_tcl(self) -> str:
        return f"setTime {self.pseudo_time}"
    

class exit(Action):
    """
    Action to exit the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(exit, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def to_tcl(self) -> str:
        return "exit"


        