#CAN FUNCTIONALITY

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

from .CANInstrument import CANInstrument
from .CANSettings import CANSettings
clr.AddReference("System.Collections")

@attribute(OpenTap.Display("CAN Functionality", "CAN Settings", "MTS - CAN"))
@attribute(OpenTap.AllowAnyChild())
class CANFunctionality(TestStep):
    Instrument = property(CANInstrument, None).add_attribute(
        OpenTap.Display("Instrument", "Select the CAN Instrument.", "Resources"))

    # Locate database path (three levels up from script)
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    db_dir = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
    db_path = os.path.join(db_dir, "Database_Table.db")

    # Connect to database and fetch Model names
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Model FROM ReadDIDModel;")
    rows = cursor.fetchall()
    model_list = [row[0] for row in rows]
    cursor.close()
    conn.close()

    def getdata(self):
        script_path = os.path.abspath(__file__)
        script_directory = os.path.dirname(script_path)
        dbpath = os.path.abspath(os.path.join(script_directory, '..', '..', '..', 'Database_Table.db'))

        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()

        model_to_filter = self.ModelName.strip().lower()
        cursor.execute("""
            SELECT CommandDescription, DID, RequestID, ResponseID
            FROM ReadDIDCommands
            WHERE lower(trim(Model)) = ?
        """, (model_to_filter,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        global data_list
        data_list = [list(row) for row in rows]

    # database
    ModelName = property(String, "").add_attribute(
        OpenTap.AvailableValues("ModelNames")).add_attribute(
        OpenTap.Display("Model", "Select a Model", "Database"))

    Description = property(String, "").add_attribute(OpenTap.AvailableValues("descriptions")).add_attribute(OpenTap.Display("Select description", "Select description", "Database"))
    ActionShown = property(Boolean, False) \
        .add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))
    Commands = property(String, "").add_attribute(
        OpenTap.AvailableValues("Cancommand")).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))
    TX_ID = property(String, "").add_attribute(OpenTap.AvailableValues("tx_id")).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))
    RX_ID = property(String, "").add_attribute(OpenTap.AvailableValues("rx_id")).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))
    #Input
    ServiceStr = property(String, "Default(1)") \
        .add_attribute(OpenTap.AvailableValues("ServiceLst")) \
        .add_attribute(
        OpenTap.Display("1.Services", "Service", "Input"))
    Command1 = property(String, "0.5").add_attribute(OpenTap.Display("2.Commands", "Add a COMMAND HERE", "INPUT"))
    ServiceLst = property(List[String], None).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))
    SeedVal = property(String, "").add_attribute(OpenTap.Display("2.Input Seed", "Seed Value", "INPUT"))

    Response = property(String, "").add_attribute(OpenTap.Display("3.Response", "Receive a Response Here", "INPUT"))
    Publish = property(Boolean, True).add_attribute(OpenTap.Display("4.Publish", "Enable if you are publish", "INPUT"))
    Timeout = property(Double, 1.0).add_attribute(OpenTap.Display("5.Timeout", "Add a timeout.", "INPUT"))
    TX_Timeout = property(Double, 0.5).add_attribute(OpenTap.Display("6.Interval", "Add a timeout to the can To send The Can message With timeout delay.", "INPUT"))
    Exact_Match = property(Boolean, True) \
        .add_attribute(Display("7.Equals", "Enable if you want to compare exactly between two inputs.", "INPUT"))

    Start_Byte = property(Int32, 0) \
        .add_attribute(Display("8.Start Byte", "Start index for extraction", "INPUT"))

    End_Byte = property(Int32, 2) \
        .add_attribute(Display("9.End Byte", "End index for extraction", "INPUT"))

    #Output
    ReceivedData = property(String, "").add_attribute(OpenTap.Display("7.ReceivedData", "Received Data", "Output")).add_attribute(Output())


    Logging = property(OpenTap.Enabled[String], None).add_attribute(OpenTap.Display("Logging", "Path of where the log file will be stored.", "Result Logging", 1))
    Points = property(Int32, 200).add_attribute(OpenTap.Display("Points", "Number points to store.", "Result Logging", 1))

    @property(List[String])
    @attribute(Browsable(False))
    @attribute(XmlIgnore(True))
    def descriptions(self):
        lst = List[String]()
        try:
            script_path = os.path.abspath(__file__)
            script_directory = os.path.dirname(script_path)
            dbpath = os.path.abspath(os.path.join(script_directory, '..', '..', '..', 'Database_Table.db'))

            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()

            model_to_filter = self.ModelName.strip().lower()
            cursor.execute(
                "SELECT CommandDescription FROM ReadDIDCommands WHERE lower(trim(Model)) = ?",
                (model_to_filter,))
            rows = cursor.fetchall()

            for row in rows:
                lst.Add(row[0])

            cursor.close()
            conn.close()
        except Exception as e:
            self.log.Warning(f"Failed to fetch descriptions: {e}")

        return lst

    @property(List[String])
    @attribute(Browsable(False))
    @attribute(XmlIgnore(True))
    def Cancommand(self):
        lst = List[String]()
        for row in data_list:
            lst.Add(row[1])
        return lst

    @property(List[String])
    @attribute(Browsable(False))
    @attribute(XmlIgnore(True))
    def tx_id(self):
        lst = List[String]()
        for row in data_list:
            lst.Add(row[2])
        return lst

    @property(List[String])
    @attribute(Browsable(False))
    @attribute(XmlIgnore(True))
    def rx_id(self):
        lst = List[String]()
        for row in data_list:
            lst.Add(row[3])
        return lst

    @property(List[String])
    @attribute(Browsable(False))
    @attribute(XmlIgnore(True))
    def ModelNames(self):
        lst = List[String]()

        # Move DB access here dynamically
        try:
            script_path = os.path.abspath(__file__)
            script_dir = os.path.dirname(script_path)
            db_dir = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
            db_path = os.path.join(db_dir, "Database_Table.db")

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT Model FROM ReadDIDModel;")
            rows = cursor.fetchall()

            for row in rows:
                lst.Add(row[0])

            cursor.close()
            conn.close()
        except Exception as e:
            self.log.Warning(f"Error reading models from database: {e}")

        return lst

    def __init__(self):
        super().__init__()
        self.ActionShown = False
        self.Logging = OpenTap.Enabled[String]()
        self.Logging.IsEnabled = True
        self.Logging.Value = "C:\\SessionLogs\\"

        self.ServiceLst = List[String]()
        # self.ServiceLst.Add("CAN Open")
        # self.ServiceLst.Add("CAN Close")
        self.ServiceLst.Add("Request Seed")
        self.ServiceLst.Add("SendKey")
        self.ServiceLst.Add("Tester Presence")
        self.ServiceLst.Add("Send Single Frame")
        self.ServiceLst.Add("Send Multi Frame")
        self.ServiceLst.Add("Read Single Frame")
        self.ServiceLst.Add("Read Multi Frame")
        self.ServiceLst.Add("Send Single Frame + Read Single Frame")
        self.ServiceLst.Add("Send Single Frame + Read Multi Frame")
        self.ServiceLst.Add("Send Multi Frame + Read Single Frame")
        self.ServiceLst.Add("Send Multi Frame + Read Multi Frame")
        self.ServiceLst.Add("Send Multi frame From Seed + Read Multi Frame")
        self.ServiceLst.Add("Testing")



    @attribute(Browsable(True))
    @method()
    def Run(self):
        super().Run()
        self.getdata()

        index = self.descriptions.index(self.Description)
        CMD, TX_ID, RX_ID = self.Cancommand[index], self.tx_id[index], self.rx_id[index]
        self.log.Info(f"TX: {TX_ID}, RX: {RX_ID}")

        received_data = self.Instrument.do_measurement1(
            CMD, TX_ID, RX_ID, self.Timeout, self.Response,
            self.ServiceStr, self.SeedVal, self.Command1, self.TX_Timeout
        )
        self.log.Info(f"Received data: {received_data}")

        def strip_spaces(s: str) -> str:
            if not s:
                return ""
            return s.replace(" ", "").replace("\t", "").replace("\n", "").upper()

        def split_bytes(hex_str):
            return [hex_str[i:i + 2] for i in range(0, len(hex_str), 2)]

        expected = strip_spaces(self.Response)
        actual = strip_spaces(received_data)

        # --- Ignore Tester Presence response completely ---
        if actual == "027E000000000000":
            self.log.Info("Tester Presence response ignored. Not storing or publishing.")
            # no verdict, no self.ReceivedData, just return
            return

        bytes_list = split_bytes(actual)

        start = max(0, self.Start_Byte)
        end = min(len(bytes_list) - 1, self.End_Byte)
        extracted = "".join(bytes_list[start:end + 1])

        verdict_set = False

        # --- Always check TIMEOUT / NO RESPONSE ---
        if not actual or "TIMEOUT" in actual.upper() or "NO RESPONSE" in actual.upper():
            self.UpgradeVerdict(OpenTap.Verdict.Fail)
            self.log.Error(f"Timeout or no response. Actual: {actual}")
            verdict_set = True

        # --- Always check negative response (NRC) ---
        elif len(bytes_list) >= 3 and bytes_list[0] == "7F":
            nrc = bytes_list[2] if len(bytes_list) > 2 else "??"
            nrc_dict = {
                "10": "General Reject",
                "11": "Service Not Supported",
                "12": "Sub-Function Not Supported",
                "22": "Conditions Not Correct",
                "33": "Security Access Denied",
                "35": "Invalid Key",
                "36": "Exceeded Number of Attempts",
                "78": "Response Pending"
            }
            meaning = nrc_dict.get(nrc, "Unknown NRC")
            self.UpgradeVerdict(OpenTap.Verdict.Fail)
            self.log.Error(f"Negative response received: {actual} (NRC={nrc} → {meaning})")
            verdict_set = True

        # --- Only perform comparison if we have an expected value ---
        if expected and not verdict_set:
            if self.Exact_Match:
                if expected == extracted:
                    self.log.Info(f"Matched Both Inputs: {expected} == {extracted}")
                    self.UpgradeVerdict(OpenTap.Verdict.Pass)
                else:
                    self.log.Info(f"Inputs are Not Matching: {expected} != {extracted}")
                    self.UpgradeVerdict(OpenTap.Verdict.Fail)
            else:
                if expected in extracted:
                    self.log.Info(f"Matched: {expected} found in {extracted}")
                    self.UpgradeVerdict(OpenTap.Verdict.Pass)
                else:
                    self.log.Info(f"Not Matched: {expected} not in {extracted}")
                    self.UpgradeVerdict(OpenTap.Verdict.Fail)

        # --- If no expected value and no errors, just pass ---
        elif not expected and not verdict_set:
            self.UpgradeVerdict(OpenTap.Verdict.Pass)

        if self.Publish:
            self.PublishResult("data", ["value", "lsl", "usl", "unit"],
                               [actual, expected, expected, "-"])

        # Store only if it’s not Tester Presence
        self.ReceivedData = str(actual)






