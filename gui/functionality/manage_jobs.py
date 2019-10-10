from PyQt5.QtWidgets import QTableWidgetItem
from idact import show_cluster, load_environment
from idact.detail.slurm.run_scancel import run_scancel
from idact.detail.slurm.run_squeue import run_squeue

from gui.functionality.idact_app import IdactApp, WindowType
from gui.helpers.decorators import addToClass
from gui.helpers.worker import Worker


class ManageJobs:
    def __init__(self, idact_app):
        self.idact_app = idact_app
        idact_app.ui.cluster_name_jobs_edit.setText(idact_app.parameters['manage_jobs_arguments']['cluster_name'])
        idact_app.ui.show_jobs_button.clicked.connect(idact_app.concurrent_show_jobs)
        idact_app.ui.cancel_job_button.clicked.connect(idact_app.concurrent_cancel_job)

    @addToClass(IdactApp)
    def concurrent_show_jobs(self):
        worker = Worker(self.show_jobs)
        worker.signals.result.connect(self.handle_complete_show_jobs)
        worker.signals.error.connect(self.handle_error_show_jobs)
        self.threadpool.start(worker)

    @addToClass(IdactApp)
    def handle_complete_show_jobs(self, jobs):
        counter = len(jobs)
        self.show_jobs_window.ui.jobs_table.setRowCount(counter)

        for i in range(counter):
            self.show_jobs_window.ui.jobs_table.setItem(i, 0, QTableWidgetItem(str(jobs[i].job_id)))
            self.show_jobs_window.ui.jobs_table.setItem(i, 1, QTableWidgetItem(str(jobs[i].end_time)))
            self.show_jobs_window.ui.jobs_table.setItem(i, 2, QTableWidgetItem(str(jobs[i].node_count)))
            self.show_jobs_window.ui.jobs_table.setItem(
                i, 3, QTableWidgetItem(','.join(jobs[i].node_list)) if jobs[i].node_list else '')
            self.show_jobs_window.ui.jobs_table.setItem(
                i, 4, QTableWidgetItem(str(jobs[i].reason if jobs[i].reason else '')))
            self.show_jobs_window.ui.jobs_table.setItem(i, 5, QTableWidgetItem(jobs[i].state))

        self.show_jobs_window.show()

    @addToClass(IdactApp)
    def handle_error_show_jobs(self, exception):
        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while listing jobs", WindowType.error)

        self.ui.show_jobs_button.setEnabled(True)

    @addToClass(IdactApp)
    def show_jobs(self):
        self.ui.show_jobs_button.setEnabled(False)
        load_environment()
        cluster_name = self.ui.cluster_name_jobs_edit.text()
        self.parameters['manage_jobs_arguments']['cluster_name'] = cluster_name
        cluster = show_cluster(name=cluster_name)
        node = cluster.get_access_node()
        jobs = list(run_squeue(node).values())
        self.ui.show_jobs_button.setEnabled(True)
        return jobs

    @addToClass(IdactApp)
    def concurrent_cancel_job(self):
        worker = Worker(self.cancel_job)
        worker.signals.result.connect(self.handle_complete_cancel_job)
        worker.signals.error.connect(self.handle_error_cancel_job)
        self.threadpool.start(worker)

    @addToClass(IdactApp)
    def handle_complete_cancel_job(self):
        self.popup_window.show_message("Cancel command has been successfully executed", WindowType.success)

    @addToClass(IdactApp)
    def handle_error_cancel_job(self, exception):
        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occured while cancelling job", WindowType.error)

        self.ui.cancel_job_button.setEnabled(True)

    @addToClass(IdactApp)
    def cancel_job(self):
        self.ui.cancel_job_button.setEnabled(False)
        load_environment()
        cluster_name = self.ui.cluster_name_jobs_edit.text()
        self.parameters['manage_jobs_arguments']['cluster_name'] = cluster_name
        self.saver.save(self.parameters)
        job_id = int(self.ui.job_id_edit.text())
        cluster = show_cluster(name=cluster_name)
        node = cluster.get_access_node()
        run_scancel(job_id, node)
        self.ui.cancel_job_button.setEnabled(True)
