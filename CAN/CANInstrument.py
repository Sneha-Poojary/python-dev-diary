from opentap import *
from opentap import *
import re
from udsoncan.connections import PythonIsoTpConnection
from System import Double, String, Int32
from udsoncan.client import Client
import can
import time
import threading
from udsoncan.services import ReadDataByIdentifier
from udsoncan.exceptions import NegativeResponseException
import isotp
import udsoncan.configs
from udsoncan import AsciiCodec
from udsoncan import Request, services, Response
import struct
from datetime import datetime
from udsoncan import services
from udsoncan.exceptions import *
from udsoncan import DidCodec
from udsoncan import Request, Response, services
from udsoncan.common.Routine import Routine
from udsoncan.common.dtc import Dtc
from udsoncan.common.dids import DataIdentifier
from udsoncan.common.MemoryLocation import MemoryLocation
from udsoncan.common.DynamicDidDefinition import DynamicDidDefinition
from udsoncan.common.CommunicationType import CommunicationType
from udsoncan.common.DataFormatIdentifier import DataFormatIdentifier
from udsoncan.common.Baudrate import Baudrate
from udsoncan.common.IOControls import IOValues, IOMasks
from udsoncan.common.Filesize import Filesize
from udsoncan.connections import BaseConnection
from udsoncan.BaseService import BaseService
import can
import cantools
import time
from udsoncan.exceptions import *
from udsoncan.configs import default_client_config
from udsoncan.typing import ClientConfig, TypedDict
import logging
import binascii
import functools
import time
import random
import binascii
import threading
from udsoncan.connections import IsoTPConnection
import isotp
import threading
import time
import can
from opentap import TestStep, attribute
import OpenTap
from OpenTap import Log, DisplayAttribute, Display, Output, Unit, OutputAttribute, UnitAttribute,AvailableValues, EnabledIfAttribute
from System import Array, Double, Byte, Int32, String, Boolean
import clr
import csv
from System.Collections.Generic import List
from opentap import *
@attribute(OpenTap.Display("CAN", "Manages CAN interface", "MTS - CAN"))
class CANInstrument(Instrument):
    canBaudrate = property(Int32, 500000).add_attribute(OpenTap.Display("Baudrate", "The baudrate for CAN communication."))
    canDevice = property(String, "nixnet").add_attribute(OpenTap.Display("CAN Device", "Specify CAN device interface."))
    Channel = property(String, "CAN3").add_attribute(OpenTap.Display("Channel", "Specify CAN device channel."))
    CAN_Log = property(Boolean, False).add_attribute(
        OpenTap.Display("CAN Log", "Enable if you save the CAN Log"))
    CAN_LOG_Path = property(String, "") \
        .add_attribute(Display("CAN_LOG_Path", "Path to CAN Log")) \
        .add_attribute(OpenTap.FilePathAttribute, OpenTap.FilePathAttribute.BehaviorChoice.Open)
    def __init__(self):
        super(CANInstrument, self).__init__()
        self.Name = "CAN"
        self.bus = None
        self.count = 0
        self.is_bus_open = False
        self.log.Info("CAN initialized.")
        self.cyclic_thread = None
        self.keep_running_event = threading.Event()
        # ============================================
        # SINGLE LOG FILE FOR COMPLETE SESSION
        # ============================================

        self.CAN_Log_File = None

        self.log.Info("CAN initialized.")

        # =================================================
        # CREATE SINGLE LOG FILE
        # =================================================

    def Create_CAN_Log_File(self):

        import os
        import datetime

        # ============================================
        # USE SAME FILE FOR COMPLETE SESSION
        # ============================================

        if self.CAN_Log_File:
            return self.CAN_Log_File

        now = datetime.datetime.now()

        # ============================================
        # FOLDER STRUCTURE
        # ============================================

        year_folder = now.strftime("%Y")
        month_folder = now.strftime("%B")
        date_folder = now.strftime("%d-%m-%Y")

        final_folder = os.path.join(
            self.CAN_LOG_Path,
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

        self.CAN_Log_File = os.path.join(
            final_folder,
            file_name
        )

        # ============================================
        # CREATE FILE FIRST TIME
        # ============================================

        with open(self.CAN_Log_File, "w") as f:
            f.write(
                "Timestamp,Message\n"
            )

        self.log.Info(
            f"CAN Log File Created : "
            f"{self.CAN_Log_File}"
        )

        return self.CAN_Log_File

    def Write_CAN_Log(self, message):

        import datetime

        if not self.CAN_Log:
            return

        try:

            log_file = self.Create_CAN_Log_File()

            with open(log_file, "a") as f:

                f.write(
                    f"{datetime.datetime.now()},"
                    f"{message}\n"
                )

        except Exception as e:

            self.log.Info(
                f"CAN Log Write Error : "
                f"{str(e)}"
            )    @method(String)

    def do_measurement1(self, Commands, TX_ID,RX_ID, Timeout, SessionNo, ServiceStr,SeedValue,Command1,TX_TimeoutTX_Timeout):
        timeout = float(Timeout)

        try:

            import can
            import time
            if ServiceStr == "Request Seed":
                import time
                import can
                try:
                    TxID_int = int(TX_ID, 16)
                    RxID_int = int(RX_ID, 16)
                    uds_data = [int(x, 16) for x in Commands.strip().split()]

                    if len(uds_data) > 8:
                        self.log.Info("Data length exceeds CAN single frame size (8 bytes).")
                        return "Error: Data length exceeds CAN single frame size (8 bytes)."

                    # Pad with 0x00 if less than 8 bytes
                    while len(uds_data) < 8:
                        uds_data.append(0x00)
                    self.log.Info(f"TX ID: {TX_ID}")
                    # === Send Command ===
                    try:
                        msg = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=uds_data)
                        self.bus.send(msg)
                        self.log.Info(f"Command Sent Successfully, the Command is:{[hex(x) for x in uds_data]}")

                    except Exception as e:
                        self.log.Info(f"Error sending CAN message: {str(e)}")
                        return f"Error sending CAN message: {str(e)}"

                    # === Receive Response ===
                    start_time = time.time()
                    response_frames = []
                    total_payload = []
                    expected_len = None


                    while True:
                        if timeout > 0 and (time.time() - start_time) > timeout:
                            self.log.Info("Timeout waiting for response")
                            return None

                        response_msg = self.bus.recv(0)
                        if response_msg and response_msg.arbitration_id == RxID_int:

                            frame = list(response_msg.data)
                            pci_type = frame[0] >> 4
                            self.log.Info(
                                f"Raw Response: ID={hex(response_msg.arbitration_id)}, Data={response_msg.data.hex()}")
                            self.log.Info(f"Matched ID Data: {frame}")

                            if pci_type == 0x0:
                                self.log.Info("Skipping unrelated Single Frame response.")
                                continue

                            if pci_type == 0x1:  # First Frame
                                expected_len = ((frame[0] & 0x0F) << 8) + frame[1]
                                total_payload.extend(frame[2:])
                                response_frames.append(frame)
                                flow_control_frame = [0x30, 0x00, 0x14] + [0x00] * 5
                                fc_msg = can.Message(arbitration_id=TxID_int, is_extended_id=False,
                                                     data=flow_control_frame)
                                self.bus.send(fc_msg)
                                self.log.Info(f"Sent Flow Control Frame: {[hex(x) for x in flow_control_frame]}")
                                continue
                            elif pci_type == 0x2:  # Consecutive Frame
                                total_payload.extend(frame[1:])
                                response_frames.append(frame)

                            if expected_len > 0 and len(total_payload) >= expected_len:
                                break

                        time.sleep(0.001)

                    if not response_frames:
                        self.log.Info("No matching response received")
                        return None

                    while total_payload and total_payload[-1] in (0x00, 0xCC):
                        total_payload.pop()
                    self.log.Info(f"Full ISO-TP Payload: {[hex(x) for x in total_payload]}")
                    iso_payload_hex = ''.join(f'{x:02X}' for x in total_payload)
                    self.log.Info(f"Full ISO-TP Payload: {iso_payload_hex}")
                    return iso_payload_hex

                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    return None
            elif ServiceStr == "SendKey":
                try:
                    import time
                    import can

                    self.log.Info(f"Seed Value: {SeedValue}")

                    TxID_int = int(TX_ID, 16)
                    RxID_int = int(RX_ID, 16)

                    self.log.Info(f"TX_ID: {TX_ID}")

                    # ==================================================
                    # CONVERT HEX SEED TO BYTES
                    # ==================================================

                    key_bytes = bytes.fromhex(SeedValue)

                    if len(key_bytes) != 16:
                        self.log.Info(
                            "Seed/key length is not 16 bytes"
                        )

                        self.Write_CAN_Log(
                            "ERROR | Seed/key length is not 16 bytes"
                        )

                        return None

                    # ==================================================
                    # UDS SECURITY ACCESS PAYLOAD
                    # ==================================================

                    full_payload = [
                                       0x27,
                                       0x62
                                   ] + list(key_bytes)

                    self.log.Info(
                        f"Full Payload: "
                        f"{[hex(b) for b in full_payload]}"
                    )

                    # ==================================================
                    # SEND FIRST FRAME
                    # ==================================================

                    frame1 = [
                                 0x10,
                                 0x12
                             ] + full_payload[:6]

                    frame1 += [0x00] * (
                            8 - len(frame1)
                    )

                    self.bus.send(
                        can.Message(
                            arbitration_id=TxID_int,
                            is_extended_id=False,
                            data=frame1
                        )
                    )

                    frame1_hex = ' '.join(
                        f"{x:02X}"
                        for x in frame1
                    )

                    self.log.Info(
                        f"Sent Frame 1: "
                        f"{[hex(b) for b in frame1]}"
                    )

                    self.Write_CAN_Log(
                        f"TX | ID:{TX_ID} | FF | DATA:{frame1_hex}"
                    )

                    time.sleep(0.011)

                    # ==================================================
                    # SEND CONSECUTIVE FRAME 1
                    # ==================================================

                    frame2 = [
                                 0x21
                             ] + full_payload[6:13]

                    frame2 += [0x00] * (
                            8 - len(frame2)
                    )

                    self.bus.send(
                        can.Message(
                            arbitration_id=TxID_int,
                            is_extended_id=False,
                            data=frame2
                        )
                    )

                    frame2_hex = ' '.join(
                        f"{x:02X}"
                        for x in frame2
                    )

                    self.log.Info(
                        f"Sent Frame 2: "
                        f"{[hex(b) for b in frame2]}"
                    )

                    self.Write_CAN_Log(
                        f"TX | ID:{TX_ID} | CF SN:1 | DATA:{frame2_hex}"
                    )

                    time.sleep(0.011)

                    # ==================================================
                    # SEND CONSECUTIVE FRAME 2
                    # ==================================================

                    frame3 = [
                                 0x22
                             ] + full_payload[13:]

                    frame3 += [0x00] * (
                            8 - len(frame3)
                    )

                    self.bus.send(
                        can.Message(
                            arbitration_id=TxID_int,
                            is_extended_id=False,
                            data=frame3
                        )
                    )

                    frame3_hex = ' '.join(
                        f"{x:02X}"
                        for x in frame3
                    )

                    self.log.Info(
                        f"Sent Frame 3: "
                        f"{[hex(b) for b in frame3]}"
                    )

                    self.Write_CAN_Log(
                        f"TX | ID:{TX_ID} | CF SN:2 | DATA:{frame3_hex}"
                    )

                    self.log.Info(
                        "Manual ISO-TP key send complete."
                    )

                    # ==================================================
                    # RECEIVE RESPONSE
                    # ==================================================

                    start_time = time.time()

                    response = None

                    while time.time() - start_time < 0.5:

                        msg = self.bus.recv(0)

                        if (
                                msg and
                                msg.arbitration_id == RxID_int
                        ):

                            response = msg.data

                            response_hex = ' '.join(
                                f"{x:02X}"
                                for x in response
                            )

                            self.log.Info(
                                f"Received Response: "
                                f"{response.hex()}"
                            )

                            # ==================================================
                            # SAVE RX LOG
                            # ==================================================

                            self.Write_CAN_Log(
                                f"RX | ID:{RX_ID} | DATA:{response_hex}"
                            )

                            if response == 2:
                                break

                        time.sleep(0.00)

                    # ==================================================
                    # NO RESPONSE
                    # ==================================================

                    if not response:
                        self.log.Info(
                            "No response received after sending key."
                        )

                        self.Write_CAN_Log(
                            "TIMEOUT | No response received after sending key"
                        )

                        return None

                    # ==================================================
                    # FINAL RESPONSE
                    # ==================================================

                    final_response = response.hex()

                    self.Write_CAN_Log(
                        f"SECURITY ACCESS RESPONSE | DATA:{final_response}"
                    )

                    return final_response

                except Exception as e:

                    self.log.Info(
                        f"Exception occurred: {str(e)}"
                    )

                    self.Write_CAN_Log(
                        f"ERROR | {str(e)}"
                    )

                    return None
            elif ServiceStr == "Tester Presence":
                import time
                import can
                try:
                    TX_ID = TX_ID
                    RxID = int(RX_ID, 16)
                    self.log.Info(f"TX_ID: {TX_ID}")

                    # Prepare frame
                    command_bytes1 = [0x02, 0x3E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                    self.log.Info(f"Frame: {[hex(x) for x in command_bytes1]}")

                    # Read timeout property (default 0.5s = 500 ms)
                    try:
                        send_interval = float(self.TX_Timeout)  # seconds
                    except:
                        send_interval = 0.5  # fallback default
                    self.log.Info(f"Tester Presence interval: {send_interval} seconds")

                    start_time = time.time()
                    response_data = None

                    while timeout == 0 or (time.time() - start_time) < timeout:
                        # Send tester presence
                        msg1 = can.Message(
                            arbitration_id=int(TX_ID, 16),
                            is_extended_id=False,
                            data=command_bytes1
                        )
                        self.bus.send(msg1)
                        self.log.Info("Tester Presence Sent")

                        # Listen for response briefly
                        response_msg = self.bus.recv(0.01)
                        if response_msg:
                            self.log.Info(
                                f"RX: ID={hex(response_msg.arbitration_id)}, "
                                f"Data={[hex(b) for b in response_msg.data]}"
                            )
                            if response_msg.arbitration_id == RxID:
                                response_data = response_msg.data.hex()
                                self.log.Info(f"Matched ID Data: {response_data}")

                        # Wait configured interval (e.g., 0.5s = 500 ms)
                        time.sleep(send_interval)

                    #return response_data

                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    return None
            elif ServiceStr == "Send Single Frame":
                try:
                    # TXID and timeout
                    TxID_int = int(TX_ID, 16)
                    uds_data = [int(x, 16) for x in Commands.strip().split()]

                    if len(uds_data) > 8:
                        self.log.Info("Data length exceeds CAN single frame size (8 bytes).")
                        return "Error: Data length exceeds CAN single frame size (8 bytes)."

                    # Pad with 0x00 if less than 8 bytes
                    while len(uds_data) < 8:
                        uds_data.append(0x00)

                    self.log.Info(f"TX ID: {TX_ID}")
                    msg = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=uds_data)
                    self.bus.send(msg)
                    self.log.Info(f"Command Sent Successfully: {[hex(x) for x in uds_data]}")

                    return ' '.join(f"{x:02X}" for x in uds_data)

                except ValueError as e:
                    self.log.Info(f"Invalid command format: {str(e)}")
                    return f"Invalid command format: {str(e)}"
                except Exception as e:
                    self.log.Info(f"Error sending CAN message: {str(e)}")
                    return f"Error sending CAN message: {str(e)}"
            elif ServiceStr == "Send Multi Frame":
                try:
                    #TXID and timeout
                    TxID_int = int(TX_ID, 16)
                    timeout = float(timeout)

                    #check the command lenghth
                    uds_data = [int(x, 16) for x in Commands.split()]
                    length = len(uds_data)

                    # === Send Command ===
                    first_frame_length = length
                    FF_DL = [(0x10 | (first_frame_length >> 8)), (first_frame_length & 0xFF)]
                    command_bytes1 = FF_DL + uds_data[:6]
                    msg1 = can.Message(arbitration_id=TxID_int, is_extended_id=False,
                                       data=command_bytes1 + [0x00] * (8 - len(command_bytes1)))
                    self.bus.send(msg1)
                    self.log.Info(f"Sent First Frame: {[hex(x) for x in command_bytes1]}")
                    time.sleep(0.01)
                    self.log.Info(f"TX ID: {TX_ID}")

                    seq_num = 1
                    offset = 6
                    while offset < len(uds_data):
                        frame_data = [0x20 | (seq_num & 0x0F)] + uds_data[offset:offset + 7]
                        while len(frame_data) < 8:
                            frame_data.append(0x00)
                        msg_cf = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=frame_data)
                        self.bus.send(msg_cf)
                        self.log.Info(f"Sent CF#{seq_num}: {[hex(x) for x in frame_data]}")
                        offset += 7
                        seq_num = (seq_num + 1) % 16
                        time.sleep(0.01)  # handle STmin spec
                    command = {[hex(x) for x in command_bytes1],[hex(x) for x in frame_data]}
                    return command

                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    return None
            elif ServiceStr == "Read Single Frame":
                try:
                    RxID_int = int(RX_ID, 16)
                    timeout_val = float(timeout)
                    self.log.Info(f"Listening for RX ID: {hex(RxID_int)} for {timeout_val} seconds")

                    start_time = time.time()
                    response_data = None

                    while timeout_val == 0 or (time.time() - start_time) < timeout_val:
                        response_msg = self.bus.recv(0)
                        if response_msg and response_msg.arbitration_id == RxID_int:
                            raw_data = list(response_msg.data)
                            self.log.Info(f"Matched ID Data: {[hex(x) for x in raw_data]}")

                            # Return all 8 bytes as-is
                            response_data = ' '.join(f'{x:02X}' for x in raw_data)
                            self.log.Info(f"Raw Response: {response_data}")
                            break
                    if not response_data:
                        self.log.Info("No matching response received within timeout.")
                        return "Timeout: No response received"

                    return response_data

                except ValueError:
                    self.log.Info("Invalid RX ID or timeout format.")
                    return "Error: Invalid RX ID or timeout format."
                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    return f"Error: {str(e)}"
            elif ServiceStr == "Read Multi Frame":
                try:
                    RxID_int = int(RX_ID, 16)
                    TxID_int = int(TX_ID, 16)
                    timeout = float(timeout)
                    self.log.Info(f"RX ID: {RxID_int}, TX ID : {TxID_int}")

                    start_time = time.time()
                    response_frames = []
                    total_payload = []
                    expected_len = None

                    while True:
                        if timeout > 0 and (time.time() - start_time) > timeout:
                            self.log.Info("Timeout waiting for response")
                            return None

                        response_msg = self.bus.recv(0)
                        if response_msg and response_msg.arbitration_id == RxID_int:

                            frame = list(response_msg.data)
                            pci_type = frame[0] >> 4
                            self.log.Info(f"Raw Response: ID={hex(response_msg.arbitration_id)}, Data={response_msg.data.hex()}")
                            self.log.Info(f"Matched ID Data: {frame}")

                            if pci_type == 0x0:
                                self.log.Info("Skipping unrelated Single Frame response.")
                                continue

                            if pci_type == 0x1:  # First Frame
                                expected_len = ((frame[0] & 0x0F) << 8) + frame[1]
                                total_payload.extend(frame[2:])
                                response_frames.append(frame)
                                flow_control_frame = [0x30, 0x00, 0x14] + [0x00] * 5
                                fc_msg = can.Message(arbitration_id=TxID_int, is_extended_id=False,
                                                     data=flow_control_frame)
                                self.bus.send(fc_msg)
                                self.log.Info(f"Sent Flow Control Frame: {[hex(x) for x in flow_control_frame]}")
                                continue
                            elif pci_type == 0x2:  # Consecutive Frame
                                total_payload.extend(frame[1:])
                                response_frames.append(frame)

                            if expected_len > 0 and len(total_payload) >= expected_len:
                                break

                    if not response_frames:
                        self.log.Info("No matching response received.")
                        return None
                    while total_payload and total_payload[-1] in (0x00, 0xCC):
                        total_payload.pop()
                    self.log.Info(f"Full ISO-TP Payload: {[hex(x) for x in total_payload]}")
                    iso_payload_hex = ' '.join(f'{x:02X}' for x in total_payload)
                    self.log.Info(f"Full ISO-TP Payload: {iso_payload_hex}")
                    return iso_payload_hex

                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    return None
            #EDITED
            elif ServiceStr == "Send Single Frame + Read Single Frame":
                try:
                    TxID_int = int(TX_ID, 16)
                    RxID_int = int(RX_ID, 16)
                    Commands = Command1

                    # ============================================
                    # Parse command input
                    # ============================================
                    uds_data = [int(x, 16) for x in Commands.strip().split()]

                    if len(uds_data) > 8:
                        self.log.Info("Data too large for single CAN frame (max 8 bytes).")
                        return "Error: Data too large for single CAN frame."

                    # Pad to 8 bytes
                    while len(uds_data) < 8:
                        uds_data.append(0x00)

                    # ============================================
                    # SEND CAN FRAME
                    # ============================================
                    self.log.Info(f"Sending to TX ID: {TX_ID}")
                    msg = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=uds_data)
                    self.bus.send(msg)
                    tx_data_str = ' '.join(f"{x:02X}" for x in uds_data)
                    self.log.Info(f"Sent: {tx_data_str}")

                    # ============================================
                    # SAVE TX LOG
                    # ============================================

                    self.Write_CAN_Log(
                        f"TX | ID:{TX_ID} | DATA:{tx_data_str}"
                    )

                    # ============================================
                    # RECEIVE RESPONSE
                    # ============================================
                    start_time = time.time()
                    response_data = None

                    while True:
                        elapsed = time.time() - start_time
                        if timeout > 0 and elapsed > timeout:
                            self.log.Info("Timeout: No response received.")
                            # ============================================
                            # SAVE TIMEOUT LOG
                            # ============================================

                            self.Write_CAN_Log(
                                "TIMEOUT | No response received"
                            )
                            return "Timeout: No response received"

                        response_msg = self.bus.recv(0)  # Non-blocking
                        if response_msg and response_msg.arbitration_id == RxID_int:
                            raw_data = list(response_msg.data)
                            rx_data_str = ' '.join(f"{x:02X}" for x in raw_data)
                            self.log.Info(f"Received from {RX_ID}: {rx_data_str}")
                            # ============================================
                            # SAVE RX LOG
                            # ============================================

                            self.Write_CAN_Log(
                                f"RX | ID:{RX_ID} | DATA:{rx_data_str}"
                            )

                            response_data = rx_data_str
                            break

                    return response_data

                except ValueError as ve:
                    self.log.Info(f"Invalid input: {ve}")
                    self.Write_CAN_Log(
                        f"ERROR | {str(ve)}"
                    )
                    return f"Error: {ve}"
                except Exception as e:
                    self.log.Info(f"Unexpected error: {e}")
                    self.Write_CAN_Log(
                        f"ERROR | {str(e)}"
                    )
                    return f"Error: {e}"
            elif ServiceStr == "Send Single Frame + Read Multi Frame":
                try:
                    TxID_int = int(TX_ID, 16)
                    RxID_int = int(RX_ID, 16)
                    Commands = Command1
                    # ============================================
                    # Parse command input
                    # ============================================
                    uds_data = [int(x, 16) for x in Commands.strip().split()]

                    if len(uds_data) > 8:
                        self.log.Info("Data length exceeds CAN single frame size (8 bytes).")
                        return "Error: Data length exceeds CAN single frame size (8 bytes)."

                    # Pad with 0x00 if less than 8 bytes
                    while len(uds_data) < 8:
                        uds_data.append(0x00)

                    # ============================================
                    # SEND CAN FRAME
                    # ============================================
                    self.log.Info(f"TX ID: {TX_ID}")
                    # === Send Command ===
                    try:
                        msg = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=uds_data)
                        self.bus.send(msg)
                        tx_data_str = ' '.join(f"{x:02X}" for x in uds_data)
                        self.log.Info(f"Sent: {tx_data_str}")
                        # ============================================
                        # SAVE TX LOG
                        # ============================================

                        self.Write_CAN_Log(
                            f"TX | ID:{TX_ID} | DATA:{tx_data_str}"
                        )

                    except Exception as e:
                        self.log.Info(f"Error sending CAN message: {str(e)}")
                        self.Write_CAN_Log(
                            f"Error sending CAN message: | {str(e)}"
                        )
                        return f"Error sending CAN message: {str(e)}"
                    # ============================================
                    # RECEIVE RESPONSE
                    # ============================================

                    start_time = time.time()
                    response_frames = []
                    total_payload = []
                    expected_len = None

                    while True:
                        if timeout > 0 and (time.time() - start_time) > timeout:
                            self.log.Info("Timeout waiting for response")
                            self.Write_CAN_Log(
                                "TIMEOUT | No response received"
                            )
                            return "Timeout: No response received"

                        response_msg = self.bus.recv(0)
                        if response_msg and response_msg.arbitration_id == RxID_int:

                            frame = list(response_msg.data)
                            pci_type = frame[0] >> 4
                            raw_hex = ' '.join(f"{x:02X}" for x in frame)
                            self.log.Info(
                                f"Raw Response: ID={hex(response_msg.arbitration_id)}, Data={response_msg.data.hex()}")
                            self.log.Info(f"Matched ID Data: {frame}")
                            # ============================================
                            # SAVE RAW RX FRAME LOG
                            # ============================================

                            self.Write_CAN_Log(
                                f"RX | ID:{RX_ID}  | DATA:{raw_hex}"
                            )

                            # ============================================
                            # IGNORE SINGLE FRAME
                            # ============================================
                            if pci_type == 0x0:
                                self.log.Info("Skipping unrelated Single Frame response.")
                                continue
                            # ============================================
                            # FIRST FRAME
                            # ============================================
                            if pci_type == 0x1:  # First Frame
                                expected_len = ((frame[0] & 0x0F) << 8) + frame[1]
                                total_payload.extend(frame[2:])
                                response_frames.append(frame)
                                # ============================================
                                # SEND FLOW CONTROL
                                # ============================================
                                flow_control_frame = [0x30, 0x00, 0x14] + [0x00] * 5
                                fc_msg = can.Message(arbitration_id=TxID_int, is_extended_id=False,
                                                     data=flow_control_frame)
                                self.bus.send(fc_msg)
                                fc_hex = ' '.join(
                                    f"{x:02X}" for x in flow_control_frame
                                )

                                self.log.Info(
                                    f"Sent Flow Control Frame: "
                                    f"{[hex(x) for x in flow_control_frame]}"
                                )
                                # ============================================
                                # SAVE FLOW CONTROL LOG
                                # ============================================

                                self.Write_CAN_Log(
                                    f"TX | ID:{TX_ID} | DATA:{fc_hex}"
                                )

                                continue
                            # ============================================
                            # CONSECUTIVE FRAME
                            # ============================================

                            elif pci_type == 0x2:  # Consecutive Frame
                                total_payload.extend(frame[1:])
                                response_frames.append(frame)

                            # ============================================
                            # COMPLETE PAYLOAD RECEIVED
                            # ============================================

                            if expected_len > 0 and len(total_payload) >= expected_len:
                                break
                    # ============================================
                    # NO RESPONSE
                    # ============================================
                    if not response_frames:
                        self.log.Info("No matching response received.")
                        self.Write_CAN_Log(
                            "ERROR | No matching response received"
                        )
                        return None
                    # ============================================
                    # FINAL ISO-TP PAYLOAD
                    # ============================================
                    self.log.Info(
                        f"Full ISO-TP Payload: "
                        f"{[hex(x) for x in total_payload]}"
                    )

                    iso_payload_hex = ''.join(
                        f'{x:02X}' for x in total_payload
                    )

                    self.log.Info(
                        f"Full ISO-TP Payload: {iso_payload_hex}"
                    )
                    # ============================================
                    # SAVE FINAL PAYLOAD LOG
                    # ============================================

                    self.Write_CAN_Log(
                        f"ISO-TP PAYLOAD | DATA:{iso_payload_hex}"
                    )
                    return iso_payload_hex

                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    self.Write_CAN_Log(
                        f"ERROR | {str(e)}"
                    )
                    return f"Unexpected error: {str(e)}"
            elif ServiceStr == "Send Multi Frame + Read Single Frame":
                try:

                    TxID_int = int(TX_ID, 16)
                    RxID_int = int(RX_ID, 16)
                    timeout = float(Timeout)
                    Commands = Command1
                    Commands = [int(x, 16) for x in Commands.split()]

                    self.log.Info(f"Commands: {Commands}")
                    self.log.Info(f"TX_ID: {TX_ID}")

                    total_len = len(Commands)
                    if total_len <= 7:
                        self.log.Info("Error: Data too short for multi-frame transmission.")
                        self.Write_CAN_Log(
                            "ERROR | Data too short for multi-frame transmission"
                        )
                        return None

                    # ==================================================
                    # STEP 1 : SEND FIRST FRAME
                    # ==================================================

                    first_frame = [(0x10 | ((total_len >> 8) & 0x0F)), total_len & 0xFF] + Commands[:6]
                    msg1 = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=first_frame)
                    self.bus.send(msg1)
                    ff_hex = ' '.join(f"{x:02X}" for x in first_frame)
                    self.log.Info(f"Sent First Frame: {[hex(x) for x in first_frame]}")
                    # ==================================================
                    # SAVE FIRST FRAME LOG
                    # ==================================================

                    self.Write_CAN_Log(
                        f"TX | ID:{TX_ID} | FF | DATA:{ff_hex}"
                    )
                    time.sleep(0.011)
                    # ==================================================
                    # STEP 2 : WAIT FOR FLOW CONTROL FRAME
                    # ==================================================

                    start_time = time.time()
                    while True:
                        if (time.time() - start_time) > timeout:
                            self.log.Info("Timeout waiting for Flow Control Frame")
                            self.Write_CAN_Log(
                                "TIMEOUT | Waiting for Flow Control Frame"
                            )
                            return None

                        fc_msg = self.bus.recv(0)
                        if fc_msg and fc_msg.arbitration_id == RxID_int:
                            fc_data = list(fc_msg.data)
                            # ==================================================
                            # SAVE RX FLOW CONTROL FRAME
                            # ==================================================

                            fc_hex = ' '.join(f"{x:02X}" for x in fc_data)

                            self.Write_CAN_Log(
                                f"RX | ID:{RX_ID} | FC | DATA:{fc_hex}"
                            )

                            if fc_data[0] >> 4 == 0x3:
                                self.log.Info(
                                    f"Raw Response: ID={hex(fc_msg.arbitration_id)}, Data={fc_msg.data.hex()}")
                                block_size = fc_data[1]
                                st_min = fc_data[2] / 1000.0
                                self.log.Info(f"Received Flow Control: BS={block_size}, STmin={st_min}")
                                break

                    # ==================================================
                    # STEP 3 : SEND CONSECUTIVE FRAMES
                    # ==================================================

                    sn = 1
                    remaining_data = Commands[6:]
                    while remaining_data:
                        frame_data = [0x20 | (sn & 0x0F)] + remaining_data[:7]
                        remaining_data = remaining_data[7:]
                        if len(frame_data) < 8:
                            frame_data += [0x00] * (8 - len(frame_data))
                        msg = can.Message(arbitration_id=TxID_int, is_extended_id=False, data=frame_data)
                        self.bus.send(msg)
                        cf_hex = ' '.join(
                            f"{x:02X}" for x in frame_data
                        )
                        self.log.Info(f"Sent CF SN={sn}: {[hex(x) for x in frame_data]}")
                        # ==================================================
                        # SAVE CONSECUTIVE FRAME LOG
                        # ==================================================

                        self.Write_CAN_Log(
                            f"TX | ID:{TX_ID} | CF SN:{sn} | DATA:{cf_hex}"
                        )
                        sn = (sn + 1) % 16
                        time.sleep(st_min if st_min > 0 else 0.01)

                    # ============================================
                    # RECEIVE RESPONSE
                    # ============================================

                    start_time = time.time()

                    response_frames = []
                    total_payload = []
                    expected_len = None
                    frame_count = 0

                    while True:

                        if timeout > 0 and (time.time() - start_time) > timeout:
                            self.log.Info(
                                "Timeout waiting for response frames."
                            )

                            self.Write_CAN_Log(
                                "TIMEOUT | No response received"
                            )

                            return "Timeout: No response received"

                        response_msg = self.bus.recv(0)

                        if response_msg and response_msg.arbitration_id == RxID_int:

                            frame = list(response_msg.data)

                            pci_type = frame[0] >> 4

                            raw_hex = ' '.join(
                                f"{x:02X}" for x in frame
                            )

                            self.log.Info(
                                f"Raw Response: "
                                f"ID={hex(response_msg.arbitration_id)}, "
                                f"Data={response_msg.data.hex()}"
                            )

                            self.log.Info(
                                f"Matched ID Data: {frame}"
                            )

                            # ============================================
                            # SAVE RAW RX FRAME LOG
                            # ============================================

                            self.Write_CAN_Log(
                                f"RX | ID:{RX_ID} | DATA:{raw_hex}"
                            )

                            # ============================================
                            # SINGLE FRAME
                            # ============================================

                            if pci_type == 0x0:

                                payload_len = frame[0] & 0x0F

                                payload = frame[1:1 + payload_len]

                                payload_hex = ' '.join(
                                    f'{x:02X}' for x in payload
                                )

                                self.log.Info(
                                    f"Single Frame Payload: "
                                    f"{[hex(x) for x in payload]}"
                                )

                                # ============================================
                                # SAVE SINGLE FRAME PAYLOAD
                                # ============================================

                                self.Write_CAN_Log(
                                    f"SINGLE FRAME PAYLOAD | DATA:{payload_hex}"
                                )

                                return payload_hex

                            # ============================================
                            # FIRST FRAME
                            # ============================================

                            elif pci_type == 0x1:

                                expected_len = (
                                        ((frame[0] & 0x0F) << 8)
                                        + frame[1]
                                )

                                total_payload.extend(frame[2:])

                                response_frames.append(frame)

                                self.log.Info(
                                    f"First Frame Detected | "
                                    f"Expected Length: {expected_len}"
                                )

                                # ============================================
                                # SEND FLOW CONTROL FRAME
                                # ============================================

                                flow_control_frame = [
                                                         0x30,
                                                         0x00,
                                                         0x14
                                                     ] + [0x00] * 5

                                fc_msg = can.Message(
                                    arbitration_id=TxID_int,
                                    is_extended_id=False,
                                    data=flow_control_frame
                                )

                                self.bus.send(fc_msg)

                                fc_hex = ' '.join(
                                    f"{x:02X}" for x in flow_control_frame
                                )

                                self.log.Info(
                                    f"Sent Flow Control Frame: "
                                    f"{fc_hex}"
                                )

                                # ============================================
                                # SAVE FLOW CONTROL LOG
                                # ============================================

                                self.Write_CAN_Log(
                                    f"TX | ID:{TX_ID} | FLOW CONTROL | DATA:{fc_hex}"
                                )

                            # ============================================
                            # CONSECUTIVE FRAME
                            # ============================================

                            elif pci_type == 0x2:

                                total_payload.extend(frame[1:])

                                response_frames.append(frame)

                                self.log.Info(
                                    f"Consecutive Frame Received | "
                                    f"SN={frame[0] & 0x0F}"
                                )

                            frame_count += 1

                            # ============================================
                            # COMPLETE PAYLOAD RECEIVED
                            # ============================================

                            if (
                                    expected_len is not None and
                                    len(total_payload) >= expected_len
                            ):
                                self.log.Info(
                                    "Expected length received, stopping."
                                )

                                break

                    # ============================================
                    # NO RESPONSE
                    # ============================================

                    if not response_frames and not total_payload:
                        self.log.Info(
                            "No matching response received."
                        )

                        self.Write_CAN_Log(
                            "ERROR | No matching response received"
                        )

                        return None

                    # ============================================
                    # REMOVE PADDING
                    # ============================================

                    while total_payload and total_payload[-1] in (0x00, 0xCC):
                        total_payload.pop()

                    # ============================================
                    # FORMAT FINAL PAYLOAD
                    # ============================================

                    iso_payload_hex = ' '.join(
                        f'{x:02X}' for x in total_payload
                    )

                    self.log.Info(
                        f"Full ISO-TP Payload: "
                        f"{iso_payload_hex}"
                    )

                    # ============================================
                    # SAVE FINAL PAYLOAD LOG
                    # ============================================

                    self.Write_CAN_Log(
                        f"ISO-TP PAYLOAD | DATA:{iso_payload_hex}"
                    )

                    return iso_payload_hex

                except Exception as e:

                    self.log.Info(
                        f"Unexpected error: {str(e)}"
                    )

                    self.Write_CAN_Log(
                        f"ERROR | {str(e)}"
                    )

                    return f"Unexpected error: {str(e)}"
            elif ServiceStr == "Send Multi Frame + Read Multi Frame":

                    try:

                        TxID_int = int(TX_ID, 16)
                        RxID_int = int(RX_ID, 16)
                        timeout = float(Timeout)

                        Commands = Command1
                        Commands = [int(x, 16) for x in Commands.split()]

                        self.log.Info(f"Commands: {Commands}")
                        self.log.Info(f"TX_ID: {TX_ID}")

                        total_len = len(Commands)

                        if total_len <= 7:
                            self.log.Info(
                                "Error: Data too short for multi-frame transmission."
                            )

                            self.Write_CAN_Log(
                                "ERROR | Data too short for multi-frame transmission"
                            )

                            return None

                        # ==================================================
                        # STEP 1 : SEND FIRST FRAME
                        # ==================================================

                        first_frame = [
                                          (0x10 | ((total_len >> 8) & 0x0F)),
                                          total_len & 0xFF
                                      ] + Commands[:6]

                        msg1 = can.Message(
                            arbitration_id=TxID_int,
                            is_extended_id=False,
                            data=first_frame
                        )

                        self.bus.send(msg1)

                        ff_hex = ' '.join(
                            f"{x:02X}" for x in first_frame
                        )

                        self.log.Info(
                            f"Sent First Frame: "
                            f"{[hex(x) for x in first_frame]}"
                        )

                        self.Write_CAN_Log(
                            f"TX | ID:{TX_ID} | FF | DATA:{ff_hex}"
                        )

                        time.sleep(0.011)

                        # ==================================================
                        # STEP 2 : WAIT FOR FLOW CONTROL
                        # ==================================================

                        start_time = time.time()

                        while True:

                            if (time.time() - start_time) > timeout:
                                self.log.Info(
                                    "Timeout waiting for Flow Control Frame"
                                )

                                self.Write_CAN_Log(
                                    "TIMEOUT | Waiting for Flow Control Frame"
                                )

                                return None

                            fc_msg = self.bus.recv(0)

                            if fc_msg and fc_msg.arbitration_id == RxID_int:

                                fc_data = list(fc_msg.data)

                                fc_hex = ' '.join(
                                    f"{x:02X}" for x in fc_data
                                )

                                self.Write_CAN_Log(
                                    f"RX | ID:{RX_ID} | FC | DATA:{fc_hex}"
                                )

                                if fc_data[0] >> 4 == 0x3:
                                    self.log.Info(
                                        f"Raw Response: "
                                        f"ID={hex(fc_msg.arbitration_id)}, "
                                        f"Data={fc_msg.data.hex()}"
                                    )

                                    block_size = fc_data[1]

                                    st_min = fc_data[2] / 1000.0

                                    self.log.Info(
                                        f"Received Flow Control: "
                                        f"BS={block_size}, "
                                        f"STmin={st_min}"
                                    )

                                    break

                        # ==================================================
                        # STEP 3 : SEND CONSECUTIVE FRAMES
                        # ==================================================

                        sn = 1

                        remaining_data = Commands[6:]

                        while remaining_data:

                            frame_data = [
                                             0x20 | (sn & 0x0F)
                                         ] + remaining_data[:7]

                            remaining_data = remaining_data[7:]

                            if len(frame_data) < 8:
                                frame_data += [0x00] * (8 - len(frame_data))

                            msg = can.Message(
                                arbitration_id=TxID_int,
                                is_extended_id=False,
                                data=frame_data
                            )

                            self.bus.send(msg)

                            cf_hex = ' '.join(
                                f"{x:02X}" for x in frame_data
                            )

                            self.log.Info(
                                f"Sent CF SN={sn}: "
                                f"{[hex(x) for x in frame_data]}"
                            )

                            self.Write_CAN_Log(
                                f"TX | ID:{TX_ID} | CF SN:{sn} | DATA:{cf_hex}"
                            )

                            sn = (sn + 1) % 16

                            time.sleep(
                                st_min if st_min > 0 else 0.01
                            )

                        # ==================================================
                        # RECEIVE RESPONSE
                        # ==================================================

                        start_time = time.time()

                        response_frames = []
                        total_payload = []
                        expected_len = None

                        while True:

                            if timeout > 0 and (
                                    time.time() - start_time
                            ) > timeout:
                                self.log.Info(
                                    "Timeout waiting for response"
                                )

                                self.Write_CAN_Log(
                                    "TIMEOUT | No response received"
                                )

                                return None

                            response_msg = self.bus.recv(0)

                            if (
                                    response_msg and
                                    response_msg.arbitration_id == RxID_int
                            ):

                                frame = list(response_msg.data)

                                pci_type = frame[0] >> 4

                                raw_hex = ' '.join(
                                    f"{x:02X}" for x in frame
                                )

                                self.log.Info(
                                    f"Raw Response: "
                                    f"ID={hex(response_msg.arbitration_id)}, "
                                    f"Data={response_msg.data.hex()}"
                                )

                                self.log.Info(
                                    f"Matched ID Data: {frame}"
                                )

                                # ==========================================
                                # SAVE RX FRAME LOG
                                # ==========================================

                                self.Write_CAN_Log(
                                    f"RX | ID:{RX_ID}  | DATA:{raw_hex}"
                                )

                                # ==========================================
                                # IGNORE SINGLE FRAME
                                # ==========================================

                                if pci_type == 0x0:
                                    self.log.Info(
                                        "Skipping unrelated Single Frame response."
                                    )

                                    continue

                                # ==========================================
                                # FIRST FRAME
                                # ==========================================

                                if pci_type == 0x1:

                                    expected_len = (
                                            ((frame[0] & 0x0F) << 8)
                                            + frame[1]
                                    )

                                    total_payload.extend(frame[2:])

                                    response_frames.append(frame)

                                    flow_control_frame = [
                                                             0x30,
                                                             0x00,
                                                             0x14
                                                         ] + [0x00] * 5

                                    fc_msg = can.Message(
                                        arbitration_id=TxID_int,
                                        is_extended_id=False,
                                        data=flow_control_frame
                                    )

                                    self.bus.send(fc_msg)

                                    fc_hex = ' '.join(
                                        f"{x:02X}"
                                        for x in flow_control_frame
                                    )

                                    self.log.Info(
                                        f"Sent Flow Control Frame: "
                                        f"{[hex(x) for x in flow_control_frame]}"
                                    )

                                    self.Write_CAN_Log(
                                        f"TX | ID:{TX_ID} | FLOW CONTROL | DATA:{fc_hex}"
                                    )

                                    continue

                                # ==========================================
                                # CONSECUTIVE FRAME
                                # ==========================================

                                elif pci_type == 0x2:

                                    total_payload.extend(frame[1:])

                                    response_frames.append(frame)

                                # ==========================================
                                # COMPLETE PAYLOAD RECEIVED
                                # ==========================================

                                if (
                                        expected_len > 0 and
                                        len(total_payload) >= expected_len
                                ):
                                    break

                        # ==================================================
                        # NO RESPONSE
                        # ==================================================

                        if not response_frames:
                            self.log.Info(
                                "No matching response received."
                            )

                            self.Write_CAN_Log(
                                "ERROR | No matching response received"
                            )

                            return None

                        # ==================================================
                        # REMOVE PADDING
                        # ==================================================

                        while (
                                total_payload and
                                total_payload[-1] in (0x00, 0xCC)
                        ):
                            total_payload.pop()

                        self.log.Info(
                            f"Full ISO-TP Payload: "
                            f"{[hex(x) for x in total_payload]}"
                        )

                        iso_payload_hex = ' '.join(
                            f'{x:02X}'
                            for x in total_payload
                        )

                        self.log.Info(
                            f"Full ISO-TP Payload: "
                            f"{iso_payload_hex}"
                        )

                        # ==================================================
                        # SAVE FINAL PAYLOAD
                        # ==================================================

                        self.Write_CAN_Log(
                            f"ISO-TP PAYLOAD | DATA:{iso_payload_hex}"
                        )

                        return iso_payload_hex

                    except Exception as e:

                        self.log.Info(
                            f"Unexpected error: {str(e)}"
                        )

                        self.Write_CAN_Log(
                            f"ERROR | {str(e)}"
                        )

                        return None
            elif ServiceStr == "Send Multi frame From Seed + Read Multi Frame":
                import time
                import can

                try:

                    RxID_int = int(RX_ID, 16)
                    TxID_int = int(TX_ID, 16)

                    # ==================================================
                    # PREPARE COMMAND
                    # ==================================================

                    Commands = Command1
                    Commands = [int(x, 16) for x in Commands.split()]

                    self.log.Info(
                        f"TX_ID: {hex(TxID_int)}, "
                        f"RX_ID: {hex(RxID_int)}"
                    )

                    SeedValue_bytes = [
                        int(x, 16)
                        for x in SeedValue.split()
                    ]

                    self.log.Info(f"SeedValue:{SeedValue}")

                    Commands += SeedValue_bytes

                    self.log.Info(f"Commands:{Commands}")

                    total_len = len(Commands)

                    self.log.Info(f"total_len:{total_len}")

                    # ==================================================
                    # STEP 1 : SEND FIRST FRAME
                    # ==================================================

                    first_frame = [
                                      (0x10 | ((total_len >> 8) & 0x0F)),
                                      total_len & 0xFF
                                  ] + Commands[:6]

                    msg1 = can.Message(
                        arbitration_id=TxID_int,
                        is_extended_id=False,
                        data=first_frame
                    )

                    self.bus.send(msg1)

                    ff_hex = ' '.join(
                        f"{x:02X}"
                        for x in first_frame
                    )

                    self.log.Info(
                        f"Sent First Frame: "
                        f"{[hex(x) for x in first_frame]}"
                    )

                    self.Write_CAN_Log(
                        f"TX | ID:{TX_ID} | FF | DATA:{ff_hex}"
                    )

                    time.sleep(0.011)

                    # ==================================================
                    # STEP 2 : WAIT FOR FLOW CONTROL
                    # ==================================================

                    start_time = time.time()

                    while True:

                        fc_msg = self.bus.recv(0)

                        if not fc_msg:

                            if (time.time() - start_time) > timeout:
                                self.log.Info(
                                    "Timeout waiting for Flow Control Frame"
                                )

                                self.Write_CAN_Log(
                                    "TIMEOUT | Waiting for Flow Control Frame"
                                )

                                return None

                            continue

                        if fc_msg.arbitration_id == RxID_int:

                            fc_data = list(fc_msg.data)

                            fc_hex = ' '.join(
                                f"{x:02X}"
                                for x in fc_data
                            )

                            self.Write_CAN_Log(
                                f"RX | ID:{RX_ID} | FC | DATA:{fc_hex}"
                            )

                            if fc_data[0] >> 4 == 0x3:
                                self.log.Info(
                                    f"Raw Response: "
                                    f"ID={hex(fc_msg.arbitration_id)}, "
                                    f"Data={fc_msg.data.hex()}"
                                )

                                block_size = fc_data[1]

                                st_min = fc_data[2] / 1000.0

                                self.log.Info(
                                    f"Received Flow Control: "
                                    f"BS={block_size}, "
                                    f"STmin={st_min}"
                                )

                                break

                    # ==================================================
                    # STEP 3 : SEND CONSECUTIVE FRAMES
                    # ==================================================

                    sn = 1

                    remaining_data = Commands[6:]

                    while remaining_data:

                        frame_data = [
                                         0x20 | (sn & 0x0F)
                                     ] + remaining_data[:7]

                        remaining_data = remaining_data[7:]

                        if len(frame_data) < 8:
                            frame_data += [0x00] * (
                                    8 - len(frame_data)
                            )

                        msg = can.Message(
                            arbitration_id=TxID_int,
                            is_extended_id=False,
                            data=frame_data
                        )

                        self.bus.send(msg)

                        cf_hex = ' '.join(
                            f"{x:02X}"
                            for x in frame_data
                        )

                        self.log.Info(
                            f"Sent CF SN={sn}: "
                            f"{[hex(x) for x in frame_data]}"
                        )

                        self.Write_CAN_Log(
                            f"TX | ID:{TX_ID} | CF SN:{sn} | DATA:{cf_hex}"
                        )

                        sn = (sn + 1) % 16

                        time.sleep(
                            st_min if st_min > 0 else 0.01
                        )

                    # ==================================================
                    # RECEIVE RESPONSE
                    # ==================================================

                    start_time = time.time()

                    response_frames = []
                    total_payload = []
                    expected_len = None

                    while True:

                        if timeout > 0 and (
                                time.time() - start_time
                        ) > timeout:
                            self.log.Info(
                                "Timeout waiting for response"
                            )

                            self.Write_CAN_Log(
                                "TIMEOUT | No response received"
                            )

                            return None

                        response_msg = self.bus.recv(0)

                        if not response_msg:
                            continue

                        if response_msg.arbitration_id != RxID_int:
                            continue

                        frame = list(response_msg.data)

                        pci_type = frame[0] >> 4

                        raw_hex = ' '.join(
                            f"{x:02X}"
                            for x in frame
                        )

                        self.log.Info(
                            f"Raw Response: "
                            f"ID={hex(response_msg.arbitration_id)}, "
                            f"Data={response_msg.data.hex()}"
                        )

                        # ==================================================
                        # SAVE RX FRAME LOG
                        # ==================================================

                        self.Write_CAN_Log(
                            f"RX | ID:{RX_ID} | DATA:{raw_hex}"
                        )

                        # ==================================================
                        # SINGLE FRAME
                        # ==================================================

                        if pci_type == 0x0:

                            payload_len = frame[0] & 0x0F

                            payload = frame[1:1 + payload_len]

                            # Negative Response
                            if payload and payload[0] == 0x7F:
                                self.log.Info(
                                    "Negative Response (SF), ignoring and waiting..."
                                )

                                self.Write_CAN_Log(
                                    f"NEGATIVE RESPONSE | DATA:{' '.join(f'{x:02X}' for x in payload)}"
                                )

                                continue

                            iso_payload_hex = ' '.join(
                                f'{x:02X}'
                                for x in payload
                            )

                            self.log.Info(
                                f"Full ISO-TP Payload (SF): "
                                f"{iso_payload_hex}"
                            )

                            self.Write_CAN_Log(
                                f"ISO-TP PAYLOAD | DATA:{iso_payload_hex}"
                            )

                            return iso_payload_hex

                        # ==================================================
                        # FIRST FRAME
                        # ==================================================

                        elif pci_type == 0x1:

                            expected_len = (
                                    ((frame[0] & 0x0F) << 8)
                                    + frame[1]
                            )

                            total_payload = frame[2:]

                            response_frames = [frame]

                            # Flow Control
                            flow_control_frame = [
                                                     0x30,
                                                     0x00,
                                                     0x14
                                                 ] + [0x00] * 5

                            fc_msg = can.Message(
                                arbitration_id=TxID_int,
                                is_extended_id=False,
                                data=flow_control_frame
                            )

                            self.bus.send(fc_msg)

                            fc_hex = ' '.join(
                                f"{x:02X}"
                                for x in flow_control_frame
                            )

                            self.log.Info(
                                f"Sent Flow Control Frame: "
                                f"{[hex(x) for x in flow_control_frame]}"
                            )

                            self.Write_CAN_Log(
                                f"TX | ID:{TX_ID} | FLOW CONTROL | DATA:{fc_hex}"
                            )

                            continue

                        # ==================================================
                        # CONSECUTIVE FRAME
                        # ==================================================

                        elif pci_type == 0x2:

                            total_payload.extend(frame[1:])

                            response_frames.append(frame)

                            if (
                                    expected_len and
                                    len(total_payload) >= expected_len
                            ):

                                # Negative Response
                                if (
                                        total_payload and
                                        total_payload[0] == 0x7F
                                ):
                                    self.log.Info(
                                        "Negative Response (MF), ignoring and waiting..."
                                    )

                                    self.Write_CAN_Log(
                                        f"NEGATIVE RESPONSE | DATA:{' '.join(f'{x:02X}' for x in total_payload)}"
                                    )

                                    total_payload = []
                                    expected_len = None
                                    response_frames = []

                                    continue

                                iso_payload_hex = ' '.join(
                                    f'{x:02X}'
                                    for x in total_payload[:expected_len]
                                )

                                self.log.Info(
                                    f"Full ISO-TP Payload (MF): "
                                    f"{iso_payload_hex}"
                                )

                                self.Write_CAN_Log(
                                    f"ISO-TP PAYLOAD | DATA:{iso_payload_hex}"
                                )

                                return iso_payload_hex

                except Exception as e:

                    self.log.Info(
                        f"Unexpected error: {str(e)}"
                    )

                    self.Write_CAN_Log(
                        f"ERROR | {str(e)}"
                    )

                    return None
            elif ServiceStr == "Testing":
                try:
                    ArbitID = "794"
                    self.log.Info(f"ArbitID: {ArbitID}")

                    # Frame 1: Request diagnostic data
                    Commands = f"04, 31, 01, F1, 06"
                    command_bytes1 = [int(x.strip(), 16) for x in Commands.split(',')]
                    self.log.Info(f"Frame 1: {[hex(x) for x in command_bytes1]}")

                    try:
                        msg1 = can.Message(
                            arbitration_id=int(ArbitID, 16),
                            is_extended_id=True,
                            data=command_bytes1
                        )

                        # --- Start periodic sending every 100ms ---
                        task = self.bus.send_periodic(msg1, 0.1)  # adjust period as needed
                        self.log.Info("Cyclic transmission started...")

                        start_time = time.time()
                        timeout = 5  # run for 5 seconds
                        received_responses = []

                        while (time.time() - start_time) < timeout:
                            # Keep listening while cyclic sender works in background
                            response_msg = self.bus.recv(0.05)  # non-blocking
                            if response_msg:
                                self.log.Info(
                                    f"Raw Response: ID={hex(response_msg.arbitration_id)}, "
                                    f"Data={response_msg.data.hex()}"
                                )

                                if response_msg.arbitration_id == 0x7A4:
                                    received_responses.append(response_msg.data)

                        # --- Stop sending after 5 sec ---
                        task.stop()
                        self.log.Info("Cyclic transmission stopped.")

                        if received_responses:
                            data_payload = bytearray()
                            for i, frame in enumerate(received_responses):
                                self.log.Info(f"Frame {i + 1} Data: {frame.hex().upper()}")

                                if i == 0:
                                    data_payload.extend(frame[5:])
                                else:
                                    data_payload.extend(frame[1:])

                            Cleaned = data_payload.hex().upper()
                            self.log.Info(f"Cleaned Payload Hex: {Cleaned}")
                            return Cleaned
                        else:
                            self.log.Info("No response frames received from ECU.")
                            return None

                    except Exception as e:
                        self.log.Info(f"Error sending CAN message: {str(e)}")
                        return None

                except Exception as e:
                    self.log.Info(f"Unexpected error: {str(e)}")
                    return None
        except NegativeResponseException as e:

                    self.log.Info(
                        f"Negative response received. Code: {e.code}"
                    )

                    self.Write_CAN_Log(
                        f"NEGATIVE RESPONSE | CODE:{e.code}"
                    )

                    return f"Negative Response: {e.code}"

        except Exception as e:

                    self.log.Info(
                        f"Error: {str(e)}"
                    )

                    self.log.Info("SendKey")

                    self.Write_CAN_Log(
                        f"ERROR | SendKey | {str(e)}"
                    )

                    return None

    # def CANopen1(self):
    #     super().Open()
    #     try:
    #         if not self.is_bus_open:
    #             self.bus = can.interface.Bus(
    #                 channel=self.Channel,
    #                 interface=self.canDevice,
    #                 bitrate=self.canBaudrate
    #             )
    #             self.is_bus_open = True
    #             self.log.Info(f"CAN Bus initialized: Channel={self.Channel}, Baudrate={self.canBaudrate}")
    #         else:
    #             self.log.Info("CAN Bus already open.")
    #         return True
    #     except Exception as e:
    #         self.log.Info(f"Failed to initialize CAN Bus: {e}")
    #         return False
    #
    # def CANclose1(self):
    #     if self.bus is not None:
    #         try:
    #             self.bus.shutdown()
    #             self.log.Info("CAN Bus closed.")
    #         except Exception as e:
    #             self.log.Info(f"Error closing CAN Bus: {e}")
    #         finally:
    #             self.bus = None
    #             self.is_bus_open = False
    #
    #     super().Close()
    def Open(self):
        super().Open()
        try:
            if not self.is_bus_open:
                self.bus = can.interface.Bus(channel=self.Channel, interface=self.canDevice, bitrate=self.canBaudrate)
                self.is_bus_open = True
                self.log.Info(f"CAN Bus initialized: Channel={self.Channel}, Baudrate={self.canBaudrate}")
                return True
            else:
                self.log.Info("CAN Bus already open.")
                return True
        except Exception as e:
            self.log.Info(f"Failed to initialize CAN Bus: {e}")
            return None

    # def Close(self):
    #     super().Close()
    #     if hasattr(self, "bus") and self.bus is not None:
    #         self.bus.shutdown()
    #         self.is_bus_open = False
    #         self.log.Info("CAN Bus closed.")
    def Close(self):

        super().Close()

        if hasattr(self, "bus") and self.bus is not None:

            self.bus.shutdown()

            self.is_bus_open = False

            self.log.Info("CAN Bus closed.")

        # ============================================
        # RESET LOG FILE FOR NEXT RUN
        # ============================================

        self.CAN_Log_File = None
