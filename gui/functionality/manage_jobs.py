""" One of the widgets that main window composes of.

    See :class:`.MainWindow`
    Similar modules: class:`.AddCluster`, :class:`.RemoveCluster`,
    :class:`.IdactNotebook`, :class:`.AdjustTimeouts`
    Helpers: class:`.ShowJobsWindow`
"""
from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from idact.detail.slurm.run_scancel import run_scancel
from idact.detail.slurm.run_squeue import run_squeue
from idact import show_cluster, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker
from gui.helpers.custom_exceptions import NoClustersError


class ManageJobs(QWidget):
    """ Module of GUI that is responsible for allowing the management of jobs
    in the slurm queue.
    """

    def __init__(self, data_provider, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('manage-jobs.ui', self)

        self.parent = parent
        self.data_provider = data_provider
        self.cluster_names = self.data_provider.get_cluster_names()
        self.popup_window = PopUpWindow()
        self.cluster = None

        self.ui.show_jobs_button.clicked.connect(self.concurrent_show_jobs)
        self.ui.refresh_button.clicked.connect(self.concurrent_show_jobs)
        self.ui.deploy_button.clicked.connect(self.concurrent_deploy_notebook)
        self.ui.cancel_job_button.clicked.connect(self.concurrent_cancel_job)

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_list_modification)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_list_modification)
        self.ui.cluster_names_box.addItems(self.cluster_names)

        self.ui.deploy_button.setEnabled(False)
        self.ui.cancel_job_button.setEnabled(False)
        self.ui.jobs_table.itemSelectionChanged.connect(
            lambda: self.ui.cancel_job_button.setEnabled(
                len(self.ui.jobs_table.selectedIndexes()) > 0))

    def change_buttons_to_disabled_or_not(self):
        any_item_selected = len(self.ui.jobs_table.selectedIndexes()) > 0
        self.ui.deploy_button.setEnabled(any_item_selected)
        self.ui.cancel_job_button.setEnabled(any_item_selected)

    def concurrent_show_jobs(self):
        """ Setups the worker that allows to run the show_jobs functionality
        in the parallel thread.
        """
        self.ui.show_jobs_button.setEnabled(False)
        self.ui.refresh_button.setEnabled(False)

        worker = Worker(self.show_jobs)
        worker.signals.result.connect(self.handle_complete_show_jobs)
        worker.signals.error.connect(self.handle_error_show_jobs)
        self.parent.threadpool.start(worker)

    def handle_complete_show_jobs(self, jobs):
        """ Handles the completion of show jobs function.
        """
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
        """ Handles the error thrown while showing jobs.

            :param exception: Instance of the exception.
        """
        self.ui.show_jobs_button.setEnabled(True)
        self.ui.refresh_button.setEnabled(True)

        if isinstance(exception, NoClustersError):
            self.popup_window.show_message("There are no added clusters", WindowType.error)
        elif isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while listing jobs", WindowType.error, exception)

    def show_jobs(self):
        """ Main function responsible for showing jobs.
        """
        load_environment()
        cluster_name = str(self.ui.cluster_names_box.currentText())
        if not cluster_name:
            raise NoClustersError()
        self.cluster = show_cluster(name=cluster_name)
        node = self.cluster.get_access_node()
        jobs = list(run_squeue(node).values())
        return jobs

    def concurrent_deploy_notebook(self):
        self.ui.deploy_button.setEnabled(False)

        worker = Worker(self.deploy_notebook)
        worker.signals.result.connect(self.handle_complete_deploy_notebook)
        worker.signals.error.connect(self.handle_error_deploy_notebook)
        self.parent.threadpool.start(worker)

    def handle_complete_deploy_notebook(self):
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("Notebook has been successfully deployed",
                                       WindowType.success)

    def handle_error_deploy_notebook(self, exception):
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("An error occurred while deploying notebook", WindowType.error)
        self.ui.deploy_button.setEnabled(True)

    def deploy_notebook(self):
        pass

    def concurrent_cancel_job(self):
        """ Setups the worker that allows to run the cancel_job functionality
        in the parallel thread.
        """
        self.ui.cancel_job_button.setEnabled(False)

        worker = Worker(self.cancel_job)
        worker.signals.result.connect(self.handle_complete_cancel_job)
        worker.signals.error.connect(self.handle_error_cancel_job)
        self.parent.threadpool.start(worker)

    def handle_complete_cancel_job(self):
        """ Handles the completion of cancel job function.
        """
        self.ui.cancel_job_button.setEnabled(True)
        self.popup_window.show_message("Cancel command has been successfully executed", WindowType.success)
        self.concurrent_show_jobs()

    def handle_error_cancel_job(self, exception):
        """ Handles the error thrown while cancelling job.

            :param exception: Instance of the exception.
        """
        self.ui.cancel_job_button.setEnabled(True)

        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while cancelling job", WindowType.error)

        self.ui.cancel_job_button.setEnabled(True)

    def cancel_job(self):
        """ Main function responsible for cancelling a job.
        """
        self.ui.cancel_job_button.setEnabled(False)

        load_environment()
        node = self.cluster.get_access_node()

        indexes = self.ui.jobs_table.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            job_id = int(self.ui.jobs_table.item(index.row(), 0).text())
            run_scancel(job_id, node)

    def handle_cluster_list_modification(self):
        """ Handles the modification of the clusters list.
        """
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)
