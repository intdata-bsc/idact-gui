""" One of the helper widgets.

    See: :class:`.ProgramInfoWindow`, :class:`.PopUpWindow`,
    :class:`.YesOrNoWindow`, :class:`.ShowJobsWindow`,
    :class:`.EditNativeArgumentsWindow`, :class:`.HelpWindow`
"""
from PyQt5.QtWidgets import QWidget

from gui.helpers.ui_loader import UiLoader


class ShowLogsWindow(QWidget):
    """ Helper widget window for displaying logs.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('logs.ui', self)

    def write(self, text):
        """ Writes the text to the window.

            :param text: Log text to be shown.
        """
        self.ui.logs_browser.append(text)
