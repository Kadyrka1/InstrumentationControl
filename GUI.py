from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class PlotArea(FigureCanvasQTAgg):
    def __init__(self):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)

    def show_plot(self, x, y):
        self.axes.clear()
        self.axes.plot(x, y)
        self.axes.grid(True)
        self.draw()


def make_window():
    window = QMainWindow()
    window.setWindowTitle("Controller")
    window.resize(800, 600)
    
    central = QWidget()
    layout = QVBoxLayout(central)
    
    connect_btn = QPushButton("Connect")
    disconnect_btn = QPushButton("Disconnect") 
    acquire_btn = QPushButton("Acquire")
    
    button_box = QHBoxLayout()
    button_box.addWidget(connect_btn)
    button_box.addWidget(disconnect_btn)
    button_box.addWidget(acquire_btn)
    layout.addLayout(button_box)
    
    status = QLabel("Ready")
    layout.addWidget(status)
    
    wg_select = QComboBox()
    os_select = QComboBox()
    wave_select = QComboBox()
    freq_input = QLineEdit("1000")
    ampl_input = QLineEdit("1.0")
    offset_input = QLineEdit("0.0")
    
    wave_select.addItems(["SIN", "SQU", "RAMP", "TRI", "NOIS"])
    
    settings_box = QGroupBox("Settings")
    settings_layout = QFormLayout(settings_box)
    settings_layout.addRow("WG:", wg_select)
    settings_layout.addRow("OS:", os_select)
    settings_layout.addRow("Wave:", wave_select)
    settings_layout.addRow("Freq:", freq_input)
    settings_layout.addRow("Ampl:", ampl_input)
    settings_layout.addRow("Offset:", offset_input)
    
    layout.addWidget(settings_box)
    
    plot = PlotArea()
    layout.addWidget(plot)
    
    window.setCentralWidget(central)
    
    return window, connect_btn, disconnect_btn, acquire_btn, status, wg_select, os_select, wave_select, freq_input, ampl_input, offset_input, plot