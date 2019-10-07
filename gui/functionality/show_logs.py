from gui.functionality.idact_app import IdactApp
from gui.helpers.decorators import addToClass


class ShowLogs:
    def __init__(self, idact_app):
        idact_app.ui.show_logs_button.clicked.connect(idact_app.open_show_logs)

    @addToClass(IdactApp)
    def open_show_logs(self):
        self.show_logs_window.show()
