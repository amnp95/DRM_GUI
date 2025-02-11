from typing import List, Optional, Dict, Any
import numpy as np
import pyvista as pv
import warnings

from meshmaker.components.Mesh.meshPartBase import MeshPart
from meshmaker.components.Element.elementBase import Element
from meshmaker.components.Material.materialBase import Material
  

class Assembler:
    """
    Singleton Assembler class to manage multiple AssemblySection instances.
    
    This class ensures only one Assembler instance exists in the program 
    and keeps track of all created assembly sections with dynamic tag management.
    """
    _instance = None
    _assembly_sections: Dict[int, 'AssemblySection'] = {}
    AssembeledMesh = None
    AssembeledActor = None
    # AbsorbingMesh = None
    # AbsorbingMeshActor = None
    
    def __new__(cls):
        """
        Implement singleton pattern. 
        Ensures only one Assembler instance is created.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance





    @classmethod
    def get_instance(cls):
        """
        Class method to get the single Assembler instance.
        
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
        
        Args:
            meshparts (List[str]): List of mesh part names to be assembled
            num_partitions (int, optional): Number of partitions. Defaults to 1.
            partition_algorithm (str, optional): Algorithm for partitioning. Defaults to "kd-tree".
            merging_points (bool, optional): Whether to merge points during assembly. Defaults to True.
            **kwargs: Additional keyword arguments to pass to AssemblySection constructor
        
        Returns:
            AssemblySection: The newly created and registered assembly section
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
        
        Args:
            assembly_section (AssemblySection): The AssemblySection to add
        
        Returns:
            int: Unique tag for the added assembly section
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
        
        Args:
            tag (int): Tag of the assembly section
        
        Returns:
            AssemblySection: The requested assembly section
        
        Raises:
            KeyError: If no assembly section with the given tag exists
        """
        return self._assembly_sections[tag]
    

    def list_assembly_sections(self) -> List[int]:
        """
        List all tags of assembly sections.
        
        Returns:
            List[int]: Tags of all added assembly sections
        """
        return list(self._assembly_sections.keys())
    

    def clear_assembly_sections(self) -> None:
        """
        Clear all tracked assembly sections.
        """
        self._assembly_sections.clear()


    def get_sections(self) -> Dict[int, 'AssemblySection']:
        """
        Get all assembly sections.
        
        Returns:
            Dict[int, AssemblySection]: Dictionary of all assembly sections, keyed by their tags
        """
        return self._assembly_sections.copy()
    

    def get_section(self, tag: int) -> 'AssemblySection':
        """
        Get an assembly section by its tag.
        
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
        Assemble all registered AssemblySections into a single mesh.
        
        Args:
            merge_points (bool, optional): Whether to merge points during assembly. Defaults to True.
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
        """
        if self.AssembeledMesh is not None:
            del self.AssembeledMesh
            self.AssembeledMesh = None
        
            

class AssemblySection:
    def __init__(
        self, 
        meshparts: List[str], 
        num_partitions: int = 1, 
        partition_algorithm: str = "kd-tree", 
        merging_points: bool = True
    ):
        """
        Initialize an AssemblySection by combining multiple mesh parts.

        Args:
            meshparts (List[str]): List of mesh part names to be assembled
            num_partitions (int, optional): Number of partitions. Defaults to 1.
            partition_algorithm (str, optional): Algorithm for partitioning. Defaults to "kd-tree".
            merging_points (bool, optional): Whether to merge points during assembly. Defaults to True.
        
        Raises:
            ValueError: If no valid mesh parts are provided
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

        Args:
            meshpart_names (List[str]): List of mesh part names to validate

        Returns:
            List[MeshPart]: List of validated mesh parts

        Raises:
            ValueError: If no valid mesh parts are found
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

        Returns:
            bool: True if all mesh parts have the same number of degrees of freedom
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

        Raises:
            ValueError: If mesh parts have different degrees of freedom
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
        
        Returns:S
            List[str]: Names of mesh parts
        """
        return [meshpart.user_name for meshpart in self.meshparts_list]
    

    def assign_actor(self, actor) -> None:
        """
        Assign a PyVista actor to the assembly section.
        
        Args:
            actor: PyVista actor to assign
        """
        self.actor = actor

        





        

        
            
                                         
