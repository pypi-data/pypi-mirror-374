"""Vpn connectors."""

from nbforager.api.connector import Connector


class VpnAC:
    """Vpn connectors."""

    def __init__(self, **kwargs):
        """Init VpnAC."""
        self.ike_policies = self.IkePoliciesC(**kwargs)
        self.ike_proposal = self.IkeProposalC(**kwargs)
        self.ipsec_policies = self.IpsecPoliciesC(**kwargs)
        self.ipsec_profiles = self.IpsecProfilesC(**kwargs)
        self.ipsec_proposals = self.IpsecProposalsC(**kwargs)
        self.l2vpn_terminations = self.L2vpnTerminationsC(**kwargs)
        self.l2vpns = self.L2vpnsC(**kwargs)
        self.tunnel_groups = self.TunnelGroupsC(**kwargs)
        self.tunnel_terminations = self.TunnelTerminationsC(**kwargs)
        self.tunnels = self.TunnelsC(**kwargs)

    class IkePoliciesC(Connector):
        """IkePoliciesC, v3.7."""

        path = "vpn/ike-policies/"

    class IkeProposalC(Connector):
        """IkeProposalC, v3.7."""

        path = "vpn/ike-proposal/"

    class IpsecPoliciesC(Connector):
        """IkePoliciesC, v3.7."""

        path = "vpn/ipsec-policies/"

    class IpsecProfilesC(Connector):
        """IpsecProfilesC, v3.7."""

        path = "vpn/ipsec-profiles/"

    class IpsecProposalsC(Connector):
        """IpsecProposalsC, v3.7."""

        path = "vpn/ipsec-proposals/"

    class L2vpnTerminationsC(Connector):
        """L2vpnTerminationsC, v3.7."""

        path = "vpn/l2vpn-terminations/"

    class L2vpnsC(Connector):
        """L2vpnsC, v3.7."""

        path = "vpn/l2vpns/"

    class TunnelGroupsC(Connector):
        """IkePoliciesC, v3.7."""

        path = "vpn/tunnel-groups/"

    class TunnelTerminationsC(Connector):
        """TunnelTerminationsC, v3.7."""

        path = "vpn/tunnel-terminations/"

    class TunnelsC(Connector):
        """TunnelsC, v3.7."""

        path = "vpn/tunnels/"
