from idact import load_environment, show_cluster, SynchronizedDeployments, Nodes, JupyterDeployment, DaskDeployment
from idact.detail.allocation.finalize_allocation import finalize_allocation
from idact.detail.slurm.run_squeue import run_squeue


class DeploymentsProvider:
    def __init__(self):
        self.cluster_deployments = dict()

    def get_deployments(self, cluster_name: str, update=False) -> SynchronizedDeployments:
        if cluster_name not in self.cluster_deployments:
            load_environment()
            cluster = show_cluster(name=cluster_name)
            self.cluster_deployments[cluster_name] = cluster.pull_deployments()

        if update:
            self.update_deployments(cluster_name)
        return self.cluster_deployments[cluster_name]

    def add_deployment(self, cluster_name, deployment):
        if isinstance(deployment, Nodes):
            for nodes_collection in self.get_deployments(cluster_name).nodes:
                if nodes_collection.uuid == deployment.uuid:
                    self.get_deployments(cluster_name).nodes.remove(nodes_collection)
                    break
            self.get_deployments(cluster_name).nodes.append(deployment)

        elif isinstance(deployment, JupyterDeployment):
            for jupyter_deployment in self.get_deployments(cluster_name).jupyter_deployments:
                if jupyter_deployment.uuid == deployment.uuid:
                    self.get_deployments(cluster_name).jupyter_deployments.remove(jupyter_deployment)
                    break
            self.get_deployments(cluster_name).jupyter_deployments.append(deployment)
        elif isinstance(deployment, DaskDeployment):
            for dask_deployment in self.get_deployments(cluster_name).dask_deployments:
                if dask_deployment.uuid == deployment.uuid:
                    self.get_deployments(cluster_name).dask_deployments.remove(dask_deployment)
                    break
            self.get_deployments(cluster_name).dask_deployments.append(deployment)

    def update_deployments(self, cluster_name: str):
        cluster = show_cluster(cluster_name)
        nodes = self.cluster_deployments[cluster_name].nodes
        nodes_to_remove = []

        squeue = run_squeue(cluster.get_access_node())

        for nodes_collection in nodes:
            allocation = nodes_collection._allocation
            if allocation._job_id not in squeue:
                nodes_to_remove.append(nodes_collection)
            elif nodes_collection._nodes[0].host is None \
                    and squeue[allocation._job_id].node_list is not None \
                    and squeue[allocation._job_id].state == 'RUNNING':
                finalize_allocation(allocation_id=allocation._job_id,
                                    hostnames=squeue[allocation._job_id].node_list,
                                    nodes=nodes_collection._nodes,
                                    parameters=allocation._parameters,
                                    allocated_until=squeue[allocation._job_id].end_time,
                                    config=cluster.config)
                nodes_collection._allocation._done_waiting = True
                nodes.append(nodes_collection)
                nodes_to_remove.append(nodes_collection)
                cluster.push_deployment(nodes_collection)

        jupyter_deployments = self.cluster_deployments[cluster_name].jupyter_deployments
        jupyter_deployments_to_remove = []
        for nodes_collection in reversed(nodes_to_remove):
            for node in nodes_collection._nodes:
                for jupyter_deployment in jupyter_deployments:
                    if node == jupyter_deployment.deployment.node:
                        jupyter_deployments_to_remove.append(jupyter_deployment)
            nodes.remove(nodes_collection)

        for jupyter_deployment in reversed(jupyter_deployments_to_remove):
            jupyter_deployments.remove(jupyter_deployment)
