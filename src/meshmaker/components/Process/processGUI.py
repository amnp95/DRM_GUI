from qtpy.QtGui import QDrag, QPixmap, QColor, QPainter
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, 
    QListWidgetItem, QTabWidget, QDialog, QMessageBox, QMenu, QAction, 
    QAbstractItemView, QFrame, QSplitter, QApplication
)
from qtpy.QtCore import Qt, QMimeData, QPoint

from meshmaker.components.Process.process import ProcessManager
from meshmaker.components.Recorder.recorderBase import Recorder, RecorderManager
from meshmaker.components.Analysis.analysis import Analysis, AnalysisManager


class ComponentDragItem(QListWidgetItem):
    """
    Custom list item that can be dragged for components
    """
    def __init__(self, tag, component_type, name, parent=None):
        super().__init__(f"{name} (Tag: {tag})", parent)
        self.tag = tag
        self.component_type = component_type
        self.setToolTip(f"Drag to add {component_type} with tag {tag} to process")
        

class ComponentListWidget(QListWidget):
    """
    List widget that supports drag operations for components
    """
    def __init__(self, component_type, parent=None):
        """
        Initialize component list widget
        
        Args:
            component_type (str): Type of component ('Analysis' or 'Recorder')
            parent: Parent widget
        """
        super().__init__(parent)
        self.component_type = component_type
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
    def startDrag(self, supportedActions):
        """
        Start drag operation when item is dragged
        """
        item = self.currentItem()
        if not item:
            return
            
        # Create mime data
        mimeData = QMimeData()
        mimeData.setText(f"{self.component_type}:{item.tag}")
        
        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        
        # Create a pixmap for the drag icon
        pixmap = QPixmap(200, 30)
        pixmap.fill(QColor(230, 230, 250))  # Light lavender color
        
        # Add text to the pixmap
        painter = QPainter(pixmap)
        painter.drawText(10, 20, f"{self.component_type}: {item.tag}")
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(10, 15))
        
        # Execute drag
        result = drag.exec_(Qt.CopyAction)


class ProcessListWidget(QListWidget):
    """
    List widget to display process steps with drop support
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process_manager = ProcessManager()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def dragEnterEvent(self, event):
        """Accept drag events from component lists"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Accept move events for component drops"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop events to add components to process"""
        if event.mimeData().hasText():
            text = event.mimeData().text()
            component_type, tag = text.split(':')
            tag = int(tag)
            
            # Get the component based on type
            component = None
            description = ""
            
            if component_type == "Analysis":
                component = AnalysisManager().get_analysis(tag)
                description = f"Analysis: {component.name} ({component.analysis_type})"
            elif component_type == "Recorder":
                component = RecorderManager().get_recorder(tag)
                description = f"Recorder: {component.recorder_type}"
            
            if component:
                # Add to process manager
                self.process_manager.add_step(component, description)
                
                # Refresh the list
                self.refresh_process_list()
            
            event.acceptProposedAction()
    
    def refresh_process_list(self):
        """Refresh the process steps list"""
        self.clear()
        
        # Add each step from the process manager
        for i, step in enumerate(self.process_manager.get_steps()):
            component_ref = step["component"]
            component = component_ref()  # Get the actual component from weak reference
            
            if component:
                # Create list item
                description = step["description"] or f"Step {i+1}"
                item = QListWidgetItem(f"{i+1}. {description}")
                item.setToolTip(f"Step {i+1}: {description}")
                self.addItem(item)
    
    def show_context_menu(self, position):
        """Show context menu for process items"""
        # Get selected items
        selected_items = self.selectedItems()
        if not selected_items:
            return
        
        # Create menu
        menu = QMenu()
        remove_action = QAction("Remove from process", self)
        remove_action.triggered.connect(self.remove_selected_steps)
        menu.addAction(remove_action)
        
        # Execute menu
        menu.exec_(self.mapToGlobal(position))
    
    def remove_selected_steps(self):
        """Remove selected steps from the process"""
        # Get selected rows in reverse order (to avoid index shifting when removing)
        selected_rows = sorted([self.row(item) for item in self.selectedItems()], reverse=True)
        
        for row in selected_rows:
            self.process_manager.remove_step(row)
        
        # Refresh list
        self.refresh_process_list()


class ProcessTab(QWidget):
    """
    Tab for a specific component type in the process GUI
    """
    def __init__(self, component_type, parent=None):
        """
        Initialize process tab
        
        Args:
            component_type (str): Type of component ('Analysis' or 'Recorder')
            parent: Parent widget
        """
        super().__init__(parent)
        self.component_type = component_type
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI elements"""
        layout = QVBoxLayout(self)
        
        # Label
        label = QLabel(f"Available {self.component_type} Components")
        layout.addWidget(label)
        
        # Component list
        self.component_list = ComponentListWidget(self.component_type)
        layout.addWidget(self.component_list)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_components)
        layout.addWidget(refresh_btn)
        
        # Add button (alternative to drag-and-drop)
        add_btn = QPushButton(f"Add Selected {self.component_type} to Process")
        add_btn.clicked.connect(self.add_to_process)
        layout.addWidget(add_btn)
        
        # Initial refresh
        self.refresh_components()
    
    def refresh_components(self):
        """Refresh the components list"""
        self.component_list.clear()
        
        if self.component_type == "Analysis":
            # Get analyses from the manager
            manager = AnalysisManager()
            for tag, analysis in manager.get_all_analyses().items():
                item = ComponentDragItem(tag, self.component_type, analysis.name)
                self.component_list.addItem(item)
        
        elif self.component_type == "Recorder":
            # Get recorders from the manager
            manager = RecorderManager()
            for tag, recorder in manager.get_all_recorders().items():
                item = ComponentDragItem(tag, self.component_type, recorder.recorder_type)
                self.component_list.addItem(item)
    
    def add_to_process(self):
        """Add selected component to process (alternative to drag-and-drop)"""
        selected_items = self.component_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", f"Please select a {self.component_type} to add to process")
            return
        
        item = selected_items[0]
        tag = item.tag
        
        # Get component
        component = None
        description = ""
        
        if self.component_type == "Analysis":
            component = AnalysisManager().get_analysis(tag)
            description = f"Analysis: {component.name} ({component.analysis_type})"
        elif self.component_type == "Recorder":
            component = RecorderManager().get_recorder(tag)
            description = f"Recorder: {component.recorder_type}"
        
        if component:
            # Add to process manager
            ProcessManager().add_step(component, description)
            
            # Notify parent to refresh process list
            if hasattr(self.parent(), 'refresh_process_panel'):
                self.parent().refresh_process_panel()


