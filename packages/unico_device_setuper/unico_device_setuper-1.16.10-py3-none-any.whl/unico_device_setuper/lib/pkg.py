import dataclasses
import pathlib
import typing

import pydantic

from unico_device_setuper.lib import aapt, adb, util


class Package(pydantic.BaseModel):
    label: str
    name: str
    version: str | None = None


async def get_apk_path_map(adb: adb.Adb):
    prefix = 'package:'
    apk_path_map: dict[str, pathlib.Path] = {}
    for line in await adb.shell('pm list package -f'):
        if line.startswith(prefix):
            (path, _, name) = line.removeprefix(prefix).rpartition('=')
            apk_path_map[name] = pathlib.Path(path)
    return apk_path_map


async def get_package_from_apk_path(apk_path: pathlib.Path, name: str, aapt: aapt.Aapt):
    package_prefix = 'package:'
    launchable_activity_prefix = 'launchable-activity:'
    base_label_prefix = 'application-label:'
    label_fr_prefix = 'application-label-fr:'

    launchable_activity_label = None
    base_label = None
    label_fr = None
    version = None

    line_generator = aapt.dump_badging(apk_path)
    try:
        async for line in line_generator:
            if line.startswith(launchable_activity_prefix):
                line_value = line.removeprefix(launchable_activity_prefix)
                _, _, label_and_after = line_value.partition('label=')
                label_value_and_space, _, _ = label_and_after.partition("='")
                launchable_activity_label = ' '.join(label_value_and_space.split()[:-1])[1:-1]
            if line.startswith(label_fr_prefix):
                label_fr = line.removeprefix(label_fr_prefix)[1:-1]
            if line.startswith(base_label_prefix):
                base_label = line.removeprefix(base_label_prefix)[1:-1]
            if line.startswith(package_prefix):
                line_value = line.removeprefix(package_prefix)
                _, _, version_and_after = line_value.partition('versionName=')
                version_and_space, _, _ = version_and_after.partition("='")
                version = ' '.join(version_and_space.split()[:-1])[1:-1]
    except util.SubprocessError:
        await line_generator.aclose()

    label = launchable_activity_label or label_fr or base_label
    if label is None:
        return None

    return Package(label=label, name=name, version=version)


async def get_permissions_from_apk_path(apk_path: pathlib.Path, aapt: aapt.Aapt):
    # uses-permission: name='android.permission.INTERNET'
    permissions_prefix = 'uses-permission:'
    permissions: set[str] = set()
    line_generator = aapt.dump_badging(apk_path)
    try:
        async for line in line_generator:
            if line.startswith(permissions_prefix):
                _, _, value = line.removeprefix(permissions_prefix).split()[0].partition('=')
                permissions.add(value[1:-1])
    except util.SubprocessError:
        await line_generator.aclose()

    return permissions


def make_package_name_display_line_map(packages: list[Package]):
    max_label_length = max(len(p.label) for p in packages)
    package_name_display_line_map: dict[str, str] = {}
    for package in packages:
        package_name_display_line_map[package.name] = (
            f'[cyan]{package.label:<{max_label_length}}[/cyan]'
            f'[blue] {package.name}[/blue]'
            + (f'[bright_black] ({package.version})[/bright_black]' if package.version else '')
        )
    return package_name_display_line_map


async def close_package(adb: adb.Adb, package_name: str):
    await adb.shell(f'am force-stop {package_name}')

    am_stack_output = await adb.shell('am stack list')
    for unstriped_line in am_stack_output:
        line = unstriped_line.strip()
        task_prefix = 'taskId='
        if line.startswith(task_prefix):
            id, _, task_info = line.removeprefix(task_prefix).partition(':')
            try:
                id = int(id)
            except ValueError:
                continue
            name, _, _ = task_info.partition('/')
            if name.strip() == package_name:
                print('removing task id', id, name)
                await adb.shell(f'am stack remove {id}')


@dataclasses.dataclass
class InstalledPackage[T]:
    version: T
    checksum: str

    @classmethod
    async def get(
        cls,
        package_name: str,
        adb: adb.Adb,
        aapt: aapt.Aapt,
        version_parser: typing.Callable[[str], T | None],
    ) -> typing.Self | None:
        apk_path = (await get_apk_path_map(adb)).get(package_name)
        if apk_path is not None:
            package = await get_package_from_apk_path(apk_path, package_name, aapt)
            if package is not None and package.version is not None:
                parsed_version = version_parser(package.version)
                if parsed_version is not None:
                    md5sum_output = await adb.shell(f'md5sum {apk_path}')
                    checksum = md5sum_output[0].split()[0]
                    return cls(parsed_version, checksum)
        return None
