
from enum import Enum
import struct

class uint8:
    def __init__(self, value):
        self.Bits = 8
        self.Signed = False
        self.Value = value

class uint32:
    def __init__(self, value):
        self.Bits = 32
        self.Signed = False
        self.Value = value

class CRadioSelectionType(Enum):

    # Data type used to hold value.
    type = uint8

    # Enum values.
    eInvalid     = -1
    eVoiceImint  = 0
    eBowman      = 1
    eGroundRadio = 2
    eAirRadio    = 3
    eICLive      = 4
    eGuardRadio1 = 5
    eGuardRadio2 = 6
    eGuardRadio3 = 7

class CVcpLampColoursType(Enum):

    # Data type used to hold value.
    type = uint8

    # Enum values.
    eInvalid = -1
    eOff     = 0
    eGreen   = 1
    eRed     = 2

class CVcpRadioStatus:
    def __init__(self):
        self.Volume = uint32(0)
        self.ClearLampColour = CVcpLampColoursType.eInvalid
        self.SecureLampColour = CVcpLampColoursType.eInvalid
        self.IsActive = False
        self.IsSecure = False
        self.NoCrypto = False

class CVcpStatus:
    def __init__(self):
        self.SelectedRadio = CRadioSelectionType.eInvalid
        self.GroundRadio = CVcpRadioStatus()
        self.GuardVolume = uint8(0)
        self.AirRadio = CVcpRadioStatus()

    def Serialise(self):

        return b"xFF"
    
    def GetLength(self):
        return 0

class Message:
    def __init__(self):
        self.Id      = 0
        self.Payload = None

    def GetLength(self):
        if self.Payload != None:
            return self.Payload.GetLength()
        else:
            return 0

    def PutMessageHeader(self, data):

        # Message length.
        data += struct.pack(">I", self.GetLength())

        # Message ID.
        data += struct.pack(">I", self.Id)

        return data

    def PutMessageFooter(self, data):

        # Seperator.
        data += struct.pack(">I", 5921370)

        return data

    def Serialise(self):
        data = bytes()
        data += self.PutMessageHeader(data)
        data += self.Payload.Serialise()
        data += self.PutMessageFooter(data)
        return data

class MVcpRadioStatus(Message):
    def __init__(self):
        self.Id      = 973258752
        self.Payload = CVcpStatus()




