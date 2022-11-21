from nornir_routeros.utils import clean_kwargs


def test_clean_kwargs():
    in_ = {"name_": "abc", "foo": "bar"}
    want = {"name": "abc", "foo": "bar"}

    assert clean_kwargs(in_) == want
