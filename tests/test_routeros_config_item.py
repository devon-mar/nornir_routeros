from nornir.core import Nornir

from nornir_routeros.plugins.tasks import routeros_config_item, routeros_get


def test_change_identity(nr: Nornir) -> None:
    """
    A test where the item has no ID.
    """
    result = nr.run(
        task=routeros_config_item,
        path="/system/identity",
        where={},
        properties={"name": "{{ host.name }}"},
        template_property_values=True,
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, repr(device_result.result)
    assert device_result.changed is True
    assert device_result.result["name"] == "router1"

    # Test idempotency
    idemp = nr.run(
        task=routeros_config_item,
        path="/system/identity",
        where={},
        properties={"name": "{{ host.name }}"},
        template_property_values=True,
    )
    assert len(result["router1"]) == 1
    idemp_result = idemp["router1"][0]
    assert idemp_result.failed is False, repr(idemp_result.result)
    assert idemp_result.changed is False
    assert isinstance(idemp_result.result, dict)
    assert idemp_result.result["name"] == "router1"


def test_address_list(nr: Nornir) -> None:
    result = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "10.0.0.0/8", "list": "test1"},
        properties={"address": "10.0.0.0/8", "list": "test1"},
        add_if_missing=True,
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result)
    assert device_result.changed is True
    assert isinstance(device_result.result, dict)
    assert device_result.result["address"] == "10.0.0.0/8"

    idemp = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "10.0.0.0/8", "list": "test1"},
        properties={"address": "10.0.0.0/8", "list": "test1"},
        add_if_missing=False,
    )
    assert len(idemp["router1"]) == 1
    idemp_result = idemp["router1"][0]
    assert idemp_result.failed is False, str(idemp_result.result)
    assert idemp_result.changed is False
    assert isinstance(idemp_result.result, dict)
    assert idemp_result.result["address"] == "10.0.0.0/8"

    update = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        properties={"address": "10.0.0.0/16", "list": "test1"},
        where={"list": "test1"},
        add_if_missing=False,
    )
    assert len(update["router1"]) == 1
    update_result = update["router1"][0]
    assert update_result.failed is False, str(update_result.result)
    assert update_result.changed is True
    assert isinstance(update_result.result, dict)
    assert update_result.result["address"] == "10.0.0.0/16"

    verify = nr.run(
        task=routeros_get,
        path="/ip/firewall/address-list",
        address="10.0.0.0/16",
        list="test1",
    )
    assert len(verify["router1"].result) == 1

    delete = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        properties=None,
        where={"list": "test1"},
    )
    assert len(delete["router1"]) == 1
    delete_result = delete["router1"][0]
    assert delete_result.failed is False, repr(delete_result.result)
    assert delete_result.changed is True
    assert isinstance(delete_result.result, dict), repr(delete_result.result)
    assert delete_result.result["address"] == "10.0.0.0/16"

    delete_idemp = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        properties=None,
        where={"list": "test1"},
    )
    assert delete_idemp["router1"].failed is False
    assert delete_idemp["router1"].changed is False
    assert delete_idemp["router1"].result is None


def test_add_if_missing_false_failure(nr: Nornir) -> None:
    no_add_failure = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "10.0.0.0/8", "list": "RFC1918"},
        properties={"address": "10.0.0.0/8", "list": "RFC1918"},
        add_if_missing=False,
    )
    assert len(no_add_failure["router1"]) == 1
    no_add_result = no_add_failure["router1"][0]
    assert no_add_result.failed is True, str(no_add_result.result)
    assert no_add_result.changed is False


def test_empty_jinja2_template_value_error(nr: Nornir) -> None:
    result = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "172.16.0.0/12", "list": "RFC1918"},
        properties={"address": "{{ '' }}", "list": "RFC1918"},
        add_if_missing=True,
        template_property_values=True,
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is True
    assert "ValueError: " in device_result.result


def test_no_template(nr: Nornir) -> None:
    result = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.0/24", "list": "no-template"},
        properties={
            "address": "192.0.2.0/24",
            "list": "no-template",
            # If jinja2 was enabled, we should get an error since this is falsey
            "comment": "",
        },
        add_if_missing=True,
    )
    assert len(result["router1"]) == 1
    assert result["router1"].failed is False
    assert result["router1"].changed is True


def test_add_dry_run(nr_dry_run):
    result = nr_dry_run.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.168.0.0/16", "list": "dry-run-test"},
        properties={"address": "192.168.0.0/16", "list": "dry-run-test"},
        add_if_missing=True,
    )
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, device_result.result
    assert device_result.changed is True
    assert device_result.result is None

    get = nr_dry_run.run(
        task=routeros_get, path="/ip/firewall/address-list", address="192.168.0.0/16"
    )
    assert len(get["router1"]) == 1
    assert len(get["router1"].result) == 0


