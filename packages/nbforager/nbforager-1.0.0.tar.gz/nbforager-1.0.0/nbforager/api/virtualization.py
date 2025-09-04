"""Virtualization connectors."""

from nbforager.api.connector import Connector


class VirtualizationAC:
    """Virtualization connectors."""

    def __init__(self, **kwargs):
        """Init VirtualizationAC."""
        self.cluster_groups = self.ClusterGroupsC(**kwargs)
        self.cluster_types = self.ClusterTypesC(**kwargs)
        self.clusters = self.ClustersC(**kwargs)
        self.interfaces = self.InterfacesC(**kwargs)
        self.virtual_disks = self.VirtualDisksC(**kwargs)
        self.virtual_machines = self.VirtualMachinesC(**kwargs)

    class ClusterGroupsC(Connector):
        """ClusterGroupsC, v3."""

        path = "virtualization/cluster-groups/"

    class ClusterTypesC(Connector):
        """ClusterTypesC, v3."""

        path = "virtualization/cluster-types/"

    class ClustersC(Connector):
        """ClustersC, v3."""

        path = "virtualization/clusters/"

    class InterfacesC(Connector):
        """InterfacesC, v3."""

        path = "virtualization/interfaces/"

    class VirtualDisksC(Connector):
        """VirtualDisksC, v3.7."""

        path = "virtualization/virtual-disks/"

    class VirtualMachinesC(Connector):
        """VirtualMachinesC, v3."""

        path = "virtualization/virtual-machines/"
