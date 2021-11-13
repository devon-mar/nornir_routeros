import pytest

import os

from nornir import InitNornir


@pytest.fixture(scope="session")
def nr():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": f"{current_dir}/inventory/hosts.yml"
            }
        }
    )
    return nornir


@pytest.fixture(scope="session")
def nr_no_ssl():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    nornir = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": f"{current_dir}/inventory/hosts_no_ssl.yml"
            }
        }
    )
    return nornir


@pytest.fixture(scope="function", autouse=True)
def reset_hosts(nr):
    nr.data.reset_failed_hosts()
