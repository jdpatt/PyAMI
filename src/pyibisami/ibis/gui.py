"""Dialog widgets for viewing and selecting IBIS models, components, and pins.

Removed any references to PyBERT since this could in standalone or incorporated into a different application.
"""

from typing import TYPE_CHECKING

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from .model import IBISModel, Model


class IBISModelView(QDialog):
    """A PySide6 dialog for viewing an IBIS model's details."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, model: "Model", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"IBIS Model Viewer: {model.name}")
        self.model = model
        self._init_ui()
        self._populate_fields()

    def _init_ui(self):
        """Initialize the UI for the IBIS Model View."""
        # pylint: disable=too-many-statements
        layout = QVBoxLayout(self)

        # Model type (readonly)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Model type:"))
        self.model_type_label = QLabel()
        self.model_type_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row1.addWidget(self.model_type_label)
        layout.addLayout(row1)

        # Ccomp (readonly)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Ccomp:"))
        self.ccomp_label = QLabel()
        self.ccomp_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row2.addWidget(self.ccomp_label)
        layout.addLayout(row2)

        # Temperature Range (readonly)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Temperature Range:"))
        self.trange_label = QLabel()
        self.trange_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row3.addWidget(self.trange_label)
        layout.addLayout(row3)

        # Voltage Range (readonly)
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Voltage Range:"))
        self.vrange_label = QLabel()
        self.vrange_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row4.addWidget(self.vrange_label)
        layout.addLayout(row4)

        # Horizontal group: Cref, Vref, Vmeas, Rref
        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Cref:"))
        self.cref_label = QLabel()
        self.cref_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row5.addWidget(self.cref_label)
        row5.addWidget(QLabel("Vref:"))
        self.vref_label = QLabel()
        self.vref_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row5.addWidget(self.vref_label)
        row5.addWidget(QLabel("Vmeas:"))
        self.vmeas_label = QLabel()
        self.vmeas_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row5.addWidget(self.vmeas_label)
        row5.addWidget(QLabel("Rref:"))
        self.rref_label = QLabel()
        self.rref_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row5.addWidget(self.rref_label)
        layout.addLayout(row5)

        # Output/I/O or Input specific fields
        self.extra_fields_layout = QVBoxLayout()
        layout.addLayout(self.extra_fields_layout)

        # Horizontal divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider)

        # Horizontal group: IV Plot, Algorithmic Model
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Impedance (Ohms):"))
        self.impedance_label = QLabel("")
        self.impedance_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row6.addWidget(self.impedance_label)
        row6.addWidget(QLabel("Slew Rate (V/ns):"))
        self.slew_rate_label = QLabel("")
        self.slew_rate_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row6.addWidget(self.slew_rate_label)
        layout.addLayout(row6)

        # IV Plot using pyqtgraph
        self.iv_plot = pg.PlotWidget()
        self.iv_plot.setBackground("w")
        self.iv_plot.setMinimumHeight(300)
        self.iv_plot.showGrid(x=True, y=True)
        layout.addWidget(self.iv_plot)
        self.iv_plot.setMouseEnabled(False, False)
        self.iv_plot.addLegend()
        self.iv_plot.hideButtons()

        # OK button
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        layout.addWidget(self.button_box)

    def _populate_fields(self):
        self.model_type_label.setText(str(self.model.mtype))
        self.ccomp_label.setText(str(self.model.ccomp))
        self.trange_label.setText(str(self.model.temperature_range))
        self.vrange_label.setText(str(self.model.voltage_range))
        self.cref_label.setText(str(self.model.cref))
        self.vref_label.setText(str(self.model.vref))
        self.vmeas_label.setText(str(self.model.vmeas))
        self.rref_label.setText(str(self.model.rref))
        self.impedance_label.setText(str(round(self.model.impedance, 2)))

        mtype = self.model.mtype.lower()
        if mtype in ("output", "i/o"):
            self.slew_rate_label.setText(str(round(self.model.slew, 2)))
            self.generate_output_iv_plot()
        elif mtype == "input":
            self.generate_input_iv_plot()

    def generate_output_iv_plot(self):
        """Generate the output I-V plot."""
        plotdata = self.model.plot_data
        self.iv_plot.clear()
        self.iv_plot.plot(
            plotdata["pd_vs"], plotdata["pd_ityps"], pen=pg.mkPen("b", style=Qt.SolidLine), name="PD-Typ"
        )
        self.iv_plot.plot(plotdata["pd_vs"], plotdata["pd_imins"], pen=pg.mkPen("b", style=Qt.DotLine), name="PD-Min")
        self.iv_plot.plot(plotdata["pd_vs"], plotdata["pd_imaxs"], pen=pg.mkPen("b", style=Qt.DashLine), name="PD-Max")
        self.iv_plot.plot(
            plotdata["pu_vs"], plotdata["pu_ityps"], pen=pg.mkPen("r", style=Qt.SolidLine), name="PU-Typ"
        )
        self.iv_plot.plot(plotdata["pu_vs"], plotdata["pu_imins"], pen=pg.mkPen("r", style=Qt.DotLine), name="PU-Min")
        self.iv_plot.plot(plotdata["pu_vs"], plotdata["pu_imaxs"], pen=pg.mkPen("r", style=Qt.DashLine), name="PU-Max")
        self.iv_plot.setTitle("Pull-Up/Down I-V Curves")
        self.iv_plot.getAxis("left").setLabel("Iout (A)")
        self.iv_plot.getAxis("bottom").setLabel("Vout (V)")
        self.iv_plot.setRange(
            xRange=[0, self.model.voltage_range[0]], yRange=[0, 0.1]
        )  # pylint: disable=unexpected-keyword-arg

    def generate_input_iv_plot(self):
        """Generate the input I-V plot."""
        plotdata = self.model.plot_data
        self.iv_plot.clear()
        if self.model.gnd_clamp:
            self.iv_plot.plot(
                plotdata["gc_vs"], plotdata["gc_ityps"], pen=pg.mkPen("b", style=Qt.SolidLine), name="PD-Typ"
            )
            self.iv_plot.plot(
                plotdata["gc_vs"], plotdata["gc_imins"], pen=pg.mkPen("b", style=Qt.DotLine), name="PD-Min"
            )
            self.iv_plot.plot(
                plotdata["gc_vs"], plotdata["gc_imaxs"], pen=pg.mkPen("b", style=Qt.DashLine), name="PD-Max"
            )
        if self.model.power_clamp:
            self.iv_plot.plot(
                plotdata["pc_vs"], plotdata["pc_ityps"], pen=pg.mkPen("r", style=Qt.SolidLine), name="PU-Typ"
            )
            self.iv_plot.plot(
                plotdata["pc_vs"], plotdata["pc_imins"], pen=pg.mkPen("r", style=Qt.DotLine), name="PU-Min"
            )
            self.iv_plot.plot(
                plotdata["pc_vs"], plotdata["pc_imaxs"], pen=pg.mkPen("r", style=Qt.DashLine), name="PU-Max"
            )
        self.iv_plot.setTitle("Power/GND Clamp I-V Curves")
        self.iv_plot.getAxis("left").setLabel("Iin (A)")
        self.iv_plot.getAxis("bottom").setLabel("Vin (V)")
        self.iv_plot.setRange(
            xRange=[0, self.model.voltage_range[0]], yRange=[0, 0.1]
        )  # pylint: disable=unexpected-keyword-arg


class IBISModelSelector(QDialog):
    """A PySide6 dialog for selecting an IBIS model, component, and pin dynamically."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, ibis_model: "IBISModel", parent=None):
        super().__init__(parent)
        self.setWindowTitle("IBIS Model Selector")
        self.ibis_model = ibis_model
        self._init_ui()
        self._populate_fields()
        self._connect_signals()

    def _init_ui(self):
        """Initialize the UI for the IBIS Model Selector."""
        # pylint: disable=too-many-statements
        layout = QVBoxLayout(self)

        # First row: File name (readonly), spring, rev (readonly)
        row1 = QHBoxLayout()
        self.file_name_label = QLabel()
        self.file_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row1.addWidget(QLabel("File name:"))
        row1.addWidget(self.file_name_label)
        row1.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row1.addWidget(QLabel("rev:"))
        self.file_rev_label = QLabel()
        self.file_rev_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row1.addWidget(self.file_rev_label)
        layout.addLayout(row1)

        # Second row: IBIS ver (readonly), spring, Date (readonly)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("IBIS ver:"))
        self.ibis_ver_label = QLabel()
        self.ibis_ver_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row2.addWidget(self.ibis_ver_label)
        row2.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row2.addWidget(QLabel("Date:"))
        self.date_label = QLabel()
        self.date_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        row2.addWidget(self.date_label)
        layout.addLayout(row2)

        # Third row: Component, Pin, Model (all dropdowns)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Component:"))
        self.comp_combo = QComboBox()
        row3.addWidget(self.comp_combo)
        row3.addWidget(QLabel("Pin:"))
        self.pin_combo = QComboBox()
        row3.addWidget(self.pin_combo)
        row3.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        row3.addWidget(self.model_combo)
        self.view_model_button = QPushButton("View Model")
        row3.addWidget(self.view_model_button)
        layout.addLayout(row3)

        # --- Horizontal divider ---
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider)

        # --- Component fields (readonly) ---
        component_row = QVBoxLayout()
        comp_row1 = QHBoxLayout()
        comp_row1.addWidget(QLabel("Manufacturer:"))
        self.manufacturer_label = QLabel()
        self.manufacturer_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        comp_row1.addWidget(self.manufacturer_label)
        component_row.addLayout(comp_row1)

        comp_row2 = QHBoxLayout()
        comp_row2.addWidget(QLabel("Package:"))
        self.package_label = QLabel()
        self.package_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        comp_row2.addWidget(self.package_label)
        component_row.addLayout(comp_row2)
        layout.addLayout(component_row)

        # OK/Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        layout.addStretch()

    def _populate_fields(self):
        """Populate the fields for the IBIS Model Selector."""
        self.file_name_label.setText(str(getattr(self.ibis_model, "filename", "")))
        self.file_rev_label.setText(str(getattr(self.ibis_model, "revision", "")))
        self.ibis_ver_label.setText(str(getattr(self.ibis_model, "version", "")))
        self.date_label.setText(str(getattr(self.ibis_model, "date", "")))
        # Populate component combo
        self.comp_combo.blockSignals(True)
        self.comp_combo.clear()
        components = list(self.ibis_model.components.keys())
        self.comp_combo.addItems(components)
        self.comp_combo.setCurrentText(self.ibis_model.current_component.name)
        self.comp_combo.blockSignals(False)
        self._update_pins()
        self._update_models()
        self._update_component_fields()

    def _connect_signals(self):
        """Connect the signals for the IBIS Model Selector."""
        self.comp_combo.currentTextChanged.connect(self._on_component_changed)
        self.pin_combo.currentTextChanged.connect(self._on_pin_changed)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        self.view_model_button.clicked.connect(self._on_view_model_clicked)

    def _on_component_changed(self, comp_name):
        """Update the pins and models when the component changes."""
        if comp_name in self.ibis_model.components:
            setattr(self.ibis_model, "current_component", comp_name)
            self._update_pins()
            self._update_models()
            self._update_component_fields()

    def _on_pin_changed(self, pin_name):
        """Update the models when the pin changes."""
        if pin_name in self.ibis_model.pins:
            setattr(self.ibis_model, "current_pin", pin_name)
            self._update_models()

    def _on_model_changed(self, model_name):
        """Update the current model when the model changes."""
        if model_name and model_name != "Select model...":
            try:
                setattr(self.ibis_model, "current_model", model_name)
            except AttributeError:
                pass

    def _on_view_model_clicked(self):
        """Open the IBIS Model View GUI."""
        self.ibis_model.current_model.gui()

    def _update_pins(self):
        """Update the pins for the IBIS Model Selector."""
        pins = list(self.ibis_model.pins.keys())
        self.pin_combo.blockSignals(True)
        self.pin_combo.clear()
        self.pin_combo.addItems(pins)
        self.pin_combo.setCurrentText(self.ibis_model.current_pin.name)
        self.pin_combo.blockSignals(False)

    def _update_models(self):
        """Update the models for the IBIS Model Selector."""
        model_names = self.ibis_model.get_models(self.ibis_model.current_pin.model_name)
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        current_model_name = getattr(self.ibis_model.current_model, "name", None)

        self.model_combo.addItems(model_names)
        self.model_combo.setCurrentText(current_model_name)
        self.model_combo.blockSignals(False)

    def _update_component_fields(self):
        """Update the component fields for the IBIS Model Selector."""
        comp = self.ibis_model.current_component
        self.manufacturer_label.setText(str(getattr(comp, "manufacturer", "")))
        self.package_label.setText(str(getattr(comp, "package", "")))
