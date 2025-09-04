import asyncio
import concurrent.futures
import enum
import json
import os
import pathlib
import sys
import typing
import warnings

import pydantic
import slugify

from unico_device_setuper.lib import aio, cnsl, util

if typing.TYPE_CHECKING:
    from openpyxl import cell
    from openpyxl.worksheet import _read_only, worksheet


class Line[T](pydantic.BaseModel):
    program: T | None = None
    vehicle_profile: T | None = None
    depot: T | None = None
    div: T | None = None
    letter1: T | None = None
    code1: T | None = None
    letter2: T | None = None
    code2: T | None = None
    outlet1: T | None = None
    outlet2: T | None = None


class Depot(enum.Enum):
    IVH = enum.auto()
    ISSY = enum.auto()
    URBASER_2 = enum.auto()
    IB = enum.auto()
    CLICHY = enum.auto()
    ROM = enum.auto()
    AUBER = enum.auto()
    SAMSIC = enum.auto()
    URBASER_3 = enum.auto()


class Outlet(enum.Enum):
    IVRY_PARIS_13 = enum.auto()
    NONE = enum.auto()
    ISSEANE_OM = enum.auto()
    IVRY_DERICHEBOURG_MM = enum.auto()
    PARIS_15_MM = enum.auto()
    ROMAINVILLE_OM_D = enum.auto()
    SMM = enum.auto()
    IVRY_OM_D = enum.auto()
    ST_OUEN_OM_D = enum.auto()
    PARIS_17_MM = enum.auto()
    ST_DENIS = enum.auto()
    ROMAINVILLE_MM_D = enum.auto()
    MARDI_MATIN_REAFFECTE_MARDI_APRES_MIDI = enum.auto()
    ROMAINVILLE_OM = enum.auto()
    ROMAINVILLE_MM = enum.auto()


class VehicleProfile(enum.Enum):
    VE = enum.auto()
    VM = enum.auto()
    VL = enum.auto()
    VXL = enum.auto()
    BC3 = enum.auto()
    LA4 = enum.auto()
    BA5 = enum.auto()
    LA7 = enum.auto()
    BLM19 = enum.auto()
    GRM = enum.auto()
    LA5 = enum.auto()


class Record(pydantic.BaseModel):
    letter: str
    code: str
    depot: Depot | None = None
    outlet: Outlet
    vehicle_profile: VehicleProfile
    source_file: str
    source_line: int


def update_indices(indices: Line[int], value: str, index: int):  # noqa: C901
    match value:
        case 'programme':
            indices.program = index
        case 'engin':
            indices.vehicle_profile = index
        case 'garage':
            indices.depot = index
        case 'div':
            indices.div = index
        case 'lettre_itineraire':
            if indices.letter1 is None:
                indices.letter1 = index
            elif indices.letter2 is None:
                indices.letter2 = index
        case 'itineraire_1':
            indices.code1 = index
        case 'itineraire_2':
            indices.code2 = index
        case 'exutoire_itineraire_1':
            indices.outlet1 = index
        case 'exutoire_itineraire_2':
            indices.outlet2 = index
        case _:
            return


def get_line_indices(cells: tuple['cell.Cell', ...]):
    indices: Line[int] = Line()
    for i, c in enumerate(cells):
        update_indices(indices, slugify.slugify(str(c.value), separator='_'), i)

    for k, v in indices.model_dump().items():
        if v is None:
            cnsl.print_red(f'Cannot find column {k}')

    return indices


def get_line(indices: Line[int], cells: tuple['cell.Cell', ...]):
    line: Line[str] = Line(
        **{
            k: slugify.slugify(str(value), separator='_')
            if (value := typing.cast('typing.Any', cells[i]).value) is not None
            else None
            for (k, i) in indices.model_dump().items()
            if i is not None
        }
    )
    return line


def read_worksheet(ws: 'worksheet.Worksheet | _read_only.ReadOnlyWorksheet', *, name: str):
    records: list[Record] = []

    rows: list[tuple[cell.Cell, ...]] = []
    try:
        for row in ws.iter_rows():
            rows.append(row)  # pyright: ignore[reportArgumentType] # noqa: PERF402 handles the case when we crash in the middle
    except Exception:  # noqa: BLE001
        cnsl.warn('Could not read some lines of file')

    if len(rows) < 5:
        cnsl.warn('Not enough lines in file')
        return records

    indices = get_line_indices(rows[4])

    for i, cells in enumerate(rows):
        if i <= 4:
            continue
        line = get_line(indices, cells)

        if line.vehicle_profile is None or line.depot is None:
            cnsl.warn(f'Skipping line {i}')
            continue

        vehicle_profile = VehicleProfile[line.vehicle_profile.upper()]
        depot = Depot[line.depot.upper()]

        if line.outlet1 and line.letter1 and line.code1:
            records.append(
                Record(
                    letter=line.letter1,
                    code=line.code1.replace('MM', 'PE'),
                    depot=depot,
                    outlet=Outlet[line.outlet1.upper()],
                    vehicle_profile=vehicle_profile,
                    source_file=name,
                    source_line=i + 1,
                )
            )
        else:
            cnsl.warn(f'Skipping first round of line {i + 1}')

        if line.outlet2 and line.letter2 and line.code2:
            records.append(
                Record(
                    letter=line.letter2,
                    code=line.code2.replace('MM', 'PE'),
                    depot=depot,
                    outlet=Outlet[line.outlet2.upper()],
                    vehicle_profile=vehicle_profile,
                    source_file=name,
                    source_line=i + 1,
                )
            )
        else:
            cnsl.warn(f'Skipping second round of line {i + 1}')

    return records


def display_records(records: list[Record]):
    json.dump(
        {
            letter: {
                code: list(
                    {
                        (r.vehicle_profile.name, r.depot.name if r.depot else '', r.outlet.name)
                        for r in letter_code_record
                    }
                )
                for (code, letter_code_record) in util.groupby(
                    letter_record, key=lambda r: r.code
                ).items()
            }
            for (letter, letter_record) in util.groupby(records, lambda r: r.letter).items()
        },
        sys.stdout,
    )
    cnsl.print()


def handle_file(path: pathlib.Path):
    from openpyxl.chartsheet import chartsheet
    from openpyxl.reader import excel
    from openpyxl.worksheet import _write_only

    warnings.simplefilter(action='ignore')
    cnsl.print_blue(f'Handling {path.name}')
    with path.open(mode='rb') as f:
        try:
            ws = excel.load_workbook(
                f, read_only=True, keep_vba=False, data_only=True, keep_links=False
            )['base']
            assert not isinstance(ws, chartsheet.Chartsheet)
            assert not isinstance(ws, _write_only.WriteOnlyWorksheet)
        except Exception:  # noqa: BLE001
            cnsl.warn('Skipping file')
            return list[Record]()

        return read_worksheet(ws, name=path.name)


async def compile_(paths: list[pathlib.Path]):
    records = list[Record]()
    loop = asyncio.get_running_loop()

    with concurrent.futures.ProcessPoolExecutor() as executor:

        async def async_handle_file(path: pathlib.Path):
            return await loop.run_in_executor(executor, handle_file, path)

        async for file_records in aio.iter_unordered(
            (async_handle_file(path) for path in paths), max_concurrency=os.cpu_count() or 1
        ):
            records.extend(file_records)

    display_records(records)
