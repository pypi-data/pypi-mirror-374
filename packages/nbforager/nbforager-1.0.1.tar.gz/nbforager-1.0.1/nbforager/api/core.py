"""Core connectors."""

from nbforager.api.connector import Connector


class CoreAC:
    """Core connectors."""

    def __init__(self, **kwargs):
        """Init CoreAC."""
        self.background_queues = self.BackgroundQueuesC(**kwargs)
        self.background_tasks = self.BackgroundTasksC(**kwargs)
        self.background_workers = self.BackgroundWorkersC(**kwargs)
        self.data_files = self.DataFilesC(**kwargs)
        self.data_sources = self.DataSourcesC(**kwargs)
        self.jobs = self.JobsC(**kwargs)
        self.object_changes = self.ObjectChangesC(**kwargs)

    class BackgroundQueuesC(Connector):
        """BackgroundQueuesC, v4.2."""

        path = "core/background-queues/"

    class BackgroundTasksC(Connector):
        """BackgroundTasksC, v4.2."""

        path = "core/background-tasks/"

    class BackgroundWorkersC(Connector):
        """BackgroundWorkersC, v4.2."""

        path = "core/background-workers/"

    class DataFilesC(Connector):
        """DataFilesC, v3."""

        path = "core/data-files/"

    class DataSourcesC(Connector):
        """DataSourcesC, v3."""

        path = "core/data-sources/"

    class JobsC(Connector):
        """JobsC, v3."""

        path = "core/jobs/"

    class ObjectChangesC(Connector):
        """ObjectChangesC, v4.1."""

        path = "core/object-changes/"
