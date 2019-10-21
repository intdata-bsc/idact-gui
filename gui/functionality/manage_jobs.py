import os
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTableWidgetItem

from idact.detail.slurm.run_scancel import run_scancel
from idact.detail.slurm.run_squeue import run_squeue
from idact import show_cluster, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.worker import Worker


class ManageJobs(QWidget):
    def __init__(self, data_provider, parent=None):
        QWidget.__init__(self, parent=parent)
        self.parent = parent
        self.data_provider = data_provider

        self.show_jobs_window = ShowJobsWindow()
        self.popup_window = PopUpWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/manage-jobs.ui'))
        
        self.ui.show_jobs_button.clicked.connect(self.concurrent_show_jobs)
        self.ui.refresh_button.clicked.connect(self.concurrent_show_jobs)
        self.ui.cancel_job_button.clicked.connect(self.concurrent_cancel_job)
        self.ui.jobs_table.itemSelectionChanged.connect(
            lambda: self.ui.cancel_job_button.setEnabled(
                len(self.ui.jobs_table.selectedIndexes()) > 0))

        self.ui.cancel_job_button.setEnabled(False)

        self.current_cluster = ''
        self.cluster_names = self.data_provider.get_cluster_names()

        if len(self.cluster_names) > 0:
            self.current_cluster = self.cluster_names[0]
        else:
            self.current_cluster = ''

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_list_modification)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_list_modification)
        self.ui.cluster_names_box.activated[str].connect(self.item_pressed)
        self.ui.cluster_names_box.addItems(self.cluster_names)

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)

    def concurrent_show_jobs(self):
        self.ui.show_jobs_button.setEnabled(False)
        self.ui.refresh_button.setEnabled(False)

        worker = Worker(self.show_jobs)
        worker.signals.result.connect(self.handle_complete_show_jobs)
        worker.signals.error.connect(self.handle_error_show_jobs)
        self.parent.threadpool.start(worker)

    def handle_complete_show_jobs(self, jobs):
        self.ui.show_jobs_button.setEnabled(True)
        self.ui.refresh_button.setEnabled(True)

        counter = len(jobs)
        self.ui.jobs_table.setRowCount(counter)

        for i in range(counter):
            self.ui.jobs_table.setItem(i, 0, QTableWidgetItem(str(jobs[i].job_id)))
            self.ui.jobs_table.setItem(i, 1, QTableWidgetItem(str(jobs[i].end_time)))
            self.ui.jobs_table.setItem(i, 2, QTableWidgetItem(str(jobs[i].node_count)))
            self.ui.jobs_table.setItem(
                i, 3, QTableWidgetItem(','.join(jobs[i].node_list)) if jobs[i].node_list else '')
            self.ui.jobs_table.setItem(
                i, 4, QTableWidgetItem(str(jobs[i].reason if jobs[i].reason else '')))
            self.ui.jobs_table.setItem(i, 5, QTableWidgetItem(jobs[i].state))

    def handle_error_show_jobs(self, exception):
        self.ui.show_jobs_button.setEnabled(True)
        self.ui.refresh_button.setEnabled(True)

        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while listing jobs", WindowType.error)

    def show_jobs(self):
        load_environment()
        cluster_name = self.current_cluster
        cluster = show_cluster(name=cluster_name)
        node = cluster.get_access_node()
        jobs = list(run_squeue(node).values())
        return jobs

    def concurrent_cancel_job(self):
        self.ui.cancel_job_button.setEnabled(False)
        self.ui.cancel_job_button.setEnabled(False)

        worker = Worker(self.cancel_job)
        worker.signals.result.connect(self.handle_complete_cancel_job)
        worker.signals.error.connect(self.handle_error_cancel_job)
        self.parent.threadpool.start(worker)

    def handle_complete_cancel_job(self):
        self.ui.cancel_job_button.setEnabled(True)
        self.popup_window.show_message("Cancel command has been successfully executed\nRefreshing table may be needed",
                                       WindowType.success)

    def handle_error_cancel_job(self, exception):
        self.ui.cancel_job_button.setEnabled(True)

        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while cancelling job", WindowType.error)

        self.ui.cancel_job_button.setEnabled(True)

    def cancel_job(self):
        self.ui.cancel_job_button.setEnabled(False)
        load_environment()
        cluster_name = self.current_cluster
        self.saver.save(self.parameters)

        indexes = self.ui.jobs_table.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            job_id = int(self.ui.jobs_table.item(index.row(), 0).text())
            cluster = show_cluster(name=cluster_name)
            node = cluster.get_access_node()
            run_scancel(job_id, node)

        self.ui.cancel_job_button.setEnabled(True)

    def handle_cluster_list_modification(self):
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)

    def item_pressed(self, item_pressed):
        self.current_cluster = item_pressed


class ShowJobsWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.setWindowTitle('Jobs')

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/show-jobs.ui'))

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)
