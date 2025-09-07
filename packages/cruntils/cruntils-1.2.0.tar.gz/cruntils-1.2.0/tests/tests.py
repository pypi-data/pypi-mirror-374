
# Core Python imports.
import os
import sys

# Modify path so we can include the version of cruntils in this directory
# instead of relying on the user having it installed.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our package.
import cruntils

# EGM96 tests.
# NB. Please read notes on EGM implementation.
# Tests are performed against the sample values provided in the readme.txt
# that comes with the EGM96 geoid data. The original values are:
#
# Latitude     Longitude    Geoid Height metres
# 38.6281550,  269.7791550, -31.628
# -14.6212170, 305.0211140, -2.969
# 46.8743190,  102.4487290, -43.575
# -23.6174460, 133.8747120, 15.871
# 38.6254730,  359.9995000, 50.066
# -0.4667440,  0.0023000,   17.329
# Instanciate the egm object.
egm = cruntils.gis.Egm()

location = cruntils.gis.CLocation(38.6281550, 269.7791550, True, False)
assert egm.GetHeight(*location.GetLatLon(True)) == -31.61

location = cruntils.gis.CLocation(-14.6212170, 305.0211140, True, False)
assert egm.GetHeight(*location.GetLatLon(True)) == -2.97

location = cruntils.gis.CLocation(46.8743190, 102.4487290, True, False)
assert egm.GetHeight(*location.GetLatLon(True)) == -43.62

location = cruntils.gis.CLocation(-23.6174460, 133.8747120, True, False)
assert egm.GetHeight(*location.GetLatLon(True)) == 15.93

location = cruntils.gis.CLocation(38.6254730, 359.9995000, True, False)
assert egm.GetHeight(*location.GetLatLon(True)) == 50.04

location = cruntils.gis.CLocation(-0.4667440, 0.0023000, True, False)
assert egm.GetHeight(*location.GetLatLon(True)) == 17.34

# Location class testing.
location = cruntils.gis.CLocation(29.97914809004421, 31.13419577459987)
location.SetName("The Great Pyramid of Giza")
assert location.GetLat(True)  == 29.97914809004421
assert location.GetLat(False) == 119.97914809004421
assert location.GetLon(True)  == 31.13419577459987
assert location.GetLon(False) == 31.13419577459987
assert egm.GetHeight(*location.GetLatLon(True)) == 15.46
assert cruntils.gis.LatDdToDms(location.GetLat()) == "29 58 44.9331 N"
assert cruntils.gis.LonDdToDms(location.GetLon()) == "031 08 03.1048 E"

location = cruntils.gis.CLocation(13.412544924724, 103.866982081196)
assert location.GetLat(True)  == 13.412544924724
assert location.GetLat(False) == 103.412544924724
assert location.GetLon(True)  == 103.866982081196
assert location.GetLon(False) == 103.866982081196
assert egm.GetHeight(*location.GetLatLon(True)) == -20.74
assert cruntils.gis.LatDdToDms(location.GetLat()) == "13 24 45.1617 N"
assert cruntils.gis.LonDdToDms(location.GetLon()) == "103 52 01.1355 E"

location = cruntils.gis.CLocation(-33.856814228066426, 151.21527245566526)
assert location.GetLat(True)  == -33.856814228066426
assert location.GetLat(False) == 56.143185771933574
assert location.GetLon(True)  == 151.21527245566526
assert location.GetLon(False) == 151.21527245566526
assert egm.GetHeight(*location.GetLatLon(True)) == 22.46
assert cruntils.gis.LatDdToDms(location.GetLat()) == "33 51 24.5312 S"
assert cruntils.gis.LonDdToDms(location.GetLon()) == "151 12 54.9808 E"

location = cruntils.gis.CLocation(48.85824194192016, 2.2947293419960277)
assert location.GetLat(True)  == 48.85824194192016
assert location.GetLat(False) == 138.85824194192017
assert location.GetLon(True)  == 2.2947293419960277
assert location.GetLon(False) == 2.2947293419960277
assert egm.GetHeight(*location.GetLatLon(True)) == 44.58
assert cruntils.gis.LatDdToDms(location.GetLat(), 3) == "48 51 29.671 N"
assert cruntils.gis.LonDdToDms(location.GetLon()) == "002 17 41.0256 E"

