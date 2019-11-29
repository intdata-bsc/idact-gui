from contextlib import ExitStack

from PyQt5.QtWidgets import QWidget, QTreeWidgetItem
from idact import show_cluster
from idact.detail.deployment.cancel_local_on_exit import cancel_local_on_exit
from idact.detail.jupyter_app.sleep_until_allocation_ends import sleep_until_allocation_ends
from idact.detail.nodes.node_impl import NodeImpl

from gui.functionality.deployments_provider import DeploymentsProvider
from gui.functionality.loading_window import LoadingWindow
from gui.functionality.popup_window import WindowType, PopUpWindow
from gui.helpers.custom_exceptions import NoClustersError
from gui.helpers.parameter_saver import ParameterSaver
from gui.helpers.ui_loader import UiLoader
from gui.helpers.worker import Worker


class RunningNotebooks(QWidget):
    def __init__(self, data_provider, deployments_provider: DeploymentsProvider, parent=None):
        super().__init__(parent=parent)
        self.ui = UiLoader.load_ui_from_file('running-notebooks.ui', self)

        self.parent = parent
        self.data_provider = data_provider
        self.deployments_provider = deployments_provider

        self.popup_window = PopUpWindow()
        self.loading_window = LoadingWindow()
        self.saver = ParameterSaver()
        self.parameters = self.saver.get_map()
        self.deployments = None
        self.cluster_name = None

        self.ui.show_nodes_and_notebooks_button.clicked.connect(self.concurrent_show_nodes_and_notebooks)
        self.ui.refresh_button.clicked.connect(self.concurrent_show_nodes_and_notebooks)
        self.ui.open_notebook_button.clicked.connect(self.open_notebook)
        self.ui.deploy_button.clicked.connect(self.concurrent_deploy_notebook)
        self.ui.cancel_job_button.clicked.connect(self.concurrent_cancel_job)

        self.cluster_names = self.data_provider.get_cluster_names()

        self.data_provider.remove_cluster_signal.connect(self.handle_cluster_list_modification)
        self.data_provider.add_cluster_signal.connect(self.handle_cluster_list_modification)
        self.ui.cluster_names_box.addItems(self.cluster_names)

        self.ui.open_notebook_button.setEnabled(False)
        self.ui.deploy_button.setEnabled(False)
        self.ui.cancel_job_button.setEnabled(False)

        self.ui.nodes_tree.itemSelectionChanged.connect(self.change_buttons_to_disabled_or_not)

    def change_buttons_to_disabled_or_not(self):
        selected_items = self.ui.nodes_tree.selectedItems()

        if len(selected_items) == 1:
            selected_item = selected_items[0]
            if selected_item.parent() and selected_item.parent().parent():
                self.ui.open_notebook_button.setEnabled(selected_item.text(6) != "")
                self.ui.deploy_button.setEnabled(selected_item.text(6) == "" and selected_item.text(1) != "None")
                self.ui.cancel_job_button.setEnabled(False)
                return

            if selected_item.parent() and selected_item.parent().parent() is None:
                self.ui.open_notebook_button.setEnabled(False)
                self.ui.deploy_button.setEnabled(False)
                self.ui.cancel_job_button.setEnabled(True)
                return

        self.ui.open_notebook_button.setEnabled(False)
        self.ui.deploy_button.setEnabled(False)
        self.ui.cancel_job_button.setEnabled(False)

    def concurrent_show_nodes_and_notebooks(self):
        self.ui.show_nodes_and_notebooks_button.setEnabled(False)
        self.ui.refresh_button.setEnabled(False)

        worker = Worker(self.show_nodes_and_notebooks)
        worker.signals.result.connect(self.handle_complete_show_nodes_and_notebooks)
        worker.signals.error.connect(self.handle_error_show_nodes_and_notebooks)
        self.parent.threadpool.start(worker)

    def handle_complete_show_nodes_and_notebooks(self):
        self.ui.show_nodes_and_notebooks_button.setEnabled(True)
        self.ui.refresh_button.setEnabled(True)

        root = QTreeWidgetItem()

        for nodes_collection in self.deployments.nodes:
            nodes_item = QTreeWidgetItem()
            for node in nodes_collection._nodes:
                node_item = QTreeWidgetItem()
                node_item.setText(1, str(node.host))
                node_item.setText(2, str(node.port))
                node_item.setText(3, str(node.cores))
                node_item.setText(4, str(node.memory))
                node_item.setText(5, str(node.allocated_until))
                local_port = ""
                for jupyter_deployment in self.deployments.jupyter_deployments:
                    if node == jupyter_deployment.deployment.node:
                        local_port = str(jupyter_deployment.local_port)
                        break
                node_item.setText(6, local_port)

                nodes_item.addChild(node_item)
            nodes_item.setText(0, 'Job ID: ' + str(nodes_collection._allocation._job_id))
            root.addChild(nodes_item)
        root.setText(0, self.cluster_name)
        self.ui.nodes_tree.clear()
        self.ui.nodes_tree.addTopLevelItem(root)
        self.ui.nodes_tree.expandAll()

    def handle_error_show_nodes_and_notebooks(self, exception):
        self.ui.show_nodes_and_notebooks_button.setEnabled(True)
        self.ui.refresh_button.setEnabled(True)

        if isinstance(exception, NoClustersError):
            self.popup_window.show_message("There are no added clusters", WindowType.error)
        elif isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while listing nodes and notebooks", WindowType.error, exception)

    def show_nodes_and_notebooks(self):
        self.cluster_name = str(self.ui.cluster_names_box.currentText())
        self.deployments = self.deployments_provider.get_deployments(self.cluster_name, update=True)

    def concurrent_deploy_notebook(self):
        self.loading_window.show_message("Notebook is being deployed")
        self.ui.deploy_button.setEnabled(False)

        worker = Worker(self.deploy_notebook)
        worker.signals.result.connect(self.handle_complete_deploy_notebook)
        worker.signals.error.connect(self.handle_error_deploy_notebook)
        self.parent.threadpool.start(worker)

    def handle_complete_deploy_notebook(self):
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("Notebook has been closed", WindowType.success)

    def handle_error_deploy_notebook(self, exception):
        self.loading_window.close()
        self.ui.deploy_button.setEnabled(True)
        self.popup_window.show_message("An error occurred while deploying notebook", WindowType.error, exception)
        self.ui.deploy_button.setEnabled(True)

    def deploy_notebook(self):
        item = self.ui.nodes_tree.selectedItems()[0]
        node = self.get_node_for_tree_item(item)
        nodes_collection = item.parent()
        nodes_collection_index = nodes_collection.indexOfChild(item)
        nodes = self.deployments.nodes[nodes_collection_index]

        with ExitStack() as stack:
            notebook = node.deploy_notebook()
            stack.enter_context(cancel_local_on_exit(notebook))
            cluster = show_cluster(name=self.cluster_name)
            cluster.push_deployment(notebook)
            self.deployments_provider.add_deployment(self.cluster_name, notebook)
            notebook.open_in_browser()
            self.loading_window.close()
            self.concurrent_show_nodes_and_notebooks()
            sleep_until_allocation_ends(nodes=nodes)

    def get_node_for_tree_item(self, item):
        node_collection = item.parent()
        node_index = node_collection.indexOfChild(item)

        root = node_collection.parent()
        nodes_index = root.indexOfChild(node_collection)

        return self.deployments.nodes[nodes_index]._nodes[node_index]

    def concurrent_cancel_job(self):
        self.ui.cancel_job_button.setEnabled(False)

        worker = Worker(self.cancel_job)
        worker.signals.result.connect(self.handle_complete_cancel_job)
        worker.signals.error.connect(self.handle_error_cancel_job)
        self.parent.threadpool.start(worker)

    def handle_complete_cancel_job(self):
        self.ui.cancel_job_button.setEnabled(True)
        self.popup_window.show_message("Cancel command has been successfully executed", WindowType.success)

    def handle_error_cancel_job(self, exception):
        self.ui.cancel_job_button.setEnabled(True)

        if isinstance(exception, KeyError):
            self.popup_window.show_message("The cluster does not exist", WindowType.error)
        else:
            self.popup_window.show_message("An error occurred while cancelling job", WindowType.error, exception)

    def cancel_job(self):
        item = self.ui.nodes_tree.selectedItems()[0]
        nodes = self.get_nodes_collection_for_tree_item(item)
        nodes.cancel()
        self.concurrent_show_nodes_and_notebooks()

    def get_nodes_collection_for_tree_item(self, item):
        root = item.parent()
        nodes_index = root.indexOfChild(item)

        return self.deployments.nodes[nodes_index]

    def concurrent_open_notebook(self):
        self.ui.open_notebook_button.setEnabled(False)

        worker = Worker(self.open_notebook)
        worker.signals.result.connect(self.handle_complete_open_notebook)
        worker.signals.error.connect(self.handle_error_open_notebook)
        self.parent.threadpool.start(worker)

    def handle_complete_open_notebook(self):
        self.ui.open_notebook_button.setEnabled(True)

    def handle_error_open_notebook(self, exception):
        self.ui.open_notebook_button.setEnabled(True)
        self.popup_window.show_message("An error occurred while opening notebook", WindowType.error, exception)

    def open_notebook(self):
        for item in self.ui.nodes_tree.selectedItems():
            node_collection: QTreeWidgetItem = item.parent()
            node_index = node_collection.indexOfChild(item)
            root: QTreeWidgetItem = node_collection.parent()
            nodes_index = root.indexOfChild(node_collection)

            node: NodeImpl = self.deployments.nodes[nodes_index]._nodes[node_index]
            for jupyter_deployment in self.deployments.jupyter_deployments:
                if node == jupyter_deployment.deployment.node:
                    jupyter_deployment.open_in_browser()
                    return

    def handle_cluster_list_modification(self):
        self.cluster_names = self.data_provider.get_cluster_names()
        self.ui.cluster_names_box.clear()
        self.ui.cluster_names_box.addItems(self.cluster_names)
