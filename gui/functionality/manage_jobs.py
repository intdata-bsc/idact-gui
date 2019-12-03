""" One of the widgets that main window composes of.

    See :class:`.MainWindow`
    Similar modules: class:`.AddCluster`, :class:`.RemoveCluster`,
    :class:`.IdactNotebook`, :class:`.AdjustTimeouts`
    Helpers: class:`.ShowJobsWindow`
"""
from contextlib import ExitStack

from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from idact import show_cluster, load_environment
from idact.detail.allocation.allocation_parameters import AllocationParameters
from idact.detail.config.client.client_cluster_config import ClusterConfigImpl
from idact.detail.deployment.cancel_local_on_exit import cancel_local_on_exit
from idact.detail.entry_point.fetch_port_info import fetch_port_info
from idact.detail.jupyter_app.sleep_until_allocation_ends import sleep_until_allocation_ends
from idact.detail.nodes.get_access_node import get_access_node
from idact.detail.nodes.node_impl import NodeImpl
from idact.detail.nodes.nodes_impl import NodesImpl
from idact.detail.slurm.run_scancel import run_scancel
from idact.detail.slurm.run_squeue import run_squeue
from idact.detail.slurm.slurm_allocation import SlurmAllocation
from idact.detail.slurm.squeue_result import SqueueResult

from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.custom_exceptions import NoClustersError
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker


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

        self.ui.jobs_table.itemSelectionChanged.connect(self.change_buttons_to_disabled_or_not)

        self.ui.deploy_button.setEnabled(False)
        self.ui.cancel_job_button.setEnabled(False)

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_list_modification)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_list_modification)
        self.ui.cluster_names_box.addItems(self.cluster_names)

    def change_buttons_to_disabled_or_not(self):
        items_selected = len(self.ui.jobs_table.selectedIndexes())
        self.ui.deploy_button.setEnabled(items_selected == 1)
        self.ui.cancel_job_button.setEnabled(items_selected >= 1)

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
            self.ui.jobs_table.setItem(i, 1, QTableWidgetItem(str(jobs[i].end_time.astimezone())))
            self.ui.jobs_table.setItem(i, 2, QTableWidgetItem(str(jobs[i].node_count)))
            self.ui.jobs_table.setItem(
                i, 3, (QTableWidgetItem(','.join(jobs[i].node_list) if jobs[i].node_list else '')))
            self.ui.jobs_table.setItem(
                i, 4, QTableWidgetItem(str(jobs[i].reason) if jobs[i].reason else ''))
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
        """ Setups the worker that allows to run the deploy_notebook functionality
        in the parallel thread.
        """
        self.ui.deploy_button.setEnabled(False)

        worker = Worker(self.deploy_notebook)
        worker.signals.result.connect(self.handle_complete_deploy_notebook)
        worker.signals.error.connect(self.handle_error_deploy_notebook)
        self.parent.threadpool.start(worker)

    def handle_complete_deploy_notebook(self):
        """ Handles the completion of deploy of the notebook.
        """
        self.popup_window.show_message("Notebook has been closed",
                                       WindowType.success)

    def handle_error_deploy_notebook(self, exception):
        """ Handles the error thrown while deploying notebook.

            :param exception: Instance of the exception.
        """
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("An error occurred while deploying notebook", WindowType.error, exception)

    def deploy_notebook(self):
        """ Main function responsible for deploying the notebook on the node.
        """
        indexes = self.ui.jobs_table.selectedIndexes()
        job_id = int(self.ui.jobs_table.item(indexes[0].row(), 0).text())

        with ExitStack() as stack:
            load_environment()

            config = self.cluster.config
            assert isinstance(config, ClusterConfigImpl)

            access_node = get_access_node(config=config)

            def run_squeue_task() -> SqueueResult:
                job_squeue = run_squeue(node=access_node)
                return job_squeue[job_id]

            job = run_squeue_task()

            node_count = job.node_count
            nodes_in_cluster = [NodeImpl(config=config) for _ in range(node_count)]

            port_info = fetch_port_info(job_id, config)
            [node_name, port] = port_info.split(" ")[0].split(":")

            nodes_in_cluster[0].make_allocated(host=node_name,
                                               port=int(port),
                                               cores=None,
                                               memory=None,
                                               allocated_until=job.end_time)

            entry_point_script_path = "~/.idact/entry_points"

            allocation = SlurmAllocation(
                job_id=job_id,
                access_node=access_node,
                nodes=nodes_in_cluster,
                entry_point_script_path=entry_point_script_path,
                parameters=AllocationParameters())

            nodes = NodesImpl(nodes=nodes_in_cluster,
                              allocation=allocation)

            notebook = nodes[0].deploy_notebook()
            stack.enter_context(cancel_local_on_exit(notebook))

            self.cluster.push_deployment(nodes)
            self.cluster.push_deployment(notebook)

            notebook.open_in_browser()
            sleep_until_allocation_ends(nodes=nodes)

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
        """ Handles the error thrown while cancelling the job.

            :param exception: Instance of the exception.
        """
        self.ui.cancel_job_button.setEnabled(True)

        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while cancelling job", WindowType.error)

    def cancel_job(self):
        """ Main function responsible for cancelling the job.
        """
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
