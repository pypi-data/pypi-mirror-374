"""Circuits connectors."""

from nbforager.api.base_ac import BaseAC
from nbforager.api.connector import Connector


class CircuitsAC(BaseAC):
    """Circuits connectors."""

    def __init__(self, **kwargs):
        """Init CircuitsAC."""
        self.circuit_group_assignments = self.CircuitGroupAssignmentsC(**kwargs)
        self.circuit_groups = self.CircuitGroupsC(**kwargs)
        self.circuit_terminations = self.CircuitTerminationsC(**kwargs)
        self.circuit_types = self.CircuitTypesC(**kwargs)
        self.circuits = self.CircuitsC(**kwargs)
        self.provider_accounts = self.ProviderAccountsC(**kwargs)
        self.provider_networks = self.ProviderNetworksC(**kwargs)
        self.providers = self.ProvidersC(**kwargs)
        self.virtual_circuit_terminations = self.VirtualCircuitTerminationsC(**kwargs)
        self.virtual_circuit_types = self.VirtualCircuitTypesC(**kwargs)
        self.virtual_circuits = self.VirtualCircuitsC(**kwargs)

    class CircuitGroupAssignmentsC(Connector):
        """CircuitTerminationsC, v4.1."""

        path = "circuits/circuit-group-assignments/"

    class CircuitGroupsC(Connector):
        """CircuitGroupsC, v4.1."""

        path = "circuits/circuit-groups/"

    class CircuitTerminationsC(Connector):
        """CircuitTerminationsC, v3."""

        path = "circuits/circuit-terminations/"

    class CircuitTypesC(Connector):
        """CircuitTypesC, v3."""

        path = "circuits/circuit-types/"

    class CircuitsC(Connector):
        """CircuitsC, v3."""

        path = "circuits/circuits/"

    class ProviderAccountsC(Connector):
        """ProviderAccountsC, v3."""

        path = "circuits/provider-accounts/"

    class ProviderNetworksC(Connector):
        """ProviderNetworksC, v3."""

        path = "circuits/provider-networks/"

    class ProvidersC(Connector):
        """ProvidersC, v3."""

        path = "circuits/providers/"

    class VirtualCircuitTerminationsC(Connector):
        """VirtualCircuitTerminationsC, v4.2."""

        path = "circuits/virtual-circuit-terminations/"

    class VirtualCircuitTypesC(Connector):
        """VirtualCircuitTypesC, v4.2."""

        path = "circuits/virtual-circuit-types/"

    class VirtualCircuitsC(Connector):
        """VirtualCircuitsC, v4.2."""

        path = "circuits/virtual-circuits/"
