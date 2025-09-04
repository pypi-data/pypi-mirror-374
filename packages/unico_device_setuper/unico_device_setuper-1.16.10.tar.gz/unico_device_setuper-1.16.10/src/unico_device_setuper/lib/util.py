import asyncio
import collections
import contextlib
import dataclasses
import datetime
import hashlib
import os
import pathlib
import shutil
import subprocess
import time
import types
import typing
import uuid

APP_NAME = 'com.unico.dev.device_setuper'

### Path stuff


def module_path(module: types.ModuleType):
    module_file = module.__file__
    assert module_file is not None
    return pathlib.Path(module_file).parent.absolute()


@contextlib.contextmanager
def temporary_dir(base: pathlib.Path):
    dir_path = base / str(uuid.uuid4())
    dir_path.mkdir(exist_ok=True, parents=True)
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)


### Subprocess stuff


async def _stream_line_reader(stream: asyncio.StreamReader | None):
    if stream is None:
        return

    while True:
        line = await stream.readline()
        if len(line) == 0:
            break

        yield line.decode()


async def _read_loop(stream: asyncio.StreamReader | None, storage: list[str]):
    async for line in _stream_line_reader(stream):
        storage.append(line)


@dataclasses.dataclass
class SubprocessError(Exception):
    command: str
    return_code: int
    stdout: str
    stderr: str

    def __post_init__(self):
        self.args = tuple(f'{k}: {v}' for k, v in dataclasses.asdict(self).items())


async def exec_proc(exe: pathlib.Path, *args: str):
    process = await asyncio.subprocess.create_subprocess_exec(
        exe, *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    stderr_reader = asyncio.get_event_loop().create_task(_read_loop(process.stderr, stderr_lines))
    killed = False

    line_generator = _stream_line_reader(process.stdout)
    try:
        async for line in line_generator:
            stdout_lines.append(line)
            yield line.rstrip('\n')
    except GeneratorExit:
        await line_generator.aclose()
        killed = True
        process.kill()

    (return_code, _) = await asyncio.gather(process.wait(), stderr_reader)

    stdout = ''.join(stdout_lines)
    stderr = ''.join(stderr_lines)

    if not killed and return_code != 0:
        raise SubprocessError(
            command=f'{exe.name} {' '.join(args)}',
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
        )


def is_file(path: pathlib.Path):
    return path.exists() and path.is_file()


def is_executable(path: pathlib.Path):
    return is_file(path) and os.access(path, os.X_OK)


### Other


def groupby[T, K: typing.Hashable](
    values: typing.Iterable[T], key: typing.Callable[[T], K]
) -> typing.Mapping[K, typing.Sequence[T]]:
    key_values_map: dict[K, list[T]] = collections.defaultdict(list)
    for value in values:
        key_values_map[key(value)].append(value)
    return key_values_map


async def wrap_async[T](t: T) -> T:
    return t


def now():
    return datetime.datetime.now(tz=datetime.UTC)


def make_archive(source: pathlib.Path, destination: pathlib.Path):
    shutil.make_archive(
        base_name=destination.stem,
        format=destination.suffix[1:],
        root_dir=source.parent,
        base_dir=source.name,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(destination.name, destination)


def parse_int(s: str):
    with contextlib.suppress(ValueError):
        return int(s)
    return None


def no_none[T](col: typing.Collection[T | None]) -> typing.TypeGuard[typing.Collection[T]]:
    return all(e is not None for e in col)


def explore[T](base: typing.Iterable[T], explorer: typing.Callable[[T], typing.Iterable[T]]):
    explored = set[T]()
    to_explore = set(base)

    while len(to_explore) > 0:
        current = to_explore.pop()
        if current in explored:
            continue
        explored.add(current)
        yield current
        to_explore.update(explorer(current))


def safe_unlink(path: pathlib.Path):
    with contextlib.suppress(OSError):
        path.unlink(missing_ok=True)


def dump_iso_datetime(dt: datetime.datetime):
    return dt.astimezone(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def load_iso_datetime(s: str):
    return datetime.datetime.fromisoformat(s)


class SupportsRead[T: str | bytes](typing.Protocol):
    def read(self, n: int = ..., /) -> T: ...


class SupportsWrite[T: str | bytes](typing.Protocol):
    def write(self, s: T, /) -> int: ...


_TIMEDELTA_PREFIXES_RATIOS = [
    (60 * 60 * 24 * 7, 'w'),
    (60 * 60 * 24, 'd'),
    (60 * 60, 'h'),
    (60, 'm'),
    (1, 's'),
]


def format_timdelta_s(seconds: float):
    if seconds < 1e-3:
        return '0s'

    if seconds < 1:
        return f'{1000 * seconds:0.0f} ms'

    if seconds < 60:
        return f'{seconds:1.1f}s'

    seconds = round(seconds)
    parts: list[str] = []
    for part_seconds, part_name in _TIMEDELTA_PREFIXES_RATIOS:
        count = seconds // part_seconds
        if count > 0:
            seconds -= count * part_seconds
            parts.append(f'{count}{part_name}')

    return ' '.join(parts[:2])


def file_part_generator(file: pathlib.Path, part_size_bytes: int):
    with file.open('rb') as f:
        while len(content := f.read(part_size_bytes)) > 0:
            yield content


def get_local_checksum(path: pathlib.Path):
    h = hashlib.md5()
    for part in file_part_generator(path, part_size_bytes=2**20):
        h.update(part)
    return h.hexdigest()


@dataclasses.dataclass
class Timer:
    _t0: float = dataclasses.field(init=False, default=0.0)
    _t1: float | None = dataclasses.field(init=False, default=None)

    @property
    def duration(self):
        end = time.perf_counter() if self._t1 is None else self._t1
        return datetime.timedelta(seconds=end - self._t0)

    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *args: object):
        self._t1 = time.perf_counter()


async def sleep(td: datetime.timedelta):
    await asyncio.sleep(td.total_seconds())


@contextlib.asynccontextmanager
async def ensure_min_duration(duration: datetime.timedelta):
    with Timer() as timer:
        yield
    if timer.duration < duration:
        await sleep(duration - timer.duration)
