#PCAN SETINGS
from opentap import *
import OpenTap
from System import Int32
from System import Double, String, Int32

@attribute(OpenTap.Display("CAN Settings", "CAN Protocol Settings."))
class CANSettings(OpenTap.ComponentSettings):
    def __init__(self):
        super().__init__()
    NumberOfPoints = property(Int32, 600)\
        .add_attribute(OpenTap.Display("Number of points"))
