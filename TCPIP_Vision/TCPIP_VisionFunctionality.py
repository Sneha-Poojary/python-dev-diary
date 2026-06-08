from opentap import *
from opentap import *
from .TCPIP_VisionInstrument import TCPIP_Vision_CLIENTInstrument
import clr
from System.Collections.Generic import List
from opentap import *
import OpenTap
from System import Array, Double, Byte, Int32, String, Boolean
from System.ComponentModel import Browsable
from System.Xml.Serialization import XmlIgnore
from System import Double
from OpenTap import Log, DisplayAttribute, Display, Output, Unit, OutputAttribute, UnitAttribute,AvailableValues, EnabledIfAttribute
clr.AddReference("System.Collections")

@attribute(OpenTap.Display("Vision TCP/IP Communication", "TCP/IP Protocol Settings", "MTS - Vision"))
@attribute(OpenTap.AllowAnyChild())
class TCPIP_Vision_CLIENTFunctionality(TestStep):

    Instrument = property(TCPIP_Vision_CLIENTInstrument, None) \
        .add_attribute(OpenTap.Display("Instrument", "The instrument to use in the step", "Resources"))

    DATA = property(String, "") \
        .add_attribute(OpenTap.Display("DATA", "Enter DATA", "Input"))

    Response = property(String, "OK") \
        .add_attribute(OpenTap.Display("RESPONSE", "Response should compare only {RT,00898,OK,01,OK,0000096} this format", "Input"))

    ServiceStr = property(String, "Open") \
        .add_attribute(OpenTap.AvailableValues("ServiceLst")) \
        .add_attribute(
        OpenTap.Display("1.Service", "Service", "Types"))
    ServiceLst = property(List[String], None).add_attribute(OpenTap.EnabledIf("ActionShown", True, HideIfDisabled=True))

    Timeout = property(Double, 0.0) \
        .add_attribute(OpenTap.Display("Timeout", "Enter CLIENT MODBUS Timeout Here.", "Input"))

    Output = property(String, "")\
        .add_attribute(Display("Output", "", "Output", 0))\
        .add_attribute(Output())

    # ==================================================
    # Publish
    # ==================================================
    Test_ID =  property(Int32, 0).add_attribute(OpenTap.Display("Test_ID", "Add a Test_ID.", "Publish"))
    Publish = property(Boolean, True).add_attribute(OpenTap.Display("Publish", "Enable if you are publish", "Publish"))
    Select_dut = property(String, "DUT1") \
        .add_attribute(OpenTap.AvailableValues("Available")) \
        .add_attribute(OpenTap.Display("Select DUT", "Select DUT", "Publish"))
    @property(List[String])
    @attribute(Browsable(False))
    @attribute(XmlIgnore(True))
    def Available(self):
        available_dut = List[String]()
        available_dut.Add("DUT1")
        available_dut.Add("DUT2")
        available_dut.Add("DUT3")
        available_dut.Add("DUT4")
        available_dut.Add("DUT5")

    def __init__(self):
        super().__init__()

        self.ServiceLst = List[String]()
        self.ServiceLst.Add("OPEN")
        self.ServiceLst.Add("CLOSE")
        self.ServiceLst.Add("SEND")
        self.ServiceLst.Add("RECEIVE")

    @method()
    def Run(self):

        super().Run()

        # =========================================================
        # Convert Timeout
        # =========================================================
        try:
            timeout_value = float(self.Timeout)

        except ValueError:

            self.log.Error(
                f"Invalid timeout value: {self.Timeout}"
            )

            self.UpgradeVerdict(OpenTap.Verdict.Fail)

            return

        # =========================================================
        # Perform Measurement
        # =========================================================
        received_data = self.Instrument.do_measurement(
            self.DATA,
            timeout_value,
            self.ServiceStr
        )

        self.log.Info(f"received_data: {received_data}")

        # =========================================================
        # Common Error Handling
        # =========================================================
        error_keywords = [
            "ERROR",
            "TIMEOUT",
            "[WinError 10057]",
            "[WinError 10061]",
            "SOCKET_ERROR",
            "SOCKET_NOT_OPEN"
        ]

        for error in error_keywords:

            if error in received_data:
                self.log.Error(f"Detected Error: {error}")

                self.UpgradeVerdict(OpenTap.Verdict.Fail)

                return

        # =========================================================
        # OPEN
        # =========================================================
        if self.ServiceStr == "OPEN":

            if received_data in ["OPEN_OK", "OPEN_ALREADY"]:

                self.UpgradeVerdict(OpenTap.Verdict.Pass)

            else:

                self.UpgradeVerdict(OpenTap.Verdict.Fail)

        # =========================================================
        # SEND
        # =========================================================
        elif self.ServiceStr == "SEND":

            if "SEND_OK" in received_data:

                self.UpgradeVerdict(OpenTap.Verdict.Pass)

            else:

                self.UpgradeVerdict(OpenTap.Verdict.Fail)

        # =========================================================
        # RECEIVE
        # =========================================================
        elif self.ServiceStr == "RECEIVE":

            try:

                parts = received_data.split(",")

                if len(parts) < 3:
                    self.log.Error(
                        "Invalid response format"
                    )

                    self.UpgradeVerdict(OpenTap.Verdict.Fail)

                    return

                # Third comma separated value
                third_value = parts[2].strip()

                self.log.Info(
                    f"Extracted Third Value: {third_value}"
                )

                # Empty expected response
                if self.Response == "":

                    self.log.Info(
                        "Empty expected response -> PASS"
                    )

                    self.UpgradeVerdict(OpenTap.Verdict.Pass)

                # Compare response
                elif third_value == self.Response:

                    self.log.Info(
                        f"Matched: {third_value}"
                    )

                    self.UpgradeVerdict(OpenTap.Verdict.Pass)

                else:

                    self.log.Error(
                        f"Mismatch: Expected={self.Response}, "
                        f"Received={third_value}"
                    )

                    self.UpgradeVerdict(OpenTap.Verdict.Fail)

            except Exception as e:

                self.log.Error(
                    f"Receive Parsing Error: {e}"
                )

                self.UpgradeVerdict(OpenTap.Verdict.Fail)

        # =========================================================
        # CLOSE
        # =========================================================
        elif self.ServiceStr == "CLOSE":

            if received_data == "CLOSE_OK":

                self.UpgradeVerdict(OpenTap.Verdict.Pass)

            else:

                self.UpgradeVerdict(OpenTap.Verdict.Fail)

        # =========================================================
        # INVALID SERVICE
        # =========================================================
        else:

            self.log.Error(
                f"Invalid ServiceStr: {self.ServiceStr}"
            )

            self.UpgradeVerdict(OpenTap.Verdict.Fail)

        if self.Publish:
            self.PublishResult(
                f"{self.Select_dut}",
                [f"{self.Select_dut}", "lsl", "usl", "unit"],
                [str(received_data), self.Response, self.Response, "-"]
            )
            self.log.Info("Data Published Successfully")
        self.Output = str(received_data)