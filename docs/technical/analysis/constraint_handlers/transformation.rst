Transformation constraint handler
=================================

The Transformation constraint handler enforces constraints exactly by using a transformation matrix method. It effectively removes constrained degrees of freedom from the system of equations.

Parameters
----------

No parameters required.

Usage Example
-------------

.. code-block:: python

    # Create a MeshMaker instance
    mk = MeshMaker()
    
    # Create a Transformation constraint handler
    mk.analysis.constraint.create_handler("Transformation") 