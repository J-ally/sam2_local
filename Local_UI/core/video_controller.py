from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
from datetime import datetime, timedelta
import sys
import os

# Add utils to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.time_utils import extract_start_time_video_path

class VideoController(QObject):
    """
    Controller for a single video player.
    """
    # Signals
    playStateChanged = pyqtSignal(bool)  # True for playing, False for paused
    positionChanged = pyqtSignal(int)    # Position in milliseconds
    durationChanged = pyqtSignal(int)    # Duration in milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_player = None
        self.is_playing = False
        self.duration = 0
        self.position = 0
        
    def add_player(self, player):
        """Add the video player to control."""
        self.video_player = player
        
        # Connect the player's signals
        player.media_player.positionChanged.connect(self.update_position)
        player.media_player.durationChanged.connect(self.update_duration)
        
        # Connect player to controller
        if hasattr(player, 'toggle_play_signal'):
            player.toggle_play_signal.connect(self.toggle_play)
    
    def toggle_play(self):
        """Toggle play/pause state for video."""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.video_player.media_player.play()
        else:
            self.video_player.media_player.pause()
        
        # Emit signal for UI updates
        self.playStateChanged.emit(self.is_playing)
    
    def stop(self):
        """Stop video."""
        self.is_playing = False
        self.video_player.media_player.stop()
        self.position = 0
        self.positionChanged.emit(0)
        self.playStateChanged.emit(self.is_playing)
    
    def set_position(self, position):
        """Set position for video."""
        self.position = position
        self.video_player.media_player.setPosition(position)
        self.positionChanged.emit(position)
    
    def update_position(self, position):
        """Update current position from player."""
        self.position = position
        self.positionChanged.emit(position)
    
    def update_duration(self, duration):
        """Update duration from player."""
        self.duration = duration
        self.durationChanged.emit(duration)
    
    @pyqtSlot()
    def rewind(self):
        """Rewind video by 10 seconds."""
        new_position = max(0, self.position - 10000)
        self.set_position(new_position)
    
    @pyqtSlot()
    def forward(self):
        """Fast forward video by 10 seconds."""
        new_position = min(self.duration, self.position + 10000)
        self.set_position(new_position)
    
    def cleanup(self):
        """Disconnect all signals and prepare for safe shutdown."""
        try:
            # Stop playback
            self.is_playing = False
            
            # Disconnect player signals
            if self.video_player:
                try:
                    self.video_player.media_player.positionChanged.disconnect(self.update_position)
                    self.video_player.media_player.durationChanged.disconnect(self.update_duration)
                    if hasattr(self.video_player, 'toggle_play_signal'):
                        self.video_player.toggle_play_signal.disconnect(self.toggle_play)
                except:
                    pass
            
            # Clear reference
            self.video_player = None
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def __del__(self):
        """Ensure proper cleanup when the controller is destroyed."""
        self.cleanup()
