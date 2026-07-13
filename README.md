# romq

[![Python](https://img.shields.io/badge/python-3.14+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-WIP-yellow)]()

`romq` is a library and CLI utility for ROM metadata inspection and search.

## Table of contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI](#cli)
  - [Library](#library)
- [License](#license)

## Features

- **Inspect**: Extract metadata from ROM files.
- **Search**: Scan a directory tree for ROMs by metadata (mapper, format, mirroring, etc.).
- **Supported systems**:
    - **NES**: `iNES 1.0`, `iNES 2.0` (partial — bytes 13–15 not parsed yet).
    - Support for other consoles is planned.

## Installation

### Requirements

- Python 3.14+

### Install

Install via `uv`:

```bash
uv add romq
```

Or using `pip`:

```bash
pip install romq
```

## Usage

### CLI

**Inspect a ROM:**
```bash
romq nes inspect roms/rom.nes
```

*Output:*
```
ROM: roms/rom.nes
  Format           iNES 2.0
  Console          NES
  TV System        RP2C02 (NTSC NES)
  Mapper           4
  Submapper        0
  Mirroring        Horizontal
  Trainer          False
  Alternate NT     False
  Battery-backed   False
  PRG ROM          131072
  CHR ROM          131072
  PRG RAM          0
  PRG NVRAM        0
  CHR RAM          0
  CHR NVRAM        0
```

See `romq nes inspect --help` for all available options.

**Search a directory tree with filters:**
```bash/
romq nes search --mapper-id 4 ./roms
```

*Output:*
```
roms/rom.zip
  [iNES 2.0 | RP2C02 (NTSC NES) | Mapper 4 | Horizontal | PRG 131072 | CHR 131072]
roms/rom2.7z
  [iNES 2.0 | RP2C02 (NTSC NES) | Mapper 4 | Horizontal | PRG 262144 | CHR 262144]
ROM matches: 2, Errors: 0
```

See `romq nes search --help` for all available options.

### Library

`romq` is also available as a Python module.

#### Inspect a ROM

```python
import romq

try:
    rom_info = romq.nes.inspect_rom("roms/rom.nes")
    # Or from a archive (ZIP, 7z)
    # romq.nes.inspect_rom("roms/rom.zip")

    print(rom_info.mapper_id)       # 4
    print(rom_info.rom_format)      # RomFormat.INES_20
    print(rom_info.console_type)    # ConsoleType.NES
    # See `romq.nes.RomInfo` for all available fields
except romq.errors.RomqError as error:
    print(f"ROM inspection error: {error}")
except OSError:
    print("System error")
```

#### Search ROMs

```python
import romq

# Find all ROMs in a directory
result = romq.nes.search_roms("/roms")

# Apply any combination of filters to narrow results
result = romq.nes.search_roms(
    "/roms/nes",
    query=romq.nes.SearchQuery(
        mapper_id=4,
        submapper_id=0,
        rom_format=romq.nes.RomFormat.INES_20,
        mirroring=romq.nes.Mirroring.HORIZONTAL,
        console_type=romq.nes.ConsoleType.NES,
        tv_system=romq.nes.TvSystem.NTSC,
        has_battery=True,
        has_trainer=False,
        has_alternate_nt=False,
    )
)

# Use a predicate for complex logic (field filters are ignored if predicate is given)
def custom_filter(metadata: romq.nes.RomMetadata) -> bool:
    return (
        metadata.prg_rom_size > 16384
        and metadata.mapper_id in (1, 4)
        and metadata.tv_system == romq.nes.TvSystem.NTSC
        # See `romq.nes.RomMetadata` for all available fields
    )

result = romq.nes.search_roms("/roms", predicate=custom_filter)

# results.matches contains successful matches
for match in result.matches:
    print(f"{match.filepath}: mapper_id={match.metadata.mapper_id}")

# results.failures contains details about files that couldn't be parsed
for failure in result.failures:
    print(f"Error: {failure.filepath}:{failure.error}")
```

## License

MIT
