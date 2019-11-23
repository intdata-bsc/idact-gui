""" One of the helpers for the gui application.

    Similar modules: class:`.DataProvider`, :class:`.ParameterSaver`,
    :class:`.NativeArgsSaver`, :class:`.UiLoader`, :class:`.ConfigurationProvider`
"""
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    """ 
        :attr:`.finished`: Signal used to inform about normal finish of the worker job.
        :attr:`.error`: Signal used to inform about finish with error of the worker job.
                        The object parametr is the Error instance.
        :attr:`.result`: Signal used to inform about the result of the worker job.
                         The object parametr is the result of the job.
    """
    finished = pyqtSignal()
    error = pyqtSignal(object)
    result = pyqtSignal(object)


class Worker(QRunnable):
    """ Runs the task in thread and signals about its finish.
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """ Runs the task and signals about trown error or given result
        by emiting the WorkerSignals.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit(e)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
