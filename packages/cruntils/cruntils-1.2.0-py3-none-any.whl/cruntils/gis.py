
# Core Python imports.
from enum import Enum
import math
import os

# Local imports.
from . import utils

# There is no single "correct" equatorial radius for performing calculations
# with latitude and longitude values - the radius to use is dependent on the
# reference ellipsoid the values use.
#
# As such, these calculations all need improving. They should be built into
# the new location class.
wgs84_earth_equatorial_radius_m = 6378137

class ELatLon(Enum):
    """ Specify if a coordinate is a latitude or longitude.
    """
    Lat = 1
    Lon = 2

class ECoordFormat(Enum):
    """ Various coordinate formats.
    """
    LatLonRad = 1
    LatLonDd  = 2
    LatLonDms = 3

class EReferenceEllipsoid(Enum):
    """ Various reference ellipsoids.
    """
    Airy1830 = 1
    Wgs84    = 2

class CLocation():
    """ A class for representing a single geographic location.
    """

    def __init__(self, lat=None, lon=None, lat_signed=True, lon_signed=True):
        self.Latitude = lat
        self.Longitude = lon
        self.LatSigned = lat_signed
        self.LonSigned = lon_signed
        self.ReferenceEllipsoid = EReferenceEllipsoid.Wgs84

        self.Name = ""

    def SetName(self, name):
        self.Name = name

    def SetLatLon(self, lat, lon, lat_signed=True, lon_signed=True):
        self.Latitude = lat
        self.Longitude = lon
        self.LatSigned = lat_signed
        self.LonSigned = lon_signed

    def GetLat(self, signed=True):
        """ As per ISO 6709, latitudes run from 90 to -90.

        Give the user the option to express this as an un-signed number
        running from 180 to 0.

        When converting latitudes between signed and un-signed the position of
        0 moves. For 90 to -90, 0 is on the equator. For 180 to 0, 0 is on the
        south pole. As such, to convert between the to we just shift the value
        by 90 degrees.
        """
        if signed:
            if self.LatSigned:
                return self.Latitude
            else:
                return self.Latitude -90
        else:
            if self.LatSigned:
                return self.Latitude + 90
            else:
                return self.Latitude

    def GetLon(self, signed=True):
        """ As per ISO 6709, longitudes run from -180 to 180.

        Give the user the option to express this as an un-signed number
        running from 0 to 360.

        When converting longitudes between signed and un-signed, the position
        of 0 does not move. As such, we can just add or subtract a full
        rotation if required.
        """
        return utils.ConvertAngle(self.Longitude, signed)

    def GetLatLon(self, signed=True):
        """ Convenience function for getting lat and lon.
        """
        lat = self.GetLat(signed)
        lon = self.GetLon(signed)
        return lat, lon

def BearingBetween(lat_1, lon_1, lat_2, lon_2, degrees=True):
    """ Calculate initial bearing between two locations.

    From: https://www.movable-type.co.uk/scripts/latlong.html
    """
    if degrees:
        lat_1 = utils.DegToRad(lat_1)
        lon_1 = utils.DegToRad(lon_1)
        lat_2 = utils.DegToRad(lat_2)
        lon_2 = utils.DegToRad(lon_2)

    delta_lon = lon_2 - lon_1

    brg = math.atan2(
        math.sin(delta_lon) * math.cos(lat_2),
        (math.cos(lat_1) * math.sin(lat_2)) - 
            (math.sin(lat_1) * math.cos(lat_2) * math.cos(delta_lon))
    )

    return utils.RadToDeg(brg)

