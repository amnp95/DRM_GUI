from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union, Type

class Recorder(ABC):
    """
    Base abstract class for all recorder types in OpenSees.
    
    Recorders are used to monitor what is happening during the analysis 
    and generate output for the user. The output may go to the screen, 
    files, databases, or to remote processes through TCP/IP options.
    """
    _recorders = {}  # Class-level dictionary to track all recorders
    _next_tag = 1   # Class variable to track the next tag to assign

    def __init__(self, recorder_type: str):
        """
        Initialize a new recorder with a sequential tag
        
        Args:
            recorder_type (str): The type of recorder (e.g., 'Node', 'Element', 'VTKHDF')
        """
        self.tag = Recorder._next_tag
        Recorder._next_tag += 1
        
        self.recorder_type = recorder_type
        
        # Register this recorder in the class-level tracking dictionary
        Recorder._recorders[self.tag] = self

    @classmethod
    def get_recorder(cls, tag: int) -> 'Recorder':
        """
        Retrieve a specific recorder by its tag.
        
        Args:
            tag (int): The tag of the recorder
        
        Returns:
            Recorder: The recorder with the specified tag
        
        Raises:
            KeyError: If no recorder with the given tag exists
        """
        if tag not in cls._recorders:
            raise KeyError(f"No recorder found with tag {tag}")
        return cls._recorders[tag]

    @classmethod
    def remove_recorder(cls, tag: int) -> None:
        """
        Delete a recorder by its tag.
        
        Args:
            tag (int): The tag of the recorder to delete
        """
        if tag in cls._recorders:
            del cls._recorders[tag]
            # Recalculate _next_tag if needed
            if cls._recorders:
                cls._next_tag = max(cls._recorders.keys()) + 1
            else:
                cls._next_tag = 1

    @classmethod
    def get_all_recorders(cls) -> Dict[int, 'Recorder']:
        """
        Retrieve all created recorders.
        
        Returns:
            Dict[int, Recorder]: A dictionary of all recorders, keyed by their unique tags
        """
        return cls._recorders
    
    @classmethod
    def clear_all(cls) -> None:
        """
        Clear all recorders and reset tags.
        """
        cls._recorders.clear()
        cls._next_tag = 1

    @abstractmethod
    def to_tcl(self) -> str:
        """
        Convert the recorder to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        pass

    @staticmethod
    def get_parameters() -> List[tuple]:
        """
        Get the parameters defining this recorder
        
        Returns:
            List[tuple]: List of (parameter name, description) tuples
        """
        pass

    @abstractmethod
    def get_values(self) -> Dict[str, Union[str, int, float, list]]:
        """
        Get the parameters defining this recorder
        
        Returns:
            Dict[str, Union[str, int, float, list]]: Dictionary of parameter values
        """
        pass


class NodeRecorder(Recorder):
    """
    Node recorder class records the response of a number of nodes 
    at every converged step.
    """
    def __init__(self, **kwargs):
        """
        Initialize a Node Recorder
        
        Args:
            file_name (str, optional): Name of file to which output is sent
            xml_file (str, optional): Name of XML file to which output is sent
            binary_file (str, optional): Name of binary file to which output is sent
            inet_addr (str, optional): IP address of remote machine
            port (int, optional): Port on remote machine awaiting TCP
            precision (int, optional): Number of significant digits (default: 6)
            time_series (int, optional): Tag of previously constructed TimeSeries
            time (bool, optional): Places domain time in first output column
            delta_t (float, optional): Time interval for recording
            close_on_write (bool, optional): Opens and closes file on each write
            nodes (List[int], optional): Tags of nodes whose response is being recorded
            node_range (List[int], optional): Start and end node tags
            region (int, optional): Tag of previously defined region
            dofs (List[int]): List of DOF at nodes whose response is requested
            resp_type (str): String indicating response required
        """
        super().__init__("Node")
        self.file_name = kwargs.get("file_name", None)
        self.xml_file = kwargs.get("xml_file", None)
        self.binary_file = kwargs.get("binary_file", None)
        self.inet_addr = kwargs.get("inet_addr", None)
        self.port = kwargs.get("port", None)
        self.precision = kwargs.get("precision", 6)
        self.time_series = kwargs.get("time_series", None)
        self.time = kwargs.get("time", False)
        self.delta_t = kwargs.get("delta_t", None)
        self.close_on_write = kwargs.get("close_on_write", False)
        self.nodes = kwargs.get("nodes", None)
        self.node_range = kwargs.get("node_range", None)
        self.region = kwargs.get("region", None)
        self.dofs = kwargs.get("dofs", [])
        self.resp_type = kwargs.get("resp_type", "")
        
        # Validate the recorder parameters
        self.validate()

    def validate(self):
        """
        Validate recorder parameters
        
        Raises:
            ValueError: If the parameters are invalid
        """
        # Check that only one output destination is specified
        output_options = [
            self.file_name is not None,
            self.xml_file is not None,
            self.binary_file is not None,
            (self.inet_addr is not None and self.port is not None)
        ]
        if sum(output_options) > 1:
            raise ValueError("Only one of -file, -xml, -binary, or -tcp may be used")
        
        # Check that only one node selection method is specified
        node_options = [
            self.nodes is not None,
            self.node_range is not None,
            self.region is not None
        ]
        if sum(node_options) > 1:
            raise ValueError("Only one of -node, -nodeRange, or -region may be used")
        
        # Check that at least one node selection method is specified
        if sum(node_options) == 0:
            raise ValueError("One of -node, -nodeRange, or -region must be specified")
        
        # Check that dofs and resp_type are specified
        if not self.dofs:
            raise ValueError("DOFs must be specified")
        
        if not self.resp_type:
            raise ValueError("Response type must be specified")
        
        # Check that resp_type is valid
        valid_resp_types = [
            "disp", "vel", "accel", "incrDisp", "reaction", "rayleighForces"
        ]
        # Allow "eigen $mode" format
        if not (self.resp_type in valid_resp_types or self.resp_type.startswith("eigen ")):
            raise ValueError(f"Invalid response type: {self.resp_type}. " 
                           f"Valid types are: {', '.join(valid_resp_types)}, or 'eigen $mode'")

    def to_tcl(self) -> str:
        """
        Convert the Node recorder to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """
        cmd = "recorder Node"
        
        # Output destination
        if self.file_name:
            cmd += f" -file {self.file_name}"
        elif self.xml_file:
            cmd += f" -xml {self.xml_file}"
        elif self.binary_file:
            cmd += f" -binary {self.binary_file}"
        elif self.inet_addr and self.port:
            cmd += f" -tcp {self.inet_addr} {self.port}"
        
        # Other options
        if self.precision != 6:
            cmd += f" -precision {self.precision}"
        
        if self.time_series:
            cmd += f" -timeSeries {self.time_series}"
        
        if self.time:
            cmd += " -time"
        
        if self.delta_t:
            cmd += f" -dT {self.delta_t}"
        
        if self.close_on_write:
            cmd += " -closeOnWrite"
        
        # Node selection
        if self.nodes:
            cmd += f" -node {' '.join(map(str, self.nodes))}"
        elif self.node_range:
            cmd += f" -nodeRange {self.node_range[0]} {self.node_range[1]}"
        elif self.region:
            cmd += f" -region {self.region}"
        
        # DOFs and response type
        cmd += f" -dof {' '.join(map(str, self.dofs))} {self.resp_type}"
        
        return cmd

    @staticmethod
    def get_parameters() -> List[tuple]:
        """
        Get the parameters defining this recorder
        
        Returns:
            List[tuple]: List of (parameter name, description) tuples
        """
        return [
            ("file_name", "Name of file to which output is sent"),
            ("xml_file", "Name of XML file to which output is sent"),
            ("binary_file", "Name of binary file to which output is sent"),
            ("inet_addr", "IP address of remote machine"),
            ("port", "Port on remote machine awaiting TCP"),
            ("precision", "Number of significant digits (default: 6)"),
            ("time_series", "Tag of previously constructed TimeSeries"),
            ("time", "Places domain time in first output column"),
            ("delta_t", "Time interval for recording"),
            ("close_on_write", "Opens and closes file on each write"),
            ("nodes", "Tags of nodes whose response is being recorded"),
            ("node_range", "Start and end node tags"),
            ("region", "Tag of previously defined region"),
            ("dofs", "List of DOF at nodes whose response is requested"),
            ("resp_type", "String indicating response required")
        ]

    def get_values(self) -> Dict[str, Union[str, int, float, list, bool]]:
        """
        Get the parameters defining this recorder
        
        Returns:
            Dict[str, Union[str, int, float, list, bool]]: Dictionary of parameter values
        """
        return {
            "file_name": self.file_name,
            "xml_file": self.xml_file,
            "binary_file": self.binary_file,
            "inet_addr": self.inet_addr,
            "port": self.port,
            "precision": self.precision,
            "time_series": self.time_series,
            "time": self.time,
            "delta_t": self.delta_t,
            "close_on_write": self.close_on_write,
            "nodes": self.nodes,
            "node_range": self.node_range,
            "region": self.region,
            "dofs": self.dofs,
            "resp_type": self.resp_type
        }


class VTKHDFRecorder(Recorder):
    """
    The VTKHDF recorder type is a whole model recorder designed to record 
    the model geometry and metadata, along with selected response quantities.
    The output of this recorder is in the .h5 file format, which can be 
    visualized using visualization tools like ParaView.
    """
    def __init__(self, **kwargs):
        """
        Initialize a VTKHDF Recorder
        
        Args:
            file_base_name (str): Base name of the file to which output is sent
            resp_types (List[str]): List of strings indicating response types to record
            delta_t (float, optional): Time interval for recording
            r_tol_dt (float, optional): Relative tolerance for time step matching
        """
        super().__init__("VTKHDF")
        self.file_base_name = kwargs.get("file_base_name", "")
        self.resp_types = kwargs.get("resp_types", [])
        self.delta_t = kwargs.get("delta_t", None)
        self.r_tol_dt = kwargs.get("r_tol_dt", None)
        
        # Validate the recorder parameters
        self.validate()

    def validate(self):
        """
        Validate recorder parameters
        
        Raises:
            ValueError: If the parameters are invalid
        """
        # Check that file_base_name is specified
        if not self.file_base_name:
            raise ValueError("File base name must be specified")
        
        # Check that at least one response type is specified
        if not self.resp_types:
            raise ValueError("At least one response type must be specified")
        
        # Check that resp_types are valid
        valid_resp_types = [
            "disp", "vel", "accel", "stress3D6", "strain3D6", "stress2D3", "strain2D3"
        ]
        for resp_type in self.resp_types:
            if resp_type not in valid_resp_types:
                raise ValueError(f"Invalid response type: {resp_type}. "
                               f"Valid types are: {', '.join(valid_resp_types)}")

    def to_tcl(self) -> str:
        """
        Convert the VTKHDF recorder to a TCL command string for OpenSees
        
        Returns:
            str: The TCL command string
        """

        # separete name and format of the file
        name = self.file_base_name.split(".")
        fileformat = name[-1]
        name = name[0]
        name = name+"$pid"
        file_base_name = name+"." + fileformat

        cmd = f"recorder vtkhdf {file_base_name}"
        
        # Add optional parameters
        if self.delta_t is not None:
            cmd += f" -dT {self.delta_t}"

        if self.r_tol_dt is not None:
            cmd += f" -rTolDt {self.r_tol_dt}"

        # Add response types
        for resp_type in self.resp_types:
            cmd += f" {resp_type}"
        
        
        
        return cmd

    @staticmethod
    def get_parameters() -> List[tuple]:
        """
        Get the parameters defining this recorder
        
        Returns:
            List[tuple]: List of (parameter name, description) tuples
        """
        return [
            ("file_base_name", "Base name of the file to which output is sent"),
            ("resp_types", "List of strings indicating response types to record"),
            ("delta_t", "Time interval for recording"),
            ("r_tol_dt", "Relative tolerance for time step matching")
        ]

    def get_values(self) -> Dict[str, Union[str, list, float]]:
        """
        Get the parameters defining this recorder
        
        Returns:
            Dict[str, Union[str, list, float]]: Dictionary of parameter values
        """
        return {
            "file_base_name": self.file_base_name,
            "resp_types": self.resp_types,
            "delta_t": self.delta_t,
            "r_tol_dt": self.r_tol_dt
        }


class RecorderRegistry:
    """
    A registry to manage recorder types and their creation.
    """
    _recorder_types = {
        'node': NodeRecorder,
        'vtkhdf': VTKHDFRecorder
    }

    @classmethod
    def register_recorder_type(cls, name: str, recorder_class: Type[Recorder]):
        """
        Register a new recorder type for easy creation.
        
        Args:
            name (str): The name of the recorder type
            recorder_class (Type[Recorder]): The class of the recorder
        """
        cls._recorder_types[name.lower()] = recorder_class

    @classmethod
    def get_recorder_types(cls):
        """
        Get available recorder types.
        
        Returns:
            List[str]: Available recorder types
        """
        return list(cls._recorder_types.keys())

    @classmethod
    def create_recorder(cls, recorder_type: str, **kwargs) -> Recorder:
        """
        Create a new recorder of a specific type.
        
        Args:
            recorder_type (str): Type of recorder to create
            **kwargs: Parameters for recorder initialization
        
        Returns:
            Recorder: A new recorder instance
        
        Raises:
            KeyError: If the recorder type is not registered
        """
        if recorder_type.lower() not in cls._recorder_types:
            raise KeyError(f"Recorder type {recorder_type} not registered")
        
        return cls._recorder_types[recorder_type.lower()](**kwargs)


class RecorderManager:
    """
    Singleton class for managing recorders
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecorderManager, cls).__new__(cls)
        return cls._instance

    def create_recorder(self, recorder_type: str, **kwargs) -> Recorder:
        """Create a new recorder"""
        return RecorderRegistry.create_recorder(recorder_type, **kwargs)

    def get_recorder(self, tag: int) -> Recorder:
        """Get recorder by tag"""
        return Recorder.get_recorder(tag)

    def remove_recorder(self, tag: int) -> None:
        """Remove recorder by tag"""
        Recorder.remove_recorder(tag)

    def get_all_recorders(self) -> Dict[int, Recorder]:
        """Get all recorders"""
        return Recorder.get_all_recorders()

    def get_available_types(self) -> List[str]:
        """Get list of available recorder types"""
        return RecorderRegistry.get_recorder_types()
    
    def clear_all(self):
        """Clear all recorders"""  
        Recorder.clear_all()


# Example usage
if __name__ == "__main__":
    # Create a RecorderManager instance
    recorder_manager = RecorderManager()
    
    # Create a Node recorder
    node_recorder = recorder_manager.create_recorder(
        "node",
        file_name="nodesD.out",
        time=True,
        nodes=[1, 2, 3, 4],
        dofs=[1, 2],
        resp_type="disp"
    )
    
    # Output the TCL command
    print(node_recorder.to_tcl())
    
    # Create a VTKHDF recorder
    vtkhdf_recorder = recorder_manager.create_recorder(
        "vtkhdf",
        file_base_name="results",
        resp_types=["disp", "vel", "accel", "stress3D6", "strain3D6"],
        delta_t=0.1,
        r_tol_dt=0.00001
    )
    
    # Output the TCL command
    print(vtkhdf_recorder.to_tcl())