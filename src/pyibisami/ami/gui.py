"""Dialog widgets for editing AMI parameters using PySide6.

Original author: David Banas <capn.freako@gmail.com>, David Patterson

Original date:   June 3, 2025

Copyright (c) 2025 David Banas & David Patterson; all rights reserved World wide.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .parameter import AMIParameter


class AMIParameterDialog(QDialog):
    """A dialog for editing AMI parameters using PySide6, supporting nested groups."""

    def __init__(self, name: str, params: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{name} -AMI Parameter Editor")
        self.setMinimumSize(800, 600)  # Standard minimum size
        self.widgets: dict[str, QWidget] = {}  # param name -> widget
        self.param_map: dict[str, AMIParameter] = {}  # param name -> AMIParameter
        self.main_layout = QVBoxLayout(self)
        self._add_reserved_params_groupbox(params["Reserved_Parameters"], self.main_layout)
        self.model_specific_groupbox = QGroupBox("Model Specific Parameters")
        self.model_specific_groupbox_layout = QFormLayout(self.model_specific_groupbox)
        self._build_gui(params["Model_Specific"], self.model_specific_groupbox_layout)
        self.main_layout.addWidget(self.model_specific_groupbox)
        self.main_layout.addStretch()

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

    def _add_reserved_params_groupbox(self, params: dict, parent_layout: QVBoxLayout):
        group_box = QGroupBox("Reserved Parameters")
        group_layout = QVBoxLayout(group_box)
        for pname, param in params.items():
            value = str(param.pvalue) if hasattr(param, "pvalue") else str(param)
            label = QLabel(f"{pname}: {value}")
            group_layout.addWidget(label)
        parent_layout.addWidget(group_box)

    def _build_gui(self, params: dict, parent_layout, prefix: str = ""):
        """Recursively build the GUI."""
        for pname in sorted(params.keys()):
            param = params[pname]
            full_name = f"{prefix}{pname}" if prefix == "" else f"{prefix}_{pname}"
            if isinstance(param, AMIParameter):
                if param.pusage not in ("In", "InOut"):
                    continue
                widget, label = self._make_widget_for_param(param, full_name)
                label_text = f"{label} ({param.pdescription})" if param.pdescription else label
                parent_layout.addRow(label_text, widget)
                self.widgets[full_name] = widget
                self.param_map[full_name] = param
            elif isinstance(param, dict):
                group_box = QGroupBox(pname.split("_")[-1])
                group_layout = QFormLayout(group_box)
                desc = param.get("description", None)
                if desc:
                    group_layout.addRow(QLabel(f"<i>{desc}</i>"))
                self._build_gui(param, group_layout, full_name)
                parent_layout.addRow(group_box)

    def _make_widget_for_param(self, param: AMIParameter, pname: str):
        label = pname.split("_")[-1]
        ptype = param.ptype
        pformat = param.pformat
        tooltip = param.pdescription or ""

        # Boolean is outside of the match statement because it could be encoded as a  List or Value.
        # ptype is the only true indicator of the type while the others use pformat.
        if ptype == "Boolean":
            cb_widget = QCheckBox()
            cb_widget.setChecked(bool(param.pvalue))
            cb_widget.setToolTip(tooltip)
            return cb_widget, label

        match pformat:
            case None | "Value" | "":
                lb_widget = QLabel(str(param.pvalue) if param.pvalue is not None else "")
                lb_widget.setToolTip(tooltip)
                return lb_widget, label
            case "Range":
                if ptype in ("Float", "UI"):
                    spin_widget = QDoubleSpinBox()
                    spin_widget.setMinimum(float(param.pmin))
                    spin_widget.setMaximum(float(param.pmax))
                    spin_widget.setValue(float(param.pvalue))
                    spin_widget.setToolTip(tooltip)
                    return spin_widget, label
                else:
                    slider_layout = QHBoxLayout()
                    min_label = QLabel(str(int(param.pmin)))
                    max_label = QLabel(str(int(param.pmax)))
                    value_label = QLabel(str(int(param.pvalue)))
                    value_label.setFixedWidth(20)

                    slider = QSlider(Qt.Orientation.Horizontal, tickPosition=QSlider.TickPosition.TicksBelow)
                    slider.setMinimum(int(param.pmin))
                    slider.setMaximum(int(param.pmax))
                    slider.setValue(int(param.pvalue))
                    slider.setToolTip(tooltip)

                    # Update value label when slider moves
                    slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

                    slider_layout.addWidget(min_label)
                    slider_layout.addWidget(slider)
                    slider_layout.addWidget(max_label)
                    slider_layout.addWidget(value_label)

                    widget = QWidget()
                    widget.setLayout(slider_layout)
                    widget._slider = slider  # type: ignore
                    return widget, label
            case "List":
                com_widget = QComboBox()
                items = param.plist_tip if param.plist_tip else param.pvalue
                if not items:
                    items = [str(param.pdefault)] if param.pdefault else []
                # Convert to list and remove duplicates while preserving order
                unique_items = list(dict.fromkeys(str(i) for i in items))
                com_widget.addItems(unique_items)
                if param.pdefault:
                    com_widget.setCurrentText(str(param.pdefault))
                com_widget.setToolTip(tooltip)
                return com_widget, label
            case _:
                raise ValueError(f"Unrecognized AMI parameter format: {pformat}!")

    def get_values(self) -> tuple[dict, dict]:
        """Return a dict of parameter values as currently set in the dialog, and the param_map."""
        values = {}
        for pname, widget in self.widgets.items():
            if isinstance(widget, QCheckBox):
                values[pname] = widget.isChecked()  # type: ignore
            elif isinstance(widget, QComboBox):
                values[pname] = widget.currentText()  # type: ignore
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                values[pname] = widget.value()  # type: ignore
            elif isinstance(widget, QLineEdit):
                values[pname] = widget.text()  # type: ignore
            elif isinstance(widget, QWidget) and hasattr(widget, "_slider"):
                values[pname] = widget._slider.value()  # type: ignore
        return values, self.param_map
