Process
---------------------------------

Understanding the Process Component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Process`` component is a core part of the MeshMaker library that manages the sequence of operations in a structural analysis. It implements a system for defining, organizing, and executing analysis steps in a coherent order.

The Process component provides functionality to:
- Add steps to the analysis process
- Insert steps at specific positions
- Remove steps
- Track the current step during execution
- Convert the entire process to OpenSees TCL commands

Each step in the process consists of a component object (such as a constraint, pattern, recorder, or analysis) and an optional description.

Accessing the Process Component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two ways to access the Process component in your code:

1. **Direct Access**: Import and use the ProcessManager class directly
   
   .. code-block:: python
      
      from meshmaker.components.Process.process import ProcessManager
      
      # Get the singleton instance
      process_manager = ProcessManager()
      
      # Use the process manager directly
      process_manager.add_step(...)

2. **Through MeshMaker** (Recommended): Access via the MeshMaker class's .process property
   
   .. code-block:: python
      
      from meshmaker.components.MeshMaker import MeshMaker
      
      # Create a MeshMaker instance
      mk = MeshMaker()
      
      # Access the ProcessManager through the .process property
      mk.process.add_step(...)

The second approach is recommended as it provides a unified interface to all of MeshMaker's components and ensures proper initialization of all dependencies.

How Process Works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Process component provides several key capabilities:

1. **Step Management**: Add, insert, remove, and clear steps in the analysis process
2. **Step Tracking**: Keep track of the current step during execution
3. **Process Iteration**: Iterate through all steps in the process
4. **TCL Generation**: Convert the entire process to OpenSees TCL commands

When a step is added to the process:

1. A weak reference to the component is stored (to avoid circular references)
2. The step description is stored alongside the component reference
3. The step is added to the internal list of steps

Supported Component Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Process component supports the following types of components:

1. **SPConstraint**: Single-point constraints that fix specific degrees of freedom
2. **mpConstraint**: Multi-point constraints that relate degrees of freedom between nodes
3. **Pattern**: Load patterns that define how loads are applied to the structure
4. **Recorder**: Recorders that capture the response of the structure during analysis
5. **Analysis**: Analysis objects that define how the solution is performed

ProcessManager API Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: meshmaker.components.Process.process.ProcessManager

Process Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Managing the analysis process is the primary function of the ProcessManager. There are several operations available:

1. **Adding Steps**
   - Appends a new step to the end of the process
   - Requires a component object and an optional description

2. **Inserting Steps**
   - Inserts a step at a specific position in the process
   - Useful for modifying an existing process

3. **Removing Steps**
   - Removes a step at a specific position
   - Automatically adjusts the current step tracking if needed

4. **Clearing Steps**
   - Removes all steps from the process
   - Resets the current step tracking

5. **Getting Steps**
   - Retrieves all steps or a specific step
   - Useful for inspecting the current process state

Example of creating and managing a process:

.. code-block:: python

   from meshmaker.components.MeshMaker import MeshMaker
   
   # Create a MeshMaker instance
   mk = MeshMaker()
   
   # Create components for the process
   sp_constraint = mk.constraint.sp.create_constraint(...)
   pattern = mk.pattern.create_pattern(...)
   analysis = mk.analysis.create_analysis(...)
   recorder = mk.recorder.create_node_recorder(...)
   
   # Add steps to the process
   mk.process.add_step(sp_constraint, "Apply boundary conditions")
   mk.process.add_step(pattern, "Apply gravity loads")
   mk.process.add_step(recorder, "Set up recorder")
   mk.process.add_step(analysis, "Run analysis")
   
   # Insert a step at position 2
   mp_constraint = mk.constraint.mp.create_constraint(...)
   mk.process.insert_step(2, mp_constraint, "Apply multi-point constraints")
   
   # Remove a step
   mk.process.remove_step(1)
   
   # Get all steps
   steps = mk.process.get_steps()
   
   # Get a specific step
   step = mk.process.get_step(0)
   
   # Clear all steps
   mk.process.clear_steps()
   
   # Generate TCL script for the process
   tcl_script = mk.process.to_tcl()

Each step in the process is executed in sequence when the analysis is run, generating the appropriate OpenSees TCL commands based on the components in each step. 