location = cruntils.gis.CLocation(27.175082927193554, 78.04218888603889)
assert location.GetLat(True)  == 27.175082927193554
assert location.GetLat(False) == 117.17508292719356
assert location.GetLon(True)  == 78.04218888603889
assert location.GetLon(False) == 78.04218888603889
assert egm.GetHeight(*location.GetLatLon(True)) == -56.65
assert cruntils.gis.LatDdToDms(location.GetLat()) == "27 10 30.2985 N"
assert cruntils.gis.LonDdToDms(location.GetLon(), 2) == "078 02 31.88 E"

location = cruntils.gis.CLocation(25.197099645751745, 55.27436713304521)
assert location.GetLat(True)  == 25.197099645751745
assert location.GetLat(False) == 115.19709964575175
assert location.GetLon(True)  == 55.27436713304521
assert location.GetLon(False) == 55.27436713304521
assert egm.GetHeight(*location.GetLatLon(True)) == -33.72
assert cruntils.gis.LatDdToDms(location.GetLat()) == "25 11 49.5587 N"
assert cruntils.gis.LonDdToDms(location.GetLon()) == "055 16 27.7217 E"

location = cruntils.gis.CLocation(-13.16288083855811, -72.54499246486483)
assert location.GetLat(True)  == -13.16288083855811
assert location.GetLat(False) == 76.83711916144189
assert location.GetLon(True)  == -72.54499246486483
assert location.GetLon(False) == 287.45500753513517
assert egm.GetHeight(*location.GetLatLon(True)) == 41.0
assert cruntils.gis.LatDdToDms(location.GetLat(), 3) == "13 09 46.371 S"
assert cruntils.gis.LonDdToDms(location.GetLon()) == "072 32 41.9729 W"

location = cruntils.gis.CLocation(40.4328165861077, 116.56384082714345)
assert location.GetLat(True)  == 40.4328165861077
assert location.GetLat(False) == 130.4328165861077
assert location.GetLon(True)  == 116.56384082714345
assert location.GetLon(False) == 116.56384082714345
assert egm.GetHeight(*location.GetLatLon(True)) == -8.84

location = cruntils.gis.CLocation(43.87893406761528, -103.45910824083181)
assert location.GetLat(True)  == 43.87893406761528
assert location.GetLat(False) == 133.8789340676153
assert location.GetLon(True)  == -103.45910824083181
assert location.GetLon(False) == 256.54089175916819
assert egm.GetHeight(*location.GetLatLon(True)) == -14.34

location = cruntils.gis.CLocation(48.636040758988834, -1.5113842779991045)
assert location.GetLat(True)  == 48.636040758988834
assert location.GetLat(False) == 138.63604075898883
assert location.GetLon(True)  == -1.5113842779991045
assert location.GetLon(False) == 358.4886157220008955
assert egm.GetHeight(*location.GetLatLon(True)) == 48.63

location = cruntils.gis.CLocation(37.971715070563704, 23.72611403397619)
assert location.GetLat(True)  == 37.971715070563704
assert location.GetLat(False) == 127.9717150705637
assert location.GetLon(True)  == 23.72611403397619
assert location.GetLon(False) == 23.72611403397619
assert egm.GetHeight(*location.GetLatLon(True)) == 38.47

location = cruntils.gis.CLocation(52.51629349301016, 13.37766047582947)
assert location.GetLat(True)  == 52.51629349301016
assert location.GetLat(False) == 142.51629349301015
assert location.GetLon(True)  == 13.37766047582947
assert location.GetLon(False) == 13.37766047582947
assert egm.GetHeight(*location.GetLatLon(True)) == 39.57

location = cruntils.gis.CLocation(-27.122237695511924, -109.28847085908615)
assert location.GetLat(True)  == -27.122237695511924
assert location.GetLat(False) == 62.87776230448807
assert location.GetLon(True)  == -109.28847085908615
assert location.GetLon(False) == 250.71152914091385
assert egm.GetHeight(*location.GetLatLon(True)) == -5.02

