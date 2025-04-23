"""
femora: Fast Efficient Meshing for OpenSees based Resilient Analysis
===================================================================

This package provides tools for creating and managing meshes for OpenSees simulations.

When imported as `import femora as fm`, the module itself acts as a MeshMaker instance,
allowing for direct access to all MeshMaker methods and properties.

Example usage:
-------------
```python
import femora as fm

# Create materials
material = fm.material.create_material(...)

# Create elements
element = fm.element.create_element(...)

# Create mesh parts
fm.meshPart.create_mesh_part(...)

# Assemble the mesh
fm.assembler.Assemble()
```
"""

from .components.MeshMaker import MeshMaker

# Create a MeshMaker instance to be used when importing the module
_instance = MeshMaker()

# Export all attributes from the MeshMaker instance to the module level
for attr_name in dir(_instance):
    if not attr_name.startswith('_'):  # Skip private attributes
        globals()[attr_name] = getattr(_instance, attr_name)

# Make the instance's properties directly accessible from the module level
material = _instance.material
element = _instance.element
meshPart = _instance.meshPart
assembler = _instance.assembler
constraint = _instance.constraint
damping = _instance.damping
region = _instance.region
analysis = _instance.analysis
timeSeries = _instance.timeSeries
pattern = _instance.pattern
recorder = _instance.recorder
process = _instance.process
drm = _instance.drm

# Also expose the underlying MeshMaker class and instance
MeshMaker = MeshMaker
get_instance = MeshMaker.get_instance