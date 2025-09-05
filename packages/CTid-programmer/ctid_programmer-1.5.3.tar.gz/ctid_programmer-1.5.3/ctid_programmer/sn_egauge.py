#
# Copyright (c) 2020-2021, 2025 eGauge Systems LLC
#       4805 Sterling Dr, Suite 1
#       Boulder, CO 80301
#       voice: 720-545-9767
#       email: davidm@egauge.net
#
# All rights reserved.
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
# pylint: disable=no-name-in-module
#
"""Serial number allocation via the eGauge serial-number API."""

import json
import logging
import os

from egauge import ctid, webapi
from egauge.webapi.cloud.credentials import CredentialsManager, LoginCanceled
from PySide6.QtWidgets import QMessageBox

from ctid_programmer import sn

log = logging.getLogger(__name__)


BAD_STATUS = "Unexpected HTTP status code."


class Manager(sn.Manager):
    def auth_wrapper(self, method, *args, **kwargs):
        while True:
            try:
                ret = method(*args, *kwargs)
                self.credentials_manager.previous_login_failed = False
                return ret
            except webapi.json_api.UnauthenticatedError:
                pass
            except LoginCanceled:
                return None

    def __init__(self, ui, state_directory_path):
        SerialNumberWithAuth = webapi.decorate_public(
            webapi.cloud.SerialNumber, self.auth_wrapper
        )
        self.credentials_manager = CredentialsManager(ui)
        self.sn_api = SerialNumberWithAuth(
            auth=webapi.auth.TokenAuth(ask=self.credentials_manager.ask)
        )
        super().__init__(
            ui, os.path.join(state_directory_path, "egauge_sn_api.bin")
        )

    def has_calibration_data(self):
        """Should return True if this serial-number manager can retrieve
        calibration data with get_calibration_data(), False otherwise.

        """
        return True

    def set_product(self, manufacturer, model):
        log.debug(f"set_product: manufacturer={manufacturer}, model={model}")

        mfg = ctid.mfg_short_name(manufacturer)
        if not super().set_product(mfg, model):
            return False

        error = None
        model_list = None
        try:
            model_list = self.sn_api.get_models()
        except webapi.Error as e:
            error = e

        if model_list is None:
            errmsg = ""
            if (
                isinstance(error, webapi.json_api.JSONAPIError)
                and error.args[0] == BAD_STATUS
            ):
                detail = "."
                try:
                    body = json.loads(error.args[2].decode("utf-8"))
                    err = body.get("detail")
                    if err is not None:
                        detail = ": " + err
                except (UnicodeError, ValueError):
                    pass
                status = error.args[1]
                errmsg = f"\n\nServer returned status {status}{detail}"
            QMessageBox.critical(
                self.ui,
                "Serial-number service failed",
                "Serial-number service failed to return "
                "model-name list.  "
                "Reverting to manual "
                "serial numbers." + errmsg,
                QMessageBox.StandardButton.Ok,
            )
            return False

        found = False
        for r in model_list:
            if r["name"] == self.product:
                found = True
                break
        if found:
            return True

        choice = QMessageBox.question(
            self.ui,
            "Create Serial-Number Record?",
            (
                "The eGauge Serial-Number service has no record "
                f'of product "{mfg} {model}".  Would you like to '
                "create one?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.No:
            return False

        result = False
        try:
            result = self.sn_api.create_model(self.product, 0xFFFFFF)
        except webapi.Error:
            log.exception(
                f'sn_api.create_model() for model "{self.product}" failed'
            )
        return result

    def set_preferences(self, prefs):
        pass

    def get(self):
        # see if we already have a serial-number for this product:
        sn = super().get()
        if sn is not None:
            log.debug(f"get: product={self.product}; using existing SN {sn}")
            return sn

        log.debug(f"get: product={self.product}; allocating new SN ")
        return self._allocate_sn()

    def commit(self, sn, info, auto_serial_number):
        meta = {}
        try:
            ret = self.sn_api.get_metadata(self.product, sn)
            if ret is not None:
                meta = ret
        except webapi.Error:
            log.exception(
                f"commit: no metadata found for {self.product} SN {sn}."
            )
        meta["ctid"] = info
        try:
            self.sn_api.set_metadata(self.product, sn, meta)
        except webapi.Error as e:
            QMessageBox.warning(
                self.ui,
                "Failed to save CTid info",
                f"Failed to save meta data for product {self.product} "
                f"serial-number {sn}: {e}.",
                QMessageBox.StandardButton.Ok,
            )

        if auto_serial_number:
            self._allocate_sn()  # allocate serial number to use next
        else:
            super().set(None)

    def get_cal_data(self, sn):
        try:
            meta = self.sn_api.get_metadata(self.product, sn)
        except webapi.Error:
            log.exception(
                f"Failed to get cal data for {self.product} SN {sn}."
            )
            return None

        if meta is None:
            return None
        if "cal" in meta:
            cal = meta["cal"]
        elif "ntc" in meta:
            # for backwards compatibility:
            cal = {}
            for key, value in meta["ntc"].items():
                cal[f"ntc_{key}"] = str(value)
        else:
            return None
        return cal

    def _allocate_sn(self):
        # allocate a new serial number:
        super().set(None)
        try:
            serial_number = self.sn_api.allocate(self.product)
            if serial_number is None:
                return None
        except webapi.Error as e:
            log.exception(f"Failed to allocate SN for product {self.product}.")
            if (
                len(e.args) > 2
                and isinstance(e.args[2], list)
                and len(e.args[2]) >= 1
            ):
                errors = e.args[2]
                # If this product is out of serial-numbers, let the user know:
                if errors[0] == "Maximum serial number reached":
                    raise sn.SpaceExhausted
                errs_msg = "\n".join(errors)
                QMessageBox.critical(
                    self.ui,
                    "Serial-number Failure",
                    f"Failed to allocate serial-number: {errs_msg}",
                    QMessageBox.StandardButton.Ok,
                )
            else:
                QMessageBox.critical(
                    self.ui,
                    "Serial-number Failure",
                    f"Failed to allocate serial-number: {e}",
                    QMessageBox.StandardButton.Ok,
                )
            return None

        super().set(serial_number)
        return serial_number
