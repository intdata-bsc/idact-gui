from PyQt5.QtWidgets import QWidget, QMessageBox


class YesOrNoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.box = QMessageBox(self)
        self.box.addButton(QMessageBox.Yes)
        self.box.addButton(QMessageBox.No)
        self.box.setDefaultButton(QMessageBox.No)
        self.box.setWindowTitle("Warning")
        self.box.setIcon(QMessageBox.Question)

    def show_message(self, message):
        self.box.setText(message)
        ret = self.box.exec_()
        if ret == QMessageBox.Yes:
            return True
        else:
            return False
