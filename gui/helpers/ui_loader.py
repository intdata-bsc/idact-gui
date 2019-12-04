""" One of the helpers for the gui application.

    Similar modules: class:`.DataProvider`, :class:`.ParameterSaver`,
    :class:`.NativeArgsSaver`, :class:`.Worker`, :class:`.ConfigurationProvider`
"""
import os

from PyQt5 import uic


class UiLoader:
    """ Loads the ui for the widget.
    """

    @staticmethod
    def load_ui_from_file(file_name, form):
        """ Loads the ui for the widget.

            :param file_name: Name of ui file to be loaded.
            :param form: Instance of the widget.
        """
        ui_path = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(ui_path, os.pardir, 'widgets_templates', file_name)
        return uic.loadUi(ui_path, form)
