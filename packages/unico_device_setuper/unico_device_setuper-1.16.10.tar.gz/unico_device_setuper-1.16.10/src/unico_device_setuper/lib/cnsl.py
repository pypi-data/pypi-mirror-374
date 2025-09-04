import asyncio
import builtins
import contextlib
import functools
import sys
import threading
import time
import typing

import rich

from unico_device_setuper.lib import util


def _colored_print(s: str, color: str, end: str | None = None):
    return rich.print(f'[{color}]{s}[/{color}]', end=end if end is not None else '\n')


def print(s: str = '', end: str | None = None):
    _colored_print(s, 'white', end)


def print_pink(s: str = '', end: str | None = None):
    _colored_print(s, 'hot_pink3', end)


def warn(s: str = '', end: str | None = None):
    _colored_print(f'⚠️  {s}', 'orange', end)


def print_gray(s: str = '', end: str | None = None):
    _colored_print(s, 'bright_black', end)


def print_red(s: str, end: str | None = None):
    _colored_print(s, 'red', end)


def print_blue(s: str, end: str | None = None):
    _colored_print(s, 'blue', end)


def print_cyan(s: str, end: str | None = None):
    _colored_print(s, 'cyan', end)


def print_greeen(s: str, end: str | None = None):
    _colored_print(s, 'green', end)


async def input(prompt: str):
    rich.print(f'[bold cyan] > {prompt}[/]', end='')
    line: list[str | None] = [None]

    def target():
        line[0] = builtins.input().strip()

    thread = threading.Thread(daemon=True, target=target)
    thread.start()

    while True:
        res = line[0]
        if res is not None:
            thread.join()
            return res
        try:
            await asyncio.sleep(0.1)
        except asyncio.exceptions.CancelledError:
            sys.stdout.write('\n')
            sys.exit()


async def choose[T](items: list[T], *, prompt: str, allow_multiple: bool = False) -> list[T]:
    if not allow_multiple:
        if len(items) == 0:
            raise RuntimeError('Cannot choose between 0 elements')
        if len(items) == 1:
            return [items[0]]
    elif len(items) == 0:
        return []

    while True:
        user_input = await input(prompt)

        if allow_multiple:
            inputs = user_input.replace(',', ' ').replace(';', '').replace('-', '').split()
        else:
            inputs = [user_input]

        indices = None
        with contextlib.suppress(ValueError):
            indices = [int(input) for input in inputs]

        if indices is not None and all(0 <= index < len(items) for index in indices):
            return [items[index] for index in indices]

        print_red('Choix invalide')


def print_items[T](
    items: list[T],
    *,
    formater: typing.Callable[[T], str],
    headers: list[str] | None,
    console: 'rich.console.Console',
):
    max_index = len(str(len(items) - 1))
    if headers is not None:
        for header in headers:
            rich.print(f" {'':>{max_index}}   {header}")
    for i, item in enumerate(items):
        console.print(f' [bold cyan]{i:>{max_index}}[/] - {formater(item)}')


async def print_choose[T](
    items: list[T],
    prompt: str,
    *,
    formater: typing.Callable[[T], str] | None = None,
    choice_formater: typing.Callable[[T], str] | None = None,
    headers: list[str] | None = None,
) -> T:
    formater = formater or str
    choice_formater = choice_formater or formater

    console = rich.console.Console(highlight=False)
    print_items(items, formater=formater, headers=headers, console=console)
    choices = await choose(items, prompt=prompt, allow_multiple=False)
    assert len(choices) == 1
    choice = choices[0]
    console.print(f'Vous avez choisi {choice_formater(choice)}', style='blue')
    return choice


async def print_choose_multiple[T](
    items: list[T],
    prompt: str,
    *,
    formater: typing.Callable[[T], str] | None = None,
    choice_formater: typing.Callable[[T], str] | None = None,
    headers: list[str] | None = None,
) -> list[T]:
    formater = formater or str
    choice_formater = choice_formater or formater

    console = rich.console.Console(highlight=False)
    print_items(items, formater=formater, headers=headers, console=console)
    choices = await choose(items, prompt=prompt, allow_multiple=True)

    if len(choices) == 0:
        console.print("Vous n'avez choisi aucun élément", style='blue')
    else:
        console.print('Vous avez choisi:', style='blue')
        for choice in choices:
            console.print(f'    - {choice_formater(choice)}', style='blue')

    return choices


@contextlib.contextmanager
def step(action: str):
    t0 = time.perf_counter()
    print(action + ' ... ', end='')
    try:
        yield
        print_greeen('ok', end='')
    except:
        print_red('error', end='')
        raise
    finally:
        print_gray(f' [{util.format_timdelta_s(time.perf_counter() - t0)}]')


def command(action: str, finished: str):
    def decorator[**P](
        f: typing.Callable[P, typing.Awaitable[bool]],
    ) -> typing.Callable[P, typing.Awaitable[bool]]:
        @functools.wraps(f)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> bool:
            print(f'\n=== {action} ===')
            t0 = time.perf_counter()
            r = await f(*args, **kwargs)
            if r:
                print_greeen(f' -> {finished}!', end='')
                print_gray(f' [{util.format_timdelta_s(time.perf_counter() - t0)}]')
            return r

        return wrapped

    return decorator


def device_display(
    serial: str, message: str, style: typing.Literal['info', 'error'], note: str | None = None
):
    match style:
        case 'info':
            printer = print_cyan
        case 'error':
            printer = print_red

    printer(f'[Appareil {serial}] {message}', end=' ' if note is not None else None)
    if note is not None:
        print_gray(note)


async def confirm(prompt: str):
    return (await input(f'{prompt} (y/N) ')).lower() != 'y'
