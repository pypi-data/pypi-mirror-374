import argparse
import pathlib
import sys
import typing


def update_file(new_version: str, path: pathlib.Path, var_name: str):
    wrote_version = False
    new_lines: list[str] = []
    for line in path.read_text().splitlines():
        if not wrote_version and line.startswith(f'{var_name} = '):
            new_lines.append(f"{var_name} = '{new_version}'")
            wrote_version = True
        else:
            new_lines.append(line)

    assert wrote_version
    path.write_text('\n'.join(new_lines) + '\n')


def get_base_path():
    return pathlib.Path(__file__).parent.parent


def get_pyproject_path():
    return get_base_path() / 'pyproject.toml'


def get_package_init_path():
    return get_base_path() / 'unico_device_setuper' / '__init__.py'


def update_files(new_version: str):
    update_file(new_version, get_pyproject_path(), 'version')
    update_file(new_version, get_package_init_path(), '__version__')


def get_current_version():
    locals: dict[str, typing.Any] = {}
    exec(get_package_init_path().read_text(), {}, locals)  # noqa: S102
    version = locals.get('__version__')
    assert isinstance(version, str)
    return version


type IncrKind = typing.Literal['major', 'minor', 'patch']


def increment(version: str, kind: IncrKind):
    major, minor, patch = map(int, version.split('.'))
    match kind:
        case 'major':
            major += 1
            minor = 0
            patch = 0
        case 'minor':
            minor += 1
            patch = 0
        case 'patch':
            patch += 1
    return f'{major}.{minor}.{patch}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'increment', choices=['major', 'minor', 'patch'], default='minor', nargs='?'
    )
    incr_kind: IncrKind = parser.parse_args(sys.argv[1:]).increment
    current_version = get_current_version()
    new_version = increment(current_version, incr_kind)
    update_files(new_version)
    print(new_version)


if __name__ == '__main__':
    main()
