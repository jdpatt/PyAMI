from pyibisami.ibis.items import Component, Model, Package, Pin


def test_pin_from_tuple():
    pin = Pin.from_tuple("pin1", ("model1", (1.0, 2.0, 3.0)))
    assert pin.name == "pin1"
    assert pin.model_name == "model1"
    assert pin.rlc_pin == (1.0, 2.0, 3.0)


def test_package_from_dict():
    package = Package(resistance=1.0, capacitance=2.0, inductance=3.0)
    assert package.resistance == 1.0
    assert package.capacitance == 2.0
    assert package.inductance == 3.0
    assert str(package) == "r_pkg=1.0, c_pkg=2.0, l_pkg=3.0"


def test_component_from_dict():
    component = Component.from_dict(
        "component1",
        {
            "name": "component1",
            "package": {"r_pkg": 1.0, "c_pkg": 2.0, "l_pkg": 3.0},
            "pin": {"pin1": ("model1", (1.0, 2.0, 3.0))},
            "diff_pin": {},
        },
    )
    assert component.name == "component1"
    assert component.package.resistance == 1.0
    assert component.package.capacitance == 2.0
    assert component.package.inductance == 3.0
    assert component.pins["pin1"].name == "pin1"
    assert component.pins["pin1"].model_name == "model1"