location = cruntils.gis.CLocation(37.819967553225766, -122.47857851638965)
assert location.GetLat(True)  == 37.819967553225766
assert location.GetLat(False) == 127.81996755322577
assert location.GetLon(True)  == -122.47857851638965
assert location.GetLon(False) == 237.52142148361037
assert egm.GetHeight(*location.GetLatLon(True)) == -32.27

location = cruntils.gis.CLocation(47.55755543652021, 10.749872777217082)
assert location.GetLat(True)  == 47.55755543652021
assert location.GetLat(False) == 137.5575554365202
assert location.GetLon(True)  == 10.749872777217082
assert location.GetLon(False) == 10.749872777217082
assert egm.GetHeight(*location.GetLatLon(True)) == 47.57

location = cruntils.gis.CLocation(43.723008691837215, 10.39664187812666)
assert location.GetLat(True)  == 43.723008691837215
assert location.GetLat(False) == 133.7230086918372
assert location.GetLon(True)  == 10.39664187812666
assert location.GetLon(False) == 10.39664187812666
assert egm.GetHeight(*location.GetLatLon(True)) == 46.88

location = cruntils.gis.CLocation(-17.925536940892446, 25.8585721157442)
assert location.GetLat(True)  == -17.925536940892446
assert location.GetLat(False) == 72.07446305910756
assert location.GetLon(True)  == 25.8585721157442
assert location.GetLon(False) == 25.8585721157442
assert egm.GetHeight(*location.GetLatLon(True)) == 7.97

location = cruntils.gis.CLocation(31.776694243124926, 35.234550416303016)
assert location.GetLat(True)  == 31.776694243124926
assert location.GetLat(False) == 121.77669424312492
assert location.GetLon(True)  == 35.234550416303016
assert location.GetLon(False) == 35.234550416303016
assert egm.GetHeight(*location.GetLatLon(True)) == 20.17

location = cruntils.gis.CLocation(55.24079494341456, -6.511485424530822)
assert location.GetLat(True)  == 55.24079494341456
assert location.GetLat(False) == 145.24079494341456
assert location.GetLon(True)  == -6.511485424530822
assert location.GetLon(False) == 353.488514575469178
assert egm.GetHeight(*location.GetLatLon(True)) == 56.43

location = cruntils.gis.CLocation(51.50135039825405, -0.14187864274170406)
assert location.GetLat(True)  == 51.50135039825405
assert location.GetLat(False) == 141.50135039825403
assert location.GetLon(True)  == -0.14187864274170406
assert location.GetLon(False) == 359.85812135725829594
assert egm.GetHeight(*location.GetLatLon(True)) == 45.98

location = cruntils.gis.CLocation(41.40370129831798, 2.1744141615926087)
assert location.GetLat(True)  == 41.40370129831798
assert location.GetLat(False) == 131.40370129831797
assert location.GetLon(True)  == 2.1744141615926087
assert location.GetLon(False) == 2.1744141615926087
assert egm.GetHeight(*location.GetLatLon(True)) == 49.49

location = cruntils.gis.CLocation(-22.95238321031523, -43.210476226821186)
assert location.GetLat(True)  == -22.95238321031523
assert location.GetLat(False) == 67.04761678968477
assert location.GetLon(True)  == -43.210476226821186
assert location.GetLon(False) == 316.789523773178814
assert egm.GetHeight(*location.GetLatLon(True)) == -5.46

location = cruntils.gis.CLocation(41.00523488627207, 28.976971976352964)
assert location.GetLat(True)  == 41.00523488627207
assert location.GetLat(False) == 131.00523488627206
assert location.GetLon(True)  == 28.976971976352964
assert location.GetLon(False) == 28.976971976352964
assert egm.GetHeight(*location.GetLatLon(True)) == 37.41

location = cruntils.gis.CLocation(41.89020999827253, 12.492330841334322)
assert location.GetLat(True)  == 41.89020999827253
assert location.GetLat(False) == 131.89020999827252
assert location.GetLon(True)  == 12.492330841334322
assert location.GetLon(False) == 12.492330841334322
assert egm.GetHeight(*location.GetLatLon(True)) == 48.46