def CartesianToLatLon(x, y, z, ellipsoid_ref):
    """ Convert cartesian coordinates to latitude, longitude, height.

    returns lat, lon, height
    """

    # Get reference ellipsoid parameters.
    if ellipsoid_ref == EReferenceEllipsoid.Airy1830:
        a, b = GetAiry1830()
    elif ellipsoid_ref == EReferenceEllipsoid.Wgs84:
        a, b = GetWgs84()

    # 1st and 2nd ellipsoid eccentricities.
    e2 = Eccentricity1(a, b)
    e22 = Eccentricity2(a, b)

    p = math.sqrt(math.pow(x, 2) + math.pow(y, 2))
    R = math.sqrt(math.pow(p, 2) + math.pow(z, 2))

    tan_beta = ((b * z) / (a * p)) * ((1 + e22) * (b/R))

    beta = math.atan(tan_beta)

    tan_lat_prime_top = (z + (e22 * b * math.pow(math.sin(beta), 3)))
    tan_lat_prime_bot = (p - ( e2 * a * math.pow(math.cos(beta), 3)))
    tan_lat_prime = tan_lat_prime_top / tan_lat_prime_bot

    lat_rad = math.atan(tan_lat_prime)

    tan_lon_prime = y / x

    lon_rad = math.atan(tan_lon_prime)

    v = a / math.sqrt(1 - (e2 * math.pow(math.sin(lat_rad), 2)))

    # Calculate lat, lon, height.
    height = (p * math.cos(lat_rad)) + (z * math.sin(lat_rad)) - (math.pow(a, 2) / v)
    lat = utils.RadToDeg(lat_rad)
    lon = utils.RadToDeg(lon_rad)

    return lat, lon, height

