from nornir_routeros.plugins.tasks import routeros_get


def test_no_ssl(nr_ssl_verify_false):
    result = nr_ssl_verify_false.run(task=routeros_get, path="/system/identity")
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is False, str(device_result.result)
    assert device_result.changed is False
