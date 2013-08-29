
"""
    TODO: Just a copy of apple2memory.py yet :(
"""

from generic.base_memory import MemoryBase, ROMBase, RAMBase

class ROM(ROMBase):
    pass

class RAM(RAMBase):
    pass

class Memory(MemoryBase):

    def read_word_bug(self, cycle, address):
        if address % 0x100 == 0xFF:
            return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address & 0xFF00) << 8)
        else:
            return self.read_word(cycle, address)

    def write_byte(self, cycle, address, value):
        if address < self.cfg.RAM_SIZE:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(cycle, address, value)
