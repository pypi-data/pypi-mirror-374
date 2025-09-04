import asyncio
import dataclasses

from unico_device_setuper.cli import stp
from unico_device_setuper.cli.command import register_unitech
from unico_device_setuper.lib import cnsl, sygic, unitech


async def get_device_name(device_id: str, setup: stp.Setup):
    unitech_client = await setup.get_unitech_client()
    if unitech_client is None:
        return None
    device_name = next(
        (
            d.name
            for d in await unitech.get_device_all_devices.request(unitech_client) or []
            if d.id_device == device_id
        ),
        None,
    )
    if device_name is None:
        cnsl.print_red("Impossible de trouver le nom de l'appereil")
        return None
    return device_name


async def activate_license(
    license: sygic.License, device_id: str, device_name: str, client: sygic.Client
):
    license = license.model_copy()
    license.license_status_type = 'active'
    license.identifier = device_id
    license.note = device_name
    license.license_identifier_type = 'device'
    await client.update_license(license)
    cnsl.print(f"Utilisation d'une license {license.product_name}")


async def rename_license(license: sygic.License, device_name: str, client: sygic.Client):
    license = license.model_copy()
    license.note = device_name
    await client.update_license(license)
    cnsl.print_gray(f'Renomage de la license {license.product_name}')


@dataclasses.dataclass
class LicensePlan:
    licenses_to_rename: list[sygic.License]
    licenses_to_activate: list[sygic.License]


async def make_license_plan(
    license_products: list[sygic.LicenseProduct], device_id: str, device_name: str, setup: stp.Setup
):
    product_license_map = await sygic.get_product_license_map(await setup.get_sygic_client())

    if len(license_products) == 0:
        cnsl.print_gray('Aucune licence à activer')
        return None

    plan = LicensePlan([], [])
    for product in license_products:
        licenses = product_license_map.get(product)

        if licenses is None:
            cnsl.print_red(f'Produit inconnu: {product.label}')
            return None

        activated_license = next(
            (license for license in licenses if license.identifier == device_id), None
        )
        if activated_license is not None:
            cnsl.print_gray(f'Une license {product.label} est déja active')
            if activated_license.note != device_name:
                plan.licenses_to_rename.append(activated_license)
        else:
            available_license = next(
                (
                    license
                    for license in licenses
                    if sygic.is_license_available(license, setup.unitech_env)
                ),
                None,
            )
            if available_license is None:
                cnsl.print_red(f'Aucune license {product.label} disponible')
                return None

            plan.licenses_to_activate.append(available_license)
    return plan


async def execute_plan(plan: LicensePlan, device_id: str, device_name: str, client: sygic.Client):
    # Sygic does not handle well concurrency

    for license in plan.licenses_to_activate:
        await activate_license(
            license=license, device_id=device_id, device_name=device_name, client=client
        )
        await asyncio.sleep(1)

    for license in plan.licenses_to_rename:
        await rename_license(license=license, device_name=device_name, client=client)
        await asyncio.sleep(1)


@cnsl.command("Enregistrement de l'appareil sur Sygic", 'Appareil enregistré sur Sygic')
async def register_sygic(setup: stp.Setup):
    device_id = await register_unitech.get_id_device(setup)
    if device_id is None:
        return False

    device_name = await get_device_name(device_id, setup)
    if device_name is None:
        return False

    license_products = await setup.get_sygic_license_products()
    if license_products is None:
        return False

    plan = await make_license_plan(
        license_products, device_id=device_id, device_name=device_name, setup=setup
    )
    if plan is None:
        return False

    await execute_plan(
        plan, device_id=device_id, device_name=device_name, client=await setup.get_sygic_client()
    )

    return True
