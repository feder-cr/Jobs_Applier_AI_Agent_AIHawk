def test_package_imports_and_has_version():
    import aihawk
    assert isinstance(aihawk.__version__, str) and aihawk.__version__
