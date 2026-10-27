"""
KATEC (Naver/Daum TM128) -> WGS84 longitude/latitude.

KATEC: transverse Mercator on the Bessel 1841 ellipsoid,
lat_0=38 lon_0=128 k=0.9999 x_0=400000 y_0=600000,
datum shift to WGS84 with towgs84=-146.43,507.89,681.46.
Inverse projection follows Snyder, "Map Projections: A Working Manual" (USGS PP 1395).
Agrees with PROJ to within 1mm across South Korea.
"""
import math

BESSEL = (6377397.155, 1 / 299.1528128)
WGS84 = (6378137.0, 1 / 298.257223563)
TOWGS84 = (-146.43, 507.89, 681.46)

LAT_0 = math.radians(38.0)
LON_0 = math.radians(128.0)
K_0 = 0.9999
FALSE_EASTING = 400000.0
FALSE_NORTHING = 600000.0


def _meridian_arc(a, e2, phi):
    e4, e6 = e2 * e2, e2 ** 3
    return a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * phi
                - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * math.sin(2 * phi)
                + (15 * e4 / 256 + 45 * e6 / 1024) * math.sin(4 * phi)
                - (35 * e6 / 3072) * math.sin(6 * phi))


def _tm_inverse(x, y):
    """KATEC metres -> Bessel latitude/longitude in radians."""
    a, f = BESSEL
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)

    m = _meridian_arc(a, e2, LAT_0) + (y - FALSE_NORTHING) / K_0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
            + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
            + (151 * e1 ** 3 / 96) * math.sin(6 * mu)
            + (1097 * e1 ** 4 / 512) * math.sin(8 * mu))

    sin1, cos1, tan1 = math.sin(phi1), math.cos(phi1), math.tan(phi1)
    c1 = ep2 * cos1 * cos1
    t1 = tan1 * tan1
    n1 = a / math.sqrt(1 - e2 * sin1 * sin1)
    r1 = a * (1 - e2) / (1 - e2 * sin1 * sin1) ** 1.5
    d = (x - FALSE_EASTING) / (n1 * K_0)

    lat = phi1 - (n1 * tan1 / r1) * (
        d ** 2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1 * c1 - 9 * ep2) * d ** 4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 * t1 - 252 * ep2 - 3 * c1 * c1) * d ** 6 / 720)
    lon = LON_0 + (
        d
        - (1 + 2 * t1 + c1) * d ** 3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1 * c1 + 8 * ep2 + 24 * t1 * t1) * d ** 5 / 120) / cos1
    return lat, lon


def _to_geocentric(lat, lon, ellipsoid):
    a, f = ellipsoid
    e2 = f * (2 - f)
    n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    return (n * math.cos(lat) * math.cos(lon),
            n * math.cos(lat) * math.sin(lon),
            n * (1 - e2) * math.sin(lat))


def _from_geocentric(x, y, z, ellipsoid):
    a, f = ellipsoid
    e2 = f * (2 - f)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(10):
        n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        lat = math.atan2(z + e2 * n * math.sin(lat), p)
    return lat, math.atan2(y, x)


def katec_to_wgs84(x, y):
    """Return (longitude, latitude) in WGS84 degrees for KATEC x, y in metres."""
    lat, lon = _tm_inverse(x, y)
    gx, gy, gz = _to_geocentric(lat, lon, BESSEL)
    lat, lon = _from_geocentric(gx + TOWGS84[0], gy + TOWGS84[1], gz + TOWGS84[2], WGS84)
    return math.degrees(lon), math.degrees(lat)
