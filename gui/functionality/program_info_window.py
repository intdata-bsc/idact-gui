""" One of the helper widgets.

    See: :class:`.PopUpWindow`, :class:`.ShowLogsWindow`,
    :class:`.YesOrNoWindow`, :class:`.ShowJobsWindow`,
    :class:`.EditNativeArgumentsWindow`
"""
from PyQt5.QtWidgets import QWidget
from gui.helpers.ui_loader import UiLoader


class ProgramInfoWindow(QWidget):
    """ Shows the info about idact-gui app.
    """
    def __init__(self):
        super().__init__()
        self.ui = UiLoader.load_ui_from_file('about.ui', self)
