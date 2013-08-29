import sys
import socket
import struct

class ROMBase(object):

    def __init__(self, start, size):
        self.start = start
        self.end = start + size - 1
        self._mem = [0x00] * size

    def load(self, address, data):
        for offset, datum in enumerate(data):
            self._mem[address - self.start + offset] = datum

    def load_file(self, address, filename):
        with open(filename, "rb") as f:
            for offset, datum in enumerate(f.read()):
                self._mem[address - self.start + offset] = ord(datum)

    def read_byte(self, address):
        assert self.start <= address <= self.end
        return self._mem[address - self.start]


class RAMBase(ROMBase):

    def write_byte(self, address, value):
        self._mem[address] = value


class MemoryBase(object):
    def __init__(self, cfg, bus, ram_class, rom_class, options=None, use_bus=True):
        self.cfg = cfg
        if use_bus:
            self.bus = bus
        self.use_bus = use_bus

        self.rom = rom_class(self.cfg.ROM_START, self.cfg.ROM_SIZE)

        if options:
            self.rom.load_file(self.cfg.ROM_START, options.rom)

        self.ram = ram_class(self.cfg.RAM_START, self.cfg.RAM_SIZE)

        if options and options.ram:
            self.ram.load_file(self.cfg.RAM_START, options.ram)

    def load(self, address, data):
        if address < self.cfg.RAM_SIZE:
            self.ram.load(address, data)

    def read_byte(self, cycle, address):
        if address < self.cfg.RAM_SIZE:
            return self.ram.read_byte(address)
        elif address < self.cfg.ROM_START:
            return self.bus_read(cycle, address)
        else:
            return self.rom.read_byte(address)

    def read_word(self, cycle, address):
        return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address + 1) << 8)

    def bus_read(self, cycle, address):
        if not self.use_bus:
            return 0
        op = struct.pack("<IBHB", cycle, 0, address, 0)
        try:
            self.bus.send(op)
            b = self.bus.recv(1)
            if len(b) == 0:
                sys.exit(0)
            return ord(b)
        except socket.error:
            sys.exit(0)

    def bus_write(self, cycle, address, value):
        if not self.use_bus:
            return
        op = struct.pack("<IBHB", cycle, 1, address, value)
        try:
            self.bus.send(op)
        except IOError:
            sys.exit(0)