location = cruntils.gis.CLocation(13.749831620390959, 100.49158250207049)
assert location.GetLat(True)  == 13.749831620390959
assert location.GetLat(False) == 103.74983162039096
assert location.GetLon(True)  == 100.49158250207049
assert location.GetLon(False) == 100.49158250207049
assert egm.GetHeight(*location.GetLatLon(True)) == -31.64

location = cruntils.gis.CLocation(40.68930946193621, -74.04454141836152)
assert location.GetLat(True)  == 40.68930946193621
assert location.GetLat(False) == 130.6893094619362
assert location.GetLon(True)  == -74.04454141836152
assert location.GetLon(False) == 285.95545858163848
assert egm.GetHeight(*location.GetLatLon(True)) == -32.87

location = cruntils.gis.CLocation(30.328526247400003, 35.444262214033294)
assert location.GetLat(True)  == 30.328526247400003
assert location.GetLat(False) == 120.3285262474
assert location.GetLon(True)  == 35.444262214033294
assert location.GetLon(False) == 35.444262214033294
assert egm.GetHeight(*location.GetLatLon(True)) == 18.39

location = cruntils.gis.CLocation(20.83065925595387, 107.096572109152)
assert location.GetLat(True)  == 20.83065925595387
assert location.GetLat(False) == 110.83065925595386
assert location.GetLon(True)  == 107.096572109152
assert location.GetLon(False) == 107.096572109152
assert egm.GetHeight(*location.GetLatLon(True)) == -23.44

location = cruntils.gis.CLocation(51.17886977737434, -1.8261692863615964)
assert location.GetLat(True)  == 51.17886977737434
assert location.GetLat(False) == 141.17886977737433
assert location.GetLon(True)  == -1.8261692863615964
assert location.GetLon(False) == 358.1738307136384036
assert egm.GetHeight(*location.GetLatLon(True)) == 47.88

location = cruntils.gis.CLocation(36.46145193248103, 25.37561594083781)
assert location.GetLat(True)  == 36.46145193248103
assert location.GetLat(False) == 126.46145193248103
assert location.GetLon(True)  == 25.37561594083781
assert location.GetLon(False) == 25.37561594083781
assert egm.GetHeight(*location.GetLatLon(True)) == 34.88

location = cruntils.gis.CLocation(35.363020326680214, 138.72969579753973)
assert location.GetLat(True)  == 35.363020326680214
assert location.GetLat(False) == 125.36302032668021
assert location.GetLon(True)  == 138.72969579753973
assert location.GetLon(False) == 138.72969579753973
assert egm.GetHeight(*location.GetLatLon(True)) == 41.25

location = cruntils.gis.CLocation(29.656121190521272, 91.11770107604704)
assert location.GetLat(True)  == 29.656121190521272
assert location.GetLat(False) == 119.65612119052128
assert location.GetLon(True)  == 91.11770107604704
assert location.GetLon(False) == 91.11770107604704
assert egm.GetHeight(*location.GetLatLon(True)) == -34.66

# Test converting angles, signed / un-signed.
assert cruntils.utils.ConvertAngle(-180, False) == 180
assert cruntils.utils.ConvertAngle(-170, False) == 190
assert cruntils.utils.ConvertAngle(-160, False) == 200
assert cruntils.utils.ConvertAngle(-150, False) == 210
assert cruntils.utils.ConvertAngle(-140, False) == 220
assert cruntils.utils.ConvertAngle(-130, False) == 230
assert cruntils.utils.ConvertAngle(-120, False) == 240
assert cruntils.utils.ConvertAngle(-110, False) == 250
assert cruntils.utils.ConvertAngle(-100, False) == 260
assert cruntils.utils.ConvertAngle(-90, False)  == 270
assert cruntils.utils.ConvertAngle(-80, False)  == 280
assert cruntils.utils.ConvertAngle(-70, False)  == 290
assert cruntils.utils.ConvertAngle(-60, False)  == 300
assert cruntils.utils.ConvertAngle(-50, False)  == 310
assert cruntils.utils.ConvertAngle(-40, False)  == 320
assert cruntils.utils.ConvertAngle(-30, False)  == 330
assert cruntils.utils.ConvertAngle(-20, False)  == 340
assert cruntils.utils.ConvertAngle(-10, False)  == 350
assert cruntils.utils.ConvertAngle(-0, False)   == 0
assert cruntils.utils.ConvertAngle(0, False)    == 0
assert cruntils.utils.ConvertAngle(45, False)   == 45
assert cruntils.utils.ConvertAngle(90, False)   == 90
assert cruntils.utils.ConvertAngle(180, False)  == 180
assert cruntils.utils.ConvertAngle(270, False)  == 270
assert cruntils.utils.ConvertAngle(360, False)  == 0
assert cruntils.utils.ConvertAngle(400, False)  == 40

