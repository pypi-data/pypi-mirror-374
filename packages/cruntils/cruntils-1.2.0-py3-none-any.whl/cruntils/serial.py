
import serial

class Vcp:
    """
    Class for connecting to VCP serial port.

    The COM port number will change depending on which USB the device is
    plugged into. As such, the port_name argument has no default value, you
    must find this yourself e.g. on Windows by using the device manager.
    """

    def __init__(
            self,
            port_name,
            baudrate = 9600,
            bytesize = 8,
            stopbits = 1,
            parity = serial.PARITY_NONE
        ):
        """ Constructor.
        """

        # Port parameters.
        self.PortName    = port_name
        self.BaudRate    = baudrate
        self.ByteSize    = bytesize
        self.StopBits    = stopbits
        self.Parity      = parity

        # Port connection.
        self.Port = None

        # Data.
        self.ReadData = ""

        # Hardware states.
        self.Volume1 = None
        self.Volume2 = None
        self.Volume3 = None
        self.Switch = [None, None, None, None]

    def __del__(self):
        """ Destructor.
        """
        self.Close()

    def Open(self):
        """ Open the port.
        """
        if self.Port == None:
            self.Port = serial.Serial(
                port = self.PortName,
                baudrate = self.BaudRate,
                bytesize = self.ByteSize,
                stopbits = self.StopBits,
                parity   = self.Parity
            )

    def Close(self):
        """ Close the port.
        """
        if self.Port != None:
            self.Port.close()

    def Read(self):
        """ Read from the port until we get a full transmission.
        """

        # If port isn't initialised, do nothing.
        if self.Port == None:
            print("Port not initialised, can't read")
            return

        # Reset the read data.
        self.ReadData = ""

        # Read data from port.
        while True:

            # Append data.
            self.ReadData += self.Port.read().decode("utf-8")

            # If last character is a ')', then we've reached the end of the
            # transmission.
            if len(self.ReadData) > 0:
                if self.ReadData[-1] == ")":
                    break

        # Update our internal state.
        self.ParseResponse(self.ReadData)

    def Write(self, data):
        """ Write to the port.
        """

        # If port isn't initialised, do nothing.
        if self.Port == None:
            print("Port not initialised, can't read")
            return

        # Convert string to binary and write to port.
        self.Port.write(data.encode("utf-8"))

    def ParseResponse(self, response_data):
        """ Parse data read from the port.
        """

        # Parse switch state.
        if response_data[1] == "S":
            self.Switch[0] = int(response_data[5])
            self.Switch[1] = int(response_data[7])
            self.Switch[2] = int(response_data[9])
            self.Switch[3] = int(response_data[11])

        # Parse volume states.
        if response_data[1] == "V":
            data_parts = response_data.split(",")
            self.Volume1 = int(data_parts[1])
            self.Volume2 = int(data_parts[2])
            self.Volume3 = int(data_parts[3].replace(")", ""))

    def PrintState(self):
        """ Print the current state of the object.
        """
        print(f"Volume 1: {self.Volume1}")
        print(f"Volume 2: {self.Volume2}")
        print(f"Volume 3: {self.Volume3}")
        print(f"Switch: {self.Switch}")

    def SetAutoUpdate(self, switch, volume):
        """ Enable auto-update mode.

        0: Disable auto-update.
        1: Enable auto-update.

        In auto-update mode the device will automatically send updates
        whenever the state changes.

        This mode can be enabled/disabled for the switch, the volume knobs, or
        both.
        """

        # Do nothing if we don't have a port.
        if self.Port == None:
            return

        # Switch.
        switch_val = 0
        if switch:
            switch_val = 1

        # Volume knobs.
        volume_val = 0
        if volume:
            volume_val = 1

        # Send appropriate auto-update request depending arguments.
        request_str = f"(U{switch_val},{volume_val})"
        self.Write(request_str)
