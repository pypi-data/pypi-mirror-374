
# Core Python imports.
import ctypes
import datetime
import os
import platform
import socket

def GetPrimaryIp(target_address = "8.8.8.8", target_port = 80):
    """ Get the system default IP address.

    This is not as simple as I expected it to be...

    On Windows you can find this rather easily using the socket module:
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    However, on the Ubuntu box I has at the time, this returned 127.0.1.1.

    After a little Googling I stumbled upon this solution:
    https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

    My understanding of this answer is we create a socket and ask the
    operating system to connect it to some arbitrary internet location. The
    operating system will then use the system's default IP address to make the
    connection. Once the connection is finished, regardless of whether it has
    succeeded or failed, the OS will have chosen a sensible IP address which
    we can use.

    I have provided default address and port values, you may wish to override
    these if you're trying to select a specific IP address on a machine with
    multiple NICs.
    """

    # Create the socket and attempt to connect to the target.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((target_address, target_port))

    # Get the socket name. This takes the form (ip, port) so we just return
    # the first component, the IP address.
    ip = sock.getsockname()[0]

    # Close the socket and return the IP.
    sock.close()
    return ip

def GetUptime():
    """ Get machine uptime in seconds.
    """

    # Windows.
    if platform.system() == "Windows":

        # Get library with function we need.
        lib = ctypes.windll.kernel32

        # Call function that gives us uptime in milliseconds.
        ut_millis = lib.GetTickCount64()

        # Return as seconds.
        return ut_millis / 1000

    # Linux.
    elif platform.system() == "Linux":

        # Use uptime to get time this machine started.
        started_str = os.popen("uptime -s").read()[:-1]
        started_dt = datetime.datetime.strptime(started_str, "%Y-%m-%d %H:%M:%S")

        # Find difference between start time and time now.
        time_now = datetime.datetime.now()
        time_diff = time_now - started_dt

        # Return time difference in seconds.
        return time_diff.total_seconds()

    # Un-supported platforms.
    else:
        print("ERROR: GetUptime() unsupported platform")
        return 0
