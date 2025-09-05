"""DataStore is used to configure Galaxy to group outputs of a tool together."""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .connection import ConnectionHelper  # Only imports for type checking

from .tool import Tool


class Datastore:
    """Groups tool outputs together.

    The constructor is not intended for external use. Use nova.galaxy.Connection.create_data_store() instead.
    """

    def __init__(self, name: str, nova_connection: "ConnectionHelper", history_id: str) -> None:
        self.name = name
        self.nova_connection = nova_connection
        self.history_id = history_id
        self.persist_store = True

    def persist(self) -> None:
        """Persist this store even after the nova connection is closed.

        Should be used carefully as tools will continue to run after even if this object is garbage collected.
        Use recover_tools() to with the same data store name to retrieve all running tools again.
        """
        self.persist_store = True

    def mark_for_cleanup(self) -> None:
        """Clean up and delete all content related to this Data Store after the associated connection is closed."""
        self.persist_store = False

    def cleanup(self) -> None:
        history = self.nova_connection.galaxy_instance.histories.get_histories(name=self.name)[0]["id"]
        self.nova_connection.galaxy_instance.histories.delete_history(history_id=history, purge=True)

    def recover_tools(self, filter_running: bool = True) -> List[Tool]:
        """Recovers all running tools in this data_store.

        Mainly used to recover all the running tools inside of this data store or any past persisted data stores that
        used the same name. Can also be used to simply get a list of all running tools in a store as well.

        Parameters
        ----------
        filter_running: bool
            If this should only recover tools that are running (true).

        Returns
        -------
            List of tools from this data store.
        """
        if filter_running:
            states = ["running", "queued"]
        else:
            states = ["running", "queued", "ok", "error"]
        jobs = self.nova_connection.galaxy_instance.jobs.get_jobs(
            state=states,  # type: ignore
            history_id=self.history_id,
        )
        tools = []
        for job in jobs:
            job_id = job["id"]
            tool_id = job["tool_id"]
            t = Tool(tool_id)
            t.assign_id(job_id, self)
            tools.append(t)
        return tools
