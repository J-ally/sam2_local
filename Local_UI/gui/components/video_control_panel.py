from PyQt5.QtWidgets import QWidget, QHBoxLayout, QToolButton, QSlider, QLabel, QStyle
from PyQt5.QtCore import Qt, QTime
from datetime import datetime, timedelta

class VideoControlPanel(QWidget):
    """
    Centralized control panel for multiple video players.
    """
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Play/Pause button
        self.play_button = QToolButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setToolTip("Play/Pause")
        
        # Instead of connecting directly to controller.toggle_play
        # self.play_button.clicked.connect(self.controller.toggle_play)
        # Use our own handler that updates the button immediately
        self.play_button.clicked.connect(self.handle_play_button)
        
        layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QToolButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.controller.stop)
        layout.addWidget(self.stop_button)
        
        # Rewind button
        self.rewind_button = QToolButton()
        self.rewind_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.rewind_button.clicked.connect(self.controller.rewind)
        layout.addWidget(self.rewind_button)
        
        # Forward button
        self.forward_button = QToolButton()
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forward_button.clicked.connect(self.controller.forward)
        layout.addWidget(self.forward_button)
        
        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 10000)
        self.position_slider.sliderReleased.connect(self.position_changed)
        layout.addWidget(self.position_slider)
        
        # Time display
        self.time_label = QLabel("00:00:00 / 00:00:00")
        layout.addWidget(self.time_label)
        
        # Connect controller signals
        self.controller.playStateChanged.connect(self.update_play_state)
        self.controller.positionChanged.connect(self.update_position)
        self.controller.durationChanged.connect(self.update_duration)
        
        # Initialize button state
        self.update_play_state(self.controller.is_playing)
    
    def position_changed(self):
        """Handle slider position changes."""
        position = int(self.position_slider.value() / 10000.0 * self.controller.duration)
        self.controller.set_position(position)
    
    def update_play_state(self, is_playing):
        """Update button based on play state."""
        if is_playing:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    
    def update_position(self, position):
        """Update slider and time display with current position."""
        # Update slider without triggering events
        if self.controller.duration > 0 and not self.position_slider.isSliderDown():
            self.position_slider.blockSignals(True)
            slider_value = int(position / self.controller.duration * 10000) if self.controller.duration > 0 else 0
            self.position_slider.setValue(slider_value)
            self.position_slider.blockSignals(False)
        
        # Update time display
        self.update_time_label()
    
    def update_duration(self, duration):
        """Update UI with new duration."""
        self.position_slider.setEnabled(duration > 0)
        self.update_time_label()
    
    def update_time_label(self):
        """Update the time display."""
        position = self.controller.position
        duration = self.controller.duration
        
        position_time = QTime(0, 0, 0).addMSecs(position)
        duration_time = QTime(0, 0, 0).addMSecs(duration)
        
        time_format = "hh:mm:ss"
        position_str = position_time.toString(time_format)
        duration_str = duration_time.toString(time_format)
        
        # Calculate real datetime if earliest start time is available
        if hasattr(self.controller, 'earliest_start_time') and self.controller.earliest_start_time:
            real_time = self.controller.earliest_start_time + timedelta(milliseconds=position)
            real_time_str = real_time.strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.setText(f"{position_str} / {duration_str} ({real_time_str})")
        else:
            self.time_label.setText(f"{position_str} / {duration_str}")
    
    def handle_play_button(self):
        """Handle play button clicks and update UI immediately."""
        self.controller.toggle_play()
        self.update_play_state(self.controller.is_playing)