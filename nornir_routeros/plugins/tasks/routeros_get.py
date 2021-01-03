from nornir.core.task import Result, Task
from nornir_routeros.plugins.connections import CONNECTION_NAME


def routeros_get(
    task: Task,
    path: str
) -> Result:
    """
    Returns a RouterOS resource.

    Args:
        path: Path to the resource. Example: /ip/firewall/filter for firewall filters.

    Returns:
        Result: A ``Result`` with result set to the item(s) under the given path.

    Examples:
        Get RouterBoard information::

            nr.run(
                task=routeros_get,
                path="/system/routerboard"
            )
    """

    api = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
    result = api.get_resource(path).get()

    return Result(
        host=task.host,
        changed=False,
        result=result
    )
