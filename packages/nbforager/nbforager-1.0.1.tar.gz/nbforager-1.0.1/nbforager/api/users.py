"""Users connectors."""

from nbforager.api.connector import Connector
from nbforager.types_ import DAny


class UsersAC:
    """Users connectors."""

    def __init__(self, **kwargs):
        """Init UsersAC."""
        self.config = self.ConfigC(**kwargs)
        self.groups = self.GroupsC(**kwargs)
        self.permissions = self.PermissionsC(**kwargs)
        self.tokens = self.TokensC(**kwargs)
        self.users = self.UsersC(**kwargs)

    class ConfigC(Connector):
        """ConfigC, v3."""

        path = "users/config/"

        def get(self, **kwargs) -> DAny:  # type: ignore
            """Get data."""
            _ = kwargs  # noqa
            return self._get_d()

    class GroupsC(Connector):
        """GroupsC, v3."""

        path = "users/groups/"

    class PermissionsC(Connector):
        """PermissionsC, v3."""

        path = "users/permissions/"

    class TokensC(Connector):
        """TokensC, v3."""

        path = "users/tokens/"

    class UsersC(Connector):
        """UsersC, v3."""

        path = "users/users/"
