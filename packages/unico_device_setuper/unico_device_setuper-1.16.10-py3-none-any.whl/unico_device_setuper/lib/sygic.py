import asyncio
import dataclasses
import datetime
import random
import typing

import httpx
import pydantic
import slugify

from unico_device_setuper.lib import cnsl, env, rl, util


class Product(pydantic.BaseModel):
    product_id: int = pydantic.Field(alias='productId')
    activation_type: str = pydantic.Field(alias='activationType')
    purchase_period: int = pydantic.Field(alias='purchasePeriod')
    product_name: str = pydantic.Field(alias='productName')
    readable_purchase_period: str = pydantic.Field(alias='readablePurchasePeriod')
    license_count: int = pydantic.Field(alias='licenseCount')
    free_license_count: int = pydantic.Field(alias='freeLicenseCount')
    activated_license_count: int = pydantic.Field(alias='activatedLicenseCount')
    deactivated_license_count: int = pydantic.Field(alias='deactivatedLicenseCount')
    expired_license_count: int = pydantic.Field(alias='expiredLicenseCount')
    outdated_license_count: int = pydantic.Field(alias='outdatedLicenseCount')
    dispatched_license_count: int = pydantic.Field(alias='dispatchedLicenseCount')
    prolonged_license_count: int = pydantic.Field(alias='prolongedLicenseCount')
    repair_count_licenses: int = pydantic.Field(alias='repairCountLicenses')
    product_identifier_type: str = pydantic.Field(alias='productIdentifierType')
    product_type: str = pydantic.Field(alias='productType')


class Order(pydantic.BaseModel):
    order_item_id: int = pydantic.Field(alias='orderItemId')
    order_id: int = pydantic.Field(alias='orderId')
    order_name: str = pydantic.Field(alias='orderName')
    order_date: datetime.datetime = pydantic.Field(alias='orderDate')
    can_be_deleted: bool = pydantic.Field(alias='canBeDeleted')
    license_count: int = pydantic.Field(alias='licenseCount')
    free_license_count: int = pydantic.Field(alias='freeLicenseCount')
    activated_license_count: int = pydantic.Field(alias='activatedLicenseCount')
    deactivated_license_count: int = pydantic.Field(alias='deactivatedLicenseCount')
    expired_license_count: int = pydantic.Field(alias='expiredLicenseCount')
    outdated_license_count: int = pydantic.Field(alias='outdatedLicenseCount')
    dispatched_license_count: int = pydantic.Field(alias='dispatchedLicenseCount')
    prolonged_license_count: int = pydantic.Field(alias='prolongedLicenseCount')
    repair_count_licenses: int = pydantic.Field(alias='repairCountLicenses')
    product_identifier_type: str = pydantic.Field(alias='productIdentifierType')
    product_type: str = pydantic.Field(alias='productType')


class License(pydantic.BaseModel):
    id: int
    identifier: str
    secondary_identifier: str | None = pydantic.Field(default=None, alias='secondaryIdentifier')
    license_identifier_type: typing.Literal['device', 'undefined'] = pydantic.Field(
        alias='licenseIdentifierType'
    )
    expiry_date: datetime.datetime | None = pydantic.Field(default=None, alias='expiryDate')
    license_status_type: typing.Literal['expired', 'active', 'free', 'deactivated'] = (
        pydantic.Field(alias='licenseStatusType')
    )
    repair_count: int | None = pydantic.Field(default=None, alias='repairCount')
    order_name: str = pydantic.Field(alias='orderName')
    product_name: str = pydantic.Field(alias='productName')
    product_code: None = pydantic.Field(default=None, alias='productCode')
    product_code_expiry: None = pydantic.Field(default=None, alias='productCodeExpiry')
    product_type_id: typing.Literal['online', 'offline'] = pydantic.Field(alias='productTypeId')
    activation_code: str | None = pydantic.Field(default=None, alias='activationCode')
    activated_first_date: datetime.datetime | None = pydantic.Field(
        default=None, alias='activatedFirstDate'
    )
    activated_last_date: datetime.datetime | None = pydantic.Field(
        default=None, alias='activatedLastDate'
    )
    purchase_period: int | None = pydantic.Field(default=None, alias='purchasePeriod')
    organization_name: str = pydantic.Field(alias='organizationName')
    note: str | None = None
    is_testing_license: bool = pydantic.Field(alias='isTestingLicense')
    license_tag: str = pydantic.Field(alias='licenseTag')
    product_validity_type_id: typing.Literal['lifetime', 'timeLimited', 'undefined'] = (
        pydantic.Field(alias='productValidityTypeId')
    )


