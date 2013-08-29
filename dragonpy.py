"""
=== Dragon 32 emulator in Python

Some links:

 * http://www.burgins.com/m6809.html
 * http://dragondata.worldofdragon.org/Publications/inside-dragon.htm
 * http://mamedev.org/source/src/mess/drivers/dragon.c.html
 * http://mamedev.org/source/src/mess/machine/dragon.c.html
 * http://koti.mbnet.fi/~atjs/mc6809/
 * http://www.colorcomputerarchive.com/coco/Documents/Manuals/Programming/6502-6809Translator%20%28Computer%20Systems%20Consultants%29.pdf

Dragon 32 resources:

 * Forum: http://archive.worldofdragon.org/phpBB3/index.php
 * Wiki: http://archive.worldofdragon.org/index.php?title=Main_Page

Dragon 32 Emulator that works:

 * http://archive.worldofdragon.org/index.php?title=Emulation
"""

from applepy import get_options, Display
from Dragon32.dragon32config import Dragon32Config
from generic.base_machine import BaseMachine


class Dragon32(BaseMachine):
    pass

if __name__ == "__main__":
    cfg = Dragon32Config()

    options = get_options()
    display = Display()
    speaker = None
    cassette = None

    apple = Dragon32(cfg, options, display, speaker, cassette)
    apple.run()
