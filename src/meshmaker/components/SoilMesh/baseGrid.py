from PySide6.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QWidget, 
                           QGridLayout, QLineEdit, QGroupBox, QSlider, QComboBox,
                           QCheckBox, QHBoxLayout, QColorDialog, QFrame)
from PySide6.QtCore import Qt, Signal
from meshmaker.utils.validator import DoubleValidator, IntValidator
from PySide6.QtGui import QColor


class ColorButton(QFrame):
    """Custom color button that shows current color and opens color picker"""
    colorChanged = Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = QColor(100, 100, 100)  # Default gray color
        
        # Set frame style
        self.setFixedSize(30, 30)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        
        # Set cursor to pointing hand
        self.setCursor(Qt.PointingHandCursor)
        
        # Set the background color
        self.update_style()

    def update_style(self):
        self.setStyleSheet(
            f"""
            ColorButton {{
                background-color: {self.color.name()};
                border: 2px solid #666666;
                border-radius: 2px;
            }}
            ColorButton:hover {{
                border: 2px solid #999999;
            }}
            """
        )

    def mousePressEvent(self, event):
        color = QColorDialog.getColor(self.color)
        if color.isValid():
            self.color = color
            self.update_style()
            # Emit the color changed signal
            self.colorChanged.emit(color.getRgbF()[:3])


    def set_color(self, color):
        """Set color from either QColor or RGB tuple"""
        if isinstance(color, tuple):
            self.color = QColor.fromRgbF(*color)
        else:
            self.color = color
        self.update_style()

