from PyQt5 import QtWidgets
from app.obsx_gui import ObscuronGUI
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ObscuronGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

