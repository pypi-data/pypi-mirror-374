"""DCIM connectors."""

from nbforager.api.connector import Connector


class DcimAC:
    """DCIM connectors."""

    def __init__(self, **kwargs):
        """Init DcimAC."""
        self.cable_terminations = self.CableTerminationsC(**kwargs)
        self.cables = self.CablesC(**kwargs)
        self.connected_device = self.ConnectedDeviceC(**kwargs)
        self.console_port_templates = self.ConsolePortTemplatesC(**kwargs)
        self.console_ports = self.ConsolePortsC(**kwargs)
        self.console_server_port_templates = self.ConsoleServerPortTemplatesC(**kwargs)
        self.console_server_ports = self.ConsoleServerPortsC(**kwargs)
        self.device_bay_templates = self.DeviceBayTemplatesC(**kwargs)
        self.device_bays = self.DeviceBaysC(**kwargs)
        self.device_roles = self.DeviceRolesC(**kwargs)
        self.device_types = self.DeviceTypesC(**kwargs)
        self.devices = self.DevicesC(**kwargs)
        self.front_port_templates = self.FrontPortTemplatesC(**kwargs)
        self.front_ports = self.FrontPortsC(**kwargs)
        self.interface_templates = self.InterfaceTemplatesC(**kwargs)
        self.interfaces = self.InterfacesC(**kwargs)
        self.inventory_item_roles = self.InventoryItemRolesC(**kwargs)
        self.inventory_item_templates = self.InventoryItemTemplatesC(**kwargs)
        self.inventory_items = self.InventoryItemsC(**kwargs)
        self.locations = self.LocationsC(**kwargs)
        self.mac_addresses = self.MacAddressesC(**kwargs)
        self.manufacturers = self.ManufacturersC(**kwargs)
        self.module_bay_templates = self.ModuleBayTemplatesC(**kwargs)
        self.module_bays = self.ModuleBaysC(**kwargs)
        self.module_type_profiles = self.ModuleTypeProfilesC(**kwargs)
        self.module_types = self.ModuleTypesC(**kwargs)
        self.modules = self.ModulesC(**kwargs)
        self.platforms = self.PlatformsC(**kwargs)
        self.power_feeds = self.PowerFeedsC(**kwargs)
        self.power_outlet_templates = self.PowerOutletTemplatesC(**kwargs)
        self.power_outlets = self.PowerOutletsC(**kwargs)
        self.power_panels = self.PowerPanelsC(**kwargs)
        self.power_port_templates = self.PowerPortTemplatesC(**kwargs)
        self.power_ports = self.PowerPortsC(**kwargs)
        self.rack_reservations = self.RackReservationsC(**kwargs)
        self.rack_roles = self.RackRolesC(**kwargs)
        self.rack_types = self.RackTypesC(**kwargs)
        self.racks = self.RacksC(**kwargs)
        self.rear_port_templates = self.RearPortTemplatesC(**kwargs)
        self.rear_ports = self.RearPortsC(**kwargs)
        self.regions = self.RegionsC(**kwargs)
        self.site_groups = self.SiteGroupsC(**kwargs)
        self.sites = self.SitesC(**kwargs)
        self.virtual_chassis = self.VirtualChassisC(**kwargs)
        self.virtual_device_contexts = self.VirtualDeviceContextsC(**kwargs)

    class CableTerminationsC(Connector):
        """CableTerminationsC, v3."""

        path = "dcim/cable-terminations/"

    class CablesC(Connector):
        """CablesC, v3."""

        path = "dcim/cables/"

    class ConnectedDeviceC(Connector):
        """ConnectedDeviceC, v3."""

        path = "dcim/connected-device/"

    class ConsolePortTemplatesC(Connector):
        """ConsolePortTemplatesC, v3."""

        path = "dcim/console-port-templates/"

    class ConsolePortsC(Connector):
        """ConsolePortsC, v3."""

        path = "dcim/console-ports/"

    class ConsoleServerPortTemplatesC(Connector):
        """ConsoleServerPortTemplatesC, v3."""

        path = "dcim/console-server-port-templates/"

    class ConsoleServerPortsC(Connector):
        """ConsoleServerPortsC, v3."""

        path = "dcim/console-server-ports/"

    class DeviceBayTemplatesC(Connector):
        """DeviceBayTemplatesC, v3."""

        path = "dcim/device-bay-templates/"

    class DeviceBaysC(Connector):
        """DeviceBaysC, v3."""

        path = "dcim/device-bays/"

    class DeviceRolesC(Connector):
        """DeviceRolesC, v3."""

        path = "dcim/device-roles/"

    class DeviceTypesC(Connector):
        """DeviceTypesC, v3."""

        path = "dcim/device-types/"

    class DevicesC(Connector):
        """DevicesC, v3."""

        path = "dcim/devices/"

    class FrontPortTemplatesC(Connector):
        """FrontPortTemplatesC, v3."""

        path = "dcim/front-port-templates/"

    class FrontPortsC(Connector):
        """FrontPortsC, v3."""

        path = "dcim/front-ports/"

    class InterfaceTemplatesC(Connector):
        """InterfaceTemplatesC, v3."""

        path = "dcim/interface-templates/"

    class InterfacesC(Connector):
        """InterfacesC, v3."""

        path = "dcim/interfaces/"

    class InventoryItemRolesC(Connector):
        """InventoryItemRolesC, v3."""

        path = "dcim/inventory-item-roles/"

    class InventoryItemTemplatesC(Connector):
        """InventoryItemTemplatesC, v3."""

        path = "dcim/inventory-item-templates/"

    class InventoryItemsC(Connector):
        """InventoryItemsC, v3."""

        path = "dcim/inventory-items/"

    class LocationsC(Connector):
        """LocationsC, v3."""

        path = "dcim/locations/"

    class MacAddressesC(Connector):
        """MacAddressesC, v3."""

        path = "dcim/mac-addresses/"

    class ManufacturersC(Connector):
        """ManufacturersC, v3."""

        path = "dcim/manufacturers/"

    class ModuleBayTemplatesC(Connector):
        """ModuleBayTemplatesC, v3."""

        path = "dcim/module-bay-templates/"

    class ModuleBaysC(Connector):
        """ModuleBaysC, v3."""

        path = "dcim/module-bays/"

    class ModuleTypeProfilesC(Connector):
        """ModuleTypeProfilesC, v4.3."""

        path = "dcim/module-type-profiles/"

    class ModuleTypesC(Connector):
        """ModuleTypesC, v3."""

        path = "dcim/module-types/"

    class ModulesC(Connector):
        """ModulesC, v3."""

        path = "dcim/modules/"

    class PlatformsC(Connector):
        """PlatformsC, v3."""

        path = "dcim/platforms/"

    class PowerFeedsC(Connector):
        """PowerFeedsC, v3."""

        path = "dcim/power-feeds/"

    class PowerOutletTemplatesC(Connector):
        """PowerOutletTemplatesC, v3."""

        path = "dcim/power-outlet-templates/"

    class PowerOutletsC(Connector):
        """PowerOutletsC, v3."""

        path = "dcim/power-outlets/"

    class PowerPanelsC(Connector):
        """PowerPanelsC, v3."""

        path = "dcim/power-panels/"

    class PowerPortTemplatesC(Connector):
        """PowerPortTemplatesC, v3."""

        path = "dcim/power-port-templates/"

    class PowerPortsC(Connector):
        """PowerPortsC, v3."""

        path = "dcim/power-ports/"

    class RackReservationsC(Connector):
        """RackReservationsC, v3."""

        path = "dcim/rack-reservations/"

    class RackRolesC(Connector):
        """RackRolesC, v3."""

        path = "dcim/rack-roles/"

    class RackTypesC(Connector):
        """RackTypesC, v4.1."""

        path = "dcim/rack-types/"

    class RacksC(Connector):
        """RacksC, v3."""

        path = "dcim/racks/"

    class RearPortTemplatesC(Connector):
        """RearPortTemplatesC, v3."""

        path = "dcim/rear-port-templates/"

    class RearPortsC(Connector):
        """RearPortsC, v3."""

        path = "dcim/rear-ports/"

    class RegionsC(Connector):
        """RegionsC, v3."""

        path = "dcim/regions/"

    class SiteGroupsC(Connector):
        """SiteGroupsC, v3."""

        path = "dcim/site-groups/"

    class SitesC(Connector):
        """SitesC, v3."""

        path = "dcim/sites/"

    class VirtualChassisC(Connector):
        """VirtualChassisC, v3."""

        path = "dcim/virtual-chassis/"

    class VirtualDeviceContextsC(Connector):
        """VirtualDeviceContextsC, v3."""

        path = "dcim/virtual-device-contexts/"
