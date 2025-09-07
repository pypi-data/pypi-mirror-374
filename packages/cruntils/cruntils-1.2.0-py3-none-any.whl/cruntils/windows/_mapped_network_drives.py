# Core Python.
import winreg

class MappedNetworkDrives:
    """
    Class for working with Windows mapped network drives.
    """

    def __init__(self):
        """Constructor"""

        # Dictionary to hold mappings.
        self.letter_unc_map = {}

        # Scan the registry to build map.
        self.scan()

    def __str__(self):
        """String representation of class"""
        out_str = ""
        for letter in self.letter_unc_map:
            out_str += f"{letter}: {self.letter_unc_map[letter]}\n"
        return out_str

    def get_unc_by_letter(self, letter: str):
        """Get UNC drive by letter.

        Return the UNC path that is mapped to the provided string.

        If there isn't a mapping for the given letter, return None.
        """
        if letter in self.letter_unc_map:
            return self.letter_unc_map[letter]
        else:
            return None

    def scan(self):
        """Scan the registry for mapped drives"""

        # Get the registry key that holds all of the mapped network drives.
        hk_cu_net = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Network")

        # Query information about network key.
        hk_cu_net_info = winreg.QueryInfoKey(hk_cu_net)
        max_subkey_index = hk_cu_net_info[0]

        # Iterate through mapped subkeys in Network registry key.
        current_index = 0
        while current_index < max_subkey_index:

            # Get current mapped drive key.
            drive_letter = winreg.EnumKey(hk_cu_net, current_index)

            # Open registry key for mapped drive.
            mapped_drive = winreg.OpenKey(hk_cu_net, drive_letter)

            # Query info about this key.
            mapped_drive_info = winreg.QueryInfoKey(mapped_drive)

            # Iterate through values backwards as the "RemotePath" value tends
            # to appear towards the end of the list.
            unc_path: str = ""
            value_index = 0
            while value_index < mapped_drive_info[1]:
                current_value = winreg.EnumValue(mapped_drive, value_index)
                if current_value[0] == "RemotePath":
                    unc_path = current_value[1]
                    unc_path = unc_path.replace("\\\\", "\\")
                    self.letter_unc_map[drive_letter] = unc_path
                    break
                value_index += 1

            # Got to next drive.
            current_index += 1