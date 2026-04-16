"""
Pulumi Dynamic Provider for CloudVision using cv_workflow from PyAVD
"""

import yaml
from pathlib import Path
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pyavd.cv_workflow import deploy_to_cv


class CloudVisionProvider(ResourceProvider):
    def _deploy_to_cv(self, cv_server, cv_token, workspace_name, inventory_path):
        """
        Deploy configurations to CloudVision using cv_workflow.
        """
        # The cv_workflow.deploy_to_cv function handles:
        # 1. Reading inventory and structured configs
        # 2. Creating configlets in CloudVision
        # 3. Creating change control
        # 4. Deploying to devices

        result = deploy_to_cv(
            server=cv_server,
            token=cv_token,
            workspace=workspace_name,
            inventory_file=inventory_path,
        )

        return result

    def diff(self, id: str, olds: dict, news: dict) -> DiffResult:
        """
        Check if deployment parameters have changed.
        """
        # Check if any deployment parameters changed
        changed = (
            olds.get("cv_server") != news.get("cv_server")
            or olds.get("workspace_name") != news.get("workspace_name")
            or olds.get("inventory_path") != news.get("inventory_path")
            or olds.get("config_hash") != news.get("config_hash")
        )
        return DiffResult(changes=changed)

    def create(self, props: dict) -> CreateResult:
        """
        Initial deployment to CloudVision.
        """
        self._deploy_to_cv(
            props["cv_server"],
            props["cv_token"],
            props["workspace_name"],
            props["inventory_path"],
        )
        return CreateResult(id_=props["workspace_name"], outs=props)

    def update(self, id: str, olds: dict, news: dict) -> UpdateResult:
        """
        Update deployment in CloudVision.
        """
        self._deploy_to_cv(
            news["cv_server"],
            news["cv_token"],
            news["workspace_name"],
            news["inventory_path"],
        )
        return UpdateResult(outs=news)


class CloudVisionDeployment(Resource):
    """
    Pulumi Resource for deploying AVD configs via CloudVision.
    """

    def __init__(
        self,
        name: str,
        cv_server: str,
        cv_token: str,
        workspace_name: str,
        inventory_path: str,
        config_hash: str = None,
        opts=None,
    ):
        """
        Args:
            name: Pulumi resource name
            cv_server: CloudVision server URL
            cv_token: CloudVision API token
            workspace_name: CloudVision workspace name
            inventory_path: Path to inventory file
            config_hash: Hash of configs to detect changes
        """
        super().__init__(
            CloudVisionProvider(),
            name,
            {
                "cv_server": cv_server,
                "cv_token": cv_token,
                "workspace_name": workspace_name,
                "inventory_path": inventory_path,
                "config_hash": config_hash,
            },
            opts,
        )
