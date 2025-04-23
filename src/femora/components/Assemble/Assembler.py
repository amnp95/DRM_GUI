from typing import List, Optional, Dict, Any
import numpy as np
import pyvista as pv
import warnings

from femora.components.Mesh.meshPartBase import MeshPart
from femora.components.Element.elementBase import Element
from femora.components.Material.materialBase import Material
  

class Assembler:
    """
    Singleton Assembler class to manage multiple AssemblySection instances.
    
    This class ensures only one Assembler instance exists in the program 
    and keeps track of all created assembly sections with dynamic tag management.
    It provides methods for creating, managing, and assembling mesh sections
    into a complete structural model.
    
    The Assembler is responsible for:
    - Creating and tracking AssemblySection instances
    - Maintaining unique tags for each section
    - Combining multiple sections into a unified mesh
    - Managing the lifecycle of assembly sections
    """
    _instance = None
    _assembly_sections: Dict[int, 'AssemblySection'] = {}
    AssembeledMesh = None
    AssembeledActor = None
    # AbsorbingMesh = None
    # AbsorbingMeshActor = None
    
    def __new__(cls):
        """
        Implement singleton pattern for the Assembler class.
        
        Ensures only one Assembler instance is created throughout the program's lifecycle.
        If an instance already exists, returns that instance instead of creating a new one.
        
        Returns:
            Assembler: The singleton Assembler instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Class method to get the single Assembler instance.
        
        This method provides an alternative way to access the singleton instance,
        creating it if it doesn't already exist.
        
        Returns:
            Assembler: The singleton Assembler instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_section(
        self, 
        meshparts: List[str], 
        num_partitions: int = 1, 
        partition_algorithm: str = "kd-tree", 
        merging_points: bool = True,
        **kwargs: Any
    ) -> 'AssemblySection':
        """
        Create an AssemblySection directly through the Assembler.
        
        This method creates a new AssemblySection from the specified mesh parts and
        automatically registers it with the Assembler. It handles initialization of
        the section, assigns a unique tag, and returns the created section.
        
        Args:
            meshparts (List[str]): List of mesh part names to be assembled. These must be
                                  names of previously created MeshPart instances.
            num_partitions (int, optional): Number of partitions for parallel processing.
                                          For kd-tree, will be rounded to next power of 2.
                                          Defaults to 1 (no partitioning).
            partition_algorithm (str, optional): Algorithm used for partitioning the mesh.
                                               Currently supports "kd-tree".
                                               Defaults to "kd-tree".
            merging_points (bool, optional): Whether to merge points that are within a 
                                           tolerance distance when assembling mesh parts.
                                           Defaults to True.
            **kwargs: Additional keyword arguments to pass to AssemblySection constructor
        
        Returns:
            AssemblySection: The newly created and registered assembly section
            
        Raises:
            ValueError: If any of the specified mesh parts don't exist or if the
                      partition algorithm is invalid
        """
        
        # Create the AssemblySection 
        assembly_section = AssemblySection(
            meshparts=meshparts,
            num_partitions=num_partitions,
            partition_algorithm=partition_algorithm,
            merging_points=merging_points,
            **kwargs
        )
        
        return assembly_section

    def delete_section(self, tag: int) -> None:
        """
        Delete an AssemblySection by its tag.
        
        Removes the specified assembly section from the internal registry and
        updates the tags of remaining sections to maintain sequential numbering.
        
        Args:
            tag (int): Tag of the assembly section to delete
        
        Raises:
            KeyError: If no assembly section with the given tag exists
        """
        # Retrieve the section to ensure it exists
        section = self.get_assembly_section(tag)
        
        # Remove the section from the internal dictionary
        del self._assembly_sections[tag]
        
        # Retag remaining sections
        self._retag_sections()

    def _add_assembly_section(self, assembly_section: 'AssemblySection') -> int:
        """
        Internally add an AssemblySection to the Assembler's tracked sections.
        
        This method is called by the AssemblySection constructor to register 
        itself with the Assembler. It assigns a unique tag to the section and 
        adds it to the internal registry.
        
        Args:
            assembly_section (AssemblySection): The AssemblySection to add
        
        Returns:
            int: Unique tag assigned to the added assembly section
        """
        # Find the first available tag starting from 1
        tag = 1
        while tag in self._assembly_sections:
            tag += 1
        
        # Store the assembly section with its tag
        self._assembly_sections[tag] = assembly_section
        
        return tag

    def _remove_assembly_section(self, tag: int) -> None:
        """
        Remove an assembly section by its tag and retag remaining sections.
        
        Internal method to delete a section from the registry and update
        tags of remaining sections to maintain sequential numbering.
        
        Args:
            tag (int): Tag of the assembly section to remove
        
        Raises:
            KeyError: If no assembly section with the given tag exists
        """
        if tag not in self._assembly_sections:
            raise KeyError(f"No assembly section with tag {tag} exists")
        
        # Remove the specified tag
        del self._assembly_sections[tag]
        
        # Retag all remaining sections to ensure continuous numbering
        self._retag_sections()

    def _retag_sections(self):
        """
        Retag all assembly sections to ensure continuous numbering from 1.
        
        This internal method is called after removing a section to ensure that
        the remaining sections have sequential tags starting from 1. It creates
        a new dictionary with updated tags and updates each section's internal tag.
        """
        # Sort sections by their current tags
        sorted_sections = sorted(self._assembly_sections.items(), key=lambda x: x[0])
        
        # Create a new dictionary with retagged sections
        new_assembly_sections = {}
        for new_tag, (_, section) in enumerate(sorted_sections, 1):
            new_assembly_sections[new_tag] = section
            section._tag = new_tag  # Update the section's tag
        
        # Replace the old dictionary with the new one
        self._assembly_sections = new_assembly_sections
    
    def get_assembly_section(self, tag: int) -> 'AssemblySection':
        """
        Retrieve an AssemblySection by its tag.
        
        Gets a specific assembly section from the internal registry using its unique tag.
        
        Args:
            tag (int): Tag of the assembly section to retrieve
        
        Returns:
            AssemblySection: The requested assembly section
        
        Raises:
            KeyError: If no assembly section with the given tag exists
        """
        return self._assembly_sections[tag]
    
    def list_assembly_sections(self) -> List[int]:
        """
        List all tags of assembly sections.
        
        Returns a list of all tags that can be used to retrieve assembly sections.
        The tags are sorted in ascending order.
        
        Returns:
            List[int]: Tags of all added assembly sections
        """
        return list(self._assembly_sections.keys())
    
    def clear_assembly_sections(self) -> None:
        """
        Clear all tracked assembly sections.
        
        Removes all assembly sections from the internal registry, effectively
        resetting the Assembler's state. This does not affect the assembled mesh
        if one has already been created.
        """
        self._assembly_sections.clear()

    def get_sections(self) -> Dict[int, 'AssemblySection']:
        """
        Get all assembly sections.
        
        Returns a copy of the internal dictionary containing all assembly sections.
        This ensures that modifications to the returned dictionary don't affect
        the Assembler's internal state.
        
        Returns:
            Dict[int, AssemblySection]: Dictionary of all assembly sections, keyed by their tags
        """
        return self._assembly_sections.copy()
    
    def get_section(self, tag: int) -> 'AssemblySection':
        """
        Get an assembly section by its tag.
        
        Alias for get_assembly_section for backward compatibility.
        
        Args:
            tag (int): Tag of the assembly section to retrieve
        
        Returns:
            AssemblySection: The requested assembly section
        
        Raises:
            KeyError: If no assembly section with the given tag exists
        """
        return self._assembly_sections[tag]
    
    def Assemble(self, merge_points: bool = True) -> None:
        """
        Assemble all registered AssemblySections into a single unified mesh.
        
        This method combines all assembly sections into a single PyVista
        UnstructuredGrid. It preserves important mesh data like element tags,
        material tags, and region information. It also handles partitioning by
        correctly updating the Core cell data to maintain distinct partition ids.
        
        Args:
            merge_points (bool, optional): Whether to merge points during assembly.
                                         If True, points within a small tolerance will
                                         be combined, creating a continuous mesh.
                                         If False, all points are preserved.
                                         Defaults to True.
                                         
        Raises:
            ValueError: If no assembly sections have been created
            Exception: If any error occurs during the assembly process
        """
        
        if self.AssembeledMesh is not None:
            del self.AssembeledMesh
            self.AssembeledMesh = None
        
        if not self._assembly_sections:
            raise ValueError("No assembly sections have been created")
        
        sorted_sections = sorted(self._assembly_sections.items(), key=lambda x: x[0])
        
        self.AssembeledMesh = sorted_sections[0][1].mesh.copy()
        num_partitions = sorted_sections[0][1].num_partitions

        try :
            for tag, section in sorted_sections[1:]:

                second_mesh = section.mesh.copy()
                second_mesh.cell_data["Core"] = second_mesh.cell_data["Core"] + num_partitions
                num_partitions = num_partitions + section.num_partitions
                self.AssembeledMesh = self.AssembeledMesh.merge(
                    second_mesh, 
                    merge_points=merge_points, 
                    tolerance=1e-5,
                    inplace=False,
                    progress_bar=True
                )
                del second_mesh
        except Exception as e:
            raise e
        
    def delete_assembled_mesh(self) -> None:
        """
        Delete the assembled mesh.
        
        Releases memory by deleting the assembled mesh, if it exists.
        This is useful when you want to clear resources or prepare for
        a new assembly operation without affecting the assembly sections.
        """
        if self.AssembeledMesh is not None:
            del self.AssembeledMesh
            self.AssembeledMesh = None
        
            

class AssemblySection:
    """
    A class representing a group of mesh parts combined into a single mesh.
    
    The AssemblySection class takes multiple mesh parts, combines them into a single
    mesh, and optionally partitions the mesh for parallel computing. Each assembly 
    section is automatically registered with the Assembler singleton and assigned
    a unique tag for identification.
    
    This class is responsible for:
    - Validating mesh parts before assembly
    - Merging mesh parts with appropriate metadata
    - Managing degrees of freedom consistency
    - Partitioning the mesh for parallel processing
    - Storing references to elements and materials
    
    Attributes:
        meshparts_list (List[MeshPart]): List of MeshPart objects in this section
        num_partitions (int): Number of partitions for parallel processing
        partition_algorithm (str): Algorithm used for partitioning the mesh
        merging_points (bool): Whether points are merged during assembly
        mesh (pyvista.UnstructuredGrid): The assembled mesh
        elements (List[Element]): Elements used in this assembly section
        materials (List[Material]): Materials used in this assembly section
        actor: PyVista actor for visualization
        _tag (int): Unique tag assigned by the Assembler
    """
    def __init__(
        self, 
        meshparts: List[str], 
        num_partitions: int = 1, 
        partition_algorithm: str = "kd-tree", 
        merging_points: bool = True
    ):
        """
        Initialize an AssemblySection by combining multiple mesh parts.
        
        This constructor takes a list of mesh part names, validates them, combines them
        into a single mesh, and optionally partitions the result. The assembled section
        is automatically registered with the Assembler singleton.
        
        If the partition algorithm is "kd-tree" and num_partitions is not a power of 2,
        it will be automatically rounded up to the next power of 2.

        Args:
            meshparts (List[str]): List of mesh part names to be assembled. These must be
                                  names of previously created MeshPart instances.
            num_partitions (int, optional): Number of partitions for parallel processing.
                                          For kd-tree, will be rounded to next power of 2.
                                          Defaults to 1 (no partitioning).
            partition_algorithm (str, optional): Algorithm used for partitioning the mesh.
                                               Currently supports "kd-tree".
                                               Defaults to "kd-tree".
            merging_points (bool, optional): Whether to merge points that are within a
                                           tolerance distance when assembling mesh parts.
                                           Defaults to True.
        
        Raises:
            ValueError: If no valid mesh parts are provided, if the partition algorithm
                      is invalid, or if mesh assembly fails
        """
        # Validate and collect mesh parts
        self.meshparts_list = self._validate_mesh_parts(meshparts)
        
        # Configuration parameters
        self.num_partitions = num_partitions
        self.partition_algorithm = partition_algorithm
        # check if the partition algorithm is valid
        if self.partition_algorithm not in ["kd-tree"]:
            raise ValueError(f"Invalid partition algorithm: {self.partition_algorithm}")

        if self.partition_algorithm == "kd-tree" :
            # If a non-power of two value is specified for 
            # n_partitions, then the load balancing simply 
            # uses the power-of-two greater than the requested value
            if self.num_partitions & (self.num_partitions - 1) != 0:
                self.num_partitions = 2**self.num_partitions.bit_length()

        # Initialize tag to None
        self._tag = None
        self.merging_points = merging_points
        
        # Assembled mesh attributes
        self.mesh: Optional[pv.UnstructuredGrid] = None
        self.elements : List[Element] = []
        self.materials : List[Material] = []

        # Assemble the mesh first
        try:
            self._assemble_mesh()
            
            # Only add to Assembler if mesh assembly is successful
            self._tag = Assembler.get_instance()._add_assembly_section(self)
        except Exception as e:
            # If mesh assembly fails, raise the original exception
            raise

        self.actor = None

    @property
    def tag(self) -> int:
        """
        Get the unique tag for this AssemblySection.
        
        The tag is a unique identifier assigned by the Assembler when the 
        AssemblySection is successfully created and registered. It can be
        used to retrieve the section from the Assembler later.
        
        Returns:
            int: Unique tag assigned by the Assembler
        
        Raises:
            ValueError: If the section hasn't been successfully added to the Assembler
        """
        if self._tag is None:
            raise ValueError("AssemblySection has not been successfully created")
        return self._tag
    
    def _validate_mesh_parts(self, meshpart_names: List[str]) -> List[MeshPart]:
        """
        Validate and retrieve mesh parts.
        
        This internal method checks that all specified mesh part names exist 
        in the MeshPart registry and retrieves the corresponding MeshPart objects.
        It also verifies that at least one valid mesh part is provided.

        Args:
            meshpart_names (List[str]): List of mesh part names to validate

        Returns:
            List[MeshPart]: List of validated MeshPart objects

        Raises:
            ValueError: If any specified mesh part doesn't exist or if no valid mesh parts are found
        """
        validated_meshparts = []
        for name in meshpart_names:
            meshpart = MeshPart._mesh_parts.get(name)
            if meshpart is None:
                raise ValueError(f"Mesh with name '{name}' does not exist")
            validated_meshparts.append(meshpart)
        
        if not validated_meshparts:
            raise ValueError("No valid mesh parts were provided")
        
        return validated_meshparts
    
    def _validate_degrees_of_freedom(self) -> bool:
        """
        Check if all mesh parts have the same number of degrees of freedom.
        
        This internal method verifies that all mesh parts in the section have
        consistent degrees of freedom, which is important for proper mesh assembly
        when merging points. If merging_points is False, this check is skipped.
        
        If inconsistent degrees of freedom are detected, a warning is issued but
        the method returns False rather than raising an exception.

        Returns:
            bool: True if all mesh parts have the same number of degrees of freedom,
                 or if merging_points is False. False if inconsistencies are detected.
        """
        if not self.merging_points:
            return True
        
        ndof_list = [meshpart.element._ndof for meshpart in self.meshparts_list]
        unique_ndof = set(ndof_list)
        
        if len(unique_ndof) > 1:
            warnings.warn("Mesh parts have different numbers of degrees of freedom", UserWarning)
            return False
        
        return True
    
    def _assemble_mesh(self):
        """
        Assemble mesh parts into a single mesh.
        
        This internal method performs the actual assembly of mesh parts into a single
        PyVista UnstructuredGrid. It:
        1. Validates degrees of freedom consistency
        2. Starts with the first mesh part as the base
        3. Adds metadata to the mesh (ElementTag, MaterialTag, Region, etc.)
        4. Merges subsequent mesh parts one by one
        5. Optionally partitions the resulting mesh for parallel processing
        
        The assembled mesh is stored in the 'mesh' attribute, with cell data arrays
        for ElementTag, MaterialTag, Region, and Core (partition ID).

        Raises:
            ValueError: If mesh parts have different degrees of freedom and this causes
                      assembly to fail, or if any other error occurs during assembly
        """
        # Validate degrees of freedom
        self._validate_degrees_of_freedom()
            
        # Start with the first mesh
        first_meshpart = self.meshparts_list[0]
        self.mesh = first_meshpart.mesh.copy()
        
        # Collect elements and materials
        ndf = first_meshpart.element._ndof
        matTag = first_meshpart.element._material.tag
        EleTag = first_meshpart.element.tag
        regionTag = first_meshpart.region.tag
        
        # Add initial metadata to the first mesh
        n_cells = self.mesh.n_cells
        n_points = self.mesh.n_points
        
        # add cell and point data
        self.mesh.cell_data["ElementTag"]  = np.full(n_cells, EleTag, dtype=np.uint16)
        self.mesh.cell_data["MaterialTag"] = np.full(n_cells, matTag, dtype=np.uint16)
        self.mesh.point_data["ndf"]        = np.full(n_points, ndf, dtype=np.uint16)
        self.mesh.cell_data["Region"]      = np.full(n_cells, regionTag, dtype=np.uint16)
        
        # Merge subsequent meshes
        for meshpart in self.meshparts_list[1:]:
            second_mesh = meshpart.mesh.copy()
            ndf = meshpart.element._ndof
            matTag = meshpart.element._material.tag
            EleTag = meshpart.element.tag
            regionTag = meshpart.region.tag
            
            n_cells_second  = second_mesh.n_cells
            n_points_second = second_mesh.n_points
            
            # add cell and point data to the second mesh
            second_mesh.cell_data["ElementTag"]  = np.full(n_cells_second, EleTag, dtype=np.uint16)
            second_mesh.cell_data["MaterialTag"] = np.full(n_cells_second, matTag, dtype=np.uint16)
            second_mesh.point_data["ndf"]        = np.full(n_points_second, ndf, dtype=np.uint16)
            second_mesh.cell_data["Region"]      = np.full(n_cells_second, regionTag, dtype=np.uint16)
            # Merge with tolerance and optional point merging
            self.mesh = self.mesh.merge(
                second_mesh, 
                merge_points=self.merging_points, 
                tolerance=1e-5,
                inplace=False,
                progress_bar=True
            )

            del second_mesh

        # partition the mesh
        self.mesh.cell_data["Core"] = np.zeros(self.mesh.n_cells, dtype=int)
        if self.num_partitions > 1:
            partitiones = self.mesh.partition(self.num_partitions,
                                              generate_global_id=True, 
                                              as_composite=True)
            for i, partition in enumerate(partitiones):
                ids = partition.cell_data["vtkGlobalCellIds"]
                self.mesh.cell_data["Core"][ids] = i
            
            del partitiones

    @property
    def meshparts(self) -> List[str]:
        """
        Get the names of mesh parts in this AssemblySection.
        
        This property returns a list of the user-friendly names of all mesh parts
        included in this assembly section. These are the names that were originally
        provided when creating the mesh parts.
        
        Returns:
            List[str]: Names of mesh parts included in this assembly section
        """
        return [meshpart.user_name for meshpart in self.meshparts_list]
    
    def assign_actor(self, actor) -> None:
        """
        Assign a PyVista actor to the assembly section.
        
        This method associates a visualization actor with the assembly section,
        which can be used for rendering the mesh in a visualization pipeline.
        
        Args:
            actor: PyVista actor to assign to this assembly section for visualization
        """
        self.actor = actor












