import os
from enum import Enum
from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox
from PyQt5.QtCore import QThreadPool
from PyQt5 import uic
from idact.detail.environment.environment_provider import EnvironmentProvider
from idact import load_environment

from gui.helpers.native_saver import NativeArgsSaver
from gui.helpers.saver import ParameterSaver

ui_path = os.path.dirname(os.path.abspath(__file__))
Ui_MainWindow, _QtBaseClass = uic.loadUiType(os.path.join(ui_path, '../widgets_templates/gui.ui'))
Ui_AddNativeArgument, _QtBaseClass = uic.loadUiType(os.path.join(ui_path, '../widgets_templates/add-native.ui'))
Ui_RemoveNativeArgument, _QtBaseClass = uic.loadUiType(os.path.join(ui_path, '../widgets_templates/remove-native.ui'))
Ui_ShowNativeArgument, _QtBaseClass = uic.loadUiType(os.path.join(ui_path, '../widgets_templates/show-native.ui'))
Ui_ShowJobs, _QtBaseClass = uic.loadUiType(os.path.join(ui_path, '../widgets_templates/show-jobs.ui'))


class IdactApp(QMainWindow):
    def __init__(self):
        super(IdactApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.saver = ParameterSaver()
        self.native_args_saver = NativeArgsSaver()
        self.add_argument_window = AddArgumentWindow()
        self.remove_argument_window = RemoveArgumentWindow()
        self.show_native_arguments_window = ShowNativeArgumentsWindow()
        self.show_jobs_window = ShowJobsWindow()
        self.parameters = self.saver.get_map()
        self.popup_window = PopUpWindow()
        self.actions_file_name = None
        self.threadpool = QThreadPool()
        self.cluster_names = []
        self.current_cluster = ''
        self.load_cluster_names()

    def load_cluster_names(self):
        load_environment()
        self.cluster_names = list(EnvironmentProvider().environment.clusters.keys())


class AddArgumentWindow(QMainWindow):
    def __init__(self):
        super(AddArgumentWindow, self).__init__()
        self.ui = Ui_AddNativeArgument()
        self.ui.setupUi(self)


class RemoveArgumentWindow(QMainWindow):
    def __init__(self):
        super(RemoveArgumentWindow, self).__init__()
        self.ui = Ui_RemoveNativeArgument()
        self.ui.setupUi(self)


class ShowNativeArgumentsWindow(QMainWindow):
    def __init__(self):
        super(ShowNativeArgumentsWindow, self).__init__()
        self.ui = Ui_ShowNativeArgument()
        self.ui.setupUi(self)


class ShowJobsWindow(QMainWindow):
    def __init__(self):
        super(ShowJobsWindow, self).__init__()
        self.ui = Ui_ShowJobs()
        self.ui.setupUi(self)


class PopUpWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.box = QMessageBox(self)
        self.box.addButton(QMessageBox.Ok)
        self.box.setDefaultButton(QMessageBox.Ok)

    def show_message(self, message, window_type):
        if window_type == WindowType.success:
            self.box.setWindowTitle("Success")
            self.box.setIcon(QMessageBox.Information)
        elif window_type == WindowType.error:
            self.box.setWindowTitle("Error")
            self.box.setIcon(QMessageBox.Critical)
        else:
            self.box.setIcon(QMessageBox.NoIcon)

        self.box.setText(message)
        ret = self.box.exec_()
        if ret == QMessageBox.Ok:
            return


class WindowType(Enum):
    success = 1
    error = 2
