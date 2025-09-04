import asyncio

import typer

from unico_device_setuper.lib import openapi

APP = typer.Typer(pretty_exceptions_enable=False)


@APP.command()
def sync_main(base_url: str = 'http://localhost:3000'):
    asyncio.run(openapi.generate_api(base_url + '/doc/openapi.json', lib_name='unitech'))


if __name__ == '__main__':
    APP()
