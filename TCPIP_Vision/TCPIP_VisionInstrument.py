from opentap import *
import socket
from opentap import *
from opentap import *
from opentap import TestStep, attribute
import OpenTap
from OpenTap import Log, DisplayAttribute, Display, Output, Unit, OutputAttribute, UnitAttribute,AvailableValues, EnabledIfAttribute
from System import Array, Double, Byte, Int32, String, Boolean
from opentap import *

@attribute(OpenTap.Display("Vision TCP/IP Communication", "Instrument settings for the TCP/IP Server", "MTS-Vision"))
class TCPIP_Vision_CLIENTInstrument(Instrument):

    TCPIP_Vision_host = property(String, '127.0.0.1') \
        .add_attribute(OpenTap.Display("Host", "The Host for Communication."))
    TCPIP_Vision_port = property(Int32, 8080) \
        .add_attribute(OpenTap.Display("Port", "Enter TCP/IP Port."))
    Vision_Log = property(Boolean, False).add_attribute(
        OpenTap.Display("Vision Log", "Enable if you save the Vision Log"))
    Vision_Log_Path = property(String, "") \
        .add_attribute(Display("Vision_Log_Path", "Copy the full folder name here")) \
        .add_attribute(OpenTap.FilePathAttribute, OpenTap.FilePathAttribute.BehaviorChoice.Open)


    def __init__(self):
        super(TCPIP_Vision_CLIENTInstrument, self).__init__()
        self.Name = "Vision"
        self.client_sockclient = None
        # ============================================
        # SINGLE LOG FILE FOR COMPLETE SESSION
        # ============================================

        self.Log_File = None

        self.log.Info("Vision initialized.")

        # =================================================
        # CREATE SINGLE LOG FILE
        # =================================================
    def Create_Log_File(self):

        import os
        import datetime

        # ============================================
        # USE SAME FILE FOR COMPLETE SESSION
        # ============================================

        if self.Log_File:
            return self.Log_File

        now = datetime.datetime.now()

        # ============================================
        # FOLDER STRUCTURE
        # ============================================

        year_folder = now.strftime("%Y")
        month_folder = now.strftime("%B")
        date_folder = now.strftime("%d-%m-%Y")

        final_folder = os.path.join(
            self.Vision_Log_Path,
            year_folder,
            month_folder,
            date_folder
        )

        # ============================================
        # CREATE FOLDER
        # ============================================

        os.makedirs(final_folder, exist_ok=True)

        # ============================================
        # FILE NAME
        # ============================================

        file_name = now.strftime(
            "%H_%M_%S_%f"
        )[:-3] + ".csv"

        self.Log_File = os.path.join(
            final_folder,
            file_name
        )

        # ============================================
        # CREATE FILE FIRST TIME
        # ============================================

        with open(self.Log_File, "w") as f:
            f.write(
                "Timestamp,Message\n"
            )

        self.log.Info(
            f"Vision Log File Created : "
            f"{self.Log_File}"
        )

        return self.Log_File

    def Write_Log(self, message):

        import datetime

        if not self.Vision_Log:
            return

        try:

            log_file = self.Create_Log_File()

            with open(log_file, "a") as f:

                f.write(
                    f"{datetime.datetime.now()},"
                    f"{message}\n"
                )

        except Exception as e:

            self.log.Info(
                f"Vision Log Write Error : "
                f"{str(e)}"
            )

    @method(String)
    def do_measurement(self, data, Timeout, ServiceStr):
        try:
            # -----------------------------
            # Timeout Configuration
            # -----------------------------
            if Timeout > 0:
                self.log.Info(f"Setting timeout to {Timeout} seconds.")
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Setting timeout to {Timeout} seconds."
                )
            else:
                self.log.Info("Timeout set to 0 (blocking mode).")
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Timeout set to 0 (blocking mode)."
                )

            # =========================================================
            # OPEN CONNECTION
            # =========================================================
            if ServiceStr == "OPEN":

                if self.client_sockclient is not None:
                    self.log.Info("Connection already open.")
                    # ==================================================
                    # SAVE LOG
                    # ==================================================

                    self.Write_Log(
                        f"| Connection already open."
                    )
                    return "OPEN_ALREADY"

                self.client_sockclient = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                if Timeout > 0:
                    self.client_sockclient.settimeout(Timeout)

                self.client_sockclient.connect(
                    (self.TCPIP_Vision_host, self.TCPIP_Vision_port)
                )

                self.log.Info(
                    f"Connected to {self.TCPIP_Vision_host}:{self.TCPIP_Vision_port}"
                )
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Connected to {self.TCPIP_Vision_host}:{self.TCPIP_Vision_port}"
                )

                return "OPEN_OK"

            # =========================================================
            # CHECK CONNECTION
            # =========================================================
            if self.client_sockclient is None:
                self.log.Error("Socket connection is not open.")
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Error| Socket connection is not open."
                )
                return "SOCKET_NOT_OPEN"

            # =========================================================
            # SEND DATA
            # =========================================================
            elif ServiceStr == "SEND":

                cmd = f"{data}\r"

                encoded_cmd = cmd.encode("ascii")

                self.client_sockclient.sendall(encoded_cmd)

                self.log.Info(
                    f"Sent ASCII : {cmd.strip()}"
                )
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Sent ASCII : {cmd.strip()}"
                )

                self.log.Info(
                    f"Sent HEX   : {encoded_cmd.hex(' ')}"
                )
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Sent HEX   : {encoded_cmd.hex(' ')}"
                )

                return f"SEND_OK : {data}"

            # =========================================================
            # RECEIVE DATA
            # =========================================================
            elif ServiceStr == "RECEIVE":

                if Timeout > 0:
                    self.client_sockclient.settimeout(Timeout)

                raw_data = self.client_sockclient.recv(1024)

                if not raw_data:
                    self.log.Warning("No data received.")
                    # ==================================================
                    # SAVE LOG
                    # ==================================================

                    self.Write_Log(
                        f"| Warning| No data received."
                    )
                    return "NO_DATA"

                # Decode safely
                decoded_data = raw_data.decode(
                    "ascii",
                    errors="ignore"
                ).strip()

                self.log.Info(
                    f"Received HEX   : {raw_data.hex(' ')}"
                )
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Received HEX   : {raw_data.hex(' ')}"
                )

                self.log.Info(
                    f"Received ASCII : {decoded_data}"
                )
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Received ASCII : {decoded_data}"
                )

                return decoded_data

            # =========================================================
            # CLOSE CONNECTION
            # =========================================================
            elif ServiceStr == "CLOSE":

                try:
                    self.client_sockclient.shutdown(socket.SHUT_RDWR)

                except Exception as e:
                    self.log.Warning(f"Shutdown skipped: {e}")
                    # ==================================================
                    # SAVE LOG
                    # ==================================================

                    self.Write_Log(
                        f"| Warning| Shutdown skipped: {e}"
                    )

                self.client_sockclient.close()

                self.client_sockclient = None

                self.log.Info("Socket connection closed.")
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    "| Socket connection closed."
                )

                return "CLOSE_OK"

            # =========================================================
            # INVALID SERVICE
            # =========================================================
            else:
                self.log.Error(f"Invalid ServiceStr: {ServiceStr}")
                # ==================================================
                # SAVE LOG
                # ==================================================

                self.Write_Log(
                    f"| Invalid ServiceStr: {ServiceStr}"
                )
                return "INVALID_SERVICE"

        # =============================================================
        # EXCEPTION HANDLING
        # =============================================================
        except ValueError as ve:

            self.log.Error(f"Value Error: {ve}")
            # ==================================================
            # SAVE LOG
            # ==================================================

            self.Write_Log(
                f"| Value Error: {ve}"
            )

            return f"VALUE_ERROR : {ve}"

        except socket.timeout:

            self.log.Error(
                f"Socket timeout after {Timeout} seconds."
            )
            # ==================================================
            # SAVE LOG
            # ==================================================

            self.Write_Log(
                f"| Socket timeout after {Timeout} seconds."
            )

            return "TIMEOUT"

        except socket.error as se:

            self.log.Error(
                f"Socket Error: {se}"
            )
            # ==================================================
            # SAVE LOG
            # ==================================================

            self.Write_Log(
                f"| Socket Error: {se}"
            )

            # Auto cleanup
            if self.client_sockclient:
                try:
                    self.client_sockclient.close()
                except:
                    pass

                self.client_sockclient = None

            return f"SOCKET_ERROR : {se}"

        except Exception as e:

            self.log.Error(
                f"Unexpected Error in do_measurement: {e}"
            )
            # ==================================================
            # SAVE LOG
            # ==================================================

            self.Write_Log(
                f"| Unexpected Error in do_measurement: {e}"
            )

            return f"ERROR : {e}"