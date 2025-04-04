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

    def export_to_tcl(self, filename=None, progress_callback=None):
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

                # # initilize regions list
                # regions = unique(self.assembler.AssembeledMesh.cell_data["Region"])
                # f.write("\n# Regions lists ======================================\n")
                # num_regions = regions.shape[0]
                # for i in range(num_regions):
                #     f.write(f"set region_{i} {}\n")

                if progress_callback:
                    progress_callback(0, "writing materials")
                    

                # Write the materials
                f.write("\n# Materials ======================================\n")
                for tag,mat in self.material.get_all_materials().items():
                    f.write(f"{mat}\n")

                if progress_callback:
                    progress_callback(5,"writing nodes and elements")

                # Write the nodes
                f.write("\n# Nodes & Elements ======================================\n")
                cores = self.assembler.AssembeledMesh.cell_data["Core"]
                num_cores = unique(cores)
                # elements  = self.assembler.AssembeledMesh.cells
                # offset    = self.assembler.AssembeledMesh.offset
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
                constraint_map = {}; # map master node to constraint
                constraint_map_rev = {}; # map slave node to master node
                for constraint in self.constraint.mp:
                    master_id = constraint.master_node - 1
                    master_nodes[master_id] = True
                    constraint_map[master_id] = constraint
                    for slave_id in constraint.slave_nodes:
                        slave_id = slave_id - 1
                        slave_nodes[slave_id] = True
                        constraint_map_rev[slave_id] = master_id

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

                    # add the master nodes that are not in the core
                    for slave_id in active_slaves:
                        active_masters = concatenate([active_masters, [constraint_map_rev[slave_id]]])
                    active_masters = unique(active_masters)

                    if not active_masters.size:
                        continue

                    f.write(f"if {{$pid == {core}}} {{\n")
                    
                    # Process all slaves first to maintain node ordering
                    # Get all slave nodes from active master nodes in a vectorized way
                    all_slaves = concatenate([constraint_map[master_id].slave_nodes for master_id in active_masters])
                    # Convert to 0-based indexing as slave nodes are stored with 1-based indexing
                    all_slaves = array(all_slaves) - 1

                    # Filter out slave nodes that are not in the curent core 
                    valid_mask = (all_slaves < num_nodes) & (all_slaves >= 0) & ~in_core[all_slaves]
                    valid_slaves = all_slaves[valid_mask]

                    # Filter out master nodes that are not in the current core
                    valid_mask = ~in_core[active_masters]
                    valid_masters = active_masters[valid_mask]

                    # Write unique master nodes
                    if valid_masters.size > 0:
                        f.write("\t# Master nodes\n")
                        for master_id in valid_masters:
                            node = nodes[master_id]
                            f.write(f"\tnode {master_id+1} {node[0]} {node[1]} {node[2]} -ndf {ndfs[master_id]}\n")


                    # Write unique slave nodes
                    if valid_slaves.size > 0:
                        f.write("\t# Slave nodes\n")
                        for slave_id in unique(valid_slaves):
                            node = nodes[slave_id]
                            f.write(f"\tnode {slave_id+1} {node[0]} {node[1]} {node[2]} -ndf {ndfs[slave_id]}\n")



                    # Write constraints after nodes
                    for master_id in active_masters:
                        f.write(f"\t{constraint_map[master_id].to_tcl()}\n")
                    
                    f.write("}\n")

                    if progress_callback:
                        progress = 65 + (core_idx + 1) / len(num_cores) * 15
                        progress_callback(min(progress, 80), "writing constraints")

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


    def addAbsorbingLayer(self, numLayers: int, numPartitions: int, partitionAlgo: str, geometry:str, 
                          rayleighDamping:float=0.95, matchDamping:bool=False
                          ,progress_callback=None, **kwargs):
        """
        Add a rectangular absorbing layer to the model
        This function is used to add an absorbing layer to the assembled mesh that has a rectangular shape 
        and has structured mesh. 

        Args:
            numLayers (int): Number of layers to add
            numPartitions (int): Number of partitions to divide the absorbing layer
            partitionAlgo (str): The algorithm to partition the absorbing layer could be ["kd-tree", "metis"]
            geometry (str): The geometry of the absorbing layer could be ["Rectangular", "Cylindrical"]
            rayleighDamping (float): The damping factor for the Rayleigh damping, default is 0.95
            matchDamping (bool): If True, the damping of the absorbing layer should match the damping of the original mesh, default is False
            kwargs (dict): 
                type (str): Type of the absorbing layer could be ["PML", "Rayleigh", "ASDA"]


        Raises:
            ValueError: If the mesh is not assembled
            ValueError: If the number of layers is less than 1
            ValueError: If the number of partitions is less than 0
            ValueError: If the geometry is not one of ["Rectangular", "Cylindrical"]
        
        Returns:
            bool: True if the absorbing layer is added successfully, False otherwise

        
        Examples:
            >>> addAbsorbingLayer(2, 2, "metis", "Rectangular", type="PML")
        """
        if self.assembler.AssembeledMesh is None:
            print("No mesh found")
            raise ValueError("No mesh found\n Please assemble the mesh first")
        if numLayers < 1:
            raise ValueError("Number of layers should be greater than 0")
        
        if numPartitions < 0:
            raise ValueError("Number of partitions should be greater or equal to 0")
        
        if geometry not in ["Rectangular", "Cylindrical"]:
            raise ValueError("Geometry should be one of ['Rectangular', 'Cylindrical']")
        
        if partitionAlgo not in ["kd-tree", "metis"]:
            raise ValueError("Partition algorithm should be one of ['kd-tree', 'metis']")
        
        if partitionAlgo == "metis":
            raise NotImplementedError("Metis partitioning algorithm is not implemented yet")
        
        if geometry == "Rectangular":
            return self._addRectangularAbsorbingLayer(numLayers, numPartitions, partitionAlgo,  
                                                      rayleighDamping, matchDamping,
                                                      progress_callback, **kwargs)
        elif geometry == "Cylindrical":
            raise NotImplementedError("Cylindrical absorbing layer is not implemented yet")
        

    def _addRectangularAbsorbingLayer(self, numLayers: int, numPartitions: int, partitionAlgo: str, 
                                      rayleighDamping:float = 0.95 , matchDamping:bool=False, 
                                      progress_callback=None, **kwargs):
        """
        Add a rectangular absorbing layer to the model
        This function is used to add an absorbing layer to the assembled mesh that has a rectangular shape 
        and has structured mesh. 

        Args:
            numLayers (int): Number of layers to add
            numPartitions (int): Number of partitions to divide the absorbing layer
            partitionAlgo (str): The algorithm to partition the absorbing layer could be ["kd-tree", "metis"]
            rayleighDamping (float): The damping factor for the Rayleigh damping, default is 0.95
            matchDamping (bool): If True, the damping of the absorbing layer should match the damping of the original mesh, default is False
            kwargs (dict): 
                type (str): Type of the absorbing layer could be ["PML", "Rayleigh", "ASDA"]


        Raises:
            ValueError: If the mesh is not assembled
            ValueError: If the number of layers is less than 1
            ValueError: If the number of partitions is less than 0

        Returns:
            bool: True if the absorbing layer is added successfully, False otherwise
        
        Examples:
            >>> _addRectangularAbsorbingLayer(2, 2, "metis", type="PML")
        """

        if self.assembler.AssembeledMesh is None:
            print("No mesh found")
            raise ValueError("No mesh found\n Please assemble the mesh first")
        if numLayers < 1:
            raise ValueError("Number of layers should be greater than 0")
        
        if numPartitions < 0:
            raise ValueError("Number of partitions should be greater or equal to 0")
        
        if partitionAlgo not in ["kd-tree", "metis"]:
            raise ValueError("Partition algorithm should be one of ['kd-tree', 'metis']")
        
        if partitionAlgo == "metis":
            raise NotImplementedError("Metis partitioning algorithm is not implemented yet")
        
        if 'type' not in kwargs:
            raise ValueError("Type of the absorbing layer should be provided \n \
                             The type of the absorbing layer could be one of ['PML', 'Rayleigh', 'ASDA']")
        else:
            if kwargs['type'] not in ["PML", "Rayleigh", "ASDA"]:
                raise ValueError("Type of the absorbing layer should be one of ['PML', 'Rayleigh', 'ASDA']")
            if kwargs['type'] == "PML":
                ndof = 9
                mergeFlag = False
            elif kwargs['type'] == "Rayleigh":
                ndof = 3
                mergeFlag = True
            elif kwargs['type'] == "ASDA":
                ndof = 3
                mergeFlag = True
                raise NotImplementedError("ASDA absorbing layer is not implemented yet")

        
        mesh = self.assembler.AssembeledMesh.copy()
        num_partitions  = mesh.cell_data["Core"].max() # previous number of partitions from the assembled mesh
        bounds = mesh.bounds
        eps = 1e-6
        bounds = tuple(array(bounds) + array([eps, -eps, eps, -eps, eps, +10]))
        
        # cheking the number of partitions compatibility
        if numPartitions == 0:
            if num_partitions > 0:
                raise ValueError("The number of partitions should be greater than 0 if your model has partitions")
            

        cube = Cube(bounds=bounds)
        cube = cube.clip(normal=[0, 0, 1], origin=[0, 0, bounds[5]-eps])
        clipped = mesh.copy().clip_surface(cube, invert=False, crinkle=True)
        
        
        # regionize the cells
        cellCenters = clipped.cell_centers(vertex=True)
        cellCentersCoords = cellCenters.points

        xmin, xmax, ymin, ymax, zmin, zmax = cellCenters.bounds

        eps = 1e-6
        left   = abs(cellCentersCoords[:, 0] - xmin) < eps
        right  = abs(cellCentersCoords[:, 0] - xmax) < eps
        front  = abs(cellCentersCoords[:, 1] - ymin) < eps
        back   = abs(cellCentersCoords[:, 1] - ymax) < eps
        bottom = abs(cellCentersCoords[:, 2] - zmin) < eps

        # create the mask
        clipped.cell_data['absRegion'] = zeros(clipped.n_cells, dtype=int)
        clipped.cell_data['absRegion'][left]                   = 1
        clipped.cell_data['absRegion'][right]                  = 2
        clipped.cell_data['absRegion'][front]                  = 3
        clipped.cell_data['absRegion'][back]                   = 4
        clipped.cell_data['absRegion'][bottom]                 = 5
        clipped.cell_data['absRegion'][left & front]           = 6
        clipped.cell_data['absRegion'][left & back ]           = 7
        clipped.cell_data['absRegion'][right & front]          = 8
        clipped.cell_data['absRegion'][right & back]           = 9
        clipped.cell_data['absRegion'][left & bottom]          = 10
        clipped.cell_data['absRegion'][right & bottom]         = 11
        clipped.cell_data['absRegion'][front & bottom]         = 12
        clipped.cell_data['absRegion'][back & bottom]          = 13
        clipped.cell_data['absRegion'][left & front & bottom]  = 14
        clipped.cell_data['absRegion'][left & back & bottom]   = 15
        clipped.cell_data['absRegion'][right & front & bottom] = 16
        clipped.cell_data['absRegion'][right & back & bottom]  = 17


        cellCenters.cell_data['absRegion'] = clipped.cell_data['absRegion']
        normals = [[-1,  0,  0],
                   [ 1,  0,  0],
                   [ 0, -1,  0],
                   [ 0,  1,  0],
                   [ 0,  0, -1],
                   [-1, -1,  0],
                   [-1,  1,  0],
                   [ 1, -1,  0],
                   [ 1,  1,  0],
                   [-1,  0, -1],
                   [ 1,  0, -1],
                   [ 0, -1, -1],
                   [ 0,  1, -1],
                   [-1, -1, -1],
                   [-1,  1, -1],
                   [ 1, -1, -1],
                   [ 1,  1, -1]]

        Absorbing = MultiBlock()

        total_cells = clipped.n_cells
        TQDM_progress = tqdm.tqdm(range(total_cells))
        TQDM_progress.reset()
        material_tags = []
        absorbing_regions = []
        element_tags = []
        region_tags = []
        
        for i in range(total_cells ):
            cell = clipped.get_cell(i)
            xmin, xmax, ymin, ymax, zmin, zmax = cell.bounds
            dx = abs((xmax - xmin))
            dy = abs((ymax - ymin))
            dz = abs((zmax - zmin))

            absregion = clipped.cell_data['absRegion'][i]
            MaterialTag = clipped.cell_data['MaterialTag'][i]
            ElementTag = clipped.cell_data['ElementTag'][i]
            regionTag  = clipped.cell_data['Region'][i]
            normal = array(normals[absregion-1])
            coords = cell.points + normal * numLayers * array([dx, dy, dz])
            coords = concatenate([coords, cell.points])
            xmin, ymin, zmin = coords.min(axis=0)
            xmax, ymax, zmax = coords.max(axis=0)
            x = arange(xmin, xmax+1e-6, dx)
            y = arange(ymin, ymax+1e-6, dy)
            z = arange(zmin, zmax+1e-6, dz)
            X,Y,Z = meshgrid(x, y, z, indexing='ij')
            tmpmesh = StructuredGrid(X,Y,Z)

            material_tags.append(MaterialTag)
            absorbing_regions.append(absregion)
            element_tags.append(ElementTag)
            region_tags.append(regionTag)

            Absorbing.append(tmpmesh)
            TQDM_progress.update(1)
            if progress_callback:
                progress_callback(( i + 1) / total_cells  * 80)
            del tmpmesh


        TQDM_progress.close()


        total_cells     = sum(block.n_cells for block in Absorbing)
        MaterialTag     = zeros(total_cells, dtype=uint16)
        AbsorbingRegion = zeros(total_cells, dtype=uint16)
        ElementTag      = zeros(total_cells, dtype=uint16)
        RegionTag       = zeros(total_cells, dtype=uint16)

        offset = 0
        for i, block in enumerate(Absorbing):
            n_cells = block.n_cells
            MaterialTag[offset:offset+n_cells] = repeat(material_tags[i], n_cells).astype(uint16)
            AbsorbingRegion[offset:offset+n_cells] = repeat(absorbing_regions[i], n_cells).astype(uint16)
            ElementTag[offset:offset+n_cells] = repeat(element_tags[i], n_cells).astype(uint16)
            RegionTag[offset:offset+n_cells] = repeat(region_tags[i], n_cells).astype(uint16)
            offset += n_cells
            if progress_callback:
                progress_callback(( i + 1) / Absorbing.n_blocks  * 20 + 80)

        Absorbing = Absorbing.combine(merge_points=True)
        Absorbing.cell_data['MaterialTag'] = MaterialTag
        Absorbing.cell_data['AbsorbingRegion'] = AbsorbingRegion
        Absorbing.cell_data['ElementTag'] = ElementTag
        Absorbing.cell_data['Region'] = RegionTag
        del MaterialTag, AbsorbingRegion, ElementTag

        Absorbingidx = Absorbing.find_cells_within_bounds(cellCenters.bounds)
        indicies = ones(Absorbing.n_cells, dtype=bool)
        indicies[Absorbingidx] = False
        Absorbing = Absorbing.extract_cells(indicies)
        Absorbing = Absorbing.clean(tolerance=1e-6,
                                    remove_unused_points=True,
                                    produce_merge_map=False,
                                    average_point_data=True,
                                    progress_bar=False)
        

        MatTag = Absorbing.cell_data['MaterialTag']
        EleTag = Absorbing.cell_data['ElementTag']
        RegTag = Absorbing.cell_data['AbsorbingRegion']
        RegionTag = Absorbing.cell_data['Region']

        Absorbing.clear_data()
        Absorbing.cell_data['MaterialTag'] = MatTag
        Absorbing.cell_data['ElementTag'] = EleTag
        Absorbing.cell_data['AbsorbingRegion'] = RegTag
        Absorbing.cell_data['Region'] = RegionTag
        Absorbing.point_data['ndf'] = full(Absorbing.n_points, ndof, dtype=uint16)

        Absorbing.cell_data["Core"] = full(Absorbing.n_cells, 0, dtype=int)

        if kwargs['type'] == "PML":
            EleTags = unique(Absorbing.cell_data['ElementTag'])
            PMLTags = {}

            # create PML Element
            xmin, xmax, ymin, ymax, zmin, zmax = mesh.bounds
            RD_width_x = (xmax - xmin)
            RD_width_y = (ymax - ymin)
            RD_Depth = (zmax - zmin)
            RD_center_x = (xmax + xmin) / 2
            RD_center_y = (ymax + ymin) / 2
            RD_center_z = zmax

            # check all the elements should of type stdBrick or bbarBrick or SSPbrick
            for tag in EleTags:
                ele = self.element.get_element(tag)

                if ele.element_type not in ["stdBrick", "bbarBrick", "SSPbrick"]:
                    raise ValueError(f"boundary elements should be of type stdBrick or bbarBrick or SSPbrick not {ele.element_type}")
                
                mat = ele.get_material()

                # check that the material is elastic
                if mat.material_name != "ElasticIsotropic" or mat.material_type != "nDMaterial":
                    raise ValueError(f"boundary elements should have an ElasticIsotropic material not {mat.material_name} {mat.material_type}")

                PMLele = self.element.create_element("PML3D", ndof, mat, 
                                            gamma = 0.5,
                                            beta  = 0.25,
                                            eta   = 1./12.0,
                                            ksi   = 1.0/48.0,
                                            PML_Thickness = numLayers*dx,
                                            m = 2,
                                            R = 1.0e-8,
                                            meshType = "Box",
                                            meshTypeParameters = [RD_center_x, RD_center_y, RD_center_z, RD_width_x, RD_width_y, RD_Depth],
                                            alpha0 = None,
                                            beta0 = None,
                                            Cp = None,
                                            )

                PMLeleTag = PMLele.tag
                PMLTags[tag] = PMLeleTag

            # update the element tags
            for i, tag in enumerate(EleTags):
                Absorbing.cell_data['ElementTag'][Absorbing.cell_data['ElementTag'] == tag] = PMLTags[tag]


        if numPartitions > 1:
            partitiones = Absorbing.partition(numPartitions,
                                              generate_global_id=True, 
                                              as_composite=True)
            
            for i, partition in enumerate(partitiones):
                ids = partition.cell_data["vtkGlobalCellIds"]
                Absorbing.cell_data["Core"][ids] = i + num_partitions + 1
            
            del partitiones

        elif numPartitions == 1:
            Absorbing.cell_data["Core"] = full(Absorbing.n_cells, num_partitions + 1, dtype=int)

        if kwargs['type'] == "Rayleigh":
            if not matchDamping:
                damping = self.damping.create_damping("frequency rayleigh", dampingFactor=rayleighDamping)
                region  = self.region.create_region("elementRegion", damping=damping)
                Absorbing.cell_data["Region"]  = full(Absorbing.n_cells, region.tag, dtype=uint16)
        
        if kwargs['type'] == "PML":
            if not matchDamping:
                damping = self.damping.create_damping("frequency rayleigh", dampingFactor=rayleighDamping)
                region  = self.region.create_region("elementRegion", damping=damping)
                Absorbing.cell_data["Region"]  = full(Absorbing.n_cells, region.tag, dtype=uint16)

        if kwargs['type'] == "ASDA":
            raise NotImplementedError("ASDA absorbing layer is not implemented yet")
    
        mesh.cell_data["AbsorbingRegion"] = zeros(mesh.n_cells, dtype=uint16)


        # make the core for the interface elemnts the same as the original mesh
        if kwargs['type'] == "PML":
            absorbingCenters = Absorbing.cell_centers(vertex=True).points
            tree = pykdtree(absorbingCenters)
            distances, indices = tree.query(cellCentersCoords, k=1)
            





        self.assembler.AssembeledMesh = mesh.merge(Absorbing, 
                                                  merge_points=mergeFlag, 
                                                  tolerance=1e-6, 
                                                  inplace=False, 
                                                  progress_bar=True)
        self.assembler.AssembeledMesh.set_active_scalars("AbsorbingRegion")


        if kwargs['type'] == "PML":
            # creating the mapping for the equal dof 
            interfacepoints = mesh.points
            xmin, xmax, ymin, ymax, zmin, zmax = mesh.bounds
            xmin = xmin + eps
            xmax = xmax - eps
            ymin = ymin + eps
            ymax = ymax - eps
            zmin = zmin + eps
            zmax = zmax + 10

            mask = (
                (interfacepoints[:, 0] > xmin) & 
                (interfacepoints[:, 0] < xmax) & 
                (interfacepoints[:, 1] > ymin) & 
                (interfacepoints[:, 1] < ymax) & 
                (interfacepoints[:, 2] > zmin) & 
                (interfacepoints[:, 2] < zmax)
            )
            mask = where(~mask)
            interfacepoints = interfacepoints[mask]

            # create the kd-tree
            tree = pykdtree(self.assembler.AssembeledMesh.points)
            distances, indices = tree.query(interfacepoints, k=2)


            # check the distances 
            distances  = abs(distances)
            # check that maximum distance is less than 1e-6
            if distances.max() > 1e-6:
                raise ValueError("The PML layer mesh points are not matching with the original mesh points")
            
            # create the equal dof
            for i, index in enumerate(indices):
                # check that the index 1 is always has 9 dof and index 0 has 3 dof
                ndf1 = self.assembler.AssembeledMesh.point_data["ndf"][index[0]]
                ndf2 = self.assembler.AssembeledMesh.point_data["ndf"][index[1]]

                if ndf1 == 9 and ndf2 == 3:
                    masterNode = index[1] + 1
                    slaveNode  = index[0] + 1
                elif ndf1 == 3 and ndf2 == 9:
                    masterNode = index[0] + 1
                    slaveNode  = index[1] + 1   
                else:
                    raise ValueError("The PML layer node should have 9 dof and the original mesh should have at least 3 dof")
                
                self.constraint.mp.create_equal_dof(masterNode, [slaveNode],[1,2,3])

                
