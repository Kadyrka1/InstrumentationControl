import sys
import pyvisa
import numpy as np

from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui_mainwindow import Ui_MainWindow


# Matplotlib Canvas
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot_waveform(self, t, v):
        self.ax.clear()
        self.ax.plot(t, v)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.set_title("Acquired Data")
        self.ax.grid(True)
        self.draw()


# Main Window Logic
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # VISA
        self.rm = pyvisa.ResourceManager()
        self.device = None

        # Matplotlib inside graphicsView
        self.canvas = MplCanvas(self)
        layout = QtWidgets.QVBoxLayout(self.ui.graphicsView)
        layout.addWidget(self.canvas)

        # Connect buttons
        self.ui.pushButton.clicked.connect(self.connect_device)
        self.ui.pushButton_2.clicked.connect(self.disconnect_device)
        self.ui.pushButton_3.clicked.connect(self.acquire_data)
        self.ui.pushButton_4.clicked.connect(self.stop_acquisition)

    # Button Callbacks
    def connect_device(self):
        try:
            resources = self.rm.list_resources()
            print("Available VISA resources:", resources)

            self.device = self.rm.open_resource('ASRL6::INSTR')
            idn = self.device.query('*IDN?')

            QtWidgets.QMessageBox.information(
                self, "Connected", f"Device connected:\n{idn}"
            )

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def disconnect_device(self):
        if self.device:
            self.device.close()
            self.device = None
            QtWidgets.QMessageBox.information(self, "Disconnected", "Device disconnected")

    def acquire_data(self):
        if not self.device:
            QtWidgets.QMessageBox.warning(self, "Warning", "Device not connected")
            return

        try:
            self.device.write("MEAS:RAW?")
            raw_data = self.device.read()

            voltages = np.array([float(v) for v in raw_data.split(',')])
            times = np.linspace(0, 1, len(voltages))

            self.canvas.plot_waveform(times, voltages)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Acquisition Error", str(e))

    def stop_acquisition(self):
        QtWidgets.QMessageBox.information(self, "Stop", "Acquisition stopped")

# Application Entry Point
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
