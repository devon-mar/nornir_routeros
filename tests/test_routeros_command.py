from nornir.core import Nornir

from nornir_routeros.plugins.tasks import routeros_command


def test_routeros_command_ping(nr: Nornir) -> None:
    result = nr.run(
        task=routeros_command, path="/", command="ping", address="127.0.0.1", count=5
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result.result)
    assert device_result.changed is False


def test_routeros_command_backup(nr: Nornir) -> None:
    result = nr.run(
        task=routeros_command, path="/system/backup", command="save", name="backup.rsc"
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result.result)
    assert device_result.changed is False


def test_routeros_command_with_dashes(nr: Nornir) -> None:
    result = nr.run(
        task=routeros_command,
        path="/",
        command="ping",
        address="127.0.0.1",
        count=5,
        # Corresponds to do-not-fragment
        do_not_fragment="true",
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result.result)
    assert device_result.changed is False
