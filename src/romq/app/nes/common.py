import functools

import romq.app.io as romq_io

open_rom = functools.partial(romq_io.open_rom, rom_extension=".nes")
