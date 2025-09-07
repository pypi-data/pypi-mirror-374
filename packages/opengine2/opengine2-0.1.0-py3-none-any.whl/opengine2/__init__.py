from PySide6 import QtWidgets
import logging
import sys

from . import gui, kbds

def exec_():
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    app = QtWidgets.QApplication(["opengine2"])

    widget = gui.Opengine2GUI()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
