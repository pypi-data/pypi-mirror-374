#!/usr/bin/env python3
#
# Copyright (c) 2016-2017, 2019-2025 eGauge Systems LLC
# 	4805 Sterling Dr, Suite 1
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#  All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import argparse
import logging
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import egauge.ctid as ctid
import importlib_metadata
import importlib_resources
import pexpect
from egauge.pyside import terminal
from pexpect import fdpexpect
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from ctid_programmer import (
    preferences,
    sensor_params,
    sn,
    sn_egauge,
    sn_local,
    template,
)
from ctid_programmer.gui.main_window import Ui_MainWindow
from ctid_programmer.gui.param_ct import Ui_Param_CT
from ctid_programmer.gui.param_linear import Ui_Param_Linear
from ctid_programmer.gui.param_ntc import Ui_Param_NTC
from ctid_programmer.gui.param_pulse import Ui_Param_Pulse
from ctid_programmer.gui.param_temp import Ui_Param_Temp
from ctid_programmer.gui.preferences_dialog import Ui_Preferences_Dialog
from ctid_programmer.gui.template_dialog import Ui_Template_Dialog

PACKAGE_NAME = "CTid-programmer"
PACKAGE_VERSION = importlib_metadata.version("CTid-programmer")
VERSION_INFO = f"""{PACKAGE_NAME} {PACKAGE_VERSION}
Copyright (c) 2018-2025 eGauge Systems LLC
License MIT: <https://opensource.org/licenses/MIT>.
This is free software: you are free to change and redistribute it.

Written by Alexandra Kaufhold and David Mosberger."""

PATH_AVRDUDE = "avrdude"
PATH_CTID_ENCODER = "ctid-encoder"

CTID_STATE_PATH = Path.home() / ".CTid"

CMD_AVRDUDE = [PATH_AVRDUDE, "-b", "300000", "-ctc2030"]

SENSOR_LONG_NAME = {
    "AC": "AC Current Sensor",
    "DC": "DC Current Sensor",
    "RC": "Rogowski Coil Sensor",
    "linear": "Linear Sensor",
    "temp": "Linear Temperature Sensor",
    "NTC": "NTC Thermistor Sensor",
    "pulse": "Pulse Sensor",
}

# Filename of template to use for each sensor-type:
CODE_TEMPLATE = {"AC": "ac.hex", "RC": "ac.hex"}

CHIP_ID_TO_NAME = {0x1E9008: ("t9", "ATtiny9"), 0x1E9003: ("t10", "ATtiny10")}


class CommandProcessor:
    def __init__(self, argv, pattern_list, logfile=None, stdout=None):
        self.pattern_list = pattern_list + [pexpect.EOF, pexpect.TIMEOUT]
        self.error = None
        self.exit_status = None
        self.pipe = None
        self.prog = None

        try:
            if stdout is not None:
                self.pipe = subprocess.Popen(
                    argv,
                    stdout=stdout,
                    stdin=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )

            if self.pipe is None or self.pipe.stderr is None:
                self.prog = pexpect.spawn(
                    argv[0],
                    argv[1:],
                    encoding="utf-8",
                    codec_errors="replace",
                    logfile=logfile,
                )
            else:
                self.prog = fdpexpect.fdspawn(
                    self.pipe.stderr,
                    encoding="utf-8",
                    codec_errors="replace",
                    logfile=logfile,
                )
        except (FileNotFoundError, pexpect.ExceptionPexpect):
            self.error = f"Failed to start command: {sys.exc_info()[1]}"
            return

    def __iter__(self):
        return self

    def __next__(self):
        while self.prog is not None:
            got = self.prog.expect(self.pattern_list, timeout=0.1)
            if got < len(self.pattern_list) - 2:
                return (got, self.prog.match)
            if got == len(self.pattern_list) - 2:
                if self.pipe is None:
                    self.prog.close()
                    self.exit_status = self.prog.exitstatus
                else:
                    self.pipe.wait()
                    self.exit_status = self.pipe.returncode
                break  # EOF: done
            if got == len(self.pattern_list) - 1:
                pass  # timeout; process events and then try again...
            QApplication.processEvents()
        raise StopIteration

    def stop(self):
        if self.error is None:
            self.error = "program interrupted by user"
        if self.prog is not None:
            self.prog.close()
            self.prog = None


