from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QSize

class RulerWidget(QWidget):
    """
    A ruler widget that displays pixel measurements.
    """
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, orientation=HORIZONTAL, max_value=2560, tick_interval=100, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.max_value = max_value
        self.tick_interval = tick_interval  # Default to 100
        
        # Set size policy
        if orientation == self.HORIZONTAL:
            self.setMinimumHeight(30)
            self.setMaximumHeight(30)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            self.setMinimumWidth(30)
            self.setMaximumWidth(30)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        # Set a white background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(palette)
    
    def sizeHint(self):
        if self.orientation == self.HORIZONTAL:
            return QSize(self.parentWidget().width(), 30)
        else:
            return QSize(30, self.parentWidget().height())
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up the font
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        # Set up the pen
        pen = QPen(QColor(80, 80, 80))
        pen.setWidth(1)
        painter.setPen(pen)
        
        if self.orientation == self.HORIZONTAL:
            self._draw_horizontal_ruler(painter)
        else:
            self._draw_vertical_ruler(painter)
    
    def _draw_horizontal_ruler(self, painter):
        width = self.width()
        scale_factor = width / self.max_value
        
        # Draw the main line
        painter.drawLine(0, 15, width, 15)
        
        # Draw ticks and labels
        for i in range(0, self.max_value + 1, self.tick_interval):
            x_pos = int(i * scale_factor)
            
            # Draw tick
            painter.drawLine(x_pos, 5, x_pos, 15)
            # Draw label
            painter.drawText(x_pos - 15, 0, 30, 20, Qt.AlignCenter, str(i))
    
    def _draw_vertical_ruler(self, painter):
        height = self.height()
        scale_factor = height / self.max_value
        
        # Draw the main line
        painter.drawLine(15, 0, 15, height)
        
        # Draw ticks and labels
        for i in range(0, self.max_value + 1, self.tick_interval):
            y_pos = int(i * scale_factor)
            
            # Draw tick
            painter.drawLine(5, y_pos, 15, y_pos)
            # Draw label
            painter.save()
            painter.translate(3, y_pos)
            painter.drawText(0, -8, 20, 16, Qt.AlignRight, str(i))
            painter.restore()