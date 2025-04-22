Usage Example
=============

Basic example of setting up a constraint handler:

.. code-block:: python

    # Create analysis object
    analysis = OpenSeesAnalysis()

    # Option 1: Auto handler (recommended for beginners)
    constraints = ConstraintHandler("Auto")

    # Option 2: Specific handler with parameters
    # constraints = ConstraintHandler("Transformation", alphaS=1.0, alphaM=1.0)

    # Set the constraint handler
    analysis.setConstraintHandler(constraints) 