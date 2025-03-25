from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtCore import QSize
from gui.components.video_player import VideoPlayer
from gui.components.ruler_widget import RulerWidget

class VideoViewer(QWidget):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.video_width = 2560  # 1440p video width
        self.video_height = 1440  # 1440p video height
        
        self.setup_layout()
    
    def setup_layout(self):
        """Create a layout for single video with pixel rulers that maintains 16:9 aspect ratio."""
        # Use grid layout for more precise control
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)
        
        # Create horizontal ruler (top)
        self.h_ruler = RulerWidget(RulerWidget.HORIZONTAL, max_value=self.video_width)
        
        # Create vertical ruler (left)
        self.v_ruler = RulerWidget(RulerWidget.VERTICAL, max_value=self.video_height)
        
        # Create corner spacer widget
        corner_spacer = QWidget()
        corner_spacer.setFixedSize(30, 30)
        
        # Create the video player
        self.video_player = VideoPlayer(self.video_path)
        self.video_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add widgets to the grid
        grid_layout.addWidget(corner_spacer, 0, 0)  # Corner space
        grid_layout.addWidget(self.h_ruler, 0, 1)    # Top ruler
        grid_layout.addWidget(self.v_ruler, 1, 0)    # Left ruler
        grid_layout.addWidget(self.video_player, 1, 1) # Video player