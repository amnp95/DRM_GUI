import os
from numpy import unique, zeros, arange, array, abs, concatenate, meshgrid, ones, full, uint16, repeat, where, isin
from pyvista import Cube, MultiBlock, StructuredGrid
import tqdm
from pykdtree.kdtree import KDTree as pykdtree
from meshmaker.components.Pattern.patternBase import H5DRMPattern

class DRM:
    """
    Singleton class for Domain Reduction Method helper functions
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of DRMHelper if it doesn't exist
        
        Returns:
            DRMHelper: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(DRM, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, meshmaker=None):
        """
        Initialize the DRMHelper instance
        
        Args:
            meshmaker: Reference to the MeshMaker instance
        """
        # Only initialize once
        if self._initialized:
            return
            
        self._initialized = True
        self.meshmaker = meshmaker
        self.h5drmpattern = None
    
    def set_meshmaker(self, meshmaker):
        """
        Set the MeshMaker reference
        
        Args:
            meshmaker: Reference to the MeshMaker instance
        """
        self.meshmaker = meshmaker

    def set_pattern(self, pattern: H5DRMPattern):
        """
        Set the pattern for the DRM
        
        Args:
            pattern: The pattern to set
        """
        self.h5drmpattern = pattern

    def createDefaultProcess(self, dT, finalTime):
        '''
        Create the default process for doing Domain Reduction method analysis
        details:
            1 create fix the boundaries of the model using macros
            2 create the vtkhdf recorder
            3 create specfic recorders
            4 create the gravity analysis
            5 create dynamic analysis
        '''
        # check if the pattern is set
        if self.h5drmpattern is None:
            raise ValueError("The pattern is not set\n Please set the pattern first")
        else:
            if not isinstance(self.h5drmpattern, H5DRMPattern):
                raise ValueError("The pattern should be of type H5DRMPattern")
        


        # first clear all the previous process
        self.meshmaker.process.clear_steps()
        self.meshmaker.analysis.clear_all()
        self.meshmaker.recorder.clear_all()
        self.meshmaker.constraint.sp.clear_all()
        # self.meshmaker.analysis.numberer.clear_all()
        self.meshmaker.analysis.system.clear_all()
        self.meshmaker.analysis.algorithm.clear_all()
        self.meshmaker.analysis.test.clear_all()
        self.meshmaker.analysis.integrator.clear_all()


        # create the fixities
        dofsVals = [1,1,1,1,1,1,1,1,1]
        c1 = self.meshmaker.constraint.sp.fixMacroXmax(dofs=dofsVals)
        c2 = self.meshmaker.constraint.sp.fixMacroXmin(dofs=dofsVals)
        c3 = self.meshmaker.constraint.sp.fixMacroYmax(dofs=dofsVals)
        c4 = self.meshmaker.constraint.sp.fixMacroYmin(dofs=dofsVals)
        c5 = self.meshmaker.constraint.sp.fixMacroZmin(dofs=dofsVals)

        # create the vtkhdf recorder
        vtkRecordr = self.meshmaker.recorder.create_recorder(recorder_type="vtkhdf",
                                      file_base_name="result",
                                      resp_types=["disp", "vel", "accel", "stress3D6", "strain3D6"],
                                      delta_t=0.02)
        
        # create the specific recorders
        # ....  to be implemented

        # create the gravity analysis
        GravityElastic = self.meshmaker.analysis.create_analysis(name="Gravity-Elastic",
                                      analysis_type="Transient",
                                      constraint_handler=self.meshmaker.analysis.constraint.create_handler("plain"),
                                      numberer=self.meshmaker.analysis.numberer.get_numberer("RCM"),
                                      system=self.meshmaker.analysis.system.create_system(system_type="mumps",icntl14=200, icntl7=7),
                                      algorithm=self.meshmaker.analysis.algorithm.create_algorithm(algorithm_type="modifiednewton", factor_once=True),
                                      test=self.meshmaker.analysis.test.create_test("relativeenergyincr",tol=1e-4, max_iter=10, print_flag=2),
                                      integrator=self.meshmaker.analysis.integrator.create_integrator(integrator_type="newmark", gamma=0.5, beta=0.25, form="D"),
                                      dt=dT,
                                      num_steps=20,
                                      )
        GravityPlastic = self.meshmaker.analysis.create_analysis(name="Gravity-Plastic",
                                        analysis_type="Transient",
                                        constraint_handler=self.meshmaker.analysis.constraint.create_handler("plain"),
                                        numberer=self.meshmaker.analysis.numberer.get_numberer("RCM"),
                                        system=self.meshmaker.analysis.system.create_system(system_type="mumps",icntl14=200, icntl7=7),
                                        algorithm=self.meshmaker.analysis.algorithm.create_algorithm(algorithm_type="modifiednewton", factor_once=True),
                                        test=self.meshmaker.analysis.test.create_test("relativeenergyincr",tol=1e-4, max_iter=10, print_flag=2),
                                        integrator=self.meshmaker.analysis.integrator.create_integrator(integrator_type="newmark", gamma=0.5, beta=0.25, form="D"),
                                        dt=dT,
                                        num_steps=50,
                                        )
        
        DynamicAnalysis = self.meshmaker.analysis.create_analysis(
                                    name="DynamicAnalysis",
                                    analysis_type="Transient",
                                    constraint_handler=self.meshmaker.analysis.constraint.create_handler("plain"),
                                    numberer=self.meshmaker.analysis.numberer.get_numberer("RCM"),
                                    system=self.meshmaker.analysis.system.create_system(system_type="mumps",icntl14=200, icntl7=7),
                                    algorithm=self.meshmaker.analysis.algorithm.create_algorithm(algorithm_type="modifiednewton", factor_once=True),
                                    test=self.meshmaker.analysis.test.create_test("relativeenergyincr",tol=1e-4, max_iter=10, print_flag=2),
                                    integrator=self.meshmaker.analysis.integrator.create_integrator(integrator_type="newmark", gamma=0.5, beta=0.25, form="D"),
                                    dt=dT,
                                    final_time=finalTime,
                                    )
        

        # self.meshmaker.process.add_step(component=c1, description="Fixing Xmax")
        # self.meshmaker.process.add_step(component=c2, description="Fixing Xmin")   
        # self.meshmaker.process.add_step(component=c3, description="Fixing Ymax")
        # self.meshmaker.process.add_step(component=c4, description="Fixing Ymin")
        # self.meshmaker.process.add_step(component=c5, description="Fixing Zmin")
        self.meshmaker.process.add_step(component=GravityElastic, description="Analysis Gravity Elastic (Transient)")
        self.meshmaker.process.add_step(component=GravityPlastic, description="Analysis Gravity Plastic (Transient)")
        
        self.meshmaker.process.add_step(component=vtkRecordr, description="Recorder vtkhdf")

        self.meshmaker.process.add_step(component=self.h5drmpattern, description="Pattern H5DRM")

        self.meshmaker.process.add_step(component=DynamicAnalysis, description="Analysis Dynamic (Transient)")

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
        if self.meshmaker.assembler.AssembeledMesh is None:
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

        if self.meshmaker.assembler.AssembeledMesh is None:
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

        
        mesh = self.meshmaker.assembler.AssembeledMesh.copy()
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
                ele = self.meshmaker.element.get_element(tag)

                if ele.element_type not in ["stdBrick", "bbarBrick", "SSPbrick"]:
                    raise ValueError(f"boundary elements should be of type stdBrick or bbarBrick or SSPbrick not {ele.element_type}")
                
                mat = ele.get_material()

                # check that the material is elastic
                if mat.material_name != "ElasticIsotropic" or mat.material_type != "nDMaterial":
                    raise ValueError(f"boundary elements should have an ElasticIsotropic material not {mat.material_name} {mat.material_type}")

                PMLele = self.meshmaker.element.create_element("PML3D", ndof, mat, 
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
                damping = self.meshmaker.damping.create_damping("frequency rayleigh", dampingFactor=rayleighDamping)
                region  = self.meshmaker.region.create_region("elementRegion", damping=damping)
                Absorbing.cell_data["Region"]  = full(Absorbing.n_cells, region.tag, dtype=uint16)
        
        if kwargs['type'] == "PML":
            if not matchDamping:
                damping = self.meshmaker.damping.create_damping("frequency rayleigh", dampingFactor=rayleighDamping)
                region  = self.meshmaker.region.create_region("elementRegion", damping=damping)
                Absorbing.cell_data["Region"]  = full(Absorbing.n_cells, region.tag, dtype=uint16)

        if kwargs['type'] == "ASDA":
            raise NotImplementedError("ASDA absorbing layer is not implemented yet")
    
        mesh.cell_data["AbsorbingRegion"] = zeros(mesh.n_cells, dtype=uint16)


        # make the core for the interface elemnts the same as the original mesh
        if kwargs['type'] == "PML":
            absorbingCenters = Absorbing.cell_centers(vertex=True).points
            tree = pykdtree(absorbingCenters)
            distances, indices = tree.query(cellCentersCoords, k=1)
            




        self.meshmaker.assembler.AssembeledMesh = mesh.merge(Absorbing, 
                                                  merge_points=mergeFlag, 
                                                  tolerance=1e-6, 
                                                  inplace=False, 
                                                  progress_bar=True)
        self.meshmaker.assembler.AssembeledMesh.set_active_scalars("AbsorbingRegion")


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
            tree = pykdtree(self.meshmaker.assembler.AssembeledMesh.points)
            distances, indices = tree.query(interfacepoints, k=2)


            # check the distances 
            distances  = abs(distances)
            # check that maximum distance is less than 1e-6
            if distances.max() > 1e-6:
                raise ValueError("The PML layer mesh points are not matching with the original mesh points")
            
            # create the equal dof
            for i, index in enumerate(indices):
                # check that the index 1 is always has 9 dof and index 0 has 3 dof
                ndf1 = self.meshmaker.assembler.AssembeledMesh.point_data["ndf"][index[0]]
                ndf2 = self.meshmaker.assembler.AssembeledMesh.point_data["ndf"][index[1]]

                if ndf1 == 9 and ndf2 == 3:
                    masterNode = index[1] + 1
                    slaveNode  = index[0] + 1
                elif ndf1 == 3 and ndf2 == 9:
                    masterNode = index[0] + 1
                    slaveNode  = index[1] + 1   
                else:
                    raise ValueError("The PML layer node should have 9 dof and the original mesh should have at least 3 dof")
                
                self.meshmaker.constraint.mp.create_equal_dof(masterNode, [slaveNode],[1,2,3])
