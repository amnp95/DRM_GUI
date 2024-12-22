from qtpy.QtGui import QAction, QPalette, QColor, QFont
from qtpy.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QStyleFactory)
from qtpy.QtCore import Qt

import pyvistaqt
import pyvista as pv
from meshmaker.components.MeshMaker import MeshMaker
from meshmaker.gui.left_panel import LeftPanel
from meshmaker.gui.console import InteractiveConsole
from meshmaker.components.drm_creators.drm_manager import DRMManager
from meshmaker.gui.plotter import PlotterManager
from meshmaker.gui.toolbar import ToolbarManager


class MainWindow(QMainWindow):
    _instance = None  # Class variable to store the single instance

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to implement singleton pattern.
        Ensures only one instance of the class is created.
        """
        if not cls._instance:
            cls._instance = super(MainWindow, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        Class method to get the singleton instance of MainWindow.
        
        Returns:
            MainWindow: The single instance of the MainWindow class.
        
        Raises:
            RuntimeError: If the instance has not been created yet.
        """
        if cls._instance is None:
            raise RuntimeError("MainWindow instance has not been created yet. "
                             "Create an instance first before calling get_instance().")
        return cls._instance

    def __init__(self):
        """
        Initialize the MainWindow.
        """
        # Ensure parent class constructor is called first
        super().__init__()

        # Check if already initialized to prevent re-initialization
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Ensure Qt event loop is running (if necessary)
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        self.font_size = 10
        self.current_theme = "Dark"
        self.drm_manager = DRMManager(self)
        self.create_palettes()
        self.meshMaker = MeshMaker.get_instance()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("DRM Analyzer")
        self.resize(1400, 800)
        
        self.setup_main_layout()
        self.setup_panels()
        self.setup_plotter()
        self.setup_console()
        self.setup_splitters()
        self.toolbar_manager = ToolbarManager(self)
        self.apply_theme()
        
        self.showMaximized()

    @classmethod
    def get_plotter(cls):
        """
        Class method to get the plotter from the singleton instance.
        
        Returns:
            pyvistaqt.BackgroundPlotter: The plotter instance.
        
        Raises:
            RuntimeError: If the MainWindow instance or plotter has not been created yet.
        """
        instance = cls.get_instance()
        if not hasattr(instance, 'plotter'):
            raise RuntimeError("Plotter has not been initialized yet.")
        return instance.plotter


    def setup_main_layout(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

    def setup_panels(self):
        self.left_panel = LeftPanel()
        self.right_panel = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.right_panel)

    def setup_plotter(self):
        self.plotter = pyvistaqt.BackgroundPlotter(show=False)
        self.plotter_widget = self.plotter.app_window
        self.plotter_widget.setMinimumHeight(400)
        self.right_panel.addWidget(self.plotter_widget)

        # Set the global plotter
        PlotterManager.set_plotter(self.plotter)

    def setup_console(self):
        self.console = InteractiveConsole()
        self.console.setMinimumHeight(200)
        self.right_panel.addWidget(self.console)
        
        # Make plotter available in console namespace
        self.console.kernel_manager.kernel.shell.push({
            'plotter': self.plotter,
            'pv': pv,
            'meshMaker': self.meshMaker,
        })

    def setup_splitters(self):
        self.main_splitter.setSizes([300, 1100])  # Left panel : Right panel ratio
        self.right_panel.setSizes([600, 200])     # Plotter : Console ratio


    def update_font_and_resize(self):
        font = QFont('Segoe UI', self.font_size)
        QApplication.setFont(font)
        self.apply_theme()
        self.update()


    def create_palettes(self):
        """Create light and dark palettes for Fusion style"""
        # Dark Palette
        self.dark_palette = QPalette()
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        self.dark_palette.setColor(QPalette.Text, Qt.white)
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(QPalette.BrightText, Qt.red)
        self.dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        # Light Palette (system default)
        self.light_palette = QApplication.style().standardPalette()
        

    def switch_theme(self, theme):
        """Switch between dark and light themes"""
        if theme == "Dark":
            QApplication.setPalette(self.dark_palette)
            self.console.set_default_style(colors='linux')
            self.console.syntax_style = 'monokai'
            self.plotter.set_background('#52576eff')
            self.current_theme = "Dark"
        else:
            QApplication.setPalette(self.light_palette)
            self.console.set_default_style(colors='lightbg')
            self.console.syntax_style = 'default'
            self.plotter.set_background('white')
            self.current_theme = "Light"
        
        # Ensure Fusion style is applied
        QApplication.setStyle(QStyleFactory.create('Fusion'))



    def apply_theme(self):
        """Apply the current theme"""
        # Use Fusion style
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # Apply the current theme's palette
        if self.current_theme == "Dark":
            QApplication.setPalette(self.dark_palette)
            self.console.set_default_style(colors='linux')
            self.console.syntax_style = 'monokai'
            self.plotter.set_background('#52576eff')
        else:
            QApplication.setPalette(self.light_palette)
            self.console.set_default_style(colors='lightbg')
            self.console.syntax_style = 'default'
            self.plotter.set_background('white')
        
        # Update font
        console_font = QFont('Monospace', self.font_size)
        self.console.font = console_font
    
    def increase_font_size(self):
        self.font_size += 1
        self.console.change_font_size(1)
        self.update_font_and_resize()
    
    def decrease_font_size(self):
        if self.font_size > 6:
            self.font_size -= 1
            self.console.change_font_size(-1)
            self.update_font_and_resize()