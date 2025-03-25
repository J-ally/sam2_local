from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy, QStyle, QLabel)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTime
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPixmap
import os


class VideoPlayer(QWidget):
    """
    A class that represents a video player widget.
    
    Attributes:
        video_path (str): Path to the video file.
    """
    # Signal emitted when user clicks on the video
    toggle_play_signal = pyqtSignal()
    
    def __init__(self, video_path=None):
        super().__init__()
        
        # Store the path
        self.video_path = video_path
        
        # Set up the UI
        self.setup_ui()
        
        # Load the video if a path was provided
        if video_path:
            self.load_video(video_path)
    
    def setup_ui(self):
        """Set up the user interface for the video player."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(320, 180)  # Minimum size for the video
        
        # Create media player
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Add video widget to layout
        self.layout.addWidget(self.video_widget)
        
        # Set focus policy to enable keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
    
    def load_video(self, video_path):
        """
        Load a video file into the player.
        
        Args:
            video_path (str): Path to the video file to load.
        """
        self.video_path = video_path
        
        if os.path.isfile(video_path):
            url = QUrl.fromLocalFile(video_path)
            content = QMediaContent(url)
            self.media_player.setMedia(content)
        else:
            print(f"Error: Video file not found: {video_path}")
    
    def toggle_play(self):
        """Toggle play/pause state of the video."""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            # Emit signal to toggle play/pause
            self.toggle_play_signal.emit()
        
        # Pass the event to the parent class
        super().mousePressEvent(event)
    
    def stop_video(self):
        """Stop video playback."""
        self.media_player.stop()
    
    
    def rewind(self):
        """Rewind 10 seconds."""
        new_position = self.media_player.position() - 10000  # 10 seconds in ms
        self.media_player.setPosition(max(0, new_position))
    
    
    def forward(self):
        """Fast forward 10 seconds."""
        new_position = self.media_player.position() + 10000  # 10 seconds in ms
        self.media_player.setPosition(min(self.media_player.duration(), new_position))
    
    
    def on_slider_pressed(self):
        """Handler when slider is pressed - pause playback temporarily."""
        self._was_playing = self.media_player.state() == QMediaPlayer.PlayingState
        if self._was_playing:
            self.media_player.pause()
    
    
    def on_slider_released(self):
        """Handler when slider is released - set position and resume if needed."""
        # Calculate position based on slider value and video duration
        position = int(self.position_slider.value() / 10000.0 * self.media_player.duration())
        self.media_player.setPosition(position)
        
        # Resume playback if it was playing before
        if self._was_playing:
            self.media_player.play()
    
    
    def on_slider_value_changed(self, value):
        """Handler when slider value changes - only update UI, not playback."""
        if not self.position_slider.isSliderDown():  # Only if user is not dragging
            position = int(value / 10000.0 * self.media_player.duration())
            self.update_time_label(position, self.media_player.duration())
    
    
    def media_state_changed(self, state):
        """Update button based on media state."""
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    
    
    def update_position(self, position):
        """Update slider position without triggering events."""
        # Block signals to prevent feedback loop
        self.position_slider.blockSignals(True)
        slider_value = int(position / self.media_player.duration() * 10000) if self.media_player.duration() > 0 else 0
        self.position_slider.setValue(slider_value)
        self.position_slider.blockSignals(False)
        
        # Update time display
        self.update_time_label(position, self.media_player.duration())
        
        # Emit our own signal
        self.positionChanged.emit(position)
    
    
    def update_duration(self, duration):
        """Update UI based on video duration."""
        self.position_slider.setEnabled(duration > 0)
        self.update_time_label(self.media_player.position(), duration)
    
    
    def update_time_label(self, position, duration):
        """Update the time label with current position and duration."""
        position_time = QTime(0, 0, 0).addMSecs(position)
        duration_time = QTime(0, 0, 0).addMSecs(duration)
        
        time_format = "hh:mm:ss"
        position_str = position_time.toString(time_format)
        duration_str = duration_time.toString(time_format)
        
        self.time_label.setText(f"{position_str} / {duration_str}")
    
    
    def handle_error(self):
        """Handle media player errors."""
        error_msg = f"Error: {self.media_player.errorString()}"
        self.time_label.setText(error_msg)
        print(error_msg)
    
    def set_active(self, is_active):
        """Set visual indication if video is active in current time window."""
        if is_active:
            self.setStyleSheet("")
        else:
            self.setStyleSheet("border: 2px solid red;")