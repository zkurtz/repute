from repute.data import Package


def test_package():
    package = Package(name="repute", version="0.1.0")
    assert package.name == "repute"
    assert package.version == "0.1.0"
    assert str(package) == "repute__0.1.0"
    assert package.dict == {"name": "repute", "version": "0.1.0"}
