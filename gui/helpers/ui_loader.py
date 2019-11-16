import os

from PyQt5 import uic


class UiLoader:
    @staticmethod
    def load_ui_from_file(file_name, form):
        ui_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_path, '../widgets_templates/' + file_name)
        return uic.loadUi(ui_path, form)
