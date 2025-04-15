from meshmaker.components.Material.materialBase import MaterialManager
from meshmaker.components.Element.elementBase import Element, ElementRegistry
from meshmaker.components.Assemble.Assembler import Assembler
from meshmaker.components.Damping.dampingBase import DampingManager
from meshmaker.components.Region.regionBase import RegionManager
from meshmaker.components.Constraint.constraint import Constraint
from meshmaker.components.Mesh.meshPartBase import MeshPartRegistry
from meshmaker.components.Mesh.meshPartInstance import *
from meshmaker.components.TimeSeries.timeSeriesBase import TimeSeriesManager
from meshmaker.components.Analysis.analysis import AnalysisManager
from meshmaker.components.Pattern.patternBase import PatternManager
from meshmaker.components.Recorder.recorderBase import RecorderManager
from meshmaker.components.Process.process import ProcessManager
from meshmaker.components.DRM.DRM import DRM
import os
from numpy import unique, zeros, arange, array, abs, concatenate, meshgrid, ones, full, uint16, repeat, where, isin
from pyvista import Cube, MultiBlock, StructuredGrid
import tqdm
from pykdtree.kdtree import KDTree as pykdtree

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
        self.assembler = Assembler()
        self.material = MaterialManager()
        self.element = ElementRegistry()
        self.damping = DampingManager()
        self.region = RegionManager()
        self.constraint = Constraint()
        self.meshPart = MeshPartRegistry()
        self.timeSeries = TimeSeriesManager()
        self.analysis = AnalysisManager()
        self.pattern = PatternManager()
        self.recorder = RecorderManager()
        self.process = ProcessManager()
        
        # Initialize DRMHelper with a reference to this MeshMaker instance
        self.drm = DRM()
        self.drm.set_meshmaker(self)
        
    def _progress_callback(self, value, message):
        """
        Default progress callback using tqdm when no callback is provided
        
        Args:
            value (float): Progress value (0-100)
            message (str): Progress message
        """
        if not hasattr(self, '_tqdm_progress'):
            # Initialize tqdm progress bar on first call
            self._tqdm_progress = tqdm.tqdm(total=100, desc="Exporting to TCL", bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}")
            self._tqdm_progress.set_postfix_str(message)
            self._tqdm_progress.update(value)
        else:
            # Update existing progress bar
            current = self._tqdm_progress.n
            increment = int(value) - current
            if increment > 0:
                self._tqdm_progress.set_postfix_str(message)
                self._tqdm_progress.update(increment)
            
        # Close the progress bar if we're finished
        if value >= 100:
            self._tqdm_progress.close()
            delattr(self, '_tqdm_progress')

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
    

    def gui(self):
        """
        Launch the GUI application
        
        This method creates and shows the GUI window for interacting with the MeshMaker.
        It ensures that a Qt application is running and initializes the main window.
        
        Returns:
            MainWindow: The main window instance
        """
        try:
            # Import required modules
            from qtpy.QtWidgets import QApplication
            from meshmaker.gui.main_window import MainWindow
            
            # Ensure a QApplication instance exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                
            # Initialize and show the main window
            main_window = MainWindow()
            
            # Only start event loop if not already running
            if not app.startingUp():
                app.exec_()
                
            return main_window
        except ImportError as e:
            print(f"Error: Unable to load GUI components. {str(e)}")
            print("Please ensure qtpy, pyvista, and other GUI dependencies are installed.")
            return None

    def export_to_tcl(self, filename=None, progress_callback=None):
        """
        Export the model to a TCL file
        
        Args:
            filename (str, optional): The filename to export to. If None, 
                                     uses model_name in model_path
            progress_callback (callable, optional): Callback function to report progress.
                                                  If None, uses tqdm progress bar.
        
        Returns:
            bool: True if export was successful, False otherwise
            
        Raises:
            ValueError: If no filename is provided and model_name/model_path are not set
        """
        # Use the default tqdm progress callback if none is provided
        if progress_callback is None:
            progress_callback = self._progress_callback
            
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

                if progress_callback:
                    progress_callback(0, "writing materials")
                    

                # Write the materials
                f.write("\n# Materials ======================================\n")
                for tag,mat in self.material.get_all_materials().items():
                    f.write(f"{mat.to_tcl()}\n")

                if progress_callback:
                    progress_callback(5,"writing nodes and elements")

                # Write the nodes
                f.write("\n# Nodes & Elements ======================================\n")
                cores = self.assembler.AssembeledMesh.cell_data["Core"]
                num_cores = unique(cores)
                nodes     = self.assembler.AssembeledMesh.points
                ndfs      = self.assembler.AssembeledMesh.point_data["ndf"]
                num_nodes = self.assembler.AssembeledMesh.n_points
                wroted    = zeros((num_nodes, len(num_cores)), dtype=bool) # to keep track of the nodes that have been written
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
                    f.write("\t"+eleclass.to_tcl(eleTag, nodeTag) + "\n")
                    f.write("}\n")     
                    if progress_callback:
                        progress_callback((i / self.assembler.AssembeledMesh.n_cells) * 45 + 5, "writing nodes and elements")

                if progress_callback:
                    progress_callback(50, "writing dampings")
                # writ the dampings 
                f.write("\n# Dampings ======================================\n")
                if self.damping.get_all_dampings() is not None:
                    for tag,damp in self.damping.get_all_dampings().items():
                        f.write(f"{damp.to_tcl()}\n")
                else:
                    f.write("# No dampings found\n")

                if progress_callback:
                    progress_callback(55, "writing regions")

                # write regions
                f.write("\n# Regions ======================================\n")
                Regions = unique(self.assembler.AssembeledMesh.cell_data["Region"])
                for i,regionTag in enumerate(Regions):
                    region = self.region.get_region(regionTag)
                    if region.get_type().lower() == "noderegion":
                        raise ValueError(f"""Region {regionTag} is of type NodeTRegion which is not supported in yet""")
                    
                    region.setComponent("element", eleTags[self.assembler.AssembeledMesh.cell_data["Region"] == regionTag])
                    f.write(f"{region.to_tcl()} \n")
                    del region
                    if progress_callback:
                        progress_callback((i / Regions.shape[0]) * 10 + 55, "writing regions")

                if progress_callback:
                    progress_callback(65, "writing constraints")


                # Write mp constraints
                f.write("\n# mpConstraints ======================================\n")

                # Precompute mappings
                core_to_idx = {core: idx for idx, core in enumerate(num_cores)}
                master_nodes = zeros(num_nodes, dtype=bool)
                slave_nodes = zeros(num_nodes, dtype=bool)
                
                # Modified data structures to handle multiple constraints per node
                constraint_map = {}  # map master node to list of constraints
                constraint_map_rev = {}  # map slave node to list of (master_id, constraint) tuples
                
                for constraint in self.constraint.mp:
                    master_id = constraint.master_node - 1
                    master_nodes[master_id] = True
                    
                    # Add constraint to master's list
                    if master_id not in constraint_map:
                        constraint_map[master_id] = []
                    constraint_map[master_id].append(constraint)
                    
                    # For each slave, record the master and constraint
                    for slave_id in constraint.slave_nodes:
                        slave_id = slave_id - 1
                        slave_nodes[slave_id] = True
                        
                        if slave_id not in constraint_map_rev:
                            constraint_map_rev[slave_id] = []
                        constraint_map_rev[slave_id].append((master_id, constraint))

                # Get mesh data
                cells = self.assembler.AssembeledMesh.cell_connectivity
                offsets = self.assembler.AssembeledMesh.offset

                for core_idx, core in enumerate(num_cores):
                    # Get elements in current core
                    eleids = where(cores == core)[0]
                    if eleids.size == 0:
                        continue
                    
                    # Get all nodes in this core's elements
                    starts = offsets[eleids]
                    ends = offsets[eleids + 1]
                    core_node_indices = concatenate([cells[s:e] for s, e in zip(starts, ends)])
                    in_core = isin(arange(num_nodes), core_node_indices)
                    
                    # Find active masters and slaves in this core
                    active_masters = where(master_nodes & in_core)[0]
                    active_slaves = where(slave_nodes & in_core)[0]

                    # Add the master nodes that are not in the core but needed for constraints
                    masters_to_add = []
                    for slave_id in active_slaves:
                        if slave_id in constraint_map_rev:
                            for master_id, _ in constraint_map_rev[slave_id]:
                                masters_to_add.append(master_id)
                    
                    # Add unique masters
                    if masters_to_add:
                        active_masters = concatenate([active_masters, array(masters_to_add)])
                        active_masters = unique(active_masters)

                    if not active_masters.size:
                        continue

                    f.write(f"if {{$pid == {core}}} {{\n")
                    
                    # Process all master nodes that are not in the current core
                    valid_mask = ~in_core[active_masters]
                    valid_masters = active_masters[valid_mask]
                    if valid_masters.size > 0:
                        f.write("\t# Master nodes not defined in this core\n")
                        for master_id in valid_masters:
                            node = nodes[master_id]
                            f.write(f"\tnode {master_id+1} {node[0]} {node[1]} {node[2]} -ndf {ndfs[master_id]}\n")

                    # Process all slave nodes that are not in the current core
                    # Collect all unique slave nodes from active master nodes' constraints
                    all_slaves = []
                    for master_id in active_masters:
                        for constraint in constraint_map[master_id]:
                            all_slaves.extend([sid - 1 for sid in constraint.slave_nodes])
                    
                    # Filter out slave nodes that are not in the current core
                    valid_slaves = array([sid for sid in all_slaves if 0 <= sid < num_nodes and not in_core[sid]])
                    
                    if valid_slaves.size > 0:
                        f.write("\t# Slave nodes not defined in this core\n")
                        for slave_id in unique(valid_slaves):
                            node = nodes[slave_id]
                            f.write(f"\tnode {slave_id+1} {node[0]} {node[1]} {node[2]} -ndf {ndfs[slave_id]}\n")

                    # Write constraints after nodes
                    f.write("\t# Constraints\n")
                    
                    # Process constraints where master is in this core
                    for master_id in active_masters:
                        for constraint in constraint_map[master_id]:
                            f.write(f"\t{constraint.to_tcl()}\n")
                    
                    f.write("}\n")

                    if progress_callback:
                        progress = 65 + (core_idx + 1) / len(num_cores) * 15
                        progress_callback(min(progress, 80), "writing constraints")
                
                # write sp constraints
                f.write("\n# spConstraints ======================================\n")
                size = len(self.constraint.sp)
                indx = 1
                for constraint in self.constraint.sp:
                    f.write(f"{constraint.to_tcl()}\n")
                    if progress_callback:
                        progress_callback(80 + indx / size * 5, "writing sp constraints")
                    indx += 1


                # write time series
                f.write("\n# Time Series ======================================\n")
                size = len(self.timeSeries)
                indx = 1
                for timeSeries in self.timeSeries:
                    f.write(f"{timeSeries.to_tcl()}\n")
                    if progress_callback:
                        progress_callback(85 + indx / size * 5, "writing time series")
                    indx += 1

                # write process
                f.write("\n# Process ======================================\n")
                indx = 1
                size = len(self.process)
                f.write(f"{self.process.to_tcl()}\n")
                # for process in self.process:
                #     print(process["component"])
                #     f.write(f"{process['component'].to_tcl()}\n")
                #     if progress_callback:
                #         progress_callback(90 + indx / size * 10, "writing process")
                #     indx += 1


                
                    

                if progress_callback:
                    progress_callback(100,"finished writing")
                 
        return True



    def export_to_vtk(self,filename=None):
        '''
        Export the model to a vtk file

        Args:
            filename (str, optional): The filename to export to. If None, 
                                    uses model_name in model_path

        Returns:
            bool: True if export was successful, False otherwise
        '''
        if True:
            # Determine the full file path
            if filename is None:
                if self.model_name is None or self.model_path is None:
                    raise ValueError("Either provide a filename or set model_name and model_path")
                filename = os.path.join(self.model_path, f"{self.model_name}.vtk")
            
            # check if the end is not .vtk then add it
            if not filename.endswith('.vtk'):
                filename += '.vtk'
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

            # Get the assembled content
            if self.assembler.AssembeledMesh is None:
                print("No mesh found")
                raise ValueError("No mesh found\n Please assemble the mesh first")
            
            # export to vtk
            # self.assembler.AssembeledMesh.save(filename, binary=True)
            try:
                self.assembler.AssembeledMesh.save(filename, binary=True)
            except Exception as e:
                raise e
        return True

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


