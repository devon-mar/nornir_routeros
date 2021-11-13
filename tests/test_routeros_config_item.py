from nornir_routeros.plugins.tasks import routeros_config_item, routeros_get


def test_change_identity(nr):
    """
    A test where the item has no ID.
    """
    result = nr.run(
        task=routeros_config_item,
        path="/system/identity",
        where={},
        properties={
            "name": "{{ host.name }}"
        }
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result.result)
    assert device_result.changed is True
    assert device_result.result[0]["name"] == "router1"

    # Test idempotency
    idemp = nr.run(
        task=routeros_config_item,
        path="/system/identity",
        where={},
        properties={
            "name": "{{ host.name }}"
        }
    )
    assert len(result["router1"]) == 1
    idemp_result = idemp["router1"][0]
    assert idemp_result.failed is False, str(idemp_result.result)
    assert idemp_result.changed is False
    assert idemp_result.result[0]["name"] == "router1"


def test_address_list(nr):
    result = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        properties={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        add_if_missing=True
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result.result)
    assert device_result.changed is True

    idemp = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        properties={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        add_if_missing=False
    )
    assert len(idemp["router1"]) == 1
    idemp_result = idemp["router1"][0]
    assert idemp_result.failed is False, str(idemp_result.result)
    assert idemp_result.changed is False

    update = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        properties={
            "address": "10.0.0.0/16",
            "list": "RFC1918"
        },
        add_if_missing=False
    )
    assert len(update["router1"]) == 1
    update_result = update["router1"][0]
    assert update_result.failed is False, str(update_result.result)
    assert update_result.changed is True

    verify = nr.run(
        task=routeros_get,
        path="/ip/firewall/address-list",
        address="10.0.0.0/16",
        list="RFC1918"
    )
    assert len(verify["router1"].result) == 1

    delete = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/16",
            "list": "RFC1918"
        }
    )
    assert len(delete["router1"]) == 1
    delete_result = delete["router1"][0]
    assert delete_result.failed is False, str(delete_result.result)
    assert delete_result.changed is True

    delete_idemp = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/16",
            "list": "RFC1918"
        }
    )
    assert delete["router1"].failed is False
    assert delete["router1"].changed is False


def test_add_if_missing_false_failure(nr):
    no_add_failure = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        properties={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        },
        add_if_missing=False
    )
    assert len(no_add_failure["router1"]) == 1
    no_add_result = no_add_failure["router1"][0]
    assert no_add_result.failed is True, str(no_add_result.result)
    assert no_add_result.changed is False


def test_empty_jinja2_template_value_error(nr):
    result = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "172.16.0.0/12",
            "list": "RFC1918"
        },
        properties={
            "address": "{{ '' }}",
            "list": "RFC1918"
        },
        add_if_missing=True
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is True
    assert "ValueError: " in device_result.result


def test_dry_run(nr_dry_run):
    result = nr_dry_run.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "192.168.0.0/16",
            "list": "dry-run-test"
        },
        properties={
            "address": "192.168.0.0/16",
            "list": "dry-run-test"
        },
        add_if_missing=True
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, device_result.result
    assert device_result.changed is True

    get = nr_dry_run.run(
        task=routeros_get,
        path="/ip/firewall/address-list",
        address="192.168.0.0/16"
    )
    assert len(get["router1"]) == 1
    assert len(get["router1"].result) == 0
