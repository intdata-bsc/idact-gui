""" One of the helper widgets.

    See: :class:`.PopUpWindow`, :class:`.ShowLogsWindow`,
    :class:`.YesOrNoWindow`, :class:`.ProgramInfoWindow`,
    :class:`.EditNativeArgumentsWindow`, :class:`.ShowJobsWindow`
"""
from PyQt5.QtWidgets import QWidget
from gui.helpers.ui_loader import UiLoader


class HelpWindow(QWidget):
    """ Shows the help info.
    """
    def __init__(self):
        super().__init__()
        self.ui = UiLoader.load_ui_from_file('help.ui', self)