def DistanceBetween(lat_1, lon_1, lat_2, lon_2, degrees=True):
    """ Calculate distance between two location in metres.

    From: https://www.movable-type.co.uk/scripts/latlong.html
    """
    global wgs84_earth_equatorial_radius_m
    
    if degrees:
        lat_1 = utils.DegToRad(lat_1)
        lon_1 = utils.DegToRad(lon_1)
        lat_2 = utils.DegToRad(lat_2)
        lon_2 = utils.DegToRad(lon_2)
        
    delta_lat = lat_2 - lat_1
    delta_lon = lon_2 - lon_1
    
    a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2)) + (math.cos(lat_1) * math.cos(lat_2) * math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = wgs84_earth_equatorial_radius_m * c
    return d

def DmsToDd(dms_str):
    """ Convert degrees minutes seconds to decimal degrees.
    """
    parts = dms_str.split(" ")
    deg = float(parts[0])
    min = float(parts[1]) / 60.0
    sec = float(parts[2]) / 3600.0
    dd = deg + min + sec
    if (parts[3] == "S") or (parts[3] == "W"):
        dd *= -1
    return dd

def DdToDms(dd, lat_or_lon, decimal_places = 4):

    # Do maths with positive value.
    dd_abs = abs(dd)
    deg = int(dd_abs)
    min = int((dd_abs - deg) * 60)
    sec = (dd_abs - deg - (min / 60)) * 3600

    # Zero pad degrees element.
    if lat_or_lon == ELatLon.Lat:
        deg_str = f"{deg}".rjust(2, "0")
    elif lat_or_lon == ELatLon.Lon:
        deg_str = f"{deg}".rjust(3, "0")

    # Zero pad minute element.
    min_str = f"{min}".rjust(2, "0")

    # Zero pad second element.
    sec_str_parts = str(round(sec, decimal_places)).split(".")
    sec_str = ".".join([sec_str_parts[0].rjust(2, "0"), str(sec_str_parts[1].ljust(decimal_places, "0"))])

    # Work out the suffix.
    if lat_or_lon == ELatLon.Lat:
        suffix = "N"
        if dd < 0:
            suffix = "S"
    elif lat_or_lon == ELatLon.Lon:
        suffix = "E"
        if dd < 0:
            suffix = "W"

    dms_str = f"{deg_str} {min_str} {sec_str} {suffix}"
    return dms_str

def LatDdToDms(dd, decimal_places = 4):
    """ Convert latitude in decimal degrees to degrees minutes seconds.
    """
    return DdToDms(dd, ELatLon.Lat, decimal_places)

def LonDdToDms(dd, decimal_places = 4):
    """ Convert longitude in decimal degrees to degrees minutes seconds.
    """
    return DdToDms(dd, ELatLon.Lon, decimal_places)

def LatLonDdToDms(lat_dd, lon_dd):
    lat_dms = DdToDms(lat_dd, ELatLon.Lat)
    lon_dms = DdToDms(lon_dd, ELatLon.Lon)
    return lat_dms, lon_dms

def Eccentricity1(a, b):
    """ Get ellipsoid first eccentricity.
    """
    return (math.pow(a, 2) - math.pow(b, 2)) / math.pow(a, 2)

def Eccentricity2(a, b):
    """ Get ellipsoid second eccentricity.
    """
    return (math.pow(a, 2) - math.pow(b, 2)) / math.pow(b, 2)

def Extrapolate(lat, lon, brg, dst, degrees=True):
    """ Calculate a new position given a start position, bearing and distance

    Given an initial latitude and longitude, calculate a new latitude and
    longitude by extrapolating from the start point along the bearing 'brg'
    for a distance specified by 'dst'.

    It is assumed that all angles (lat, lon, brg) are in degrees. If not, set
    'degrees' to False.

    The units of 'dst' is metres.
    
    From: https://www.movable-type.co.uk/scripts/latlong.html
    """
    # Calculate angular distance.
    global wgs84_earth_equatorial_radius_m
    ang_dst = dst / wgs84_earth_equatorial_radius_m

    # If angles are in degrees, convert to radians to do our maths.
    if degrees:
        lat = utils.DegToRad(lat)
        lon = utils.DegToRad(lon)
        brg = utils.DegToRad(brg)

    tlat = math.asin(
        (math.sin(lat) * math.cos(ang_dst)) + (math.cos(lat) * math.sin(ang_dst) * math.cos(brg))
    )
    tlon = lon + math.atan2(
        math.sin(brg) * math.sin(ang_dst) * math.cos(lat),
        math.cos(ang_dst) - (math.sin(lat) * math.sin(tlat))
    )
    return utils.RadToDeg(tlat), utils.RadToDeg(tlon)

def GetAiry1830():
    """ Get Airy (1830) ellpisoid parameters.
    """
    semi_major = 6377563.396
    semi_minor = 6356256.909
    return semi_major, semi_minor

def GetWgs84():
    """ Get WGS84 ellipsoid parameters.
    Also known as EPSG:4326.
    Used by Global Positioning System (GPS).
    Used by Google.
    """
    semi_major = 6378137.000
    semi_minor = 6356752.3141
    return semi_major, semi_minor

def HelmertTransform(x, y, z, reverse = False):
    """ Perform a helmert transformation on the provided coordinates.

    Returns x, y, z

    The constants here allow conversion between WGS84 and OSGB36.

    Default is WGS84 to OSGB36. Set the reverse flag true to reverse the
    operation e.g. OSGB36 to WGS84.

    These constant values come from section 6.6 of the document "A guide to
    coordinate systems in Great Britain", version 2.3.
    """

    # Metre values.
    cx = -446.448
    cy = 125.157
    cz = -542.060

    # ppm value.
    s = 20.4894

    # sec values.
    rx = -0.1502
    ry = -0.2470
    rz = -0.8421

    # Reverse if requested.
    if reverse:
        cx = cx * -1
        cy = cy * -1
        cz = cz * -1
        s  = s  * -1
        rx = rx * -1
        ry = ry * -1
        rz = rz * -1

    # Rad values.
    rx = (rx / (3600 * 180)) * math.pi
    ry = (ry / (3600 * 180)) * math.pi
    rz = (rz / (3600 * 180)) * math.pi

    # Calculate transformed values.
    xb = cx + (1 + s * 1e-6) * (x - (rz * y) + (ry * z))
    yb = cy + (1 + s * 1e-6) * ((rz * x) + y - (rx * z))
    zb = cz + (1 + s * 1e-6) * ((-ry * x) + (rx * y) + z)

    return xb, yb, zb

def LatLonHeightToEcefCartesian(lat, lon, height, coord_format, ellipsoid_ref):
    """ Convert latitude, longitude, height to ECEF cartesian coordinates.

    Returns x, y, z values in metres.

    Convert latitude, longitude, and ellipsoid height to Earth Centred Earth
    Fixed (ECEF) cartesian coordinates.

    Specify the format of the input coordinates.

    Specify the reference ellipsoid.

    Height is in metres.
    """

    # Convert DMS lat/lon to decimal radians.
    if coord_format == ECoordFormat.LatLonDd:
        lat = utils.DegToRad(lat)
        lon = utils.DegToRad(lon)
    elif coord_format == ECoordFormat.LatLonDms:
        lat = utils.DegToRad(DmsToDd(lat))
        lon = utils.DegToRad(DmsToDd(lon))

    # Get reference ellipsoid parameters.
    if ellipsoid_ref == EReferenceEllipsoid.Airy1830:
        a, b = GetAiry1830()
    elif ellipsoid_ref == EReferenceEllipsoid.Wgs84:
        a, b = GetWgs84()
    else:
        print("Invalid ellipsoid!")

    # Get ellipsoid eccentricity.
    e2 = Eccentricity1(a, b)

    # Ellipsoid transverse radius of curvature.
    v = a / math.sqrt(1 - (e2 * math.pow(math.sin(lat), 2)))

    # Cartesian coordinates.
    x = (v + height) * math.cos(lat) * math.cos(lon)
    y = (v + height) * math.cos(lat) * math.sin(lon)
    z = (((1 - e2) * v) + height) * math.sin(lat)

    return x, y, z

def LatLonToEastingNorthing(lat, lon):
    """ Convert latitude, longitude, to easting, northing.

    return easting, northing
    """

    # National grid constants.
    F0 = 0.9996012717           # Scale factor on central meridian.
    lat_0 = utils.DegToRad(49)  # True origin latitude. φ, phi
    lon_0 = utils.DegToRad(-2)  # True origin longitude. λ, lambda
    E0 = 400000                 # True origin eastings metres.
    N0 = -100000                # True origin northings metres.

    # Airy ellipsoid parameters.
    a, b = GetAiry1830()
    e2 = Eccentricity1(a, b)

    # Convert lat, lon degrees to radians.
    lat = utils.DegToRad(lat)
    lon = utils.DegToRad(lon)

    n = (a - b) / (a + b)
    v = a * F0 * math.pow(1 - (e2 * math.pow(math.sin(lat), 2)), -0.5)
    p = a * F0 * (1 - e2) * math.pow(1 - (e2 * math.pow(math.sin(lat), 2)), -1.5)
    n2 = (v / p) - 1

    # M is big, break into parts... and sub-parts!
    # The documentation is missing a minus!!!
    # Should be a minus symbol before 35/24n2...
    # Should check if they know it's incorrect...
    m1 = (1 + n + ((5/4) * math.pow(n, 2)) + ((5/4) * math.pow(n, 3))) * (lat - lat_0)

    m2_1 = ((3 * n) + (3 * math.pow(n, 2)) + ((21/8) * math.pow(n, 3))) 
    m2_2 = math.sin(lat - lat_0)
    m2_3 = math.cos(lat + lat_0)
    m2 = m2_1 * m2_2 * m2_3

    m3_1 = ((15/8) * math.pow(n, 2)) + ((15/8) * math.pow(n, 3))
    m3_2 = math.sin(2 * (lat - lat_0)) * math.cos(2 * (lat + lat_0))
    m3_3 = (35/24) * math.pow(n, 3) * math.sin(3 * (lat - lat_0)) * math.cos(3 * (lat + lat_0))
    m3 = (m3_1 * m3_2) - m3_3

    m = b * F0 * (m1 - m2 + m3)

    I = m + N0
    II = (v / 2) * math.sin(lat) * math.cos(lat)
    III = (v / 24) * math.sin(lat) * math.pow(math.cos(lat), 3) * (5 - (math.pow(math.tan(lat), 2)) + (9 * n2))
    IIIA = (v/720) * math.sin(lat) * utils.Cos5(lat) * (61 - (58 * utils.Tan2(lat)) + utils.Tan4(lat))
    IV = v * math.cos(lat)
    V = (v / 6) * math.pow(math.cos(lat), 3) * ((v / p) - math.pow(math.tan(lat), 2))
    VI = (v/120) * math.pow(math.cos(lat), 5) * (5 - (18 * utils.Tan2(lat)) + utils.Tan4(lat) + (14 * n2) - (58 * utils.Tan2(lat) * n2))

    # Finally calculate the northing and easting values.
    northing = I + (II * math.pow(lon - lon_0, 2)) + (III * math.pow(lon - lon_0, 4)) + (IIIA * math.pow(lon - lon_0, 6))
    easting = E0 + (IV * (lon - lon_0)) + (V * (math.pow(lon - lon_0, 3)) + (VI * (math.pow(lon - lon_0, 5))))

    return easting, northing

def NorthingEastingToGrid(northing, easting, digits = 10):
    """ Convert northing, easting to UK OS grid reference.
    """

    e100km = math.floor(easting / 100000)
    n100km = math.floor(northing / 100000)

    l1 = (19 - n100km) - (19 - n100km) % 5 + math.floor((e100km + 10) / 5)
    l2 = (19 - n100km) * 5 % 25 + e100km % 5

    if (l1 > 7):
        l1 += 1

    if (l2 > 7):
        l2 += 1

    letter_pair = chr(l1 + ord("A")) + chr(l2 + ord("A"))

    e = math.floor((easting % 100000) / math.pow(10, 5 - (digits / 2)))
    n = math.floor((northing % 100000) / math.pow(10, 5 - (digits / 2)))

    e = f"{int(e)}".rjust(int(digits / 2), "0")
    n = f"{int(n)}".rjust(int(digits / 2), "0")

    return f"{letter_pair} {e} {n}"

def GridToEastingNorthing(grid: str):
    """ Convert UK, OS grid reference to eastings, northings.
    """

    # Convert to uppercase.
    grid = grid.upper()

    # Convert second letter to numerical value.
    l2 = ord(grid[1]) - ord("A")
    if l2 > 7:
        l2 -= 1

    # Split grid reference into parts.
    grid_parts = grid.split(" ")

    # Calculate eastings.
    easting = ((l2 % 5) * 100000) + int(grid_parts[1])
    if grid[0] in ["J", "O", "T"]:
        easting += 500000

    # Calculate northings.
    northing = ((4 - int(l2 / 5)) * 100000) + int(grid_parts[2])
    if grid[0] == "N":
        northing += 500000
    elif grid[0] == "H":
        northing += 1000000

    return easting, northing

def EastingNorthingToLatLon(easting, northing):
    """ Convert Ordanance Survey grid easting, northing to latitude longitude.

    Converting from easting/northings to latitude/longitude is an iterative
    procedure.

    Return lat/lon in DMS format.
    """

    # True origin latitude. φ, phi
    lat_0 = utils.DegToRad(49)

    # True origin longitude. λ, lambda
    lon_0 = utils.DegToRad(-2)

    # True origin eastings metres.
    e0 = 400000

    # True origin northings metres.
    n0 = -100000

    # Scale factor on central meridian.
    f0 = 0.9996012717

    # Get ellipsoid constants.
    a, b = GetAiry1830()

    # Lat dash (radians).
    lat_dash = ((northing - n0) / (a * f0)) + lat_0

    n = (a - b) / (a + b)

    def ComputeM(n, lat_dash, lat_0, b, f0):

        # Compute m.
        m1 = (1 + n + ((5/4) * math.pow(n, 2)) + ((5/4) * math.pow(n, 3))) * (lat_dash - lat_0)
        m2_1 = ((3 * n) + (3 * math.pow(n, 2)) + ((21/8) * math.pow(n, 3)))
        m2_2 = math.sin(lat_dash - lat_0)
        m2_3 = math.cos(lat_dash + lat_0)
        m2 = m2_1 * m2_2 * m2_3
        m3_1 = ((15/8) * math.pow(n, 2)) + ((15/8) * math.pow(n, 3))
        m3_2 = math.sin(2 * (lat_dash - lat_0)) * math.cos(2 * (lat_dash + lat_0))
        m3_3 = (35/24) * math.pow(n, 3) * math.sin(3 * (lat_dash - lat_0)) * math.cos(3 * (lat_dash + lat_0))
        m3 = (m3_1 * m3_2) - m3_3
        m = b * f0 * (m1 - m2 + m3)

        return m

    M = ComputeM(n, lat_dash, lat_0, b, f0)
    while True:
        lat_dash = ((northing - n0 - M) / (a * f0)) + lat_dash
        M = ComputeM(n, lat_dash, lat_0, b, f0)

        if abs(northing - n0 - M) < 0.00000001:
            break

    # First eccentricity.
    e2 = Eccentricity1(a, b)

    v = a * f0 * math.pow(1 - e2 * utils.Sin2(lat_dash), -0.5)

    p = a * f0 * (1 - e2) * math.pow(1 - (e2 * utils.Sin2(lat_dash)), -1.5)

    n2 = (v / p) - 1

    vii = math.tan(lat_dash) / (2 * p * v)

    viii = (math.tan(lat_dash) / (24 * p * math.pow(v, 3))) * (5 + (3 * utils.Tan2(lat_dash)) + n2 - (9 * utils.Tan2(lat_dash) * n2))

    ix = (math.tan(lat_dash) / (720 * p * math.pow(v, 5))) * (61 + (90 * utils.Tan2(lat_dash)) + (45 * utils.Tan4(lat_dash)))

    x = utils.Sec(lat_dash) / v

    xi = (utils.Sec(lat_dash) / (6 * math.pow(v, 3))) * ((v / p) + (2 * utils.Tan2(lat_dash)))

    xii = (utils.Sec(lat_dash) / (120 * math.pow(v, 5))) * (5 + (28 * utils.Tan2(lat_dash)) + (24 * utils.Tan4(lat_dash)))

    xiia = (utils.Sec(lat_dash) / (5040 * math.pow(v, 7))) * (61 + (662 * utils.Tan2(lat_dash)) + (1320 * utils.Tan4(lat_dash)) + (720 * utils.Tan6(lat_dash)))

    lat = lat_dash - (vii * math.pow(easting - e0, 2)) + (viii * math.pow(easting - e0, 4)) - (ix * math.pow(easting - e0, 6))
    lat = utils.RadToDeg(lat)

    lon = lon_0 + (x * (easting - e0)) - (xi * math.pow(easting - e0, 3)) + (xii * math.pow(easting - e0, 5)) - (xiia * math.pow(easting - e0, 7))
    lon = utils.RadToDeg(lon)

    return lat, lon

class Egm():
    """ Provide EGM geoid height values.

    Provide EGM96 geoid height values for a given latitude, longitude.

    There are several different EGM models available. I've implemented the
    EGM96 model - which is probably getting a little long in the tooth at this
    point. I would like to implement additional models in the future.

    I would also like to implement a spline interpolation, in addition to the
    current bilinear interpolation.

    I've implemented 6 tests of my EGM96 geoid height calculator. These tests
    are performed against the sample values provided with the EGM96 geoid
    height data. My interpolated values are close, but not identical to the
    sample values provided. This may be because the sample values were
    interpolated using a different mechanism (my bilinear vs. their spline),
    or I may have made a mistake in my interpolation / parsing of the file.
    Either way, the values I'm producing are good enough for my purposes but
    this implementation may require further work.

    A nice online tool for value lookup.
    https://www.unavco.org/software/geodetic-utilities/geoid-height-calculator/geoid-height-calculator.html
    """
    def __init__(self):
        """ On class initialisation, read in the grid data.
        """

        # Structure holding data for different models.
        self.Data = {

            # EGM 1996, 15 minute resolution, world wide, geoid height grid.
            "9615":
            {
                "data_file_path": os.path.realpath(__file__).replace("gis.py", "EGM96_WW_15M_GH.GRD"),
                "step_size": 0.25,
                "data": []
            }
        }

        # Specify model to use.
        self.Model = "9615"

        # Load the data.
        self.LoadData()

    def LoadData(self):
        """ Read EGM data from file into memory.
        """

        # Get path to data file for selected model.
        data_file_path = self.Data[self.Model]["data_file_path"]

        # Read data from file.
        with open(data_file_path, "r") as data_file:
            data = data_file.read()

        # Parse into array.
        current_row = []
        for index, line in enumerate(data.split("\n")):

            # Skip the first line, this is just a header.
            if index == 0:
                continue

            # Skip blank lines.
            if line == "":
                continue

            # Skip the first item.
            if index == 0:
                continue

            # Break the line on space character.
            line_parts = line.split(" ")

            # Filter out empty strings.
            line_parts = list(filter(None, line_parts))

            # Add data points to current row, and convert to float as we go.
            for value in line_parts:
                current_row.append(float(value))

            # When we find a row with a single value, this is the end of the
            # current row. Add it to the row and move onto next row.
            if len(line_parts) == 1:
                self.Data[self.Model]["data"].append(current_row)
                current_row = []

    def GetHeight(self, lat, lon):
        """ Get the EGM96 geoid height for a given latitude and longitude.

        Latitudes are expected as decimal degrees in the range 90 to -90.

        Longitudes are expected as decimal degrees in the range -180 to 0 to
        180.

        Results are given as signed geoid height metres.
        """

        # The first longitude in the file is 0° e.g. where x index = 0,
        # longitude = 0°.
        # The final index in the file is for -180° e.g. 360°.
        # Longitudes are typically given as -180 to 180.
        # For this it's easier to think of them in the range 0 to 360.
        # So first convert -180 to 180 range into 0 to 360.
        # Then can use longitude values directly to index file.
        if lon < 0:
            lon = 360 + lon
        x = lon

        # The first latitude in the file is 90° e.g. where y index = 0,
        # latitude = 90°.
        # The final index in the file is for -90°.
        # Latitudes are typically given as 90 to -90.
        # So need to convert the range 90 to -90 into an index.
        y = 90 - lat

        # Get step size for current model.
        step_size = self.Data[self.Model]["step_size"]

        # Calculate the 4 surrounding points.
        x1 = x - (x % step_size)
        x2 = x1 + step_size
        y1 = y - (y % step_size)
        y2 = y1 + step_size

        # Get the geoid heights at the 4 surrounding points.
        q11 = self.Data[self.Model]["data"][int(y1 / step_size)][int(x1 / step_size)]
        q12 = self.Data[self.Model]["data"][int(y2 / step_size)][int(x1 / step_size)]
        q21 = self.Data[self.Model]["data"][int(y1 / step_size)][int(x2 / step_size)]
        q22 = self.Data[self.Model]["data"][int(y2 / step_size)][int(x2 / step_size)]

        # Bilinear Interpolation of 4 points, to get our result.
        xy1 = (((x2 - x) / (x2 - x1)) * q11) + (((x - x1) / (x2 - x1)) * q21)
        xy2 = (((x2 - x) / (x2 - x1)) * q12) + (((x - x1) / (x2 - x1)) * q22)
        yx = (((y2 - y) / (y2 - y1)) * xy1) + (((y - y1) / (y2 - y1)) * xy2)

        return round(yx, 2)

class GridGenerator:
    """ Generate a 2D grid of coordinates.

    Generate a 2D grid of coordinates between the provided top left and bottom
    right coordinates with the specified separation between points.
    """

    def __init__(self, tl: list, br: list, sep: float):

        # Initialise.
        self.lat_start = tl[0]
        self.lon_start = tl[1]
        self.lat_final = br[0]
        self.lon_final = br[1]
        self.lat = self.lat_start - sep
        self.lon = self.lon_start - sep

    def __iter__(self):
        return self

    def __next__(self):

        # Reset longitude.
        if self.lon >= self.lon_final:
            self.lon = self.lon_start
