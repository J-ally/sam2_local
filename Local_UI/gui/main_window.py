from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QMainWindow, 
                            QHBoxLayout, QSizePolicy, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt, QSize

# add the components package to the search path at index 0
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'components')))

from gui.components.video_viewer import VideoViewer
from core.video_controller import VideoController
from gui.components.video_control_panel import VideoControlPanel

class MainWindow(QMainWindow):
    """
    A class that represents the main window of the application.

    Attributes:
        video_path (str): Path to the video file.
    """
    def __init__(self, video_path):
        super().__init__()
        
        self.video_path = video_path
        
        self.video_controller = VideoController()
        
        # Set window properties
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 1280, 720)  # Smaller initial size
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Setup the single video layout
        self.setup_layout()
        
        self.show()
    
    def setup_layout(self):
        """Create a layout for single video with pixel rulers that maintains 16:9 aspect ratio."""
        # Use vertical layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create the video viewer
        self.video_viewer = VideoViewer(self.video_path)
        
        # Create video control panel
        self.control_panel = VideoControlPanel(self.video_controller)
        
        # Register player with controller
        self.video_controller.add_player(self.video_viewer.video_player)
        
        # Connect video player signals to controller
        self.video_viewer.video_player.toggle_play_signal.connect(self.video_controller.toggle_play)
        
        # Add all widgets to main layout
        self.main_layout.addWidget(self.video_viewer, 95)  # 95% for video and rulers
        self.main_layout.addWidget(self.control_panel, 5)  # 5% for controls
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        Press Esc to exit full screen mode.
        Press F to toggle full screen mode.
        Press Space to toggle play/pause.
        """
        if event.key() == Qt.Key_Escape:
            # Exit full screen mode
            if self.isFullScreen():
                self.showNormal()
        elif event.key() == Qt.Key_F:
            # Toggle full screen mode
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_Space:
            # Toggle play/pause through the controller
            self.video_controller.toggle_play()
        elif event.key() == Qt.Key_Left:
            # Rewind through controller
            self.video_controller.rewind()
        elif event.key() == Qt.Key_Right:
            # Fast forward through controller
            self.video_controller.forward()
        # New shortcut: R to toggle rulers visibility
        elif event.key() == Qt.Key_R:
            self.toggle_rulers()
        # Pass unhandled events to parent
        else:
            super().keyPressEvent(event)
    
    def toggle_rulers(self):
        """Toggle the visibility of the pixel rulers"""
        if self.video_viewer.h_ruler.isVisible():
            self.video_viewer.h_ruler.hide()
            self.video_viewer.v_ruler.hide()
        else:
            self.video_viewer.h_ruler.show()
            self.video_viewer.v_ruler.show()

    def closeEvent(self, event):
        """Handle application close event."""
        # Clean up video controller
        if hasattr(self, 'video_controller'):
            self.video_controller.cleanup()
        
        # Accept the close event
        event.accept()