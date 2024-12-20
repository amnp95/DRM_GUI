from meshmaker.components.Material.materialBase import Material
# from meshmaker.components.Element.elementBase import ElementBase
from meshmaker.components.Assemble.Assembler import Assembler
import os

class MeshMaker:
    """
    Singleton class for managing OpenSees GUI operations and file exports
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of OpenSeesGUI if it doesn't exist
        
        Returns:
            OpenSeesGUI: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(MeshMaker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initialize the OpenSeesGUI instance
        
        Args:
            **kwargs: Keyword arguments including:
                - model_name (str): Name of the model
                - model_path (str): Path to save the model
        """
        # Only initialize once
        if self._initialized:
            return
            
        self._initialized = True
        self.model = None
        self.model_name = kwargs.get('model_name')
        self.model_path = kwargs.get('model_path')
        self.assembler = Assembler.get_instance()

    @classmethod
    def get_instance(cls, **kwargs):
        """
        Get the singleton instance of OpenSeesGUI
        
        Args:
            **kwargs: Keyword arguments to pass to the constructor
            
        Returns:
            OpenSeesGUI: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    def export_to_tcl(self, filename=None):
        """
        Export the model to a TCL file
        
        Args:
            filename (str, optional): The filename to export to. If None, 
                                    uses model_name in model_path
        
        Returns:
            bool: True if export was successful, False otherwise
            
        Raises:
            ValueError: If no filename is provided and model_name/model_path are not set
        """
        try:
            # Determine the full file path
            if filename is None:
                if self.model_name is None or self.model_path is None:
                    raise ValueError("Either provide a filename or set model_name and model_path")
                filename = os.path.join(self.model_path, f"{self.model_name}.tcl")
            
            # chek if the end is not .tcl then add it
            if not filename.endswith('.tcl'):
                filename += '.tcl'
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            # Get the assembled content
            content = "hello world"
            
            # Write to file
            with open(filename, 'w') as f:
                for tag,mat in Material._materials.items():
                    f.write(f"{mat}\n")
            
                
            return True
            
        except Exception as e:
            print(f"Error exporting to TCL: {str(e)}")
            return False

    def set_model_info(self, model_name=None, model_path=None):
        """
        Update model information
        
        Args:
            model_name (str, optional): New model name
            model_path (str, optional): New model path
        """
        if model_name is not None:
            self.model_name = model_name
        if model_path is not None:
            self.model_path = model_path
        