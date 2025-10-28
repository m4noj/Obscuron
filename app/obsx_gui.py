import sys, os, traceback, uuid
from PyQt5 import QtWidgets, QtGui, QtCore
from app.crypto_engine import encrypt_file, decrypt_file

class ObscuronGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Obscuron Vault (Beta)")
        self.setGeometry(550,300,800,500)
        # self.setMinimumSize(800, 400)
        self.setWindowIcon(QtGui.QIcon("assets/logo.png") if os.path.exists("assets/logo.png") else QtGui.QIcon())
        self.setStyleSheet("background-color:#101820; color:#E6EEF6; font-family:Courier New; font-size:12pt;")
        
        with open("app/styles/organic-dark.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Header
        header = QtWidgets.QLabel("🛡️ Obscuron Vault (Beta)")
        header.setFont(QtGui.QFont("Courier New", 16, QtGui.QFont.Bold))
        layout.addWidget(header, alignment=QtCore.Qt.AlignCenter)
        
        # File selection
        file_layout = QtWidgets.QHBoxLayout()
        self.file_edit = QtWidgets.QLineEdit()
        self.file_edit.setPlaceholderText("Select file to encrypt/decrypt...")
        file_btn = QtWidgets.QPushButton("Browse")
        file_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(file_btn)
        layout.addLayout(file_layout)

        # Mode selection & password
        mode_layout = QtWidgets.QHBoxLayout()
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Encrypt", "Decrypt"])
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter strong password")
        mode_layout.addWidget(QtWidgets.QLabel("Mode"))
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        mode_layout.addWidget(QtWidgets.QLabel("Password"))
        mode_layout.addWidget(self.password_edit)
        layout.addLayout(mode_layout)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.clicked.connect(self.run_action)
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        # Progress bar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Status / log
        self.log_area = QtWidgets.QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(140)
        self.log_area.setStyleSheet("background-color:#1A1A1D; color:#E6EEF6; font-family:Courier New; font-size:11pt;")
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def browse_file(self):
        options = QtWidgets.QFileDialog.Options()
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
        if fname:
            self.file_edit.setText(fname)

    def log(self, *msgs):
        self.log_area.append(" ".join(str(m) for m in msgs))
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def run_action(self):
        path = self.file_edit.text().strip()
        pwd = self.password_edit.text()
        mode = self.mode_combo.currentText()
        if not path or not os.path.exists(path):
            QtWidgets.QMessageBox.warning(self, "Input missing", "Please select a valid file.")
            return
        if not pwd:
            QtWidgets.QMessageBox.warning(self, "Missing password", "Please enter a password.")
            return

        try:
            with open(path, "rb") as f:
                data = f.read()
            self.log(f"MODE: {mode} | FILE: {os.path.basename(path)} | SIZE: {len(data)} bytes\n")
            self.progress.setValue(20)

            if mode == "Encrypt":
                enc_bytes = encrypt_file(data, pwd, os.path.basename(path))
                self.progress.setValue(60)
                # Random filename for download
                suggested = uuid.uuid4().hex + ".obsx"
                save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save encrypted file as", suggested, "OBSCURON Files (*.obsx);;All Files (*)")
                if save_path:
                    with open(save_path, "wb") as out:
                        out.write(enc_bytes)
                    self.progress.setValue(100)
                    self.log("[ENCRYPTED] :\n", save_path)
                    self.log("----------------------\n")

            else:  # Decrypt
                plain, orig_name, ext = decrypt_file(data, pwd)
                self.progress.setValue(60)
                save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save decrypted file as", orig_name, f"*{ext};;All Files (*)")
                if save_path:
                    with open(save_path, "wb") as out:
                        out.write(plain)
                    self.progress.setValue(100)
                    self.log("[DECYPTED] :\n", save_path)
                    self.log("----------------------\n")

        except Exception as e:
            self.progress.setValue(0)
            self.log("❌ Error:", str(e))
            self.log(traceback.format_exc())

    def clear_all(self):
        self.file_edit.clear()
        self.password_edit.clear()
        self.log_area.clear()
        self.progress.setValue(0)
