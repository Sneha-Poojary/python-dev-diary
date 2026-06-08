import sys
import opentap
import clr
import csv
from System.Collections.Generic import List
from opentap import *
import OpenTap
import math
import System
from System import Array, Double, Byte, Int32, String, Boolean
from System.ComponentModel import Browsable
import System.Xml
from System.Xml.Serialization import XmlIgnore
from enum import Enum
import os
from decimal import Decimal
from System import Double
import sqlite3
from OpenTap import Log, DisplayAttribute, Display, Output, Unit, OutputAttribute, UnitAttribute,AvailableValues, EnabledIfAttribute
import re
from opentap import TestStep, attribute
import OpenTap
import struct
clr.AddReference("System.Collections")

@attribute(OpenTap.Display("CalibrationDecoder", "CAN Settings", "MTS - CANResponseDecoder"))
@attribute(OpenTap.AllowAnyChild())
class CalibrationDecoder(TestStep):
    InputData = property(String, "").add_attribute(OpenTap.Display("Input Data", "Received data from CAN", "Parameters"))
    ServiceStr = property(String, "Decimal") \
        .add_attribute(OpenTap.AvailableValues("ServiceLst")) \
        .add_attribute(
        OpenTap.Display("2.Conversion Type", "Service", "Inputs"))
    ServiceLst = property(List[String], None).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))
    ServiceStr1 = property(String, "Decimal") \
        .add_attribute(OpenTap.AvailableValues("ServiceLst1")) \
        .add_attribute(
        OpenTap.Display("1.Service", "Service", "Inputs"))
    ServiceLst1 = property(List[String], None).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))

    Gain = property(String, "") \
        .add_attribute(Unit("")) \
        .add_attribute(Display("Gain", "", "Output", 0)) \
        .add_attribute(Output())
    Offset = property(String, "") \
        .add_attribute(Unit("")) \
        .add_attribute(Display("Offset", "", "Output", 0)) \
        .add_attribute(Output())
    Calib_status = property(String, "") \
        .add_attribute(Unit("")) \
        .add_attribute(Display("Calibration Status", "", "Output", 0)) \
        .add_attribute(Output())

    lsl = property(Double, 0.00) \
        .add_attribute(OpenTap.Display("LSL","", "Input", 1.2))
    usl = property(Double, 10.00) \
        .add_attribute(OpenTap.Display("USL","", "Input", 1.3))
    unit = property(String, "V") \
        .add_attribute(OpenTap.Display("Unit","", "Input", 1.4))
    factor = property(Double, 1) \
        .add_attribute(OpenTap.Display("Factor", "", "Input", 1.2))

    Response = property(String, "01") \
        .add_attribute(OpenTap.Display("Response","", "Input", 1.5))

    Publish = property(Boolean, True) \
        .add_attribute(OpenTap.Display("Publish", "Enable if you want to publish", "Publish"))

    Logging = property(OpenTap.Enabled[String], None).add_attribute(
        OpenTap.Display("Logging", "Path of where the log file will be stored.", "Result Logging", 1))

    Points = property(Int32, 200).add_attribute(
        OpenTap.Display("Points", "Number points to store.", "Result Logging", 1))

    RetVal = property(String, "") \
        .add_attribute(Unit("")) \
        .add_attribute(Display("Output", "", "Output", 0)) \
        .add_attribute(Output())

    def __init__(self):
        super().__init__()
        self.ActionShown = False
        self.Logging = OpenTap.Enabled[String]()
        self.Logging.IsEnabled = True
        self.Logging.Value = "C:\\SessionLogs\\"

        self.ServiceLst1 = List[String]()
        self.ServiceLst1.Add("Write calibration values")
        self.ServiceLst1.Add("Read calibration values")

        self.ServiceLst = List[String]()
        self.ServiceLst.Add("Decimal")
        self.ServiceLst.Add("Ascii")
        self.ServiceLst.Add("Octal")
        self.ServiceLst.Add("Binary")
        self.RetVal = "00"
        self.Gain = "00"
        self.Offset = "00"
        self.Calib_status = "00"

    def Run(self):
        super().Run()
        InputData = self.InputData
        #byte selection for single Byte
            #select_bit = self.Byte_selection
            # # Split into 2-character chunks
            # bytes_list = [InputData[i:i+2] for i in range(0, len(InputData), 2)]
            #
            # # Adjust index (since Python is 0-based, but you want 1-based)
            # if 1 <= select_bit <= len(bytes_list):
            #     selected_byte = bytes_list[select_bit - 1]
            #     self.log.Info(f"Selected byte: {selected_byte}")
            # else:
            #     self.log.Info("Invalid bit selection")
            # output = selected_byte
            #
            # if self.Response == selected_byte:
            #     self.UpgradeVerdict(OpenTap.Verdict.Pass)
            #     if self.Publish == True:
            #         self.PublishResult("data", ["value", "lsl", "usl", "unit"], [str(selected_byte), str(self.Response),str(self.Response), "-"])
            #         self.log.Info(f"successfullly published")
            #         self.log.Info("Verdict: Pass11")
            # else:
            #     self.UpgradeVerdict(OpenTap.Verdict.Fail)
            #     if self.Publish == True:
            #         self.PublishResult("data", ["value", "lsl", "usl", "unit"], [str(selected_byte), str(self.Response),str(self.Response), "-"])
            #         self.log.Info(f"successfullly published")
            #     self.log.Info("Verdict: FAIL for response not match")

        if self.ServiceStr1 == "Write calibration values":
            clean_hex = InputData.replace(" ", "").replace(",", "").upper()
            bytes_list = [int(clean_hex[i:i + 2], 16) for i in range(0, len(clean_hex), 2)]

            gain_bytes = bytes_list[3:7]  # 4 bytes
            offset_bytes = bytes_list[7:11]  # 4 bytes
            calib_status = bytes_list[11]  # 1 byte
            output = bytes_list[3:11]
            output = ''.join(f"{b:02X}" for b in output)
            self.log.Info(f"output {output}")

            gain_hex = ''.join(f"{b:02X}" for b in gain_bytes[::-1])  # reverse for readability
            offset_hex = ''.join(f"{b:02X}" for b in offset_bytes[::-1])
            calib_hex = ''.join(f"{calib_status:02X}")
            # gain_hex = ''.join(f"{b:02X}" for b in gain_bytes)
            # offset_hex = ''.join(f"{b:02X}" for b in offset_bytes)
            # calib_hex = f"{calib_status:02X}"

            self.log.Info(f"Gain          : {gain_hex}")
            self.log.Info(f"Offset        : {offset_hex}")
            self.log.Info(f"Calib_Status  : {calib_hex}")
            self.RetVal = str(output)
            self.Gain = str(gain_hex)
            self.Offset = str(offset_hex)
            self.Calib_status = str(calib_hex)
            self.log.Info(f"calib_hex: {calib_hex}")

            if calib_hex == "01":
                self.UpgradeVerdict(OpenTap.Verdict.Pass)
                if self.Publish:
                    self.PublishResult("data", ["value", "lsl", "usl", "unit"],
                                       [calib_hex, str(self.Response), str(self.Response), "-"])
                    self.log.Info("Successfully published")
                self.log.Info("Verdict: PASS")
            else:
                self.UpgradeVerdict(OpenTap.Verdict.Fail)
                if self.Publish:
                    self.PublishResult("data", ["value", "lsl", "usl", "unit"],
                                       [calib_hex, str(self.Response), str(self.Response), "-"])
                    self.log.Info("Successfully published")
                self.log.Info("Verdict: FAIL (response not match)")

        elif self.ServiceStr1 == "Read calibration values":
            import struct
            clean_hex = InputData.replace(" ", "").replace(",", "").upper()
            bytes_list = [int(clean_hex[i:i + 2], 16) for i in range(0, len(clean_hex), 2)]
            raw_bytes = bytes_list[-3:]  # [0x5B, 0x75, 0x00]
            inv_bytes = raw_bytes[::-1]  # [0x00, 0x75, 0x5B]
            decimal_value = int(''.join(f"{b:02X}" for b in inv_bytes), 16)
            output = decimal_value * self.factor

            self.log.Info(f"Raw Bytes   : {raw_bytes}")
            self.log.Info(f"Inverted    : {inv_bytes}")
            self.log.Info(f"Decimal     : {decimal_value}")
            self.log.Info(f"With Factor : {output}")



            if output >= self.lsl and output <= self.usl:
                self.UpgradeVerdict(OpenTap.Verdict.Pass)
            else:
                self.UpgradeVerdict(OpenTap.Verdict.Fail)

            if self.Publish == True:
                self.PublishResult("data", ["value", "lsl", "usl", "unit"],
                                   [str(output), str(self.lsl), str(self.usl), str(self.unit)])
            self.RetVal = str(output)






