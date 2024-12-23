from meshmaker.components.Material.materialManager import MaterialManager
from meshmaker.components.Element.elementBase import Element
from meshmaker.components.Assemble.Assembler import Assembler
import os
from numpy import unique, zeros, arange

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
        self.material = MaterialManager.get_instance()

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
        if True:
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
            if self.assembler.AssembeledMesh is None:
                print("No mesh found")
                raise ValueError("No mesh found\n Please assemble the mesh first")
            
            # Write to file
            with open(filename, 'w') as f:

                f.write("wipe\n")
                f.write("model BasicBuilder -ndm 3\n")
                f.write("set pid [getPID]\n")
                f.write("set np [getNP]\n")

                # Writ the meshBounds
                f.write("\n# Mesh Bounds ======================================\n")
                bounds = self.assembler.AssembeledMesh.bounds
                f.write(f"set X_MIN {bounds[0]}\n")
                f.write(f"set X_MAX {bounds[1]}\n")
                f.write(f"set Y_MIN {bounds[2]}\n")
                f.write(f"set Y_MAX {bounds[3]}\n")
                f.write(f"set Z_MIN {bounds[4]}\n")
                f.write(f"set Z_MAX {bounds[5]}\n")



                # Write the materials
                f.write("\n# Materials ======================================\n")
                for tag,mat in self.material.get_all_materials().items():
                    f.write(f"{mat}\n")

                # Write the nodes
                f.write("\n# Nodes & Elements ======================================\n")
                cores = self.assembler.AssembeledMesh.cell_data["Core"]
                num_cores = unique(cores).shape[0]
                # elements  = self.assembler.AssembeledMesh.cells
                # offset    = self.assembler.AssembeledMesh.offset
                nodes     = self.assembler.AssembeledMesh.points
                ndfs      = self.assembler.AssembeledMesh.point_data["ndf"]
                num_nodes = self.assembler.AssembeledMesh.n_points
                wroted    = zeros((num_nodes, num_cores), dtype=bool) # to keep track of the nodes that have been written
                nodeTags  = arange(1, num_nodes+1, dtype=int)
                eleTags   = arange(1, self.assembler.AssembeledMesh.n_cells+1, dtype=int)


                elementClassTag = self.assembler.AssembeledMesh.cell_data["ElementTag"]


                for i in range(self.assembler.AssembeledMesh.n_cells):
                    cell = self.assembler.AssembeledMesh.get_cell(i)
                    pids = cell.point_ids
                    core = cores[i]
                    f.write("if {$pid ==" + str(core) + "} {\n")
                    # writing nodes
                    for pid in pids:
                        if not wroted[pid][core]:
                            f.write(f"\tnode {nodeTags[pid]} {nodes[pid][0]} {nodes[pid][1]} {nodes[pid][2]} -ndf {ndfs[pid]}\n")
                            wroted[pid][core] = True
                    
                    eleclass = Element._elements[elementClassTag[i]]
                    nodeTag = [nodeTags[pid] for pid in pids]
                    eleTag = eleTags[i]
                    f.write("\t"+eleclass.toString(eleTag, nodeTag) + "\n")
                    f.write("}\n")




                


            
        return True
        #     return True
            
        # except Exception as e:
        #     print(f"Error exporting to TCL: {str(e)}")
        #     return False

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
        