class TemplateListDialog(QDialog, Ui_Template_Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.ctid_prog = parent
        self.setupUi(self)
        self.listWidget.itemChanged.connect(self.item_changed)
        self.listWidget.itemDoubleClicked.connect(self.item_double_clicked)
        self.operation: str

        action = QAction("Rename", self)
        action.triggered.connect(self.rename_selected_template)
        self.listWidget.addAction(action)

        action = QAction("Delete", self)
        action.triggered.connect(self.delete_selected_template)
        self.listWidget.addAction(action)

        template_names = []
        for name, _ in self.ctid_prog.template_manager.items():
            template_names.append(name)
        template_names.sort()
        for name in template_names:
            self.add_template(name)

    def add_template(self, name):
        item = QListWidgetItem(name, self.listWidget)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        # save a copy of the original name as user data for renames:
        item.setData(Qt.ItemDataRole.UserRole, name)

    def rename_selected_template(self, is_checked):
        # pylint: disable=unused-argument
        self.listWidget.editItem(self.listWidget.currentItem())

    def delete_selected_template(self, is_checked):
        # pylint: disable=unused-argument
        item = self.listWidget.currentItem()
        self.ctid_prog.template_manager.remove(item.text())

        idx = self.listWidget.row(item)
        self.listWidget.takeItem(idx)

    def item_double_clicked(self):
        if self.operation == "save":
            self.lineEdit.setText(self.listWidget.currentItem().text())
        self.accept()

    def item_changed(self):
        item = self.listWidget.currentItem()
        if item is None:
            return
        new_name = item.text()
        old_name = item.data(Qt.ItemDataRole.UserRole)
        if new_name != old_name:
            template = self.ctid_prog.template_manager.load(old_name)
            self.ctid_prog.template_manager.save(template, new_name)
            self.ctid_prog.template_manager.remove(old_name)

    def accept(self):
        if self.operation == "save":
            new_name = self.lineEdit.text().strip().lstrip()
            if not new_name:
                QMessageBox.warning(
                    self,
                    "Template Name Missing",
                    "Please enter a template name.",
                    QMessageBox.StandardButton.Ok,
                )
                self.lineEdit.setFocus()
                self.lineEdit.selectAll()
                return
            if new_name in dict(self.ctid_prog.template_manager.items()):
                choice = QMessageBox.question(
                    self,
                    "Template Name Exists",
                    f"A template named `{new_name}' exists already. "
                    "Would you like to replace that template?",
                    QMessageBox.StandardButton.Yes,
                    QMessageBox.StandardButton.Cancel,
                )
                if choice == QMessageBox.StandardButton.Cancel:
                    return  # let user correct name
            else:
                self.add_template(new_name)
            template = self.ctid_prog.get_template()
            if template is None:
                return  # let user correct parameter issue
            self.ctid_prog.template_manager.save(template, new_name)
        else:
            item = self.listWidget.currentItem()
            name = item.text()
            template = self.ctid_prog.template_manager.load(name)
            self.ctid_prog.template_activate(template)
            self.ctid_prog.log(f"Template `{name}' loaded.")

        super().accept()


class PreferencesEditor(QDialog, Ui_Preferences_Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.ctid_prog = parent
        self.setupUi(self)
        self.readonly_params_checkbox.stateChanged.connect(
            self.readonly_params_changed
        )

    def exec(self):
        prefs = self.ctid_prog.preferences

        self.readonly_params_checkbox.setChecked(prefs.readonly_params)
        self.sn_service_combo.currentIndexChanged.connect(
            self.sn_service_changed
        )
        self.sn_service_combo.setCurrentIndex(0)
        selected_service = prefs.sn_service
        if selected_service is not None:
            for idx in range(1, self.sn_service_combo.count()):
                service_name = self.sn_service_combo.itemText(idx)
                if service_name == selected_service:
                    self.sn_service_combo.setCurrentIndex(idx)
                    break
        self.increment_spinbox.setValue(prefs.sn_increment)
        self.station_id_spinbox.setValue(prefs.station_id)
        return super().exec()

    def accept(self):
        increment = self.increment_spinbox.value()
        station_id = self.station_id_spinbox.value()

        if station_id >= increment:
            QMessageBox.critical(
                self,
                "Invalid Station Number",
                f"Station id ({station_id}) must be smaller than "
                f"the serial-number increment ({increment}).",
                QMessageBox.StandardButton.Ok,
            )
            return
        super().accept()
        prefs = self.ctid_prog.preferences
        prefs.readonly_params = self.readonly_params_checkbox.isChecked()
        if self.sn_service_combo.currentIndex() == 0:
            prefs.sn_service = None
        else:
            prefs.sn_service = self.sn_service_combo.currentText()
        prefs.sn_increment = increment
        prefs.station_id = station_id
        prefs.save()
        self.ctid_prog.prefs_changed()

    def reject(self):
        self.ctid_prog.params_set_input_enabled(
            not self.ctid_prog.preferences.readonly_params
        )
        super().reject()

    def sn_service_changed(self):
        enable = self.sn_service_combo.currentIndex() == 0
        self.increment_spinbox.setEnabled(enable)
        self.station_id_spinbox.setEnabled(enable)

    def readonly_params_changed(self):
        self.ctid_prog.params_set_input_enabled(
            not self.readonly_params_checkbox.isChecked()
        )


class UI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(window)

        self.params = {}

        ct_params = sensor_params.CT(
            Ui_Param_CT(), self.param_group, "CT Parameters"
        )
        self.params["AC"] = self.params["DC"] = self.params["RC"] = ct_params
        self.params["linear"] = sensor_params.Linear(
            Ui_Param_Linear(), self.param_group, "Linear Parameters"
        )
        self.params["temp"] = sensor_params.Temp(
            Ui_Param_Temp(), self.param_group, "Temperature Parameters"
        )
        self.params["NTC"] = sensor_params.NTC(
            Ui_Param_NTC(), self.param_group, "NTC Thermistor Parameters"
        )
        self.params["pulse"] = sensor_params.Pulse(
            Ui_Param_Pulse(), self.param_group, "Pulse Parameters"
        )

        self.current_params = self.params["AC"]
        self.current_params.activate()

        self.auto_serial_checkbox.setChecked(True)
        self.serial_spinbox.setEnabled(False)
        self.console = terminal.Terminal(self.plainTextEdit)
        self.add_mfgs()
        self.busy = False
        self.cmd = None
        self.sn_service = None
        self.mfg_id = None
        self.model = None

        self.console.write(
            VERSION_INFO + "\n\n"
            "You can use this tool to program "
            "the microcontroller of a CTid board (PCB).\n\n"
            "Please start by filling out the form on the left. "
            "Then attach the programming cable to the "
            'CTid board, and click "Program" to write the '
            "information to the microcontroller.\n"
        )
        self.welcome_msg = True  # we're displaying welcome message

        CTID_STATE_PATH.mkdir(exist_ok=True)

        self.preferences = preferences.Manager(CTID_STATE_PATH)
        self.sn: sn.Manager
        self.template_manager = template.Manager(CTID_STATE_PATH)

        for st in ctid.SENSOR_TYPE_NAME:
            name = SENSOR_LONG_NAME[st] if st in SENSOR_LONG_NAME else st
            self.sensor_type_combo.addItem(name)

        self.action_About.triggered.connect(self.about)
        self.sensor_type_combo.currentIndexChanged.connect(
            self.sensor_type_changed
        )
        self.mfg_combo.currentIndexChanged.connect(self.product_changed)
        self.model_lineEdit.editingFinished.connect(self.product_changed)
        self.auto_serial_checkbox.stateChanged.connect(
            self.auto_serial_changed
        )
        self.program_btn.clicked.connect(self.program_or_cancel)
        self.read_btn.clicked.connect(self.read)
        self.reprogram_after_cal_btn.clicked.connect(self.reprogram_after_cal)
        self.load_template_btn.clicked.connect(self.template_load)
        self.save_template_btn.clicked.connect(self.template_save)
        self.save_template_btn.setVisible(self.template_manager.may_save())

        self.template_list_dialog = TemplateListDialog(self)

        self.preferences_editor = PreferencesEditor(self)
        self.actionPreferences.triggered.connect(self.preferences_editor.exec)

        self.prefs_changed()
        self.params_set_input_enabled(not self.preferences.readonly_params)

    def about(self):
        QMessageBox.about(self, "About", VERSION_INFO)

    def log(self, msg):
        if self.welcome_msg:
            self.plainTextEdit.clear()
            self.welcome_msg = False
        self.console.write(msg + "\n")

    def template_activate(self, template):
        """Load values from template, except never load the serial-number."""
        try:
            if "model" in template:
                self.model_lineEdit.setText(template["model"])

            if "mfg" in template:
                for idx in range(self.mfg_combo.count()):
                    if self.mfg_combo.itemData(idx) == template["mfg"]:
                        # this may trigger call to product_changed() so
                        # model_lineEdit() must have been updated already...
                        self.mfg_combo.setCurrentIndex(idx)

            self.product_changed()

            # 'voltage' sensor type is now called 'linear':
            if template["sensor_type"] == "voltage":
                template["sensor_type"] = "linear"
                template["unit"] = 0

            self.sensor_type_combo.setCurrentIndex(0)
            for idx, code in enumerate(ctid.SENSOR_TYPE_NAME):
                if code == template["sensor_type"]:
                    self.sensor_type_combo.setCurrentIndex(idx)
                    break

            self.r_source_spinbox.setValue(template["r_source"])
            self.r_load_spinbox.setValue(template["r_load"])

            if self.current_params is not None:
                self.current_params.load(template)
        except KeyError as key:
            QMessageBox.warning(
                self,
                "Warning",
                f"Template is missing parameter {key}.",
                QMessageBox.StandardButton.Ok,
            )

    def template_load(self):
        self.template_list_dialog.operation = "load"
        self.template_list_dialog.template_name_frame.hide()
        self.template_list_dialog.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Open
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.template_list_dialog.exec()

    def template_save(self):
        if self.validate_form() is None:
            return
        self.template_list_dialog.operation = "save"
        self.template_list_dialog.template_name_frame.show()
        self.template_list_dialog.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.template_list_dialog.exec()

    def get_mfg_id(self):
        mfg_idx = self.mfg_combo.currentIndex()
        if mfg_idx == 0:
            return None
        return self.mfg_combo.itemData(mfg_idx)

    def get_model(self):
        model = self.model_lineEdit.text().strip().lstrip()
        if not model:
            return None
        return model

    def update_sn(self):
        if not self.auto_serial_checkbox.isChecked():
            return

        mfg_id = self.get_mfg_id()

        if mfg_id is None or self.get_model() is None:
            return

        next_sn = None
        try:
            next_sn = self.sn.get()
            if next_sn is None:
                QMessageBox.warning(
                    self,
                    "Serial Number Unavailable",
                    "Serial number service failed to return "
                    "a serial number. Reverting to "
                    "manual serial numbers.",
                    QMessageBox.StandardButton.Ok,
                )
        except sn.SpaceExhausted:
            mfg = ctid.mfg_short_name(mfg_id)
            QMessageBox.warning(
                self,
                "Serial Number Space Exhausted",
                "All available serial-numbers have been used "
                f'for "{mfg} {self.model}". Please use a different '
                "manufacturer and/or model name.",
                QMessageBox.StandardButton.Ok,
            )

        if next_sn is None:
            self.auto_serial_checkbox.setChecked(False)
            self.serial_spinbox.setEnabled(True)
            self.serial_spinbox.setValue(0)
            return

        self.serial_spinbox.setValue(next_sn)

    def sensor_type_changed(self):
        st = ctid.SENSOR_TYPE_NAME[self.sensor_type_combo.currentIndex()]
        new_params = self.params[st] if st in self.params else None

        if new_params == self.current_params:
            return  # no change

        if self.current_params is not None:
            self.current_params.deactivate()
        self.current_params = new_params

        if self.current_params is not None:
            self.current_params.activate()
            self.current_params.set_input_enabled(
                not self.preferences.readonly_params
            )

    def product_changed(self):
        mfg_id = self.get_mfg_id()
        model = self.get_model()

        log.debug(f"product_changed: mfg_id={mfg_id} model={model}")

        if mfg_id is None or model is None:
            return

        if self.mfg_id == mfg_id and self.model == model:
            return  # no change
        self.mfg_id = mfg_id
        self.model = model

        if self.sn.set_product(mfg_id, model):
            self.update_sn()
        else:
            self.auto_serial_checkbox.setChecked(False)
            self.serial_spinbox.setValue(0)

    def auto_serial_changed(self):
        auto_serial = self.auto_serial_checkbox.isChecked()
        if auto_serial:
            latest_sn = self.serial_spinbox.value()
            self.sn.activate(latest_sn)
            self.update_sn()
        else:
            self.sn.deactivate()
        self.serial_spinbox.setEnabled(not auto_serial)

    def add_mfgs(self):
        """Add companies per their table/manufacturer number as stated by CTid
        Spec Sheet.

        """
        for mfg_id, name in ctid.MFG_ID.items():
            self.mfg_combo.addItem(name, mfg_id)

    def set_input_enabled(self, enabled: bool):
        self.chip_combo.setEnabled(enabled)

        serial_enabled = enabled and not self.auto_serial_checkbox.isChecked()
        self.serial_spinbox.setEnabled(serial_enabled)

        self.load_template_btn.setEnabled(enabled)
        self.save_template_btn.setEnabled(enabled)
        self.reprogram_after_cal_btn.setEnabled(enabled)

        self.params_set_input_enabled(
            enabled and not self.preferences.readonly_params
        )

    def params_set_input_enabled(self, enabled: bool):
        self.mfg_combo.setEnabled(enabled)
        self.sensor_type_combo.setEnabled(enabled)
        self.model_lineEdit.setEnabled(enabled)
        self.r_source_spinbox.setEnabled(enabled)
        self.r_load_spinbox.setEnabled(enabled)

        if self.current_params is not None:
            self.current_params.set_input_enabled(enabled)

        self.read_btn.setEnabled(enabled)

    def cmd_start(
        self, argv, pattern_list: list[str], logfile=None, stdout=None
    ):
        self.cmd = CommandProcessor(
            argv, pattern_list, logfile=logfile, stdout=stdout
        )

    def cmd_done(self):
        if self.cmd is not None and self.cmd.error is not None:
            self.log(f"Command failed: {self.cmd.error}")

    def get_template(self):
        """Get form-data as a dictionary. No validation is performed beyond
        the constraints imposed by the user-interface controls.

        """
        template = {}

        mfg_id = self.get_mfg_id()
        if mfg_id is not None:
            template["mfg"] = mfg_id

        model = self.get_model()
        if model is not None:
            template["model"] = model

        template["sn"] = self.serial_spinbox.value()
        st_idx = self.sensor_type_combo.currentIndex()
        template["sensor_type"] = ctid.SENSOR_TYPE_NAME[st_idx]
        template["r_source"] = self.r_source_spinbox.value()
        template["r_load"] = self.r_load_spinbox.value()

        if self.current_params is not None:
            self.current_params.save(template)
            if not self.current_params.validate(template):
                return None
        return template

    def validate_form(self):
        """Validate form data and return cleaned data as a dictionary."""
        cleaned_data = self.get_template()
        if cleaned_data is None:
            return None

        if "mfg" not in cleaned_data:
            QMessageBox.warning(
                self,
                "Manufacturer Missing",
                "Please select manufacturer.",
                QMessageBox.StandardButton.Ok,
            )
            self.mfg_combo.setFocus()
            return None

        if "model" not in cleaned_data:
            QMessageBox.warning(
                self,
                "Model Name Missing",
                "Please enter model name.",
                QMessageBox.StandardButton.Ok,
            )
            self.model_lineEdit.setFocus()
            return None

        utf8_model = cleaned_data["model"].encode("utf-8")
        if len(utf8_model) > 8:
            QMessageBox.warning(
                self,
                "Model Name Too Long",
                f"Model name is {len(utf8_model)} bytes long in "
                "UTF-8 encoding. Please limit name to 8 bytes in length.",
                QMessageBox.StandardButton.Ok,
            )
            self.model_lineEdit.setFocus()
            return None
        return cleaned_data

    def show_cmd_error(self, cmd, title, msg):
        if cmd.exit_status is not None:
            msg += f" Exit status {cmd.exit_status}."
        QMessageBox.warning(self, title, msg, QMessageBox.StandardButton.Ok)

    def create_hexfile(self, cleaned_data, params):
        st = cleaned_data["sensor_type"]
        argv = [
            PATH_CTID_ENCODER,
            "-M",
            f"{cleaned_data['mfg']}",
            "-S",
            st,
            "-m",
            cleaned_data["model"],
            "-n",
            f"{cleaned_data['sn']}",
            "-l",
            f"{int(cleaned_data['r_load'])}",
            "-r",
            f"{int(cleaned_data['r_source'])}",
        ]

        if params is not None:
            argv += params.encoder_argv(cleaned_data)

        output = tempfile.mkstemp(suffix=".hex", prefix="CTid-")

        template_filename = (
            CODE_TEMPLATE[st] if st in CODE_TEMPLATE else "powered.hex"
        )

        ref = (
            importlib_resources.files("ctid_programmer")
            / "resources"
            / "code"
            / template_filename
        )
        with importlib_resources.as_file(ref) as code_template_path:
            argv.append(str(code_template_path))

            log.debug(f"create_hexfile: argv={argv}")

            self.cmd_start(argv, [], logfile=self.console, stdout=output[0])
            if isinstance(self.cmd, CommandProcessor):
                # consume command's output by iterating over it:
                for _ in self.cmd:
                    pass
            self.cmd_done()

        if self.cmd is not None and self.cmd.exit_status != 0:
            self.show_cmd_error(
                self.cmd, "Command Failed", "Failed to create hex file."
            )
            os.close(output[0])
            os.remove(output[1])
            return None

        # now that we have created the actual hexfile, it's safe to close
        # the original (empty) file created by mkstemp():
        os.close(output[0])
        return output[1]

    def detect_chip_type(self):
        self.cmd_start(
            CMD_AVRDUDE + ["-pt9", "-nq"],
            [r"[dD]evice signature = 0x([0-9a-f]+)"],
        )
        chip_id = None
        if isinstance(self.cmd, CommandProcessor):
            for _, match in self.cmd:
                if isinstance(match, re.Match):
                    chip_id = int(match.group(1), base=16)
        self.cmd_done()
        if chip_id is None:
            QMessageBox.warning(
                self,
                "No Microcontroller Detected",
                "No microcontroller detected. "
                "Please confirm programming cable is "
                "properly attached.",
                QMessageBox.StandardButton.Ok,
            )
            return None
        if chip_id not in CHIP_ID_TO_NAME:
            QMessageBox.warning(
                self,
                "Unknown Microcontroller",
                f"Unknown microcontroller chip type {chip_id:#x}.",
                QMessageBox.StandardButton.Ok,
            )
            return None
        chip = CHIP_ID_TO_NAME[chip_id]
        self.log(f"Detected {chip[1]} chip.")
        return chip[0]

    def write_flash(
        self,
        chip_type: str,
        hexfile: str,
        cleaned_data: dict,
        auto_serial_number: bool,
    ):
        """Write HEXFILE to the flash to a chip of type CHIP_TYPE. The
        HEXFILE contains the data passed in CLEANED_DATA.
        AUTO_SERILA_NUMBER must be True if the serial numbers are
        being assigned automatically, False otherwise.

        Returns True on success, False on any failure.
        """
        self.cmd_start(
            CMD_AVRDUDE + [f"-p{chip_type}", f"-Uflash:w:{hexfile}"],
            [],
            logfile=self.console,
        )
        if isinstance(self.cmd, CommandProcessor):
            for _ in self.cmd:
                pass  # consume output until program is done...
        self.cmd_done()
        if self.cmd is not None and self.cmd.exit_status != 0:
            self.show_cmd_error(
                self.cmd,
                "Programming Failed",
                "Failed to write the microcontroller flash.",
            )
            return False

        sn = cleaned_data["sn"]
        self.log(
            f"Success: CTid board has been programmed with serial number {sn}."
        )
        self.sn.commit(sn, cleaned_data, auto_serial_number)
        return True

    def read_template_from_flash(self, chip_type):
        temp = tempfile.TemporaryFile(suffix=".bin", prefix="CTid-")
        self.cmd_start(
            CMD_AVRDUDE + [f"-p{chip_type}", "-Uflash:r:-:r"],
            [],
            logfile=self.console,
            stdout=temp,
        )
        if isinstance(self.cmd, CommandProcessor):
            for _ in self.cmd:
                pass  # consume output until program is done...
        self.cmd_done()

        if self.cmd is not None and self.cmd.exit_status != 0:
            temp.close()
            self.show_cmd_error(
                self.cmd,
                "Read Failed",
                "Failed to read the microcontroller flash.",
            )
            return None

        temp.seek(0)
        flash = temp.read()
        temp.close()

        if len(flash) < 0x3E1:
            if not flash:
                QMessageBox.critical(
                    self,
                    "Read Failed",
                    "Microcontroller flash is empty.",
                    QMessageBox.StandardButton.Ok,
                )
            else:
                QMessageBox.critical(
                    self,
                    "Read Failed",
                    f"Read only {len(flash)} bytes from "
                    "microcontroller flash.",
                    QMessageBox.StandardButton.Ok,
                )
            return None
        self.log("Success: CTid board has been read.")

        CTid_table_addr = 0x3C0  # table goes in last 64 bytes
        length = flash[CTid_table_addr]
        table = flash[CTid_table_addr + 1 : CTid_table_addr + 1 + length]
        try:
            table = ctid.Table(bytes(ctid.unstuff(table)))
        except ctid.Error as e:
            self.log(f"CTid data invalid: {e}")
            return None
        except ctid.CRCError as e:
            self.log(
                f"CTid has invalid CRC: expected {e.expected} got {e.got}"
            )
            return None

        template = self.ctid_table_to_template(table)

        if template is not None:
            m = re.match(r"(.*)-[^-]+$", template["model"])
            if m is not None:
                # strip suffix off model-name:
                template["model"] = m.group(1)
        return template

    def reprogram_with_cal_params(self, chip_type):
        template = self.read_template_from_flash(chip_type)
        if template is None:
            return

        sn = template["sn"]
        mfg = template["mfg"]
        model = template["model"]

        saved_product = self.sn.product
        self.sn.set_product(mfg, model)
        cal_params = self.sn.get_cal_data(sn)
        if not cal_params:
            self.sn.restore_product(saved_product)
            QMessageBox.critical(
                self,
                "No Calibration Data Found",
                "No calibration data was found for "
                f"product {self.sn.product} with serial number {sn}.",
                QMessageBox.StandardButton.Ok,
            )
            return

        msg = ""
        for key, value in cal_params.items():
            msg += f"\t{key:>16s}: {value}\n"

        # merge the calibrated parameters with existing template:
        for name, value in cal_params.items():
            template[name] = value
        model = template["model"]

        mfg_name = ctid.mfg_short_name(mfg)
        self.console.write(
            f"\n\nFound calibration data for {mfg_name} {model} #{sn}:\n{msg}\n"
        )

        hexfile = self.create_hexfile(
            template, self.params[template["sensor_type"]]
        )
        if hexfile is None:
            self.sn.restore_product(saved_product)
            self.mark_idle()
            return
        self.write_flash(
            chip_type, hexfile, template, auto_serial_number=False
        )
        os.remove(hexfile)
        self.mark_idle()

        self.sn.restore_product(saved_product)

    def read_flash(self, chip_type):
        template = self.read_template_from_flash(chip_type)
        if template is None:
            return
        self.template_activate(template)
        self.auto_serial_checkbox.setChecked(False)
        self.serial_spinbox.setValue(template["sn"])

    def ctid_table_to_template(self, table):
        sensor_type = ctid.SENSOR_TYPE_NAME[table.sensor_type]
        template = {}
        template["mfg"] = table.mfg_id
        template["model"] = table.model
        template["sn"] = table.serial_number
        template["sensor_type"] = sensor_type
        template["r_source"] = table.r_source
        template["r_load"] = table.r_load
        self.params[sensor_type].table_to_template(table, template)
        return template

    def mark_busy(self):
        self.plainTextEdit.clear()
        self.busy = True
        self.set_input_enabled(False)
        self.program_btn.setText("Cancel")

    def mark_idle(self):
        self.busy = False
        self.program_btn.setText("Program")
        self.set_input_enabled(True)

    def chip_type(self):
        if self.chip_combo.currentIndex() == 0:
            # auto-detect chip
            chip_type = self.detect_chip_type()
        elif self.chip_combo.currentIndex() == 1:
            chip_type = "t9"
        else:
            chip_type = "t10"
        return chip_type

    def program_or_cancel(self):
        """Program the microcontroller with the info specified in the form.
        This consists of two steps: (1) creating a hex file with the
        info encoded and (2) writing the file to the microcontroller.

        """
        if self.busy:
            if self.cmd is not None:
                self.cmd.stop()  # cancel the running command
                self.cmd_done()
            self.mark_idle()
            return

        cleaned_data = self.validate_form()
        if cleaned_data is None:
            return

        self.mark_busy()

        hexfile = self.create_hexfile(cleaned_data, self.current_params)
        if hexfile is None:
            self.mark_idle()
            return

        chip_type = self.chip_type()
        if chip_type is not None:
            auto_serial_number = self.auto_serial_checkbox.isChecked()
            if self.write_flash(
                chip_type, hexfile, cleaned_data, auto_serial_number
            ):
                self.update_sn()

        os.remove(hexfile)
        self.mark_idle()

    def read(self):
        """Reads CTid parameters from the flash."""
        self.mark_busy()

        chip_type = self.chip_type()
        if chip_type is not None:
            self.read_flash(chip_type)

        self.mark_idle()

    def reprogram_after_cal(self):
        """Reads CTid parameters from the flash, lookup calibration parameters
        for the read serial-number and, if that exists, reprogram with
        those parameters.

        """
        self.mark_busy()

        chip_type = self.chip_type()
        if chip_type is not None:
            self.reprogram_with_cal_params(chip_type)

        self.mark_idle()

    def prefs_changed(self):
        prefs = self.preferences

        if self.sn_service is None or self.sn_service != prefs.sn_service:
            self.sn_service = prefs.sn_service
            if prefs.sn_service == "eGauge":
                self.sn = sn_egauge.Manager(self, CTID_STATE_PATH)
            else:
                if prefs.sn_service is not None:
                    QMessageBox.critical(
                        self,
                        "Unknown Serial Number Service",
                        f"Serial number service {prefs.sn_service} is "
                        "unknown. Reverting to locally "
                        "managed serial numbers.",
                    )
                    self.sn_service = None
                self.sn = sn_local.Manager(self, CTID_STATE_PATH)
            if self.mfg_id is not None and self.model is not None:
                self.sn.set_product(self.mfg_id, self.model)
            self.reprogram_after_cal_btn.setVisible(
                self.sn.has_calibration_data()
            )
        self.sn.set_preferences(prefs)
        self.update_sn()


parser = argparse.ArgumentParser(description="CTid GUI programmer.")
parser.add_argument(
    "-F",
    "--full-screen",
    action="store_true",
    help="Start application in full-screen mode.",
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_const",
    const=logging.DEBUG,
    dest="log_level",
    help="Show debug output.",
)
parser.add_argument(
    "-v",
    "--version",
    action="store_true",
    help="Output version information and exit.",
)
args = parser.parse_args()

if args.version:
    print(VERSION_INFO)
    sys.exit(0)

log_level = logging.ERROR if args.log_level is None else args.log_level
logging.basicConfig()
log = logging.getLogger()  # get the root logger
log.setLevel(log_level)  # sets default logging for all child loggers

app = QApplication(sys.argv)
app.setDesktopFileName("net.egauge.ctid_programmer")
window = QMainWindow()
ui = UI()

if args.full_screen:
    window.showMaximized()
else:
    window.show()
sys.exit(app.exec())