assert cruntils.utils.ConvertAngle(0, True)  == 0
assert cruntils.utils.ConvertAngle(10, True)  == 10
assert cruntils.utils.ConvertAngle(20, True)  == 20
assert cruntils.utils.ConvertAngle(30, True)  == 30
assert cruntils.utils.ConvertAngle(40, True)  == 40
assert cruntils.utils.ConvertAngle(50, True)  == 50
assert cruntils.utils.ConvertAngle(60, True)  == 60
assert cruntils.utils.ConvertAngle(70, True)  == 70
assert cruntils.utils.ConvertAngle(80, True)  == 80
assert cruntils.utils.ConvertAngle(90, True)  == 90
assert cruntils.utils.ConvertAngle(100, True)  == 100
assert cruntils.utils.ConvertAngle(110, True)  == 110
assert cruntils.utils.ConvertAngle(120, True)  == 120
assert cruntils.utils.ConvertAngle(130, True)  == 130
assert cruntils.utils.ConvertAngle(140, True)  == 140
assert cruntils.utils.ConvertAngle(150, True)  == 150
assert cruntils.utils.ConvertAngle(160, True)  == 160
assert cruntils.utils.ConvertAngle(170, True)  == 170
assert cruntils.utils.ConvertAngle(180, True)  == 180
assert cruntils.utils.ConvertAngle(190, True)  == -170
assert cruntils.utils.ConvertAngle(200, True)  == -160
assert cruntils.utils.ConvertAngle(210, True)  == -150
assert cruntils.utils.ConvertAngle(220, True)  == -140
assert cruntils.utils.ConvertAngle(230, True)  == -130
assert cruntils.utils.ConvertAngle(240, True)  == -120
assert cruntils.utils.ConvertAngle(250, True)  == -110
assert cruntils.utils.ConvertAngle(260, True)  == -100
assert cruntils.utils.ConvertAngle(270, True)  == -90
assert cruntils.utils.ConvertAngle(280, True)  == -80
assert cruntils.utils.ConvertAngle(290, True)  == -70
assert cruntils.utils.ConvertAngle(300, True)  == -60
assert cruntils.utils.ConvertAngle(310, True)  == -50
assert cruntils.utils.ConvertAngle(320, True)  == -40
assert cruntils.utils.ConvertAngle(330, True)  == -30
assert cruntils.utils.ConvertAngle(340, True)  == -20
assert cruntils.utils.ConvertAngle(350, True)  == -10
assert cruntils.utils.ConvertAngle(360, True)  == 0
assert cruntils.utils.ConvertAngle(370, True)  == 10
assert cruntils.utils.ConvertAngle(380, True)  == 20
assert cruntils.utils.ConvertAngle(390, True)  == 30
assert cruntils.utils.ConvertAngle(400, True)  == 40

# OS grid references -> OSGB36 lat/lon -> WGS84 lat/lon.

