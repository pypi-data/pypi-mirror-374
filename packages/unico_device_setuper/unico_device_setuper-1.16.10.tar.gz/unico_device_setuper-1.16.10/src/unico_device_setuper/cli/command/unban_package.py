import slugify
import tqdm

from unico_device_setuper.cli import stp
from unico_device_setuper.lib import aio, api, cnsl, pkg


async def list_packages(setup: stp.Setup):
    apk_path_map = await pkg.get_apk_path_map(setup.adb)

    packages: list[pkg.Package] = []
    with tqdm.tqdm(total=len(apk_path_map), desc='Récuperation des informations') as progress_bar:
        async for package in aio.iter_unordered(
            (
                pkg.get_package_from_apk_path(path, name, setup.aapt)
                for name, path in apk_path_map.items()
            ),
            max_concurrency=50,
        ):
            progress_bar.update(1)
            if package is not None:
                packages.append(package)
    return packages


@cnsl.command('Inclusion de nouvelles applications', 'Nouvelles applications incluses')
async def unban_package(setup: stp.Setup):
    packages_ = await api.packages_get_all.request(setup.api_client)
    assert isinstance(packages_, api.PackagesModel), packages_

    packages = [
        pkg.Package(label=p.label, name=p.name)
        for p in (packages_.packages.additional_properties if packages_.packages else {}).values()
        if not p.disabled
    ]

    package_name_display_line_map = pkg.make_package_name_display_line_map(packages)

    cnsl.print_blue('Choisir une ou plusieurs applications')
    packages = await cnsl.print_choose_multiple(
        items=sorted(packages, key=lambda p: slugify.slugify(p.label)),
        prompt='Applications: ',
        formater=lambda p: package_name_display_line_map[p.name],
        choice_formater=lambda p: p.label,
    )

    response = await api.packages_upsert_many.request(
        setup.api_client,
        [
            api.Package(name=package.name, label=package.label, disabled=True)
            for package in packages
        ],
    )

    if not isinstance(response, api.EmptyResponse):
        cnsl.print_red('Error lors la sauvegarde des applications')
        return False

    return True
