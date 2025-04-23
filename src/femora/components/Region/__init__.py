from .regionBase import initialize_region_base

# Ensure RegionBase is initialized before running any tests
# RegionBase class should have a global region with tag 0
initialize_region_base()