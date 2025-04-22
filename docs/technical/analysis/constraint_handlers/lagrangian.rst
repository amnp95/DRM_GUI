Lagrangian constraint handler
=============================

The Lagrangian constraint handler enforces constraints exactly by adding Lagrange multipliers as additional unknowns to the system.

Parameters
----------

``update_strategy`` : str, default="Automatic"
    Strategy for updating Lagrange multipliers. Options are "Once" (update only once at the beginning), "Each" (update at each iteration), and "Automatic" (adapt based on convergence).

Usage Example
-------------

.. code-block:: python

    # Create a MeshMaker instance
    mk = MeshMaker()
    
    # Create a Lagrangian constraint handler with default parameters
    mk.analysis.constraint.create_handler("Lagrangian")
    
    # Create a Lagrangian constraint handler with custom parameters
    mk.analysis.constraint.create_handler("Lagrangian", update_strategy="Each") 