import asyncio
import contextlib
import dataclasses
import datetime
import itertools
import math
import pathlib
import sys
import typing

import httpx
import pydantic
import tqdm

from unico_device_setuper.lib import aapt, adb, appium_settings, cnsl, util

DEFAULT_UPDATE_DELAY_S = 0.1
DEFAULT_SPEED_KMH = 30
DEFAULT_APPIUM_SETTINGS_VERSION = '5.14.10'
EARTH_RADIUS_M = 6_378_100
MIN_LAT = -85.05112877
MIN_LON = -180.0
MAX_LAT = 85.05112877
MAX_LON = 180.0


_128_OVER_180 = 128 / 180
_256_OVER_2_PI = 256 / (2 * math.pi)
_PI_OVER_360 = math.pi / 360
_PI_OVER_4 = math.pi / 4
_PI = math.pi
_PI_OVER_128 = math.pi / 128
_360_OVER_PI = 360 / math.pi
_180_OVER_128 = 180 / 128


@dataclasses.dataclass
class Params:
    geojson_path: pathlib.Path
    default_speed_kmh: float | None
    update_delay_s: float | None
    speed_multiplier: float | None
    appium_settings_version: str | None


@dataclasses.dataclass
class LatLon:
    lat: float
    lon: float


@dataclasses.dataclass
class Point2D:
    x: float
    y: float

    def __sub__(self, other: 'Point2D'):
        return Vec2d(dx=self.x - other.x, dy=self.y - other.y)

    def __add__(self, other: 'Vec2d'):
        return Point2D(x=self.x + other.dx, y=self.y + other.dy)


@dataclasses.dataclass
class Vec2d:
    dx: float
    dy: float

    def __mul__(self, other: float):
        return Vec2d(dx=self.dx * other, dy=self.dy * other)


def merca_project(pos: LatLon):
    return Point2D(
        x=128 + _128_OVER_180 * pos.lon,
        y=128 - _256_OVER_2_PI * math.log(math.tan(_PI_OVER_360 * pos.lat + _PI_OVER_4)),
    )


def merca_unproject(point: Point2D):
    if point.y < 0:
        lat = MAX_LAT
    elif point.y > 256:
        lat = MIN_LAT
    else:
        lat = (_360_OVER_PI * math.atan(math.exp(_PI - _PI_OVER_128 * point.y))) - 90

    if point.x < 0:
        lon = MIN_LON
    elif point.x > 256:
        lon = MAX_LON
    else:
        lon = _180_OVER_128 * point.x - 180

    return LatLon(lat, lon)


class Properties(pydantic.BaseModel):
    speeds_kmh: list[float] | None = pydantic.Field(validation_alias='speeds', default=None)


class Geometry(pydantic.BaseModel):
    type: typing.Literal['LineString']
    coordinates: list[tuple[float, float]]


class Feature(pydantic.BaseModel):
    type: typing.Literal['Feature']
    geometry: Geometry
    properties: Properties


class FeatureCollection(pydantic.BaseModel):
    type: typing.Literal['FeatureCollection']
    features: list[Feature]


@dataclasses.dataclass
class Waypoint:
    pos: LatLon
    original_pos: LatLon
    duration: datetime.timedelta

    @staticmethod
    def make_original(pos: LatLon, duration: datetime.timedelta):
        return Waypoint(pos, pos, duration)


def get_durations(coordinates: list[LatLon], speeds_kmh: list[float] | None, params: Params):
    if len(coordinates) <= 2:
        cnsl.print_red('not enough coordinates')
        sys.exit()

    default_speed_kmh = params.default_speed_kmh or DEFAULT_SPEED_KMH

    if speeds_kmh is not None:
        missing_speed_count = len(coordinates) - (len(speeds_kmh) + 1)
        if missing_speed_count != 0:
            cnsl.warn(
                f'{len(speeds_kmh)} speeds are given'
                f' but there are {len(coordinates)} coordinates: '
                + (
                    f'the last {missing_speed_count} speeds will be {default_speed_kmh} km/h'
                    if missing_speed_count > 0
                    else f'the last {-missing_speed_count} speeds will be ignored'
                )
            )
    else:
        cnsl.warn(
            f'Speeds are not specified, a constant speed of {default_speed_kmh} km/h will be used'
        )

    speed_kmh_generator = itertools.chain(speeds_kmh or [], itertools.repeat(default_speed_kmh))

    return [
        datetime.timedelta(
            seconds=(get_distance_between_m(pos1, pos2) / (speed_kmh / 3.6))
            if speed_kmh != 0
            else 0
        )
        for ((pos1, pos2), speed_kmh) in zip(
            itertools.pairwise(coordinates), speed_kmh_generator, strict=False
        )
    ]


def get_feature(path: pathlib.Path):
    return FeatureCollection.model_validate_json(path.read_text()).features[0]


def get_waypoints(geojson_path: pathlib.Path, params: Params):
    feature = get_feature(geojson_path)
    coordinates = [LatLon(lat, lon) for (lon, lat) in feature.geometry.coordinates]
    durations = get_durations(coordinates, speeds_kmh=feature.properties.speeds_kmh, params=params)
    return [
        Waypoint.make_original(pos, duration)
        for (pos, duration) in zip(coordinates, [datetime.timedelta(), *durations], strict=True)
    ]