class GetProductResponse(pydantic.BaseModel):
    grouped_order_items: list[Product] = pydantic.Field(alias='groupedOrderItems')


class GetLicensesResponse(pydantic.BaseModel):
    licenses: list[License]


class PutLicenseResponse(pydantic.BaseModel):
    pass


@dataclasses.dataclass(frozen=True)
class LicenseProduct:
    name: str
    is_dev: bool

    @staticmethod
    def from_license(license: License):
        return LicenseProduct(name=license.product_name, is_dev=license.is_testing_license)

    @property
    def label(self):
        return ('[DEV] ' if self.is_dev else '') + self.name


@dataclasses.dataclass
class Client:
    base_url: rl.Url
    http_client: httpx.AsyncClient
    api_key: str

    @property
    def _headers(self):
        return {'X-api_key': self.api_key}

    async def _request_with_retry[T](
        self,
        request_name: str,
        method: typing.Literal['get', 'put'],
        path: str,
        response_type: type[T],
        content: pydantic.BaseModel | None = None,
    ) -> T:
        n_try = 20
        errors: list[str] = []
        for _ in range(n_try):
            try:
                response = await self.http_client.request(
                    method=method,
                    url=f'{self.base_url}/{path}',
                    headers=self._headers | {'Content-Type': 'application/json'},
                    content=content.model_dump_json(by_alias=True) if content is not None else None,
                )
                if response.status_code == 200:
                    return pydantic.TypeAdapter(response_type).validate_json(response.content)
                errors.append(f'{method} {response.url} -> {response.status_code} {response.text}')
            except httpx.HTTPError as exc:
                errors.append(repr(exc))

            cnsl.print_red(f'{request_name} failed, retrying ...')
            await asyncio.sleep(random.random())

        raise RuntimeError(f'{request_name} failed {n_try} times, errors: {errors}')

    async def get_products(self):
        return (
            await self._request_with_retry(
                'getting grouped order items',
                'get',
                '/myOrder/groupedOrderItems',
                GetProductResponse,
            )
        ).grouped_order_items

    async def get_product_orders(self, product: Product):
        return await self._request_with_retry(
            'getting orders for product',
            'get',
            f'/myOrder/orderItems?productId={product.product_id}'
            f'&activationType={product.activation_type}'
            f'&purchasePeriod={product.purchase_period}',
            list[Order],
        )

    async def get_licenses(self):
        return (
            await self._request_with_retry(
                'getting licenses',
                'get',
                '/myLicense?pageIndex=0&pageSize=999999',
                GetLicensesResponse,
            )
        ).licenses

    async def update_license(self, license: License):
        await self._request_with_retry(
            'updating license',
            'put',
            '/myLicense/updateLicense',
            PutLicenseResponse,
            content=license,
        )


def is_license_available(license: License, unitech_env: env.UnitechEnv):
    return license.license_status_type == 'free' or (
        license.license_status_type == 'deactivated'
        and not (unitech_env == env.UnitechEnv.LOCAL and not license.is_testing_license)
    )


async def get_product_license_map(client: Client):
    return util.groupby(
        (license for license in await client.get_licenses()), LicenseProduct.from_license
    )


async def choose_license_products(
    product_labels: list[str] | None, client: Client, unitech_env: env.UnitechEnv
):
    product_licenses_map = await get_product_license_map(client)

    def formater(license_product: LicenseProduct):
        available_count = sum(
            is_license_available(license_, unitech_env)
            for license_ in product_licenses_map[license_product]
        )
        return f'{license_product.label} ({available_count} dispo)'

    if product_labels is None:
        cnsl.print_blue('Choisir des types de licence:')
        return await cnsl.print_choose_multiple(
            sorted(product_licenses_map.keys(), key=lambda lp: lp.label),
            prompt='Types de licence: ',
            formater=formater,
            choice_formater=lambda lp: lp.label,
        )

    product_label_licenses_map = {slugify.slugify(lp.label): lp for lp in product_licenses_map}

    license_products: list[LicenseProduct] = []
    for product_label in product_labels:
        if (
            license_product := product_label_licenses_map.get(slugify.slugify(product_label))
        ) is None:
            cnsl.print_red(f'Aucun type de license nommé [hot_pink3]`{product_label}`[/hot_pink3]')
            return None
        license_products.append(license_product)

    return license_products
