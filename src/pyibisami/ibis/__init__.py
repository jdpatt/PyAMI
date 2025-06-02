"""IBIS model classes.

Refactored from original IBIS model classes into a more object-oriented approach.

- parser.py is responsible for parsing the IBIS file and returning a dictionary.
- gui.py is responsible for displaying the GUI and handling the user interactions
- items.py are the building blocks that make up the IBIS model. (i.e. - Component, Model, Pin, etc.)
- model.py is responsible for encapsulating the IBIS model and providing a more object-oriented approach.

To initialize an IBISModel, use the from_file or from_string class methods.

Example:

```python
ibis_model = IBISModel.from_file("ibis_model.ibs")
ibis_model.gui()
```

```python
with open("ibis_model.ibs", "r") as f:
    ibis_string = f.read()
ibis_model = IBISModel.from_string(ibis_string)
```

If you really want to, you can manually create an IBISModel object.

```python
ibis_model = IBISModel(
    filename="",
    is_tx=True,
    version=7.2,
    revision="1.0",
    date="2025-06-01",
    components={},
    models={},
    model_selectors={},
)
```
"""

from .model import IBISModel

__all__ = ["IBISModel"]
