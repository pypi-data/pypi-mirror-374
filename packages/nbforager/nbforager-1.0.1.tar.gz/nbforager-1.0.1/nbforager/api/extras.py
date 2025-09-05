"""Extras connectors."""

from nbforager.api.connector import Connector


class ExtrasAC:
    """Extras connectors."""

    def __init__(self, **kwargs):
        """Init ExtrasAC."""
        self.bookmarks = self.BookmarksC(**kwargs)
        self.config_contexts = self.ConfigContextsC(**kwargs)
        self.config_templates = self.ConfigTemplatesC(**kwargs)
        self.content_types = self.ContentTypesC(**kwargs)
        self.custom_field_choice_sets = self.CustomFieldChoiceSetsC(**kwargs)
        self.custom_fields = self.CustomFieldsC(**kwargs)
        self.custom_links = self.CustomLinksC(**kwargs)
        self.event_rules = self.EventRulesC(**kwargs)
        self.export_templates = self.ExportTemplatesC(**kwargs)
        self.image_attachments = self.ImageAttachmentsC(**kwargs)
        self.journal_entries = self.JournalEntriesC(**kwargs)
        self.notification_groups = self.NotificationGroupsC(**kwargs)
        self.notifications = self.NotificationsC(**kwargs)
        self.object_changes = self.ObjectChangesC(**kwargs)
        self.object_types = self.ObjectTypesC(**kwargs)
        self.reports = self.ReportsC(**kwargs)
        self.saved_filters = self.SavedFiltersC(**kwargs)
        self.scripts = self.ScriptsC(**kwargs)
        self.subscriptions = self.SubscriptionsC(**kwargs)
        self.table_configs = self.TableConfigsC(**kwargs)
        self.tagged_objects = self.TaggedObjectsC(**kwargs)
        self.tags = self.TagsC(**kwargs)
        self.webhooks = self.WebhooksC(**kwargs)

    class BookmarksC(Connector):
        """BookmarksC, v3.6."""

        path = "extras/bookmarks/"

    class ConfigContextsC(Connector):
        """ConfigContextsC, v3."""

        path = "extras/config-contexts/"

    class ConfigTemplatesC(Connector):
        """ConfigTemplatesC, v3."""

        path = "extras/config-templates/"

    class ContentTypesC(Connector):
        """ContentTypesC, v3.5, removed v3.6."""

        path = "extras/content-types/"

    class CustomFieldChoiceSetsC(Connector):
        """CustomFieldChoiceSetsC, v3.6."""

        path = "extras/custom-field-choice-sets/"

    class CustomFieldsC(Connector):
        """CustomFieldsC, v3."""

        path = "extras/custom-fields/"

    class CustomLinksC(Connector):
        """CustomLinksC, v3."""

        path = "extras/custom-links/"

    class EventRulesC(Connector):
        """EventRulesC, v3.7."""

        path = "extras/event-rules/"

    class ExportTemplatesC(Connector):
        """ExportTemplatesC, v3."""

        path = "extras/export-templates/"

    class ImageAttachmentsC(Connector):
        """ImageAttachmentsC, v3."""

        path = "extras/image-attachments/"

    class JournalEntriesC(Connector):
        """JournalEntriesC, v3."""

        path = "extras/journal-entries/"

    class NotificationGroupsC(Connector):
        """NotificationGroupsC, v4.1."""

        path = "extras/notification-groups/"

    class NotificationsC(Connector):
        """NotificationsC, v4.1."""

        path = "extras/notifications/"

    class ObjectChangesC(Connector):
        """ObjectChangesC, v3, moved to core/object-changes in v4.1."""

        path = "extras/object-changes/"

    class ObjectTypesC(Connector):
        """ObjectTypesC, v4.2."""

        path = "extras/object-types/"

    class ReportsC(Connector):
        """ReportsC, v3, deprecated v4.0."""

        path = "extras/reports/"

    class SavedFiltersC(Connector):
        """SavedFiltersC, v3."""

        path = "extras/saved-filters/"

    class ScriptsC(Connector):
        """ScriptsC, v3."""

        path = "extras/scripts/"

    class SubscriptionsC(Connector):
        """SubscriptionsC, v4.1."""

        path = "extras/subscriptions/"

    class TableConfigsC(Connector):
        """TableConfigsC, v4.3."""

        path = "extras/table-configs/"

    class TaggedObjectsC(Connector):
        """TaggedObjectsC, v4.3."""

        path = "extras/tagged-objects/"

    class TagsC(Connector):
        """TagsC, v3."""

        path = "extras/tags/"

    class WebhooksC(Connector):
        """WebhooksC, v3."""

        path = "extras/webhooks/"