def test_delete_dry_run(nr: Nornir, nr_dry_run: Nornir) -> None:
    add = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.0/24", "list": "delete-dry"},
        properties={"address": "192.0.2.0/24", "list": "delete-dry"},
        add_if_missing=True,
    )
    assert add["router1"].failed is False, repr(add["router1"].result)
    assert add["router1"].changed is True

    delete = nr_dry_run.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        properties=None,
        where={"address": "192.0.2.0/24", "list": "delete-dry"},
    )
    assert len(delete["router1"]) == 1
    delete_result = delete["router1"][0]
    assert delete_result.failed is False, delete_result.result
    assert delete_result.changed is True
    result = delete_result.result
    assert isinstance(result, dict)
    assert result["address"] == "192.0.2.0/24"

    verify = nr.run(
        task=routeros_get,
        path="/ip/firewall/address-list",
        address="192.0.2.0/24",
        list="delete-dry",
    )
    assert len(verify["router1"].result) == 1


def test_delete_gt_1(nr: Nornir, nr_dry_run: Nornir) -> None:
    add = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.1", "list": "delete-gt1"},
        properties={"address": "192.0.2.1", "list": "delete-gt1"},
        add_if_missing=True,
    )
    assert add["router1"].failed is False, repr(add["router1"].result)
    assert add["router1"].changed is True

    add = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.2", "list": "delete-gt1"},
        properties={"address": "192.0.2.2", "list": "delete-gt1"},
        add_if_missing=True,
    )
    assert add["router1"].failed is False, repr(add["router1"].result)
    assert add["router1"].changed is True

    delete = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"list": "delete-gt1"},
        properties=None,
    )
    assert delete["router1"].failed is True, repr(delete["router1"].result)
    assert "ValueError: Expected 1" in delete["router1"].result

    delete = nr_dry_run.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"list": "delete-gt1"},
        properties=None,
    )
    assert delete["router1"].failed is True, repr(delete["router1"].result)
    assert "ValueError: Expected 1" in delete["router1"].result


def test_add_values_changed(nr: Nornir) -> None:
    add = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        # RouterOS will strip the 32
        where={"address": "192.0.2.123/32", "list": "add-values-changed"},
        properties={"address": "192.0.2.123/32", "list": "add-values-changed"},
        add_if_missing=True,
    )
    assert add["router1"].failed is True, repr(add["router1"].result)
    assert "ValueError: Expected 1" in add["router1"].result


def test_update_values_changed(nr: Nornir) -> None:
    add = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.123", "list": "update-values-changed"},
        properties={"address": "192.0.2.123", "list": "update-values-changed"},
        add_if_missing=True,
    )
    assert add["router1"].failed is False, repr(add["router1"].result)
    assert add["router1"].changed is True

    update = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        # Changing to a value that doesn't match the where
        properties={"address": "192.0.2.124", "list": "update-values-changed"},
        where={"address": "192.0.2.123", "list": "update-values-changed"},
    )
    assert update["router1"].failed is True, repr(update["router1"].result)
    assert "ValueError: Expected 1" in update["router1"].result


def test_update_dry_run(nr: Nornir, nr_dry_run: Nornir) -> None:
    add = nr.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.0/24", "list": "update-dry"},
        properties={"address": "192.0.2.0/24", "list": "update-dry"},
        add_if_missing=True,
    )
    assert add["router1"].failed is False, add["router1"].result
    assert add["router1"].changed is True
    result = add["router1"].result
    assert isinstance(result, dict), repr(result)
    assert result["address"] == "192.0.2.0/24"

    update = nr_dry_run.run(
        task=routeros_config_item,
        path="/ip/firewall/address-list",
        where={"address": "192.0.2.0/24", "list": "update-dry"},
        properties={"address": "192.0.2.0/25", "list": "update-dry"},
        add_if_missing=False,
    )
    assert "router1" in update
    assert update["router1"].failed is False, update["router1"].result
    assert update["router1"].changed is True
    result = update["router1"].result
    assert isinstance(result, dict), repr(result)
    # Should still be 24 because this is dry run.
    assert result["address"] == "192.0.2.0/24"

    verify = nr.run(
        task=routeros_get,
        path="/ip/firewall/address-list",
        address="192.0.2.0/25",
        list="update-dry",
    )
    assert len(verify["router1"].result) == 0

    # Verify that the original is still there
    verify2 = nr.run(
        task=routeros_get,
        path="/ip/firewall/address-list",
        address="192.0.2.0/24",
        list="update-dry",
    )
    assert len(verify2["router1"].result) == 1
