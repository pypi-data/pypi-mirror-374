"""Base for Application Foragers."""

from typing import Union

from nbforager import ami
from nbforager.api.circuits import CircuitsAC
from nbforager.api.core import CoreAC
from nbforager.api.dcim import DcimAC
from nbforager.api.extras import ExtrasAC
from nbforager.api.ipam import IpamAC
from nbforager.api.tenancy import TenancyAC
from nbforager.api.users import UsersAC
from nbforager.api.virtualization import VirtualizationAC
from nbforager.api.vpn import VpnAC
from nbforager.api.wireless import WirelessAC
from nbforager.nb_api import NbApi
from nbforager.nb_tree import NbTree
from nbforager.types_ import LStr

UConnector = Union[
    CircuitsAC,
    CoreAC,
    DcimAC,
    ExtrasAC,
    IpamAC,
    TenancyAC,
    UsersAC,
    VirtualizationAC,
    VpnAC,
    WirelessAC,
]


class BaseAF:
    """Base for Application Foragers."""

    def __init__(self, api: NbApi, root: NbTree, tree: NbTree):
        """Init BaseAF.

        :param root: Dictionary where data from Netbox needs to be saved.
        """
        self.api: NbApi = api
        self.root: NbTree = root
        self.tree: NbTree = tree
        self.app: str = ami.attr_name(self)
        self.connector: UConnector = getattr(api, self.app)  # connector to application

    def __repr__(self) -> str:
        """__repr__."""
        name = self.__class__.__name__
        count = self.count()
        return f"<{name}: {count}>"

    def count(self) -> int:
        """Count of the Netbox objects in the self root model.

        :return: Count of the Netbox objects.
        """
        return getattr(self.root, self.app).count()

    def get(self, nested: bool = False, **kwargs) -> None:
        """Get all objects from the Netbox, add objects to root.

        :param bool nested: True - Request base and nested objects,
            False - Request only base objects. Default is `False`.

        :param kwargs: Filtering parameters.

        :return: None. Update self object.
        """
        models: LStr = getattr(self.root, self.app).models()
        for model in models:
            getattr(self, model).get(nested=nested, **kwargs)
