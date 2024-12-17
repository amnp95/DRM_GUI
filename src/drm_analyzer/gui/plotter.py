class PlotterManager:
    """
    A centralized manager for accessing the global plotter.
    This breaks circular import dependencies by providing a clean way to access the plotter.
    """
    _plotter = None

    @classmethod
    def set_plotter(cls, plotter) -> None:
        """
        Set the global plotter instance.
        
        Args:
            plotter: The plotter instance to be set globally
        """
        cls._plotter = plotter

    @classmethod
    def get_plotter(cls):
        """
        Get the global plotter instance.
        
        Returns:
            The global plotter instance
        
        Raises:
            RuntimeError: If no plotter has been set
        """
        if cls._plotter is None:
            raise RuntimeError("Plotter has not been initialized. "
                             "Ensure MainWindow is created before accessing the plotter.")
        return cls._plotter

    @classmethod
    def remove_plotter(cls)->None:
        """
        remove the global plotter instance.
        Useful for testing or resetting the application state.
        """
        cls._plotter = None
    
    @classmethod
    def clear_plotter(cls)->None:
        """
        Clear the plotter.
        """
        cls._plotter.clear()