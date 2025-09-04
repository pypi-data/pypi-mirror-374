import pathlib

import cyclopts

from unico_device_setuper.scripts import paris_source, waymo

APP = cyclopts.App()


@APP.command
async def compile_paris_source(path: list[pathlib.Path]):
    await paris_source.compile_(path)


@APP.command
async def waymo_(
    geojson_path: pathlib.Path,
    *,
    default_speed_kmh: float | None = None,
    update_delay_s: float | None = None,
    speed_multiplier: float | None = None,
    appium_settings_version: str | None = None,
):
    await waymo.mock_locations(
        waymo.Params(
            geojson_path=geojson_path,
            default_speed_kmh=default_speed_kmh,
            update_delay_s=update_delay_s,
            speed_multiplier=speed_multiplier,
            appium_settings_version=appium_settings_version,
        )
    )
