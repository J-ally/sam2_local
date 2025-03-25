import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot

# For plotting
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class TimeSeriesView(QWidget):
    """
    Widget for visualizing RSSI time series data synchronized with video playback.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize data
        self.current_data = None
        self.current_timestamp = 0.0
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components for the time series visualization."""
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Create matplotlib figure for plotting
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        # Add canvas to layout
        self.layout.addWidget(self.canvas)
        
        # Initialize plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("RSSI Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("RSSI (dBm)")
        self.ax.grid(True)
        
        # Set the tight layout
        self.figure.tight_layout()
    
    @pyqtSlot(object, float)
    def update_data(self, data_frame, timestamp):
        """
        Update the view with new time series data.
        
        Args:
            data_frame (pd.DataFrame): DataFrame containing the RSSI data
            timestamp (float): Current video timestamp in seconds
        """
        try:
            # Store current data for reference
            self.current_data = data_frame
            self.current_timestamp = timestamp
            
            # Clear previous plot
            self.ax.clear()
            
            # Check if we have valid data
            if data_frame is None or data_frame.empty:
                self.ax.set_title("No data available")
                self.canvas.draw()
                return
            
            # Get unique sensor IDs for multiple lines
            if 'accelero_id' in data_frame.columns:
                sensor_ids = data_frame['accelero_id'].unique()
                
                # Plot data for each sensor with different color
                for sensor_id in sensor_ids:
                    sensor_data = data_frame[data_frame['accelero_id'] == sensor_id]
                    
                    if 'relative_DateTime' in sensor_data.columns and 'RSSI' in sensor_data.columns:
                        # Sort by datetime to ensure proper line plotting
                        sensor_data = sensor_data.sort_values('relative_DateTime')
                        
                        # Plot the data
                        self.ax.plot(
                            sensor_data['relative_DateTime'], 
                            sensor_data['RSSI'], 
                            label=f"Sensor {sensor_id}"
                        )
            # If no accelero_id column, plot all data as a single line
            elif 'relative_DateTime' in data_frame.columns and 'RSSI' in data_frame.columns:
                # Sort data by datetime
                data_frame = data_frame.sort_values('relative_DateTime')
                
                # Plot the data
                self.ax.plot(data_frame['relative_DateTime'], data_frame['RSSI'])
            
            # Set title with current timestamp
            time_str = self.format_time(self.current_timestamp)
            self.ax.set_title(f"RSSI Data (Video Time: {time_str})")
            
            # Add labels and grid
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("RSSI (dBm)")
            self.ax.grid(True)
            
            # Add legend if multiple sensors
            if 'accelero_id' in data_frame.columns and len(sensor_ids) > 1:
                self.ax.legend()
            
            # Format y-axis to show negative values properly
            self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%d'))
            
            # Limit y-axis range for RSSI values (typically between -100 and -30 dBm)
            y_min = min(-100, data_frame['RSSI'].min() - 5) if 'RSSI' in data_frame.columns else -100
            y_max = max(-30, data_frame['RSSI'].max() + 5) if 'RSSI' in data_frame.columns else -30
            self.ax.set_ylim([y_min, y_max])
            
            # Rotate x-axis date labels for better readability
            plt.setp(self.ax.get_xticklabels(), rotation=30, ha='right')
            
            # Update the canvas
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating time series view: {e}")
            # Set a simple error message on the plot
            self.ax.clear()
            self.ax.set_title(f"Error plotting data: {str(e)}")
            self.canvas.draw()
    
    def format_time(self, seconds):
        """Format seconds into HH:MM:SS format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"