class ProcessGUI(QDialog):
    """
    Main dialog for process management GUI
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Process Manager")
        self.resize(900, 600)
        self.process_manager = ProcessManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI elements"""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (component types)
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        # Create tabs for different component types
        self.tabs = QTabWidget()
        
        # Add tabs for component types
        self.analysis_tab = ProcessTab("Analysis")
        self.recorder_tab = ProcessTab("Recorder")
        
        self.tabs.addTab(self.analysis_tab, "Analysis")
        self.tabs.addTab(self.recorder_tab, "Recorders")
        
        left_layout.addWidget(self.tabs)
        
        # Right panel (process steps)
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("Process Steps (Drop Components Here)"))
        
        # Process list
        self.process_list = ProcessListWidget()
        right_layout.addWidget(self.process_list)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All Steps")
        clear_btn.clicked.connect(self.clear_process)
        button_layout.addWidget(clear_btn)
        
        refresh_btn = QPushButton("Refresh Process List")
        refresh_btn.clicked.connect(self.refresh_process_panel)
        button_layout.addWidget(refresh_btn)
        
        run_btn = QPushButton("Run Process")
        run_btn.clicked.connect(self.run_process)
        button_layout.addWidget(run_btn)
        
        right_layout.addLayout(button_layout)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 600])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Initial refresh
        self.refresh_process_panel()
    
    def refresh_process_panel(self):
        """Refresh the process steps list"""
        self.process_list.refresh_process_list()
    
    def clear_process(self):
        """Clear all process steps"""
        reply = QMessageBox.question(
            self, 'Clear Process',
            "Are you sure you want to clear all process steps?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.process_manager.clear_steps()
            self.refresh_process_panel()
    
    def run_process(self):
        """Execute the process (placeholder for actual execution)"""
        # Count steps
        steps = self.process_manager.get_steps()
        if not steps:
            QMessageBox.warning(self, "Empty Process", "No steps in the process to run.")
            return
        
        # This is a placeholder for actual process execution
        # In a real implementation, you would call appropriate methods on each component
        
        step_texts = []
        for i, step in enumerate(steps):
            component_ref = step["component"]
            component = component_ref()
            
            if component:
                component_type = type(component).__name__
                tag = getattr(component, 'tag', 'unknown')
                step_texts.append(f"Step {i+1}: {component_type} (Tag: {tag})")
        
        summary = "\n".join(step_texts)
        QMessageBox.information(
            self, "Process Execution",
            f"Process would execute these steps:\n\n{summary}\n\n"
            f"(This is a placeholder for actual execution.)"
        )


# Run as standalone for testing
if __name__ == "__main__":
    import sys
    
    # Create some sample components for testing
    recorder_manager = RecorderManager()
    analysis_manager = AnalysisManager()
    
    # Create sample recorders
    from meshmaker.components.Recorder.recorderBase import NodeRecorder, VTKHDFRecorder
    recorder1 = NodeRecorder(file_name="disp.out", nodes=[1, 2, 3], dofs=[1, 2], resp_type="disp")
    recorder2 = VTKHDFRecorder(file_base_name="results", resp_types=["disp", "vel"])
    recorder1 = NodeRecorder(file_name="disp.out", nodes=[1, 2, 3], dofs=[1, 2], resp_type="disp")
    
    # Create sample analyses (Note: This is simplified as actual Analysis objects require many components)
    # In a real implementation, you would create proper Analysis objects with all required components
    try:
        from meshmaker.components.Analysis.constraint_handlers import ConstraintHandlerManager
        from meshmaker.components.Analysis.numberers import NumbererManager
        from meshmaker.components.Analysis.systems import SystemManager
        from meshmaker.components.Analysis.algorithms import AlgorithmManager
        from meshmaker.components.Analysis.convergenceTests import TestManager
        from meshmaker.components.Analysis.integrators import IntegratorManager
        
        # Create components for analysis
        constraint_handler = ConstraintHandlerManager().create_handler("transformation")
        numberer = NumbererManager().get_numberer("rcm")
        system = SystemManager().create_system("bandspd")
        algorithm = AlgorithmManager().create_algorithm("newton")
        test = TestManager().create_test("normunbalance", tol=1e-6, max_iter=100)
        integrator = IntegratorManager().create_integrator("loadcontrol", incr=0.1)
        
        # Create analysis
        analysis1 = AnalysisManager().create_analysis(
            name="Static Analysis", 
            analysis_type="Static",
            constraint_handler=constraint_handler,
            numberer=numberer,
            system=system,
            algorithm=algorithm,
            test=test,
            integrator=integrator,
            num_steps=10
        )
    except Exception as e:
        print(f"Error creating analysis components: {e}")
    
    app = QApplication(sys.argv)
    gui = ProcessGUI()
    gui.show()
    sys.exit(app.exec_())