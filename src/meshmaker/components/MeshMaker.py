from meshmaker.components.Material.materialManager import MaterialManager
from meshmaker.components.Element.elementBase import Element
from meshmaker.components.Assemble.Assembler import Assembler
from meshmaker.components.Damping.dampingBase import DampingManager
from meshmaker.components.Region.regionBase import RegionManager
import os
from numpy import unique, zeros, arange, array, abs, concatenate, meshgrid, ones, full, uint16, repeat
from pyvista import Cube, MultiBlock, StructuredGrid
import tqdm


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
        self.damping = DampingManager()
        self.region = RegionManager()

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

                # # initilize regions list
                # regions = unique(self.assembler.AssembeledMesh.cell_data["Region"])
                # f.write("\n# Regions lists ======================================\n")
                # num_regions = regions.shape[0]
                # for i in range(num_regions):
                #     f.write(f"set region_{i} {}\n")

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
                    f.write("\t"+eleclass.to_tcl(eleTag, nodeTag) + "\n")
                    f.write("}\n")     

                # writ the dampings 
                f.write("\n# Dampings ======================================\n")
                if self.damping.get_all_dampings() is not None:
                    for tag,damp in self.damping.get_all_dampings().items():
                        f.write(f"{damp.to_tcl()}\n")
                else:
                    f.write("# No dampings found\n")

                # write regions
                f.write("\n# Regions ======================================\n")
                Regions = unique(self.assembler.AssembeledMesh.cell_data["Region"])
                for regionTag in Regions:
                    region = self.region.get_region(regionTag)
                    if region.get_type().lower() == "noderegion":
                        raise ValueError(f"""Region {regionTag} is of type NodeTRegion which is not supported in yet""")
                    
                    region.setComponent("element", eleTags[self.assembler.AssembeledMesh.cell_data["Region"] == regionTag])
                    f.write(f"{region.to_tcl()} \n")
                    del region

                    


                    


                 
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


    def addAbsorbingLayer(self, numLayers: int, numPartitions: int, partitionAlgo: str, geometry:str, rayleighDamping:float=0.95 ,progress_callback=None, **kwargs):
        """
        Add a rectangular absorbing layer to the model
        This function is used to add an absorbing layer to the assembled mesh that has a rectangular shape 
        and has structured mesh. 

        Args:
            numLayers (int): Number of layers to add
            numPartitions (int): Number of partitions to divide the absorbing layer
            partitionAlgo (str): The algorithm to partition the absorbing layer could be ["kd-tree", "metis"]
            geometry (str): The geometry of the absorbing layer could be ["Rectangular", "Cylindrical"]
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
            return self._addRectangularAbsorbingLayer(numLayers, numPartitions, partitionAlgo,  rayleighDamping, progress_callback, **kwargs)
        elif geometry == "Cylindrical":
            raise NotImplementedError("Cylindrical absorbing layer is not implemented yet")
        

    def _addRectangularAbsorbingLayer(self, numLayers: int, numPartitions: int, partitionAlgo: str, rayleighDamping:float = 0.95 ,progress_callback=None, **kwargs):
        """
        Add a rectangular absorbing layer to the model
        This function is used to add an absorbing layer to the assembled mesh that has a rectangular shape 
        and has structured mesh. 

        Args:
            numLayers (int): Number of layers to add
            numPartitions (int): Number of partitions to divide the absorbing layer
            partitionAlgo (str): The algorithm to partition the absorbing layer could be ["kd-tree", "metis"]
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
            raise ValueError("Type of the absorbing layer should be provided")
        else:
            if kwargs['type'] not in ["PML", "Rayleigh", "ASDA"]:
                raise ValueError("Type of the absorbing layer should be one of ['PML', 'Rayleigh', 'ASDA']")
            if kwargs['type'] == "PML":
                ndof = 9
                mergeFlag = False
                raise NotImplementedError("PML absorbing layer is not implemented yet")
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
        clipped.cell_data['Region'] = zeros(clipped.n_cells, dtype=int)
        clipped.cell_data['Region'][left]                   = 1
        clipped.cell_data['Region'][right]                  = 2
        clipped.cell_data['Region'][front]                  = 3
        clipped.cell_data['Region'][back]                   = 4
        clipped.cell_data['Region'][bottom]                 = 5
        clipped.cell_data['Region'][left & front]           = 6
        clipped.cell_data['Region'][left & back ]           = 7
        clipped.cell_data['Region'][right & front]          = 8
        clipped.cell_data['Region'][right & back]           = 9
        clipped.cell_data['Region'][left & bottom]          = 10
        clipped.cell_data['Region'][right & bottom]         = 11
        clipped.cell_data['Region'][front & bottom]         = 12
        clipped.cell_data['Region'][back & bottom]          = 13
        clipped.cell_data['Region'][left & front & bottom]  = 14
        clipped.cell_data['Region'][left & back & bottom]   = 15
        clipped.cell_data['Region'][right & front & bottom] = 16
        clipped.cell_data['Region'][right & back & bottom]  = 17


        cellCenters.cell_data['Region'] = clipped.cell_data['Region']
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
        # cellCentersCopy = cellCenters.copy()

        total_cells = clipped.n_cells
        TQDM_progress = tqdm.tqdm(range(total_cells ))
        TQDM_progress.reset()
        material_tags = []
        absorbing_regions = []
        element_tags = []
        
        for i in range(total_cells ):
            cell = clipped.get_cell(i)
            xmin, xmax, ymin, ymax, zmin, zmax = cell.bounds
            dx = abs((xmax - xmin))
            dy = abs((ymax - ymin))
            dz = abs((zmax - zmin))

            region = clipped.cell_data['Region'][i]
            MaterialTag = clipped.cell_data['MaterialTag'][i]
            ElementTag = clipped.cell_data['ElementTag'][i]
            normal = array(normals[region-1])
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
            absorbing_regions.append(region)
            element_tags.append(ElementTag)

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

        offset = 0
        for i, block in enumerate(Absorbing):
            n_cells = block.n_cells
            MaterialTag[offset:offset+n_cells] = repeat(material_tags[i], n_cells).astype(uint16)
            AbsorbingRegion[offset:offset+n_cells] = repeat(absorbing_regions[i], n_cells).astype(uint16)
            ElementTag[offset:offset+n_cells] = repeat(element_tags[i], n_cells).astype(uint16)
            offset += n_cells
            if progress_callback:
                progress_callback(( i + 1) / Absorbing.n_blocks  * 20 + 80)

        Absorbing = Absorbing.combine(merge_points=True)
        Absorbing.cell_data['MaterialTag'] = MaterialTag
        Absorbing.cell_data['AbsorbingRegion'] = AbsorbingRegion
        Absorbing.cell_data['ElementTag'] = ElementTag
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

        Absorbing.clear_data()
        Absorbing.cell_data['MaterialTag'] = MatTag
        Absorbing.cell_data['ElementTag'] = EleTag
        Absorbing.cell_data['AbsorbingRegion'] = RegTag
        Absorbing.point_data['ndf'] = full(Absorbing.n_points, ndof, dtype=uint16)

        Absorbing.cell_data["Core"] = full(Absorbing.n_cells, 0, dtype=int)

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

        damping = self.damping.create_damping("frequency rayleigh", dampingFactor=rayleighDamping)
        region  = self.region.create_region("elementRegion", damping=damping)
        Absorbing.cell_data["Region"] = full(Absorbing.n_cells, region.tag, dtype=uint16)
        
        mesh.cell_data["AbsorbingRegion"] = zeros(mesh.n_cells, dtype=uint16)
        # self.assembler.AbsorbingMesh = mesh.merge(Absorbing, 
        #                                           merge_points=mergeFlag, 
        #                                           tolerance=1e-6, 
        #                                           inplace=False, 
        #                                           progress_bar=True)
        # self.assembler.AbsorbingMesh.set_active_scalars("AbsorbingRegion")
        self.assembler.AssembeledMesh = mesh.merge(Absorbing, 
                                                  merge_points=mergeFlag, 
                                                  tolerance=1e-6, 
                                                  inplace=False, 
                                                  progress_bar=True)
        self.assembler.AssembeledMesh.set_active_scalars("AbsorbingRegion")