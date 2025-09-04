"""Tenancy connectors."""

from nbforager.api.connector import Connector


class TenancyAC:
    """Tenancy connectors."""

    def __init__(self, **kwargs):
        """Init TenancyAC."""
        self.contact_assignments = self.ContactAssignmentsC(**kwargs)
        self.contact_groups = self.ContactGroupsC(**kwargs)
        self.contact_roles = self.ContactRolesC(**kwargs)
        self.contacts = self.ContactsC(**kwargs)
        self.tenant_groups = self.TenantGroupsC(**kwargs)
        self.tenants = self.TenantsC(**kwargs)

    class ContactAssignmentsC(Connector):
        """ContactAssignmentsC, v3."""

        path = "tenancy/contact-assignments/"

    class ContactGroupsC(Connector):
        """ContactGroupsC, v3."""

        path = "tenancy/contact-groups/"

    class ContactRolesC(Connector):
        """ContactRolesC, v3."""

        path = "tenancy/contact-roles/"

    class ContactsC(Connector):
        """ContactsC, v3."""

        path = "tenancy/contacts/"

    class TenantGroupsC(Connector):
        """TenantGroupsC, v3."""

        path = "tenancy/tenant-groups/"

    class TenantsC(Connector):
        """TenantsC, v3."""

        path = "tenancy/tenants/"
