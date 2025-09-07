from symmorademo.core import get_hello, symmora_add

def test_get_hello_default():
    assert get_hello() == "***** version 2 *** : Hello, Symmora World!!!"

def  test_get_hello_custom_001():
    assert get_hello("Victoria") == "***** version 2 *** : Hello, Victoria!!!"

def test_symmora_add_001():
    assert symmora_add(7, 5) == 12
    assert symmora_add(-1, 1) == 0
    assert symmora_add(0, 0) == 0

