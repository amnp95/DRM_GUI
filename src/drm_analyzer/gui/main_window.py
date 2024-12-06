from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout , QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pyvistaqt
import pyvista as pv

from drm_analyzer.styles.themes import Themes
from drm_analyzer.gui.left_panel import LeftPanel
from drm_analyzer.gui.console import InteractiveConsole
from drm_analyzer.components.drm_creators.drm_manager import DRMManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.font_size = 10
        self.current_theme = Themes.DARK
        self.drm_manager = DRMManager(self)
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
        self.create_menu_and_toolbar()
        self.apply_theme()
        
        self.showMaximized()

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

    def setup_console(self):
        self.console = InteractiveConsole()
        self.console.setMinimumHeight(200)
        self.right_panel.addWidget(self.console)
        
        # Make plotter available in console namespace
        self.console.kernel_manager.kernel.shell.push({
            'plotter': self.plotter,
            'pv': pv
        })

    def setup_splitters(self):
        self.main_splitter.setSizes([300, 1100])  # Left panel : Right panel ratio
        self.right_panel.setSizes([600, 200])     # Plotter : Console ratio

    def create_menu_and_toolbar(self):
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        increase_size_action = QAction("Increase Size", self)
        increase_size_action.setShortcut("Ctrl+=")
        increase_size_action.triggered.connect(self.increase_font_size)
        view_menu.addAction(increase_size_action)

        decrease_size_action = QAction("Decrease Size", self)
        decrease_size_action.setShortcut("Ctrl+-")
        decrease_size_action.triggered.connect(self.decrease_font_size)
        view_menu.addAction(decrease_size_action)
            
        # Theme menu
        theme_menu = menubar.addMenu("Theme")
        
        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.switch_theme(Themes.DARK))
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.switch_theme(Themes.LIGHT))
        theme_menu.addAction(light_theme_action)

        # Add DRM menu
        drm_menu = menubar.addMenu("DRM Load")

        # Add SV Wave action
        sv_wave_action = QAction("Create SV Wave", self)
        sv_wave_action.triggered.connect(self.drm_manager.create_sv_wave)
        drm_menu.addAction(sv_wave_action)
        
        # Add Surface Wave action
        surface_wave_action = QAction("Create Surface Wave", self)
        surface_wave_action.triggered.connect(self.drm_manager.create_surface_wave)
        drm_menu.addAction(surface_wave_action)



    def switch_theme(self, theme):
        self.current_theme = theme
        self.apply_theme()

    def update_font_and_resize(self):
        font = QFont('Segoe UI', self.font_size)
        QApplication.setFont(font)
        self.apply_theme()
        self.update()

    def apply_theme(self):
        style = Themes.get_dynamic_style(self.current_theme, self.font_size)
        self.setStyleSheet(style)
        
        if self.current_theme == Themes.DARK:
            self.console.set_default_style(colors='linux')
            self.console.syntax_style = 'monokai'
            self.plotter.set_background('#52576eff')
        else:
            self.console.set_default_style(colors='lightbg')
            self.console.syntax_style = 'default'
            self.plotter.set_background('white')
        
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