from nornir_routeros.plugins.tasks import routeros_get


def test_routeros_get(nr):
    result = nr.run(task=routeros_get, path="/system/resource")
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False
    assert device_result.changed is False
    assert "platform" in device_result.result[0]
    assert device_result.result[0]["platform"] == "MikroTik"


def test_get_with_name(nr):
    result = nr.run(task=routeros_get, path="/ip/service", name_="www")
    assert len(result["router1"]) == 1
    host_result = result["router1"][0]
    assert host_result.failed is False
    assert host_result.changed is False
    assert host_result.result[0]["name"] == "www"
