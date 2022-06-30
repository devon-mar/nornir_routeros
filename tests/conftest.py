import pytest

import os

from nornir import InitNornir


@pytest.fixture(scope="session")
def nr():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {"host_file": f"{current_dir}/inventory/hosts.yml"},
        },
    )
    yield nornir
    nornir.close_connections()


@pytest.fixture(scope="session")
def nr_dry_run():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        dry_run=True,
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {"host_file": f"{current_dir}/inventory/hosts.yml"},
        },
    )
    yield nornir
    nornir.close_connections()


@pytest.fixture(scope="session")
def nr_no_ssl():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {"host_file": f"{current_dir}/inventory/hosts_no_ssl.yml"},
        },
    )
    yield nornir
    nornir.close_connections()


@pytest.fixture(scope="session")
def nr_ssl_failure():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {"host_file": f"{current_dir}/inventory/hosts_ssl_failure.yml"},
        },
    )
    yield nornir
    nornir.close_connections()


@pytest.fixture(scope="session")
def nr_ssl_verify_false():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": f"{current_dir}/inventory/hosts_ssl_verify_false.yml"
            },
        },
    )
    yield nornir
    nornir.close_connections()


@pytest.fixture(scope="function", autouse=True)
def reset_hosts(nr):
    nr.data.reset_failed_hosts()
