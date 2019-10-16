import os
from PyQt5 import uic
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from idact.core.retry import Retry
from idact.detail.environment.environment_provider import EnvironmentProvider
from idact import save_environment, load_environment

from gui.functionality.popup_window import WindowType, PopUpWindow


class AdjustTimeouts(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        
        self.popup_window = PopUpWindow()
        self.cluster_names = []
        self.current_cluster = ''
        self.load_cluster_names()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, '../widgets_templates/adjust-timeouts.ui'))
        
        load_environment()

        self.ui.cluster_names_box.addItems(self.cluster_names)

        if len(self.cluster_names) > 0:
            self.current_cluster = self.cluster_names[0]
            self.refresh_timeouts(self.current_cluster)
        else:
            self.current_cluster = ''

        self.ui.cluster_names_box.activated[str].connect(self.item_pressed)
        self.ui.save_timeouts_button.clicked.connect(self.save_timeouts)

        lay = QVBoxLayout(self)
        lay.addWidget(self.ui)

    def refresh_timeouts(self, cluster_name):
        load_environment()
        default_retries = EnvironmentProvider().environment.clusters[cluster_name].config.retries

        self.ui.port_info_count.setValue(default_retries[Retry.PORT_INFO].count)
        self.ui.jupyter_json_count.setValue(default_retries[Retry.JUPYTER_JSON].count)
        self.ui.scheduler_connect_count.setValue(default_retries[Retry.SCHEDULER_CONNECT].count)
        self.ui.dask_node_connect_count.setValue(default_retries[Retry.DASK_NODE_CONNECT].count)
        self.ui.deploy_dask_scheduler_count.setValue(default_retries[Retry.DEPLOY_DASK_SCHEDULER].count)
        self.ui.deploy_dask_worker_count.setValue(default_retries[Retry.DEPLOY_DASK_WORKER].count)
        self.ui.get_scheduler_address_count.setValue(default_retries[Retry.GET_SCHEDULER_ADDRESS].count)
        self.ui.check_worker_started_count.setValue(default_retries[Retry.CHECK_WORKER_STARTED].count)
        self.ui.cancel_deployment_count.setValue(default_retries[Retry.CANCEL_DEPLOYMENT].count)
        self.ui.squeue_after_sbatch_count.setValue(default_retries[Retry.SQUEUE_AFTER_SBATCH].count)
        self.ui.open_tunnel_count.setValue(default_retries[Retry.OPEN_TUNNEL].count)
        self.ui.validate_http_tunnel_count.setValue(default_retries[Retry.VALIDATE_HTTP_TUNNEL].count)
        self.ui.tunnel_try_again_with_any_port_count.setValue(
            default_retries[Retry.TUNNEL_TRY_AGAIN_WITH_ANY_PORT].count)

        self.ui.port_info_seconds.setValue(default_retries[Retry.PORT_INFO].seconds_between)
        self.ui.jupyter_json_seconds.setValue(default_retries[Retry.JUPYTER_JSON].seconds_between)
        self.ui.scheduler_connect_seconds.setValue(default_retries[Retry.SCHEDULER_CONNECT].seconds_between)
        self.ui.dask_node_connect_seconds.setValue(default_retries[Retry.DASK_NODE_CONNECT].seconds_between)
        self.ui.deploy_dask_scheduler_seconds.setValue(
            default_retries[Retry.DEPLOY_DASK_SCHEDULER].seconds_between)
        self.ui.deploy_dask_worker_seconds.setValue(default_retries[Retry.DEPLOY_DASK_WORKER].seconds_between)
        self.ui.get_scheduler_address_seconds.setValue(
            default_retries[Retry.GET_SCHEDULER_ADDRESS].seconds_between)
        self.ui.check_worker_started_seconds.setValue(default_retries[Retry.CHECK_WORKER_STARTED].seconds_between)
        self.ui.cancel_deployment_seconds.setValue(default_retries[Retry.CANCEL_DEPLOYMENT].seconds_between)
        self.ui.squeue_after_sbatch_seconds.setValue(default_retries[Retry.SQUEUE_AFTER_SBATCH].seconds_between)
        self.ui.open_tunnel_seconds.setValue(default_retries[Retry.OPEN_TUNNEL].seconds_between)
        self.ui.validate_http_tunnel_seconds.setValue(default_retries[Retry.VALIDATE_HTTP_TUNNEL].seconds_between)
        self.ui.tunnel_try_again_with_any_port_seconds.setValue(
            default_retries[Retry.TUNNEL_TRY_AGAIN_WITH_ANY_PORT].seconds_between)

    def save_timeouts(self):
        if self.current_cluster == '':
            self.popup_window.show_message("There are no added clusters", WindowType.error)
        else:
            default_retries = EnvironmentProvider().environment.clusters[self.current_cluster].config.retries

            default_retries[Retry.PORT_INFO].count = int(self.ui.port_info_count.text())
            default_retries[Retry.JUPYTER_JSON].count = int(self.ui.jupyter_json_count.text())
            default_retries[Retry.SCHEDULER_CONNECT].count = int(self.ui.scheduler_connect_count.text())
            default_retries[Retry.DASK_NODE_CONNECT].count = int(self.ui.dask_node_connect_count.text())
            default_retries[Retry.DEPLOY_DASK_SCHEDULER].count = int(self.ui.deploy_dask_scheduler_count.text())
            default_retries[Retry.DEPLOY_DASK_WORKER].count = int(self.ui.deploy_dask_worker_count.text())
            default_retries[Retry.GET_SCHEDULER_ADDRESS].count = int(self.ui.get_scheduler_address_count.text())
            default_retries[Retry.CHECK_WORKER_STARTED].count = int(self.ui.check_worker_started_count.text())
            default_retries[Retry.CANCEL_DEPLOYMENT].count = int(self.ui.cancel_deployment_count.text())
            default_retries[Retry.SQUEUE_AFTER_SBATCH].count = int(self.ui.squeue_after_sbatch_count.text())
            default_retries[Retry.OPEN_TUNNEL].count = int(self.ui.open_tunnel_count.text())
            default_retries[Retry.VALIDATE_HTTP_TUNNEL].count = int(self.ui.validate_http_tunnel_count.text())
            default_retries[Retry.TUNNEL_TRY_AGAIN_WITH_ANY_PORT].count = int(self.ui.tunnel_try_again_with_any_port_count.text())

            default_retries[Retry.PORT_INFO].seconds_between = int(self.ui.port_info_seconds.text())
            default_retries[Retry.JUPYTER_JSON].seconds_between = int(self.ui.jupyter_json_seconds.text())
            default_retries[Retry.SCHEDULER_CONNECT].seconds_between = int(self.ui.scheduler_connect_seconds.text())
            default_retries[Retry.DASK_NODE_CONNECT].seconds_between = int(self.ui.dask_node_connect_seconds.text())
            default_retries[Retry.DEPLOY_DASK_SCHEDULER].seconds_between = int(self.ui.deploy_dask_scheduler_seconds.text())
            default_retries[Retry.DEPLOY_DASK_WORKER].seconds_between = int(self.ui.deploy_dask_worker_seconds.text())
            default_retries[Retry.GET_SCHEDULER_ADDRESS].seconds_between = int(self.ui.get_scheduler_address_seconds.text())
            default_retries[Retry.CHECK_WORKER_STARTED].seconds_between = int(self.ui.check_worker_started_seconds.text())
            default_retries[Retry.CANCEL_DEPLOYMENT].seconds_between = int(self.ui.cancel_deployment_seconds.text())
            default_retries[Retry.SQUEUE_AFTER_SBATCH].seconds_between = int(self.ui.squeue_after_sbatch_seconds.text())
            default_retries[Retry.OPEN_TUNNEL].seconds_between = int(self.ui.open_tunnel_seconds.text())
            default_retries[Retry.VALIDATE_HTTP_TUNNEL].seconds_between = int(self.ui.validate_http_tunnel_seconds.text())
            default_retries[Retry.TUNNEL_TRY_AGAIN_WITH_ANY_PORT].seconds_between = int(self.ui.tunnel_try_again_with_any_port_seconds.text())

            save_environment()
            self.popup_window.show_message("Timeouts have been saved", WindowType.success)

    def item_pressed(self, item_pressed):
        self.current_cluster = item_pressed
        self.refresh_timeouts(item_pressed)
    
    def load_cluster_names(self):
        load_environment()
        self.cluster_names = list(EnvironmentProvider().environment.clusters.keys())
