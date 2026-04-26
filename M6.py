import sys
import pyvisa
from PyQt5.QtWidgets import *
from GUI import make_window


class Instruments:
    def __init__(self):
        pass
    
    def find(self):
        rm = pyvisa.ResourceManager()
        return rm.list_resources()
    
    def connect_wg(address):
        rm = pyvisa.ResourceManager()
        wg = rm.open_resource(address)
        wg.timeout = 5000
        wg.write('*RST')
        wg.query('*IDN?')
        return wg
    
    def connect_os(address):
        rm = pyvisa.ResourceManager()
        os = rm.open_resource(address)
        os.timeout = 10000
        os.write('*RST')
        os.query('*IDN?')
        return os
    
    def set_wave(wg, wave, freq, ampl, offset):
        wg.write(f"SOUR1:APPLy:{wave} {freq},{ampl},{offset}")
    
    def get_data(os):
        os.write("AUToscale")
        os.write(":DIGitize CHANnel1")
        os.write(":WAVeform:SOURce CHANnel1")
        os.write(":WAVeform:FORMat ASCii")
        os.write(":WAVeform:POINts:MODE NORMal")
        
        preamble = os.query(":WAVeform:PREamble?")
        pre = [float(x) for x in preamble.split(',')]
        _, _, points, _, xinc, xorg, xref, _, _, _ = pre
        
        data = os.query(":WAVeform:DATA?")
        
        if data.startswith('#'):
            header_len = int(data[1])
            data_len = int(data[2:2 + header_len])
            data = data[2 + header_len:2 + header_len + data_len]
        
        voltages = [float(v) for v in data.split(',')]
        times = [((i - xref) * xinc) + xorg for i in range(int(points))]
        
        return times, voltages


class MainWindow:
    def __init__(self):
        self.window, self.connect_btn, self.disconnect_btn, self.acquire_btn, self.status, self.wg_select, self.os_select, self.wave_select, self.freq_input, self.ampl_input, self.offset_input, self.plot = make_window()
        
        self.connect_btn.clicked.connect(self.connect)
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.acquire_btn.clicked.connect(self.acquire)
        
        self.disconnect_btn.setEnabled(False)
        self.acquire_btn.setEnabled(False)
        
        self.find_resources()
        
    def find_resources(self):
        resources = Instruments().find()
        self.wg_select.clear()
        self.os_select.clear()
        for r in resources:
            self.wg_select.addItem(r)
            self.os_select.addItem(r)
        self.status.setText(f"Found {len(resources)} devices")
    
    def connect(self):
        wg_address = self.wg_select.currentText()
        os_address = self.os_select.currentText()
        
        self.wg = Instruments.connect_wg(wg_address)
        self.os = Instruments.connect_os(os_address)
        
        wave = self.wave_select.currentText()
        freq = float(self.freq_input.text())
        ampl = float(self.ampl_input.text())
        offset = float(self.offset_input.text())
        
        Instruments.set_wave(self.wg, wave, freq, ampl, offset)
        
        self.status.setText("Connected")
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.acquire_btn.setEnabled(True)
    
    def disconnect(self):
        self.wg.close()
        self.os.close()
        self.status.setText("Disconnected")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.acquire_btn.setEnabled(False)
    
    def acquire(self):
        times, voltages = Instruments.get_data(self.os)
        self.plot.show_plot(times, voltages)
        self.status.setText("Data shown")


app = QApplication(sys.argv)
main = MainWindow()
main.window.show()
sys.exit(app.exec_())