def get_distance_between_m(pos1: LatLon, pos2: LatLon):
    """Distance in meters between 2 coordinates of the surface of the earth."""
    lat1 = math.radians(pos1.lat)
    lon1 = math.radians(pos1.lon)
    lat2 = math.radians(pos2.lat)
    lon2 = math.radians(pos2.lon)
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    return (
        2
        * EARTH_RADIUS_M
        * math.asinh(
            math.sqrt(
                math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            )
        )
    )


def make_fine_waypoints(waypoints: list[Waypoint], params: Params):
    new_waypoints: list[Waypoint] = [waypoints[0]]
    update_delay_s = datetime.timedelta(seconds=params.update_delay_s or DEFAULT_UPDATE_DELAY_S)
    for wp1, wp2 in itertools.pairwise(waypoints):
        update_count = math.ceil(wp2.duration / update_delay_s)
        p1 = merca_project(wp1.pos)
        p2 = merca_project(wp2.pos)
        delta = p2 - p1
        for i in range(update_count):
            coef = (i + 1) / update_count
            pos = merca_unproject(p1 + (delta * coef))
            new_waypoints.append(
                Waypoint(
                    pos,
                    original_pos=wp1.pos if coef < 0.5 else wp2.pos,
                    duration=wp2.duration / update_count,
                )
            )
    return new_waypoints


def bearing(vec: Vec2d):
    is_right = vec.dx < 0
    norm = math.hypot(vec.dx, vec.dy)
    if abs(norm) <= 1e-10:
        return 0
    r = -vec.dy / norm
    if 1 <= r <= 1 + 1e-10:
        angle = 0
    elif -1 >= r >= -1 - 1e-10:
        angle = math.pi
    else:
        angle = math.acos(-vec.dy / norm)
    if is_right:
        angle = 2 * math.pi - angle
    return 180 * angle / math.pi


@dataclasses.dataclass
class GpsPosition:
    pos: LatLon
    speed: float
    bearing: float

    def set(self, appium_settings: appium_settings.AppiumSettings):
        return appium_settings.set_position(
            longitude=self.pos.lon, latitude=self.pos.lat, speed=self.speed, bearing=self.bearing
        )


def get_first_gps_position(waypoints: list[Waypoint]):
    return GpsPosition(
        pos=waypoints[0].pos,
        speed=0,
        bearing=bearing(merca_project(waypoints[1].pos) - merca_project(waypoints[0].pos)),
    )


async def play_waypoints(
    waypoints: list[Waypoint], appium_settings: appium_settings.AppiumSettings, params: Params
):
    total_duration = sum((wp.duration for wp in waypoints), start=datetime.timedelta())
    speed_multiplier = params.speed_multiplier or 1
    stop_file_path = pathlib.Path('stop.txt')

    with tqdm.tqdm(
        total=total_duration.total_seconds(),
        desc='Itineraire',
        unit='s',
        bar_format='{desc}: {percentage:3.0f}%|{bar}| {elapsed}<{remaining} {rate_fmt}{postfix}',
    ) as progress_bar:
        for wp1, wp2 in itertools.pairwise(
            [Waypoint.make_original(waypoints[0].pos, datetime.timedelta()), *waypoints]
        ):
            if stop_file_path.exists():
                stop_file_path.write_text(f'{wp1.original_pos.lon}, {wp1.original_pos.lat}')

            while stop_file_path.exists():  # noqa: ASYNC110
                await asyncio.sleep(0.1)

            duration = wp2.duration / speed_multiplier
            distance_m = get_distance_between_m(wp1.pos, wp2.pos)
            p1 = merca_project(wp1.pos)
            p2 = merca_project(wp2.pos)
            speed = (
                distance_m / duration.total_seconds() if wp2.duration.total_seconds() != 0 else 0
            )
            async with util.ensure_min_duration(duration):
                await GpsPosition(pos=wp2.pos, speed=speed, bearing=bearing(p2 - p1)).set(
                    appium_settings
                )
                progress_bar.update(speed_multiplier * duration.total_seconds())


@contextlib.asynccontextmanager
async def disable_wifi_ble_scan_tmp(adb_ctx: adb.Adb):
    async with (
        adb_ctx.settings_set_tmp('ble_scan_always_enabled', '0', 'global'),
        adb_ctx.settings_set_tmp('wifi_scan_always_enabled', '0', 'global'),
    ):
        yield


async def mock_locations(params: Params):
    waypoints = get_waypoints(params.geojson_path, params)
    waypoints = make_fine_waypoints(waypoints, params)

    async with (
        httpx.AsyncClient() as http_client,
        adb.UndevicedAdb.make(http_client) as undeviced_adb,
    ):
        adb_ctx = await undeviced_adb.with_first_device()
        async with (
            aapt.Aapt.make(adb_ctx, http_client) as aapt_ctx,
            appium_settings.AppiumSettings.make(
                params.appium_settings_version or DEFAULT_APPIUM_SETTINGS_VERSION,
                adb_ctx,
                aapt_ctx,
                http_client,
            ) as appium_settings_ctx,
            disable_wifi_ble_scan_tmp(adb_ctx),
        ):
            await get_first_gps_position(waypoints).set(appium_settings_ctx)
            input('Location mocked, tap enter to start round.')
            await play_waypoints(waypoints, appium_settings_ctx, params)
            input('Round finished, tap enter to stop location mock.')
