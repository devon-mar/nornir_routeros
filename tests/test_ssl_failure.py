from nornir_routeros.plugins.tasks import routeros_get


def test_ssl_failure(nr_ssl_failure):
    result = nr_ssl_failure.run(task=routeros_get, path="/system/identity")
    assert len(result["router1"]) == 1
    device_result = result["router1"][0]
    assert device_result.failed is True
