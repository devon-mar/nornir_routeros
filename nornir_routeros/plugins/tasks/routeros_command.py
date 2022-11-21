from typing import Dict

from nornir.core.task import Result, Task

from nornir_routeros.plugins.connections import CONNECTION_NAME
from nornir_routeros.utils import clean_kwargs


def routeros_command(
    task: Task, path: str, command: str, changed: bool = False, **kwargs
) -> Result:
    """
    Runs a RouterOS command such as ping or fetch.

    Args:
        path: Path to the resource.
        command: Name of the command.
        kwargs: Args for the command. A trailing '_' can be added to
                kwargs that conflict with that of Nornir's.

    Examples:
        Ping 127.0.0.1 5 times::

            nr.run(
                task=routeros_command,
                path="/",
                command="ping",
                address="127.0.0.1",
                count=5
            )
    """

    api = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
    # See https://github.com/socialwifi/RouterOS-api/issues/39
    call_args: Dict[str, bytes] = {
        str(k): str(v).encode() for k, v in clean_kwargs(kwargs).items()
    }
    result = api.get_binary_resource(path).call(command, call_args)

    return Result(host=task.host, changed=changed, result=result)
