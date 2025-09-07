import logging
import time
import random
import subprocess
from PySide6 import QtCore, QtWidgets
from .kbds import Kbd, Kbdlist

_logger = logging.getLogger(__name__)
_prog_name = "opengine2"

class KbdlistModel(QtCore.QAbstractListModel):
    def __init__(self, kbdlist):
        super().__init__()
        self.kbdlist = kbdlist.kbds

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.kbdlist[index.row()].name
        elif role == QtCore.Qt.ToolTipRole:
            return self.kbdlist[index.row()].sortkey
        elif role == 'item':
            return self.kbdlist[index.row()]

    def rowCount(self, index):
        return len(self.kbdlist)

    def index_from_sortkey(self, sortkey):
        return next(n for n, x in enumerate(self.kbdlist) if x.sortkey == sortkey)

class Opengine2InputBox(QtWidgets.QLineEdit):
    newchar = QtCore.Signal(str, str, str,
                            name="newchar",
                            arguments=["char", "charname", "charlist"])
    newkey = QtCore.Signal(str, int, float, float,
                           name="newkey",
                           arguments=["key", "option", "timediff", "maxdelay"])

    def __init__(self, parent):
        super().__init__(parent)
        self.last_pressed_time = time.time()
        self.last_pressed_key = ''
        self.idx = 0
        self.repeat_press_timeout = 1.000 # seconds
        self.kbd = None

    def keyPressEvent(self, event):
        this_pressed_key = event.text()
        this_pressed_time = time.time()
        if (event.text() == ''
            or self.kbd is None
            or self.kbd.getchar(this_pressed_key, self.idx) is None
            or event.key() in {QtCore.Qt.Key.Key_Backspace,
                               QtCore.Qt.Key.Key_Delete}):
            super().keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.clearFocus()
        else:
            time_delta = this_pressed_time - self.last_pressed_time
            if (this_pressed_key == self.last_pressed_key
                and time_delta < self.repeat_press_timeout):
                self.idx += 1
                self.backspace()
            else:
                self.idx = 0
            self.newkey.emit(this_pressed_key, self.idx, time_delta, self.repeat_press_timeout)
            this_char = self.kbd.getchar(this_pressed_key, self.idx)
            self.newchar.emit(
                this_char,
                self.kbd.getlabel(this_pressed_key, self.idx),
                self.kbd.getcharlist(this_pressed_key))
            self.insert(this_char)
        self.last_pressed_key = this_pressed_key
        self.last_pressed_time = this_pressed_time

    @QtCore.Slot()
    def set_kbd(self, kbd):
        self.kbd = kbd

class Opengine2Widget(QtWidgets.QWidget):
    def __init__(self, main_window, cfg):
        super().__init__(main_window)

        self.kbdlist = Kbdlist.find_keyboards(cfg)
        self.kbdlist_model = KbdlistModel(self.kbdlist)
        default_keyboard = self.kbdlist_model.index_from_sortkey(cfg.default_kbd)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setColumnStretch(0, 1) # Keyboard list takes up 1/3
        self.layout.setColumnStretch(1, 2) # Display takes up 2/3
        self.layout.setRowStretch(1, 4) # And takes up as much vertical space as possible

        # Result display
        self.char_disp = QtWidgets.QLabel("...",
                                          alignment=QtCore.Qt.AlignCenter)
        self.char_disp.setStyleSheet("""font-size:40pt;""")
        self.char_disp.setMinimumHeight(200)
        self.char_disp.setMinimumWidth(300)
        self.label_text = QtWidgets.QLabel("Start typing in the text box below",
                                           alignment=QtCore.Qt.AlignCenter)
        self.alternative_text = QtWidgets.QLabel(
            "Alternatives appear when a key is pressed repeatedly",
            alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.char_disp, 0, 1, 2, 1)
        self.layout.addWidget(self.label_text, 2, 1)
        self.layout.addWidget(self.alternative_text, 3, 1)

        # buttons
        self.quit_copy_button = QtWidgets.QPushButton("&Copy && Quit")
        self.quit_button = QtWidgets.QPushButton("&Quit")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.quit_copy_button, stretch=0)
        button_layout.addWidget(self.quit_button, stretch=0)
        self.layout.addLayout(button_layout, 5, 0, 1, 2)

        self.quit_button.clicked.connect(self.parent().close)
        self.quit_copy_button.clicked.connect(self.copy_and_quit)

        # list of keyboards
        kbdlist_label = QtWidgets.QLabel("Keyboards")
        self.layout.addWidget(kbdlist_label, 0, 0)
        self.kbdlist_widget = QtWidgets.QListView(self)
        self.layout.addWidget(self.kbdlist_widget, 1, 0, 3, 1)
        self.kbdlist_widget.setModel(self.kbdlist_model)
        self.kbdlist_widget.setCurrentIndex(
            self.kbdlist_model.index(default_keyboard, 0))
        self.kbdlist_widget.clicked.connect(self.kbdlist_item_clicked)

        # Input box
        self.input_box = Opengine2InputBox(self)
        self.input_box.set_kbd(self.kbdlist.kbds[default_keyboard])
        self.layout.addWidget(self.input_box, 4, 0, 1, 2)
        self.input_box.newkey.connect(self.new_key_typed)
        self.input_box.newchar.connect(self.new_char_typed)
        self.input_box.setFocus(QtCore.Qt.OtherFocusReason)

        # Global stuff
        self.parent().statusBar().showMessage("Ready")
        self.setWindowTitle(_prog_name)

    @QtCore.Slot()
    def kbdlist_item_clicked(self, event):
        name = event.model().data(event, QtCore.Qt.DisplayRole)
        kbd = event.model().data(event, 'item')
        self.input_box.set_kbd(kbd)
        self.parent().statusBar().showMessage(f"Keyboard {name} selected")

    @QtCore.Slot()
    def copy_and_quit(self, _):
        subprocess.run(['xclip', '-sel', 'c'], input=self.input_box.text(), text=True)
        self.parent().close()

    @QtCore.Slot()
    def new_char_typed(self, char, descr, charlist):
        self.char_disp.setText(char)
        self.label_text.setText(descr)
        self.alternative_text.setText(charlist)

    @QtCore.Slot()
    def new_key_typed(self, key, index, delay, maxdelay):
        self.parent().statusBar().showMessage(
            f"Character ⟨{key}⟩ #{index} pressed in {delay:5.3f} s",
            maxdelay * 1000)

class Opengine2GUI(QtWidgets.QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self.setCentralWidget(Opengine2Widget(self, cfg))
