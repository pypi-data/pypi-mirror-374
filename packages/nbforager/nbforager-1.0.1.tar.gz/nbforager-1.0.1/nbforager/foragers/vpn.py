"""Tenancy Vpn."""

from nbforager.foragers.base_af import BaseAF
from nbforager.foragers.forager import Forager
from nbforager.nb_api import NbApi
from nbforager.nb_tree import NbTree


class VpnAF(BaseAF):
    """Vpn."""

    def __init__(self, api: NbApi, root: NbTree, tree: NbTree):
        """Init VpnAF.

        :param api: NbApi object, connector to Netbox API.
        :param root: NbTree object where raw data from Netbox needs to be saved.
        :param tree: NbTree object where transformed data from Netbox needs to be saved.
        """
        super().__init__(api, root, tree)
        self.ike_policies = self.IkePoliciesF(self)
        self.ike_proposal = self.IkeProposalF(self)
        self.ipsec_policies = self.IpsecPoliciesF(self)
        self.ipsec_profiles = self.IpsecProfilesF(self)
        self.ipsec_proposals = self.IpsecProposalsF(self)
        self.l2vpn_terminations = self.L2vpnTerminationsF(self)
        self.l2vpns = self.L2vpnsF(self)
        self.tunnel_groups = self.TunnelGroupsF(self)
        self.tunnel_terminations = self.TunnelTerminationsF(self)
        self.tunnels = self.TunnelsF(self)

    class IkePoliciesF(Forager):
        """IkePoliciesF."""

    class IkeProposalF(Forager):
        """IkeProposalF."""

    class IpsecPoliciesF(Forager):
        """IpsecPoliciesF."""

    class IpsecProfilesF(Forager):
        """IpsecProfilesF."""

    class IpsecProposalsF(Forager):
        """IpsecProposalsF."""

    class L2vpnTerminationsF(Forager):
        """L2vpnTerminationsF."""

    class L2vpnsF(Forager):
        """L2vpnsF."""

    class TunnelGroupsF(Forager):
        """TunnelGroupsF."""

    class TunnelTerminationsF(Forager):
        """TunnelTerminationsF."""

    class TunnelsF(Forager):
        """TunnelsF."""
