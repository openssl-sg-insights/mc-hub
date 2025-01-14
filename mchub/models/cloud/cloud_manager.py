from ..cloud.openstack_manager import OpenStackManager
from ..cloud.dns_manager import DnsManager


class CloudManager:
    def __init__(self, project, **kwargs):
        self.manager = OpenStackManager(project=project, **kwargs)

    @property
    def available_resources(self):
        """
        Retrieves the available cloud resources including resources from OpenStack
        and available domains.
        """
        available_resources = self.manager.available_resources
        available_resources["possible_resources"][
            "domain"
        ] = DnsManager.get_available_domains()
        return available_resources
