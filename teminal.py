from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QFrame, QVBoxLayout, QWidget, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtWidgets import QFrame, QGridLayout
from PyQt5.QtGui import QPainter, QLinearGradient, QColor

class GradientFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(self.rect().topLeft(), self.rect().bottomRight())
        gradient.setColorAt(0, QColor(63, 63, 63))  # Start color
        gradient.setColorAt(1, QColor(31, 31, 31))  # End color
        painter.fillRect(self.rect(), gradient)

class Terminal(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("DRISHTI RF MAP")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        gradient_color = """
            qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1c1f2b, stop:1 #000000);
        """
        self.setStyleSheet(f"background: {gradient_color}; color: white;")  # Set gradient background color and text color

        # self.setStyleSheet("background-color: #1c1f2b;; color: white;")  # Set overall background color and text color
        
        self.top_layout = QVBoxLayout(self)
                # Gradient Background Frame
        self.gradient_frame = GradientFrame()
        self.gradient_layout = QGridLayout(self.gradient_frame)

        # Add other widgets here...

        self.top_layout.addWidget(self.gradient_frame)

        # Other widget initialization and layout...

        self.setLayout(self.top_layout)
        
        # Logo and Heading Frame
        self.logo_heading_frame = QFrame()
        self.logo_heading_layout = QHBoxLayout(self.logo_heading_frame)
        
        # Logo
        self.logo_frame = QFrame()
        self.logo_frame.setSizePolicy(Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)  # Set size policy
        self.logo_layout = QHBoxLayout(self.logo_frame)
        self.logo_label = QLabel()
        self.logo_label.setPixmap(Qt.QPixmap("logo.png").scaledToWidth(140))
        self.logo_frame.setFixedHeight(100)
        self.logo_layout.addWidget(self.logo_label)
        self.logo_heading_layout.addWidget(self.logo_frame)
        
        # Heading
        self.heading_frame = QFrame()
        self.heading_layout = QHBoxLayout(self.heading_frame)
        self.heading_label = QLabel("<b>DRISHTI RF MAP</b>")
        self.heading_label.setStyleSheet("font-size: 40px; color: #ffffff;")  # Set font size and color
        self.heading_layout.addWidget(self.heading_label, alignment=Qt.Qt.AlignCenter)  # Align the label to the right
        self.heading_frame.setFixedHeight(58)
        self.logo_heading_layout.addWidget(self.heading_frame)
        self.top_layout.addWidget(self.logo_heading_frame)
                
        # New Frame for Input Fields
        self.input_frame = QFrame()
        self.input_layout = QVBoxLayout(self.input_frame)

        # Input Row 1
        input_row1_layout = QHBoxLayout()
        self.label1 = QLabel("FREQUENCY RANGE")
        self.label1.setStyleSheet("color: #ffffff;")  # Set label color
        input_row1_layout.addWidget(self.label1 , alignment=Qt.Qt.AlignRight)
        self.input_field1 = QLineEdit()
        self.input_field1.setFixedWidth(200)  # Set width to 200 pixels
        input_row1_layout.addWidget(self.input_field1, alignment=Qt.Qt.AlignLeft)
        self.input_layout.addLayout(input_row1_layout)

        # Input Row 2
        input_row2_layout = QHBoxLayout()
        self.label2 = QLabel("SUB FREQUENCY RANGE")
        self.label2.setStyleSheet("color: #ffffff;")  # Set label color
        input_row2_layout.addWidget(self.label2,alignment=Qt.Qt.AlignRight)
        self.input_field2 = QLineEdit()
        self.input_field2.setFixedWidth(200)  # Set width to 200 pixels
        input_row2_layout.addWidget(self.input_field2, alignment=Qt.Qt.AlignLeft)
        self.input_layout.addLayout(input_row2_layout)

        # Input Row 3
        input_row3_layout = QHBoxLayout()
        self.label3 = QLabel("RESOLUTION")
        self.label3.setStyleSheet("color: #ffffff;")  # Set label color
        input_row3_layout.addWidget(self.label3,alignment=Qt.Qt.AlignRight)
        self.input_field3 = QLineEdit()
        self.input_field3.setFixedWidth(200)  # Set width to 200 pixels
        input_row3_layout.addWidget(self.input_field3, alignment=Qt.Qt.AlignLeft)
        self.input_layout.addLayout(input_row3_layout)

        # Add the input frame to the main layout
        self.top_layout.addWidget(self.input_frame)

        # Divided Frame for Active Channels and Google Map
        self.divided_frame = QFrame()
        self.divided_layout = QHBoxLayout(self.divided_frame)
        
        # Active Channels Frame
        self.active_channels_frame = QFrame()
        self.active_channels_layout = QVBoxLayout(self.active_channels_frame)
        self.active_channels_frame.setFixedWidth(450)
        self.active_channels_frame.setStyleSheet("background-color: #000000; color: #ffffff;")  # Set background color to black and text color to white
        # Create a QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)  # Set the number of columns to 4

        # Set the column headers
        self.table_widget.setHorizontalHeaderLabels(["Frequency", "Angle", "Bandwidth", "Activity"])

        # Add the table widget to the layout
        self.active_channels_layout.addWidget(self.table_widget)

        # Add rows to the table
        for i in range(5):
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            for j in range(4):
                self.table_widget.setItem(row_position, j, QTableWidgetItem(f"data{i+1}"))

        # Add the active channels frame to the divided layout
        self.divided_layout.addWidget(self.active_channels_frame)

        # Google Map Frame
        self.google_map_frame = QFrame()
        self.google_map_layout = QVBoxLayout(self.google_map_frame)
        self.google_map_frame.setFixedWidth(790)
        self.map_image_label = QLabel()
        self.map_image_label.setPixmap(Qt.QPixmap("maps.jpeg"))
        self.google_map_layout.addWidget(self.map_image_label)
        self.google_map_layout.setContentsMargins(300 ,0 ,0, 0)  # Set padding (10 pixels on all sides)

        self.divided_layout.addWidget(self.google_map_frame)
        
        self.top_layout.addWidget(self.divided_frame)
        
        # Spacer
        self.top_layout.addStretch(1)
        
        # Waterfall and other widgets
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        # Add your waterfall and other widgets here
        self.top_layout.addWidget(self.main_widget)

        # Variables
        self.samp_rate = samp_rate = 32000

        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
    1024, window.WIN_BLACKMAN_hARRIS, 0, samp_rate, "", 1, None)
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)
        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)
        self._qtgui_waterfall_sink_x_0_win.setFixedSize(1300,200)

        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)

        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1000, 1, 0, 0)

        # Checkbox for "INCLUDE DRONE DETECTION"
        self.checkbox_include_drone_detection = QCheckBox("INCLUDE DRONE DETECTION")
        self.checkbox_include_drone_detection.setStyleSheet("color: #ffffff;")  # Set checkbox text color
        self.top_layout.addWidget(self.checkbox_include_drone_detection)
        # Connections
        self.connect((self.analog_sig_source_x_0, 0), (self.qtgui_waterfall_sink_x_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Terminal")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)

def main(top_block_cls=Terminal, options=None):
    qapp = Qt.QApplication(sys.argv)
    tb = top_block_cls()
     # Adjust width and height as needed
    # tb.resize(1360,100)

    tb.start()
    tb.showFullScreen()
    # tb.show()
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
