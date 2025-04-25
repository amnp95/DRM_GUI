Example 1: 3D Layered Soil Profile for Seismic Analysis
=======================================================

Overview
--------

This example demonstrates how to create a 3D soil profile model with multiple layers for seismic analysis. It illustrates the workflow for creating a realistic multi-layered soil column subjected to earthquake excitation, simulating wave propagation through different soil materials.

The model created in this example consists of:

* Five distinct soil layers with different properties
* 3D brick elements with gravitational body forces
* Earthquake excitation using the Kobe earthquake record
* Appropriate boundary conditions for site response analysis

.. figure:: ../images/Femora_logo.png
   :width: 600px
   :align: center
   :alt: 3D Layered Soil Model Visualization

   Conceptual visualization of the 3D layered soil model

Model Description
-----------------

**Soil Profile:**

* 20m × 20m soil column (-10m to 10m in both X and Y directions)
* Total depth of 18m
* Five distinct soil layers:
  * Three layers of "Dense Ottawa" sand (bottom, total 10m thick)
  * One layer of "Loose Ottawa" sand (middle, 6m thick)
  * One layer of "Dense Montrey" sand (top, 2m thick)

**Materials:**

* Dense Ottawa Sand: ElasticIsotropic material with E=2.0e7 Pa, nu=0.3, rho=2.02 ton/m³
* Loose Ottawa Sand: ElasticIsotropic material with E=2.0e7 Pa, nu=0.3, rho=1.94 ton/m³
* Dense Montrey Sand: ElasticIsotropic material with E=2.0e7 Pa, nu=0.3, rho=2.018 ton/m³

**Mesh:**

* Element sizes: 1.0m × 1.0m horizontally
* Variable vertical discretization:
  * Deeper layers: 1.0-1.3m element height
  * Upper layers: 0.5m element height

**Loading:**

* Kobe earthquake record applied as uniform excitation in X-direction

Code Access
-----------

The full source code for this example is available in the FEMORA repository:

* Example directory: ``examples/Example1/``
* Python script: ``examples/Example1/meshmakermodel.py``
* Data files: ``kobe.acc`` and ``kobe.time``

Detailed Tutorial
-----------------

For a step-by-step walkthrough of this example, see the :doc:`Quick Start Guide <quick_start>`.

The Quick Start Guide provides:

* Detailed explanation of each step in the model creation process
* In-depth discussion of concepts like assembly, boundary conditions, and analysis setup
* Complete code listing with explanatory comments

Results and Visualization
-------------------------

After running the example, you can:

1. Visualize the mesh in the FEMORA GUI
2. Open the generated result files in ParaView to analyze:
   * Displacements, velocities, and accelerations
   * Stresses and strains in each soil layer
   * Wave propagation patterns through the soil column

Key Concepts Demonstrated
-------------------------

* Creating a 3D multi-layered soil model
* Applying material properties to different soil types
* Setting up proper boundary conditions for seismic analysis
* Recording and analyzing dynamic response quantities
* Exporting to OpenSees TCL format for further analysis