# List of trig pillar locations.
trig_pillar_locations_list = [
    { 
        "name": "Heights Of Ramnageo",
        "grid": "HU 52944 80607",
        "easting": 452944, "northing": 1180607,
        "lat_osgb36": {"value": "60 30 22.345 N", "decimal_places": 3},
        "lon_osgb36": {"value": "001 02 09.3164 W", "decimal_places": 4},
        "lat_wgs84": {"value": "60 30 20.28 N", "decimal_places": 2},
        "lon_wgs84": {"value": "001 02 16.40 W",  "decimal_places": 2},
        "egm9615": 50.06
        },
    # { "name": "Hill Of Rigifa"     , "grid": "ND 30479 72144", "easting": 330479, "northing": 972144 },
    # { "name": "Nisa Mhor"          , "grid": "NB 09001 35458", "easting": 109001, "northing": 935458 },
    # { "name": "Kincraig Hill"      , "grid": "NT 46775 99914", "easting": 346775, "northing": 699914 },
    # { "name": "Fingland Fell"      , "grid": "NY 14968 95090", "easting": 314968, "northing": 595090 },
    # { "name": "Torrisholme Barrow" , "grid": "SD 45970 64246", "easting": 345970, "northing": 464246 },
    # { "name": "Somerton Castle"    , "grid": "SK 95322 58639", "easting": 495322, "northing": 358639 },
    # { "name": "Barr Beacon Resr"   , "grid": "SP 06070 97380", "easting": 406070, "northing": 297380 },
    # { "name": "East Wretham"       , "grid": "TL 91943 89941", "easting": 591943, "northing": 289941 },
    # { "name": "Plaistow Resr"      , "grid": "TQ 40315 71355", "easting": 540315, "northing": 171355 },
    # { "name": "Dry Hill"           , "grid": "TQ 43200 41606", "easting": 543200, "northing": 141606 },
    # { "name": "Charlton Clumps"    , "grid": "SU 10208 54575", "easting": 410208, "northing": 154575 },
    # { "name": "Pellyn-Wartha"      , "grid": "SW 75962 38767", "easting": 175962, "northing": 38767 }
]

# Test coordinate conversion routines - UK based.
for trig_pillar in trig_pillar_locations_list:

    # Convert UK OS grid to easting, northing.
    easting, northing = cruntils.gis.GridToEastingNorthing(trig_pillar["grid"])

    # Check conversion.
    assert easting == trig_pillar["easting"]
    assert northing == trig_pillar["northing"]

    # Convert easting, northing to DD lat, lon - OSGB36 reference.
    lat_dd_osgb36, lon_dd_osgb36 = cruntils.gis.EastingNorthingToLatLon(easting, northing)
    lat_dms_osgb36 = cruntils.gis.LatDdToDms(lat_dd_osgb36, trig_pillar["lat_osgb36"]["decimal_places"])
    lon_dms_osgb36 = cruntils.gis.LonDdToDms(lon_dd_osgb36, trig_pillar["lon_osgb36"]["decimal_places"])

    # Check conversion.
    assert lat_dms_osgb36 == trig_pillar["lat_osgb36"]["value"]
    assert lon_dms_osgb36 == trig_pillar["lon_osgb36"]["value"]

    # Convert OSGB36 lat, lon to WGS84 lat, lon.
    x, y, z = cruntils.gis.LatLonHeightToEcefCartesian(lat_dd_osgb36, lon_dd_osgb36, 0, cruntils.gis.ECoordFormat.LatLonDd, cruntils.gis.EReferenceEllipsoid.Airy1830)
    x, y, z = cruntils.gis.HelmertTransform(x, y, z, True)
    lat_dd_wgs84, lon_dd_wgs84, height = cruntils.gis.CartesianToLatLon(x, y, z, cruntils.gis.EReferenceEllipsoid.Wgs84)
    lat_dms_wgs84 = cruntils.gis.LatDdToDms(lat_dd_wgs84, trig_pillar["lat_wgs84"]["decimal_places"])
    lon_dms_wgs84 = cruntils.gis.LonDdToDms(lon_dd_wgs84, trig_pillar["lon_wgs84"]["decimal_places"])

    # Check conversion.
    assert lat_dms_wgs84 == trig_pillar["lat_wgs84"]["value"]
    assert lon_dms_wgs84 == trig_pillar["lon_wgs84"]["value"]

    # Get EGM96 geoid offset for this location and compare.
    assert egm.GetHeight(lat_dd_wgs84, lon_dd_wgs84) == trig_pillar["egm9615"]


grid_gen = cruntils.gis.GridGenerator(
    [51.164842, -1.776302],
    [51.142306, -1.723015],
    0.000125
)

for item in grid_gen:
    print(item)


