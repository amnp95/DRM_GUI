Key Considerations
==================

When selecting a constraint handler, consider these key factors:

* Constraint Types:
    - Single-point only → Plain or Transformation
    - Multi-point → Transformation, Penalty, or Lagrange
    - Mixed → Auto or Transformation

* Problem Size:
    - Small → Plain
    - Large → Transformation
    - Memory-constrained → Penalty

* Analysis Requirements:
    - High accuracy → Lagrange
    - Parallel computing → Penalty
    - Dynamic analysis → Transformation/Lagrange
    - Nonlinear → Transformation 