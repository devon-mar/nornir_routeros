from typing import Dict
from nornir.core.task import Result, Task
from nornir_routeros.plugins.connections import CONNECTION_NAME


def routeros_command(
    task: Task,
    path: str,
    command: str,
    command_args: Dict[str, str] = {},
    changed: bool = False,
) -> Result:
    """
    Runs a RouterOS command such as ping or fetch.

    Args:
        path: Path to the resource.
        command: Name of the command.
        kwargs: Args for the command.

    Examples:
        Ping 192.0.2.1 4 times::

            nr.run(
                task=routeros_command,
                path="/",
                command="ping",
                address="192.0.2.1",
                count="4"
            )
    """

    api = task.host.get_connection(CONNECTION_NAME, task.nornir.config)
    # See https://github.com/socialwifi/RouterOS-api/issues/39
    call_args: Dict[str, bytes] = {str(k): v.encode() for k, v in command_args.items()}
    result = api.get_binary_resource(path).call(command, call_args)

    return Result(
        host=task.host,
        changed=changed,
        result=result
    )
