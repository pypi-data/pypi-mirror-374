"""Circuits Forager."""

from nbforager.foragers.base_af import BaseAF
from nbforager.foragers.forager import Forager
from nbforager.nb_api import NbApi
from nbforager.nb_tree import NbTree


class CircuitsAF(BaseAF):
    """Circuits Forager."""

    def __init__(self, api: NbApi, root: NbTree, tree: NbTree):
        """Init CircuitsAF.

        :param api: NbApi object, connector to Netbox API.
        :param root: NbTree object where raw data from Netbox needs to be saved.
        :param tree: NbTree object where transformed data from Netbox needs to be saved.
        """
        super().__init__(api, root, tree)
        self.circuit_group_assignments = self.CircuitGroupAssignmentsF(self)
        self.circuit_groups = self.CircuitGroupsF(self)
        self.circuit_terminations = self.CircuitTerminationsF(self)
        self.circuit_types = self.CircuitTypesF(self)
        self.circuits = self.CircuitsF(self)
        self.provider_accounts = self.ProviderAccountsF(self)
        self.provider_networks = self.ProviderNetworksF(self)
        self.providers = self.ProvidersF(self)
        self.virtual_circuit_terminations = self.VirtualCircuitTerminationsF(self)
        self.virtual_circuit_types = self.VirtualCircuitTypesF(self)
        self.virtual_circuits = self.VirtualCircuitsF(self)

    class CircuitGroupAssignmentsF(Forager):
        """CircuitGroupAssignmentsF."""

    class CircuitGroupsF(Forager):
        """CircuitGroupsF."""

    class CircuitTerminationsF(Forager):
        """CircuitTerminationsF."""

    class CircuitTypesF(Forager):
        """CircuitTypesF."""

    class CircuitsF(Forager):
        """CircuitsF."""

    class ProviderAccountsF(Forager):
        """ProviderAccountsF."""

    class ProviderNetworksF(Forager):
        """ProviderNetworksF."""

    class ProvidersF(Forager):
        """ProvidersF."""

    class VirtualCircuitTerminationsF(Forager):
        """VirtualCircuitTerminationsF."""

    class VirtualCircuitTypesF(Forager):
        """VirtualCircuitTypesF."""

    class VirtualCircuitsF(Forager):
        """VirtualCircuitsF."""
