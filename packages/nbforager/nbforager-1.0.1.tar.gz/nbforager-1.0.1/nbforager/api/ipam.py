# pylint: disable=R0902,R0903

"""IPAM connectors."""

from nbforager.api.connector import Connector
from nbforager.api.ip_addresses import IpAddressesC


class IpamAC:
    """IPAM connectors."""

    def __init__(self, **kwargs):
        """Init IpamAC."""
        self.aggregates = self.AggregatesC(**kwargs)
        self.asn_ranges = self.AsnRangesC(**kwargs)
        self.asns = self.AsnsC(**kwargs)
        self.fhrp_group_assignments = self.FhrpGroupAssignmentsC(**kwargs)
        self.fhrp_groups = self.FhrpGroupsC(**kwargs)
        self.ip_addresses = IpAddressesC(**kwargs)
        self.ip_ranges = self.IpRangesC(**kwargs)
        self.l2vpn_terminations = self.L2vpnTerminationsC(**kwargs)
        self.l2vpns = self.L2vpnsC(**kwargs)
        self.prefixes = self.PrefixesC(**kwargs)
        self.rirs = self.RirsC(**kwargs)
        self.roles = self.RolesC(**kwargs)
        self.route_targets = self.RouteTargetsC(**kwargs)
        self.service_templates = self.ServiceTemplatesC(**kwargs)
        self.services = self.ServicesC(**kwargs)
        self.vlan_groups = self.VlanGroupsC(**kwargs)
        self.vlan_translation_policies = self.VlanTranslationPoliciesC(**kwargs)
        self.vlan_translation_rules = self.VlanTranslationRulesC(**kwargs)
        self.vlans = self.VlansC(**kwargs)
        self.vrfs = self.VrfsC(**kwargs)

    class AggregatesC(Connector):
        """AggregatesC, v3."""

        path = "ipam/aggregates/"

    class AsnRangesC(Connector):
        """AsnRangesC, v3."""

        path = "ipam/asn-ranges/"

    class AsnsC(Connector):
        """AsnsC, v3."""

        path = "ipam/asns/"

    class FhrpGroupAssignmentsC(Connector):
        """FhrpGroupAssignmentsC, v3."""

        path = "ipam/fhrp-group-assignments/"

    class FhrpGroupsC(Connector):
        """FhrpGroupsC, v3."""

        path = "ipam/fhrp-groups/"

    class IpRangesC(Connector):
        """IpRangesC, v3."""

        path = "ipam/ip-ranges/"

    class L2vpnTerminationsC(Connector):
        """L2vpnTerminationsC, v3, deprecated v4.3."""

        path = "ipam/l2vpn-terminations/"

    class L2vpnsC(Connector):
        """L2vpnsC, v3, deprecated v4.3."""

        path = "ipam/l2vpns/"

    class PrefixesC(Connector):
        """PrefixesC, v3."""

        path = "ipam/prefixes/"

    class RirsC(Connector):
        """RirsC, v3."""

        path = "ipam/rirs/"

    class RolesC(Connector):
        """RolesC, v3."""

        path = "ipam/roles/"

    class RouteTargetsC(Connector):
        """RouteTargetsC, v3."""

        path = "ipam/route-targets/"

    class ServiceTemplatesC(Connector):
        """ServiceTemplatesC, v3."""

        path = "ipam/service-templates/"

    class ServicesC(Connector):
        """ServicesC, v3."""

        path = "ipam/services/"

    class VlanGroupsC(Connector):
        """VlanGroupsC, v3."""

        path = "ipam/vlan-groups/"

    class VlanTranslationRulesC(Connector):
        """VlanTranslationRulesC, v4.2."""

        path = "ipam/vlan-translation-rules/"

    class VlanTranslationPoliciesC(Connector):
        """VlanTranslationPoliciesC, v4.2."""

        path = "ipam/vlan-translation-policies/"

    class VlansC(Connector):
        """VlansC, v3."""

        path = "ipam/vlans/"

    class VrfsC(Connector):
        """VrfsC, v3."""

        path = "ipam/vrfs/"
