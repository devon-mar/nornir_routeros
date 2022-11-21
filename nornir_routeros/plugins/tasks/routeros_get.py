from nornir.core.task import Result, Task

from nornir_routeros.plugins.connections import CONNECTION_NAME
from nornir_routeros.utils import clean_kwargs


def routeros_get(task: Task, path: str, **kwargs) -> Result:
    """
    Returns a RouterOS resource.
    For kwargs such as ``name`` that conflict with Nornir's, append an underscore.

    Args:
        path: Path to the resource. Example: /ip/firewall/filter for firewall filters.
        kwargs: Filter results by the given kwargs. A trailing '_' can be added to
                kwargs that conflict with that of Nornir's.

    Returns:
        Result: A ``Result`` with result set to the item(s) under the given path.

    Examples:
        Get RouterBoard information::

            nr.run(
                task=routeros_get,
                path="/system/routerboard"
            )

        Get non-dynamic addresses::

            nr.run(
                task=routeros_get,
                path="/ip/address",
                dynamic="false"
            )
    """

    api = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
    result = api.get_resource(path).get(**clean_kwargs(kwargs))

    return Result(host=task.host, changed=False, result=result)
