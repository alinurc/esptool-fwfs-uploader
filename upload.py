import sys, os, esptool, urllib.request, serial.tools.list_ports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from pathlib import Path

class ESP32Uploader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.serial_ports = list(serial.tools.list_ports.comports())
        self.serial_ports_combo = QtWidgets.QComboBox()
        for port in self.serial_ports:
            self.serial_ports_combo.addItem(port.device)
        self.serial_ports_combo.currentIndexChanged.connect(self.serial_port_changed)
        if(len(self.serial_ports) == 1):
            self.selected_port = str(self.serial_ports[0])
            self.selected_port = self.selected_port[:self.selected_port.index(" ")]


        self.setWindowTitle("ESP32-based Product Firmware Uploader")
        self.setGeometry(100, 100, 400, 200)
        icon = QtGui.QIcon("icon.ico")
        self.setWindowIcon(icon)
        tray_icon = QtWidgets.QSystemTrayIcon()
        tray_icon.setIcon(icon)

        self.firmware_path = QtWidgets.QLineEdit()
        self.firmware_path.setReadOnly(True)

        self.select_firmware_button = QtWidgets.QPushButton("Select firmware")
        self.select_firmware_button.clicked.connect(self.select_firmware)
        self.select_firmware_button.setGeometry(50, 50, 100, 100)
        self.select_firmware_button.saveGeometry()

        self.upload_firmware_button = QtWidgets.QPushButton("Upload firmware")
        self.upload_firmware_button.clicked.connect(self.upload_firmware)

        self.filesystem_path = QtWidgets.QLineEdit()
        self.filesystem_path.setReadOnly(True)

        self.select_filesystem_button = QtWidgets.QPushButton("Select filesystem")
        self.select_filesystem_button.clicked.connect(self.select_filesystem)

        self.upload_filesystem_button = QtWidgets.QPushButton("Upload filesystem")
        self.upload_filesystem_button.clicked.connect(self.upload_filesystem)

        self.download_latest_button = QtWidgets.QPushButton("Download latest")
        self.download_latest_button.clicked.connect(self.download_latest)

        firmwareLayout = QtWidgets.QHBoxLayout()
        firmwareLayout.addWidget(self.select_firmware_button)
        firmwareLayout.addWidget(self.upload_firmware_button)

        filesystemLayout = QtWidgets.QHBoxLayout()
        filesystemLayout.addWidget(self.select_filesystem_button)
        filesystemLayout.addWidget(self.upload_filesystem_button)

        miscLayout = QtWidgets.QHBoxLayout()
        miscLayout.addWidget(self.serial_ports_combo)
        miscLayout.addWidget(self.download_latest_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.firmware_path)
        layout.addLayout(firmwareLayout)
        layout.addWidget(self.filesystem_path)
        layout.addLayout(filesystemLayout)
        layout.addLayout(miscLayout)

    def select_firmware(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select firmware", "", "Binary Files (*.bin);;All Files (*)", options=options)
        if file_name:
            self.firmware_path.setText(file_name)
    
    def select_filesystem(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select filesystem", "", "Binary Files (*.bin);;All Files (*)", options=options)
        if file_name:
            self.filesystem_path.setText(file_name)

    def upload_firmware(self):
        firmware_path = self.firmware_path.text()
        if firmware_path:
            try:
                esptool.main(["--chip", "esp32", "--port", self.selected_port, "--baud", "115200", "--before", "default_reset", "--after", "hard_reset", "write_flash", "-z", "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "detect","0x1000", str(Path.home() / "Downloads/product/first-bootloader.bin"), "0x8000", str(Path.home() / "Downloads/product/partitions.bin"), "0xe000", str(Path.home() / "Downloads/product/second-bootloader.bin"), "0x10000", firmware_path])
            except:
                QtWidgets.QMessageBox.critical(None, "Error", "An error occured while uploading. Please try switching the chip to download mode.")
            else:
                QtWidgets.QMessageBox.information(None, "Done", "Firmware uploaded successfully.")

    def upload_filesystem(self):
        filesystem_path = self.filesystem_path.text()
        if filesystem_path:
            try:
                esptool.main(["--chip", "esp32", "--port", self.selected_port, "--baud", "115200", "--before", "default_reset", "--after", "hard_reset", "write_flash", "-fs", "8MB", "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "detect","0x290000", filesystem_path])
            except:
                QtWidgets.QMessageBox.critical(None, "Error", "An error occured while uploading. Please try switching the chip to download mode.")
            else:
                QtWidgets.QMessageBox.information(None, "Done", "Filesystem uploaded successfully.")

    def serial_port_changed(self, index):
        self.selected_port = str(self.serial_ports[index])
        self.selected_port = self.selected_port[:self.selected_port.index(" ")]
        print(self.selected_port)

    def download_latest(self):
        if not os.path.exists(Path.home() / "Downloads/product"):
            os.makedirs(Path.home() / "Downloads/product", exist_ok=True)
        try:
            urllib.request.urlretrieve("https://url.to/filesystem.bin", str(Path.home() / "Downloads/product/esp32/spiffs.bin"))
        except:
            QtWidgets.QMessageBox.critical(None, "Error", "Couldn't download the filesystem.")
        else:
            QtWidgets.QMessageBox.information(None, "Done", "Filesystem downloaded. Check your Downloads/product folder.")
        try:
            urllib.request.urlretrieve("https://url.to/firmware.bin", str(Path.home() / "Downloads/product/firmware.bin"))
        except:
            QtWidgets.QMessageBox.critical(None, "Error", "Couldn't download the firmware.")
        else:
            QtWidgets.QMessageBox.information(None, "Done", "Firmware downloaded. Check your Downloads folder.")
        try:
            urllib.request.urlretrieve("https://url.to/first-bootloader.bin", str(Path.home() / "Downloads/product/first-bootloader.bin"))
        except:
            QtWidgets.QMessageBox.critical(None, "Error", "Couldn't download the first stage bootloader.")
        else:
            QtWidgets.QMessageBox.information(None, "Done", "First stage bootloader downloaded. Check your Downloads folder.")
        try:
            urllib.request.urlretrieve("https://url.to/partitions.bin", str(Path.home() / "Downloads/product/partitions.bin"))
        except:
            QtWidgets.QMessageBox.critical(None, "Error", "Couldn't download the partition table.")
        else:
            QtWidgets.QMessageBox.information(None, "Done", "Partition table downloaded. Check your Downloads folder.")
        try:
            urllib.request.urlretrieve("https://url.to/second-bootloader.bin", str(Path.home() / "Downloads/product/second-bootloader.bin"))
        except:
            QtWidgets.QMessageBox.critical(None, "Error", "Couldn't download the second stage bootloader.")
        else:
            QtWidgets.QMessageBox.information(None, "Done", "Second stage bootloader downloaded. Check your Downloads folder.")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = ESP32Uploader()
    gui.show()
    sys.exit(app.exec_())