class BaseGridTab(QWidget):
    """Base class for all grid type tabs"""
    def __init__(self, parent=None, block_number=1):
        super().__init__(parent)
        self.block_number = block_number
        self.PlotFlag = False
        self.grid_actor = None
        self.grid_renderer = None
        self.current_color = None
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.form_layout = QGridLayout()
        
        # Common validators
        self.double_validator = DoubleValidator()
        self.double_validator.setBottom(0)
        self.int_validator = IntValidator()
        self.int_validator.setBottom(1)
        
        # Common fields
        self.setup_common_fields()
        self.setup_specific_fields()
        self.setup_view_options()  # New method for view options
        self.setup_buttons()
        
        # Add form layout and spacer
        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

    def setup_common_fields(self):
        # Name field
        self.form_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_edit = QLineEdit(f"Grid Block {self.block_number}")
        self.form_layout.addWidget(self.name_edit, 0, 1)

    def setup_view_options(self):
        # Create View Options group
        view_group = QGroupBox("View Options")
        view_layout = QVBoxLayout()
        
        # Checkboxes row
        checkboxes_layout = QHBoxLayout()
        
        # Visibility checkbox
        self.visibility_checkbox = QCheckBox("Visible")
        self.visibility_checkbox.setChecked(True)
        self.visibility_checkbox.stateChanged.connect(self.toggle_visibility)
        checkboxes_layout.addWidget(self.visibility_checkbox)
        
        # Show edges checkbox
        self.edges_checkbox = QCheckBox("Show Edges")
        self.edges_checkbox.setChecked(False)
        self.edges_checkbox.stateChanged.connect(self.toggle_edges)
        checkboxes_layout.addWidget(self.edges_checkbox)

        # explode checkbox
        self.explode_checkbox = QCheckBox("Explode View")
        self.explode_checkbox.setChecked(False)
        # self.explode_checkbox.stateChanged.connect(self.toggle_explode)
        checkboxes_layout.addWidget(self.explode_checkbox)
        
        checkboxes_layout.addStretch()
        view_layout.addLayout(checkboxes_layout)

        # Style dropdown
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style"))
        self.style_dropdown = QComboBox()
        self.style_dropdown.addItems(['surface', 'wireframe', 'points', 'points_gaussian'])
        style_layout.addWidget(self.style_dropdown)
        view_layout.addLayout(style_layout)
        self.style_dropdown.currentIndexChanged.connect(self.change_style)

        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        view_layout.addLayout(opacity_layout)
        
        # Color picker
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color"))
        self.color_button = ColorButton(self)
        color_layout.addWidget(self.color_button)
        self.color_button.colorChanged.connect(self.on_color_changed) 
        color_layout.addStretch()
        view_layout.addLayout(color_layout)
        
        view_group.setLayout(view_layout)
        
        # Add the group box to the main form layout
        last_row = self.get_last_row()
        self.form_layout.addWidget(view_group, last_row, 0, 1, 2)

    def setup_buttons(self):
        row = self.get_last_row()
        
        self.plot_button = QPushButton('Plot Grid Block')
        self.form_layout.addWidget(self.plot_button, row, 0, 1, 2)
        self.plot_button.setToolTip("This will replace the existing grid block and plot the new one.")

        
        self.delete_button = QPushButton('Delete Grid Block')
        self.form_layout.addWidget(self.delete_button, row + 1, 0, 1, 2)
        
        # Connect buttons to methods
        self.plot_button.clicked.connect(self.plot_grid)
        self.delete_button.clicked.connect(self.delete_grid)

    def setup_specific_fields(self):
        """Override this method in derived classes"""
        pass

    def get_last_row(self):
        """Get the last row index in the form layout"""
        return self.form_layout.rowCount()

    def create_grid(self):
        """Override this method in derived classes"""
        pass

    def plot_grid(self):
        if not hasattr(self, 'main_window'):
            self.main_window = self.window()
        
        if self.grid_actor is not None:
            self.delete_grid()
            
        grid = self.create_grid()
        if self.explode_checkbox.isChecked():
            grid = grid.explode()
        if grid is not None:
            style = self.style_dropdown.currentText()
            opacity = self.opacity_slider.value() / 100.0
            
            self.grid_actor = self.main_window.plotter.add_mesh(
                grid, 
                style=style,
                opacity=opacity,
                show_edges=self.edges_checkbox.isChecked(),
                color=self.color_button.color.getRgbF()[:3]
            )
            self.PlotFlag = True
            self.visibility_checkbox.setChecked(True)

    def toggle_visibility(self, state):
        if self.grid_actor is not None:
            self.grid_actor.visibility = bool(state)

    def toggle_edges(self, state):
        if self.grid_actor is not None:
            self.grid_actor.GetProperty().SetEdgeVisibility(bool(state))


    def change_style(self, index):
        if self.grid_actor is not None:
            if index == 0:
                self.grid_actor.GetProperty().SetRepresentationToSurface()
            if index == 1:
                self.grid_actor.GetProperty().SetRepresentationToWireframe()
            if index == 2:
                self.grid_actor.GetProperty().SetRepresentationToPoints()
            if index == 3:
                self.grid_actor.GetProperty().SetRepresentationToPoints()
                self.grid_actor.GetProperty().SetPointSize(5)

    def change_opacity(self, value):
        if self.grid_actor is not None:
            self.grid_actor.GetProperty().SetOpacity(value / 100.0) 
            # self.main_window.plotter.render()

    def on_color_changed(self, rgb_color):
        """Called when color is changed in the color button"""
        if self.grid_actor is not None:
            self.grid_actor.GetProperty().SetColor(rgb_color)
            self.main_window.plotter.render()

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.getRgbF()[:3]  # Convert to RGB tuple
            if self.grid_actor is not None:
                self.grid_actor.GetProperty().SetColor(self.current_color)
                self.main_window.plotter.render()

    def delete_grid(self):
        if self.grid_actor is not None:
            self.main_window.plotter.remove_actor(self.grid_actor)
            self.grid_actor = None
            self.PlotFlag = False
            self.visibility_checkbox.setChecked(False)

    def get_data(self):
        """Override this method in derived classes"""
        return {
            'name': self.name_edit.text(),
            'opacity': self.opacity_slider.value() / 100.0,
            'show_edges': self.edges_checkbox.isChecked(),
            'visible': self.visibility_checkbox.isChecked(),
            'color': self.current_color
        }