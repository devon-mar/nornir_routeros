from nornir_routeros.plugins.tasks import routeros_config_item


def test_change_identity(nr):
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

    delete = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={
            "address": "10.0.0.0/8",
            "list": "RFC1918"
        }
    )
    assert len(delete["router1"]) == 1
    delete_result = delete["router1"][0]
    assert delete_result.failed is False, str(delete_result.result)
    assert delete_result.changed is True

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
