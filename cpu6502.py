# ApplePy - an Apple ][ emulator in Python
# James Tauber / http://jtauber.com/
# originally written 2001, updated 2011


import BaseHTTPServer
import json
import re
import select
import socket
import struct
import sys


bus = None  # socket for bus I/O


def signed(x):
    if x > 0x7F:
        x = x - 0x100
    return x


class ROM:

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


class RAM(ROM):

    def write_byte(self, address, value):
        self._mem[address] = value


class Memory:

    def __init__(self, options=None, use_bus=True):
        self.use_bus = use_bus
        self.rom = ROM(0xD000, 0x3000)

        if options:
            self.rom.load_file(0xD000, options.rom)

        self.ram = RAM(0x0000, 0xC000)

        if options and options.ram:
            self.ram.load_file(0x0000, options.ram)

    def load(self, address, data):
        if address < 0xC000:
            self.ram.load(address, data)

    def read_byte(self, cycle, address):
        if address < 0xC000:
            return self.ram.read_byte(address)
        elif address < 0xD000:
            return self.bus_read(cycle, address)
        else:
            return self.rom.read_byte(address)

    def read_word(self, cycle, address):
        return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address + 1) << 8)

    def read_word_bug(self, cycle, address):
        if address % 0x100 == 0xFF:
            return self.read_byte(cycle, address) + (self.read_byte(cycle + 1, address & 0xFF00) << 8)
        else:
            return self.read_word(cycle, address)

    def write_byte(self, cycle, address, value):
        if address < 0xC000:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 or 0x2000 <= address < 0x5FFF:
            self.bus_write(cycle, address, value)

    def bus_read(self, cycle, address):
        if not self.use_bus:
            return 0
        op = struct.pack("<IBHB", cycle, 0, address, 0)
        try:
            bus.send(op)
            b = bus.recv(1)
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
            bus.send(op)
        except IOError:
            sys.exit(0)


class Disassemble:
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory

        self.setup_ops()

    def setup_ops(self):
        self.ops = [(1, "???")] * 0x100
        self.ops[0x00] = (1, "BRK", )
        self.ops[0x01] = (2, "ORA", self.indirect_x_mode)
        self.ops[0x05] = (2, "ORA", self.zero_page_mode)
        self.ops[0x06] = (2, "ASL", self.zero_page_mode)
        self.ops[0x08] = (1, "PHP", )
        self.ops[0x09] = (2, "ORA", self.immediate_mode)
        self.ops[0x0A] = (1, "ASL", )
        self.ops[0x0D] = (3, "ORA", self.absolute_mode)
        self.ops[0x0E] = (3, "ASL", self.absolute_mode)
        self.ops[0x10] = (2, "BPL", self.relative_mode)
        self.ops[0x11] = (2, "ORA", self.indirect_y_mode)
        self.ops[0x15] = (2, "ORA", self.zero_page_x_mode)
        self.ops[0x16] = (2, "ASL", self.zero_page_x_mode)
        self.ops[0x18] = (1, "CLC", )
        self.ops[0x19] = (3, "ORA", self.absolute_y_mode)
        self.ops[0x1D] = (3, "ORA", self.absolute_x_mode)
        self.ops[0x1E] = (3, "ASL", self.absolute_x_mode)
        self.ops[0x20] = (3, "JSR", self.absolute_mode)
        self.ops[0x21] = (2, "AND", self.indirect_x_mode)
        self.ops[0x24] = (2, "BIT", self.zero_page_mode)
        self.ops[0x25] = (2, "AND", self.zero_page_mode)
        self.ops[0x26] = (2, "ROL", self.zero_page_mode)
        self.ops[0x28] = (1, "PLP", )
        self.ops[0x29] = (2, "AND", self.immediate_mode)
        self.ops[0x2A] = (1, "ROL", )
        self.ops[0x2C] = (3, "BIT", self.absolute_mode)
        self.ops[0x2D] = (3, "AND", self.absolute_mode)
        self.ops[0x2E] = (3, "ROL", self.absolute_mode)
        self.ops[0x30] = (2, "BMI", self.relative_mode)
        self.ops[0x31] = (2, "AND", self.indirect_y_mode)
        self.ops[0x35] = (2, "AND", self.zero_page_x_mode)
        self.ops[0x36] = (2, "ROL", self.zero_page_x_mode)
        self.ops[0x38] = (1, "SEC", )
        self.ops[0x39] = (3, "AND", self.absolute_y_mode)
        self.ops[0x3D] = (3, "AND", self.absolute_x_mode)
        self.ops[0x3E] = (3, "ROL", self.absolute_x_mode)
        self.ops[0x40] = (1, "RTI", )
        self.ops[0x41] = (2, "EOR", self.indirect_x_mode)
        self.ops[0x45] = (2, "EOR", self.zero_page_mode)
        self.ops[0x46] = (2, "LSR", self.zero_page_mode)
        self.ops[0x48] = (1, "PHA", )
        self.ops[0x49] = (2, "EOR", self.immediate_mode)
        self.ops[0x4A] = (1, "LSR", )
        self.ops[0x4C] = (3, "JMP", self.absolute_mode)
        self.ops[0x4D] = (3, "EOR", self.absolute_mode)
        self.ops[0x4E] = (3, "LSR", self.absolute_mode)
        self.ops[0x50] = (2, "BVC", self.relative_mode)
        self.ops[0x51] = (2, "EOR", self.indirect_y_mode)
        self.ops[0x55] = (2, "EOR", self.zero_page_x_mode)
        self.ops[0x56] = (2, "LSR", self.zero_page_x_mode)
        self.ops[0x58] = (1, "CLI", )
        self.ops[0x59] = (3, "EOR", self.absolute_y_mode)
        self.ops[0x5D] = (3, "EOR", self.absolute_x_mode)
        self.ops[0x5E] = (3, "LSR", self.absolute_x_mode)
        self.ops[0x60] = (1, "RTS", )
        self.ops[0x61] = (2, "ADC", self.indirect_x_mode)
        self.ops[0x65] = (2, "ADC", self.zero_page_mode)
        self.ops[0x66] = (2, "ROR", self.zero_page_mode)
        self.ops[0x68] = (1, "PLA", )
        self.ops[0x69] = (2, "ADC", self.immediate_mode)
        self.ops[0x6A] = (1, "ROR", )
        self.ops[0x6C] = (3, "JMP", self.indirect_mode)
        self.ops[0x6D] = (3, "ADC", self.absolute_mode)
        self.ops[0x6E] = (3, "ROR", self.absolute_mode)
        self.ops[0x70] = (2, "BVS", self.relative_mode)
        self.ops[0x71] = (2, "ADC", self.indirect_y_mode)
        self.ops[0x75] = (2, "ADC", self.zero_page_x_mode)
        self.ops[0x76] = (2, "ROR", self.zero_page_x_mode)
        self.ops[0x78] = (1, "SEI", )
        self.ops[0x79] = (3, "ADC", self.absolute_y_mode)
        self.ops[0x7D] = (3, "ADC", self.absolute_x_mode)
        self.ops[0x7E] = (3, "ROR", self.absolute_x_mode)
        self.ops[0x81] = (2, "STA", self.indirect_x_mode)
        self.ops[0x84] = (2, "STY", self.zero_page_mode)
        self.ops[0x85] = (2, "STA", self.zero_page_mode)
        self.ops[0x86] = (2, "STX", self.zero_page_mode)
        self.ops[0x88] = (1, "DEY", )
        self.ops[0x8A] = (1, "TXA", )
        self.ops[0x8C] = (3, "STY", self.absolute_mode)
        self.ops[0x8D] = (3, "STA", self.absolute_mode)
        self.ops[0x8E] = (3, "STX", self.absolute_mode)
        self.ops[0x90] = (2, "BCC", self.relative_mode)
        self.ops[0x91] = (2, "STA", self.indirect_y_mode)
        self.ops[0x94] = (2, "STY", self.zero_page_x_mode)
        self.ops[0x95] = (2, "STA", self.zero_page_x_mode)
        self.ops[0x96] = (2, "STX", self.zero_page_y_mode)
        self.ops[0x98] = (1, "TYA", )
        self.ops[0x99] = (3, "STA", self.absolute_y_mode)
        self.ops[0x9A] = (1, "TXS", )
        self.ops[0x9D] = (3, "STA", self.absolute_x_mode)
        self.ops[0xA0] = (2, "LDY", self.immediate_mode)
        self.ops[0xA1] = (2, "LDA", self.indirect_x_mode)
        self.ops[0xA2] = (2, "LDX", self.immediate_mode)
        self.ops[0xA4] = (2, "LDY", self.zero_page_mode)
        self.ops[0xA5] = (2, "LDA", self.zero_page_mode)
        self.ops[0xA6] = (2, "LDX", self.zero_page_mode)
        self.ops[0xA8] = (1, "TAY", )
        self.ops[0xA9] = (2, "LDA", self.immediate_mode)
        self.ops[0xAA] = (1, "TAX", )
        self.ops[0xAC] = (3, "LDY", self.absolute_mode)
        self.ops[0xAD] = (3, "LDA", self.absolute_mode)
        self.ops[0xAE] = (3, "LDX", self.absolute_mode)
        self.ops[0xB0] = (2, "BCS", self.relative_mode)
        self.ops[0xB1] = (2, "LDA", self.indirect_y_mode)
        self.ops[0xB4] = (2, "LDY", self.zero_page_x_mode)
        self.ops[0xB5] = (2, "LDA", self.zero_page_x_mode)
        self.ops[0xB6] = (2, "LDX", self.zero_page_y_mode)
        self.ops[0xB8] = (1, "CLV", )
        self.ops[0xB9] = (3, "LDA", self.absolute_y_mode)
        self.ops[0xBA] = (1, "TSX", )
        self.ops[0xBC] = (3, "LDY", self.absolute_x_mode)
        self.ops[0xBD] = (3, "LDA", self.absolute_x_mode)
        self.ops[0xBE] = (3, "LDX", self.absolute_y_mode)
        self.ops[0xC0] = (2, "CPY", self.immediate_mode)
        self.ops[0xC1] = (2, "CMP", self.indirect_x_mode)
        self.ops[0xC4] = (2, "CPY", self.zero_page_mode)
        self.ops[0xC5] = (2, "CMP", self.zero_page_mode)
        self.ops[0xC6] = (2, "DEC", self.zero_page_mode)
        self.ops[0xC8] = (1, "INY", )
        self.ops[0xC9] = (2, "CMP", self.immediate_mode)
        self.ops[0xCA] = (1, "DEX", )
        self.ops[0xCC] = (3, "CPY", self.absolute_mode)
        self.ops[0xCD] = (3, "CMP", self.absolute_mode)
        self.ops[0xCE] = (3, "DEC", self.absolute_mode)
        self.ops[0xD0] = (2, "BNE", self.relative_mode)
        self.ops[0xD1] = (2, "CMP", self.indirect_y_mode)
        self.ops[0xD5] = (2, "CMP", self.zero_page_x_mode)
        self.ops[0xD6] = (2, "DEC", self.zero_page_x_mode)
        self.ops[0xD8] = (1, "CLD", )
        self.ops[0xD9] = (3, "CMP", self.absolute_y_mode)
        self.ops[0xDD] = (3, "CMP", self.absolute_x_mode)
        self.ops[0xDE] = (3, "DEC", self.absolute_x_mode)
        self.ops[0xE0] = (2, "CPX", self.immediate_mode)
        self.ops[0xE1] = (2, "SBC", self.indirect_x_mode)
        self.ops[0xE4] = (2, "CPX", self.zero_page_mode)
        self.ops[0xE5] = (2, "SBC", self.zero_page_mode)
        self.ops[0xE6] = (2, "INC", self.zero_page_mode)
        self.ops[0xE8] = (1, "INX", )
        self.ops[0xE9] = (2, "SBC", self.immediate_mode)
        self.ops[0xEA] = (1, "NOP", )
        self.ops[0xEC] = (3, "CPX", self.absolute_mode)
        self.ops[0xED] = (3, "SBC", self.absolute_mode)
        self.ops[0xEE] = (3, "INC", self.absolute_mode)
        self.ops[0xF0] = (2, "BEQ", self.relative_mode)
        self.ops[0xF1] = (2, "SBC", self.indirect_y_mode)
        self.ops[0xF5] = (2, "SBC", self.zero_page_x_mode)
        self.ops[0xF6] = (2, "INC", self.zero_page_x_mode)
        self.ops[0xF8] = (1, "SED", )
        self.ops[0xF9] = (3, "SBC", self.absolute_y_mode)
        self.ops[0xFD] = (3, "SBC", self.absolute_x_mode)
        self.ops[0xFE] = (3, "INC", self.absolute_x_mode)

    def absolute_mode(self, pc):
        a = self.cpu.read_word(pc + 1)
        return {
            "operand": "$%04X" % a,
            "memory": [a, 2, self.cpu.read_word(a)],
        }

    def absolute_x_mode(self, pc):
        a = self.cpu.read_word(pc + 1)
        e = a + self.cpu.x_index
        return {
            "operand": "$%04X,X" % a,
            "memory": [e, 1, self.cpu.read_byte(e)],
        }

    def absolute_y_mode(self, pc):
        a = self.cpu.read_word(pc + 1)
        e = a + self.cpu.y_index
        return {
            "operand": "$%04X,Y" % a,
            "memory": [e, 1, self.cpu.read_byte(e)],
        }

    def immediate_mode(self, pc):
        return {
            "operand": "#$%02X" % (self.cpu.read_byte(pc + 1)),
        }

    def indirect_mode(self, pc):
        a = self.cpu.read_word(pc + 1)
        return {
            "operand": "($%04X)" % a,
            "memory": [a, 2, self.cpu.read_word(a)],
        }

    def indirect_x_mode(self, pc):
        z = self.cpu.read_byte(pc + 1)
        a = self.cpu.read_word((z + self.cpu.x_index) % 0x100)
        return {
            "operand": "($%02X,X)" % z,
            "memory": [a, 1, self.cpu.read_byte(a)],
        }

    def indirect_y_mode(self, pc):
        z = self.cpu.read_byte(pc + 1)
        a = self.cpu.read_word(z) + self.cpu.y_index
        return {
            "operand": "($%02X),Y" % z,
            "memory": [a, 1, self.cpu.read_byte(a)],
        }

    def relative_mode(self, pc):
        return {
            "operand": "$%04X" % (pc + signed(self.cpu.read_byte(pc + 1) + 2)),
        }

    def zero_page_mode(self, pc):
        a = self.cpu.read_byte(pc + 1)
        return {
            "operand": "$%02X" % a,
            "memory": [a, 1, self.cpu.read_byte(a)],
        }

    def zero_page_x_mode(self, pc):
        z = self.cpu.read_byte(pc + 1)
        a = (z + self.cpu.x_index) % 0x100
        return {
            "operand": "$%02X,X" % z,
            "memory": [a, 1, self.cpu.read_byte(a)],
        }

    def zero_page_y_mode(self, pc):
        z = self.cpu.read_byte(pc + 1)
        a = (z + self.cpu.y_index) % 0x100
        return {
            "operand": "$%02X,Y" % z,
            "memory": [a, 1, self.cpu.read_byte(a)],
        }

    def disasm(self, pc):
        op = self.cpu.read_byte(pc)
        info = self.ops[op]
        r = {
            "address": pc,
            "bytes": [self.cpu.read_byte(pc + i) for i in range(info[0])],
            "mnemonic": info[1],
        }
        if len(info) > 2:
            r.update(info[2](pc))
        return r, info[0]


class ControlHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server, cpu):
        self.cpu = cpu
        self.disassemble = Disassemble(self.cpu, self.cpu.memory)

        self.get_urls = {
            r"/disassemble/(\d+)$": self.get_disassemble,
            r"/memory/(\d+)(-(\d+))?$": self.get_memory,
            r"/memory/(\d+)(-(\d+))?/raw$": self.get_memory_raw,
            r"/status$": self.get_status,
        }

        self.post_urls = {
            r"/memory/(\d+)(-(\d+))?$": self.post_memory,
            r"/memory/(\d+)(-(\d+))?/raw$": self.post_memory_raw,
            r"/quit$": self.post_quit,
            r"/reset$": self.post_reset,
        }

        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def log_request(self, code, size=0):
        pass

    def dispatch(self, urls):
        for r, f in urls.items():
            m = re.match(r, self.path)
            if m is not None:
                f(m)
                break
        else:
            self.send_response(404)
            self.end_headers()

    def response(self, s):
        self.send_response(200)
        self.send_header("Content-Length", str(len(s)))
        self.end_headers()
        self.wfile.write(s)

    def do_GET(self):
        self.dispatch(self.get_urls)

    def do_POST(self):
        self.dispatch(self.post_urls)

    def get_disassemble(self, m):
        addr = int(m.group(1))
        r = []
        n = 20
        while n > 0:
            dis, length = self.disassemble.disasm(addr)
            r.append(dis)
            addr += length
            n -= 1
        self.response(json.dumps(r))

    def get_memory_raw(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        self.response("".join([chr(self.cpu.read_byte(x)) for x in range(addr, end + 1)]))

    def get_memory(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        self.response(json.dumps(list(map(self.cpu.read_byte, range(addr, end + 1)))))

    def get_status(self, m):
        self.response(json.dumps(dict((x, getattr(self.cpu, x)) for x in (
            "accumulator",
            "x_index",
            "y_index",
            "stack_pointer",
            "program_counter",
            "sign_flag",
            "overflow_flag",
            "break_flag",
            "decimal_mode_flag",
            "interrupt_disable_flag",
            "zero_flag",
            "carry_flag",
        ))))

    def post_memory(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        for i, a in enumerate(range(addr, end + 1)):
            self.cpu.write_byte(a, data[i])
        self.response("")

    def post_memory_raw(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        data = self.rfile.read(int(self.headers["Content-Length"]))
        for i, a in enumerate(range(addr, end + 1)):
            self.cpu.write_byte(a, data[i])
        self.response("")

    def post_quit(self, m):
        self.cpu.quit = True
        self.response("")

    def post_reset(self, m):
        self.cpu.reset()
        self.cpu.running = True
        self.response("")


class ControlHandlerFactory:

    def __init__(self, cpu):
        self.cpu = cpu

    def __call__(self, request, client_address, server):
        return ControlHandler(request, client_address, server, self.cpu)


class CPU:

    STACK_PAGE = 0x100
    RESET_VECTOR = 0xFFFC

    def __init__(self, memory, pc=None):
        self.memory = memory

        self.control_server = memory.use_bus and BaseHTTPServer.HTTPServer(("127.0.0.1", 6502), ControlHandlerFactory(self))

        self.accumulator = 0x00
        self.x_index = 0x00
        self.y_index = 0x00

        self.carry_flag = 0
        self.zero_flag = 0
        self.interrupt_disable_flag = 0
        self.decimal_mode_flag = 0
        self.break_flag = 1
        self.overflow_flag = 0
        self.sign_flag = 0

        self.stack_pointer = 0xFF

        self.cycles = 0

        self.setup_ops()
        self.reset()
        if pc is not None:
            self.program_counter = pc
        self.running = True
        self.quit = False

    def setup_ops(self):
        self.ops = [None] * 0x100
        self.ops[0x00] = lambda: self.BRK()
        self.ops[0x01] = lambda: self.ORA(self.indirect_x_mode())
        self.ops[0x05] = lambda: self.ORA(self.zero_page_mode())
        self.ops[0x06] = lambda: self.ASL(self.zero_page_mode())
        self.ops[0x08] = lambda: self.PHP()
        self.ops[0x09] = lambda: self.ORA(self.immediate_mode())
        self.ops[0x0A] = lambda: self.ASL()
        self.ops[0x0D] = lambda: self.ORA(self.absolute_mode())
        self.ops[0x0E] = lambda: self.ASL(self.absolute_mode())
        self.ops[0x10] = lambda: self.BPL(self.relative_mode())
        self.ops[0x11] = lambda: self.ORA(self.indirect_y_mode())
        self.ops[0x15] = lambda: self.ORA(self.zero_page_x_mode())
        self.ops[0x16] = lambda: self.ASL(self.zero_page_x_mode())
        self.ops[0x18] = lambda: self.CLC()
        self.ops[0x19] = lambda: self.ORA(self.absolute_y_mode())
        self.ops[0x1D] = lambda: self.ORA(self.absolute_x_mode())
        self.ops[0x1E] = lambda: self.ASL(self.absolute_x_mode(rmw=True))
        self.ops[0x20] = lambda: self.JSR(self.absolute_mode())
        self.ops[0x21] = lambda: self.AND(self.indirect_x_mode())
        self.ops[0x24] = lambda: self.BIT(self.zero_page_mode())
        self.ops[0x25] = lambda: self.AND(self.zero_page_mode())
        self.ops[0x26] = lambda: self.ROL(self.zero_page_mode())
        self.ops[0x28] = lambda: self.PLP()
        self.ops[0x29] = lambda: self.AND(self.immediate_mode())
        self.ops[0x2A] = lambda: self.ROL()
        self.ops[0x2C] = lambda: self.BIT(self.absolute_mode())
        self.ops[0x2D] = lambda: self.AND(self.absolute_mode())
        self.ops[0x2E] = lambda: self.ROL(self.absolute_mode())
        self.ops[0x30] = lambda: self.BMI(self.relative_mode())
        self.ops[0x31] = lambda: self.AND(self.indirect_y_mode())
        self.ops[0x35] = lambda: self.AND(self.zero_page_x_mode())
        self.ops[0x36] = lambda: self.ROL(self.zero_page_x_mode())
        self.ops[0x38] = lambda: self.SEC()
        self.ops[0x39] = lambda: self.AND(self.absolute_y_mode())
        self.ops[0x3D] = lambda: self.AND(self.absolute_x_mode())
        self.ops[0x3E] = lambda: self.ROL(self.absolute_x_mode(rmw=True))
        self.ops[0x40] = lambda: self.RTI()
        self.ops[0x41] = lambda: self.EOR(self.indirect_x_mode())
        self.ops[0x45] = lambda: self.EOR(self.zero_page_mode())
        self.ops[0x46] = lambda: self.LSR(self.zero_page_mode())
        self.ops[0x48] = lambda: self.PHA()
        self.ops[0x49] = lambda: self.EOR(self.immediate_mode())
        self.ops[0x4A] = lambda: self.LSR()
        self.ops[0x4C] = lambda: self.JMP(self.absolute_mode())
        self.ops[0x4D] = lambda: self.EOR(self.absolute_mode())
        self.ops[0x4E] = lambda: self.LSR(self.absolute_mode())
        self.ops[0x50] = lambda: self.BVC(self.relative_mode())
        self.ops[0x51] = lambda: self.EOR(self.indirect_y_mode())
        self.ops[0x55] = lambda: self.EOR(self.zero_page_x_mode())
        self.ops[0x56] = lambda: self.LSR(self.zero_page_x_mode())
        self.ops[0x58] = lambda: self.CLI()
        self.ops[0x59] = lambda: self.EOR(self.absolute_y_mode())
        self.ops[0x5D] = lambda: self.EOR(self.absolute_x_mode())
        self.ops[0x5E] = lambda: self.LSR(self.absolute_x_mode(rmw=True))
        self.ops[0x60] = lambda: self.RTS()
        self.ops[0x61] = lambda: self.ADC(self.indirect_x_mode())
        self.ops[0x65] = lambda: self.ADC(self.zero_page_mode())
        self.ops[0x66] = lambda: self.ROR(self.zero_page_mode())
        self.ops[0x68] = lambda: self.PLA()
        self.ops[0x69] = lambda: self.ADC(self.immediate_mode())
        self.ops[0x6A] = lambda: self.ROR()
        self.ops[0x6C] = lambda: self.JMP(self.indirect_mode())
        self.ops[0x6D] = lambda: self.ADC(self.absolute_mode())
        self.ops[0x6E] = lambda: self.ROR(self.absolute_mode())
        self.ops[0x70] = lambda: self.BVS(self.relative_mode())
        self.ops[0x71] = lambda: self.ADC(self.indirect_y_mode())
        self.ops[0x75] = lambda: self.ADC(self.zero_page_x_mode())
        self.ops[0x76] = lambda: self.ROR(self.zero_page_x_mode())
        self.ops[0x78] = lambda: self.SEI()
        self.ops[0x79] = lambda: self.ADC(self.absolute_y_mode())
        self.ops[0x7D] = lambda: self.ADC(self.absolute_x_mode())
        self.ops[0x7E] = lambda: self.ROR(self.absolute_x_mode(rmw=True))
        self.ops[0x81] = lambda: self.STA(self.indirect_x_mode())
        self.ops[0x84] = lambda: self.STY(self.zero_page_mode())
        self.ops[0x85] = lambda: self.STA(self.zero_page_mode())
        self.ops[0x86] = lambda: self.STX(self.zero_page_mode())
        self.ops[0x88] = lambda: self.DEY()
        self.ops[0x8A] = lambda: self.TXA()
        self.ops[0x8C] = lambda: self.STY(self.absolute_mode())
        self.ops[0x8D] = lambda: self.STA(self.absolute_mode())
        self.ops[0x8E] = lambda: self.STX(self.absolute_mode())
        self.ops[0x90] = lambda: self.BCC(self.relative_mode())
        self.ops[0x91] = lambda: self.STA(self.indirect_y_mode(rmw=True))
        self.ops[0x94] = lambda: self.STY(self.zero_page_x_mode())
        self.ops[0x95] = lambda: self.STA(self.zero_page_x_mode())
        self.ops[0x96] = lambda: self.STX(self.zero_page_y_mode())
        self.ops[0x98] = lambda: self.TYA()
        self.ops[0x99] = lambda: self.STA(self.absolute_y_mode(rmw=True))
        self.ops[0x9A] = lambda: self.TXS()
        self.ops[0x9D] = lambda: self.STA(self.absolute_x_mode(rmw=True))
        self.ops[0xA0] = lambda: self.LDY(self.immediate_mode())
        self.ops[0xA1] = lambda: self.LDA(self.indirect_x_mode())
        self.ops[0xA2] = lambda: self.LDX(self.immediate_mode())
        self.ops[0xA4] = lambda: self.LDY(self.zero_page_mode())
        self.ops[0xA5] = lambda: self.LDA(self.zero_page_mode())
        self.ops[0xA6] = lambda: self.LDX(self.zero_page_mode())
        self.ops[0xA8] = lambda: self.TAY()
        self.ops[0xA9] = lambda: self.LDA(self.immediate_mode())
        self.ops[0xAA] = lambda: self.TAX()
        self.ops[0xAC] = lambda: self.LDY(self.absolute_mode())
        self.ops[0xAD] = lambda: self.LDA(self.absolute_mode())
        self.ops[0xAE] = lambda: self.LDX(self.absolute_mode())
        self.ops[0xB0] = lambda: self.BCS(self.relative_mode())
        self.ops[0xB1] = lambda: self.LDA(self.indirect_y_mode())
        self.ops[0xB4] = lambda: self.LDY(self.zero_page_x_mode())
        self.ops[0xB5] = lambda: self.LDA(self.zero_page_x_mode())
        self.ops[0xB6] = lambda: self.LDX(self.zero_page_y_mode())
        self.ops[0xB8] = lambda: self.CLV()
        self.ops[0xB9] = lambda: self.LDA(self.absolute_y_mode())
        self.ops[0xBA] = lambda: self.TSX()
        self.ops[0xBC] = lambda: self.LDY(self.absolute_x_mode())
        self.ops[0xBD] = lambda: self.LDA(self.absolute_x_mode())
        self.ops[0xBE] = lambda: self.LDX(self.absolute_y_mode())
        self.ops[0xC0] = lambda: self.CPY(self.immediate_mode())
        self.ops[0xC1] = lambda: self.CMP(self.indirect_x_mode())
        self.ops[0xC4] = lambda: self.CPY(self.zero_page_mode())
        self.ops[0xC5] = lambda: self.CMP(self.zero_page_mode())
        self.ops[0xC6] = lambda: self.DEC(self.zero_page_mode())
        self.ops[0xC8] = lambda: self.INY()
        self.ops[0xC9] = lambda: self.CMP(self.immediate_mode())
        self.ops[0xCA] = lambda: self.DEX()
        self.ops[0xCC] = lambda: self.CPY(self.absolute_mode())
        self.ops[0xCD] = lambda: self.CMP(self.absolute_mode())
        self.ops[0xCE] = lambda: self.DEC(self.absolute_mode())
        self.ops[0xD0] = lambda: self.BNE(self.relative_mode())
        self.ops[0xD1] = lambda: self.CMP(self.indirect_y_mode())
        self.ops[0xD5] = lambda: self.CMP(self.zero_page_x_mode())
        self.ops[0xD6] = lambda: self.DEC(self.zero_page_x_mode())
        self.ops[0xD8] = lambda: self.CLD()
        self.ops[0xD9] = lambda: self.CMP(self.absolute_y_mode())
        self.ops[0xDD] = lambda: self.CMP(self.absolute_x_mode())
        self.ops[0xDE] = lambda: self.DEC(self.absolute_x_mode(rmw=True))
        self.ops[0xE0] = lambda: self.CPX(self.immediate_mode())
        self.ops[0xE1] = lambda: self.SBC(self.indirect_x_mode())
        self.ops[0xE4] = lambda: self.CPX(self.zero_page_mode())
        self.ops[0xE5] = lambda: self.SBC(self.zero_page_mode())
        self.ops[0xE6] = lambda: self.INC(self.zero_page_mode())
        self.ops[0xE8] = lambda: self.INX()
        self.ops[0xE9] = lambda: self.SBC(self.immediate_mode())
        self.ops[0xEA] = lambda: self.NOP()
        self.ops[0xEC] = lambda: self.CPX(self.absolute_mode())
        self.ops[0xED] = lambda: self.SBC(self.absolute_mode())
        self.ops[0xEE] = lambda: self.INC(self.absolute_mode())
        self.ops[0xF0] = lambda: self.BEQ(self.relative_mode())
        self.ops[0xF1] = lambda: self.SBC(self.indirect_y_mode())
        self.ops[0xF5] = lambda: self.SBC(self.zero_page_x_mode())
        self.ops[0xF6] = lambda: self.INC(self.zero_page_x_mode())
        self.ops[0xF8] = lambda: self.SED()
        self.ops[0xF9] = lambda: self.SBC(self.absolute_y_mode())
        self.ops[0xFD] = lambda: self.SBC(self.absolute_x_mode())
        self.ops[0xFE] = lambda: self.INC(self.absolute_x_mode(rmw=True))

    def reset(self):
        self.program_counter = self.read_word(self.RESET_VECTOR)

    def run(self, bus_port):
        global bus
        bus = socket.socket()
        bus.connect(("127.0.0.1", bus_port))

        while not self.quit:

            timeout = 0
            if not self.running:
                timeout = 1
            # Currently this handler blocks from the moment
            # a connection is accepted until the response
            # is sent. TODO: use an async HTTP server that
            # handles input data asynchronously.
            if self.control_server:
                sockets = [self.control_server]
                rs, _, _ = select.select(sockets, [], [], timeout)
                for s in rs:
                    if s is self.control_server:
                        self.control_server._handle_request_noblock()
                    else:
                        pass

            count = 1000
            while count > 0 and self.running:
                self.cycles += 2  # all instructions take this as a minimum
                op = self.read_pc_byte()
                func = self.ops[op]
                if func is None:
                    print "UNKNOWN OP"
                    print hex(self.program_counter - 1)
                    print hex(op)
                    break
                else:
                    self.ops[op]()
                count -= 1

    def test_run(self, start, end):
        self.program_counter = start
        while True:
            self.cycles += 2  # all instructions take this as a minimum
            if self.program_counter == end:
                break
            op = self.read_pc_byte()
            func = self.ops[op]
            if func is None:
                print "UNKNOWN OP"
                print hex(self.program_counter - 1)
                print hex(op)
                break
            else:
                self.ops[op]()

    ####

    def get_pc(self, inc=1):
        pc = self.program_counter
        self.program_counter += inc
        return pc

    def read_byte(self, address):
        return self.memory.read_byte(self.cycles, address)

    def read_word(self, address):
        return self.memory.read_word(self.cycles, address)

    def read_word_bug(self, address):
        return self.memory.read_word_bug(self.cycles, address)

    def read_pc_byte(self):
        return self.read_byte(self.get_pc())

    def read_pc_word(self):
        return self.read_word(self.get_pc(2))

    def write_byte(self, address, value):
        self.memory.write_byte(self.cycles, address, value)

    ####

    def status_from_byte(self, status):
        self.carry_flag = [0, 1][0 != status & 1]
        self.zero_flag = [0, 1][0 != status & 2]
        self.interrupt_disable_flag = [0, 1][0 != status & 4]
        self.decimal_mode_flag = [0, 1][0 != status & 8]
        self.break_flag = [0, 1][0 != status & 16]
        self.overflow_flag = [0, 1][0 != status & 64]
        self.sign_flag = [0, 1][0 != status & 128]

    def status_as_byte(self):
        return self.carry_flag | self.zero_flag << 1 | self.interrupt_disable_flag << 2 | self.decimal_mode_flag << 3 | self.break_flag << 4 | 1 << 5 | self.overflow_flag << 6 | self.sign_flag << 7

    ####

    def push_byte(self, byte):
        self.write_byte(self.STACK_PAGE + self.stack_pointer, byte)
        self.stack_pointer = (self.stack_pointer - 1) % 0x100

    def pull_byte(self):
        self.stack_pointer = (self.stack_pointer + 1) % 0x100
        return self.read_byte(self.STACK_PAGE + self.stack_pointer)

    def push_word(self, word):
        hi, lo = divmod(word, 0x100)
        self.push_byte(hi)
        self.push_byte(lo)

    def pull_word(self):
        s = self.STACK_PAGE + self.stack_pointer + 1
        self.stack_pointer += 2
        return self.read_word(s)

    ####

    def immediate_mode(self):
        return self.get_pc()

    def absolute_mode(self):
        self.cycles += 2
        return self.read_pc_word()

    def absolute_x_mode(self, rmw=False):
        if rmw:
            self.cycles += 1
        return self.absolute_mode() + self.x_index

    def absolute_y_mode(self, rmw=False):
        if rmw:
            self.cycles += 1
        return self.absolute_mode() + self.y_index

    def zero_page_mode(self):
        self.cycles += 1
        return self.read_pc_byte()

    def zero_page_x_mode(self):
        self.cycles += 1
        return (self.zero_page_mode() + self.x_index) % 0x100

    def zero_page_y_mode(self):
        self.cycles += 1
        return (self.zero_page_mode() + self.y_index) % 0x100

    def indirect_mode(self):
        self.cycles += 2
        return self.read_word_bug(self.absolute_mode())

    def indirect_x_mode(self):
        self.cycles += 4
        return self.read_word_bug((self.read_pc_byte() + self.x_index) % 0x100)

    def indirect_y_mode(self, rmw=False):
        if rmw:
            self.cycles += 4
        else:
            self.cycles += 3
        return self.read_word_bug(self.read_pc_byte()) + self.y_index

    def relative_mode(self):
        pc = self.get_pc()
        return pc + 1 + signed(self.read_byte(pc))

    ####

    def update_nz(self, value):
        value = value % 0x100
        self.zero_flag = [0, 1][(value == 0)]
        self.sign_flag = [0, 1][((value & 0x80) != 0)]
        return value

    def update_nzc(self, value):
        self.carry_flag = [0, 1][(value > 0xFF)]
        return self.update_nz(value)

    ####

    # LOAD / STORE

    def LDA(self, operand_address):
        self.accumulator = self.update_nz(self.read_byte(operand_address))

    def LDX(self, operand_address):
        self.x_index = self.update_nz(self.read_byte(operand_address))

    def LDY(self, operand_address):
        self.y_index = self.update_nz(self.read_byte(operand_address))

    def STA(self, operand_address):
        self.write_byte(operand_address, self.accumulator)

    def STX(self, operand_address):
        self.write_byte(operand_address, self.x_index)

    def STY(self, operand_address):
        self.write_byte(operand_address, self.y_index)

    # TRANSFER

    def TAX(self):
        self.x_index = self.update_nz(self.accumulator)

    def TXA(self):
        self.accumulator = self.update_nz(self.x_index)

    def TAY(self):
        self.y_index = self.update_nz(self.accumulator)

    def TYA(self):
        self.accumulator = self.update_nz(self.y_index)

    def TSX(self):
        self.x_index = self.update_nz(self.stack_pointer)

    def TXS(self):
        self.stack_pointer = self.x_index

    # SHIFTS / ROTATES

    def ASL(self, operand_address=None):
        if operand_address is None:
            self.accumulator = self.update_nzc(self.accumulator << 1)
        else:
            self.cycles += 2
            self.write_byte(operand_address, self.update_nzc(self.read_byte(operand_address) << 1))

    def ROL(self, operand_address=None):
        if operand_address is None:
            a = self.accumulator << 1
            if self.carry_flag:
                a = a | 0x01
            self.accumulator = self.update_nzc(a)
        else:
            self.cycles += 2
            m = self.read_byte(operand_address) << 1
            if self.carry_flag:
                m = m | 0x01
            self.write_byte(operand_address, self.update_nzc(m))

    def ROR(self, operand_address=None):
        if operand_address is None:
            if self.carry_flag:
                self.accumulator = self.accumulator | 0x100
            self.carry_flag = self.accumulator % 2
            self.accumulator = self.update_nz(self.accumulator >> 1)
        else:
            self.cycles += 2
            m = self.read_byte(operand_address)
            if self.carry_flag:
                m = m | 0x100
            self.carry_flag = m % 2
            self.write_byte(operand_address, self.update_nz(m >> 1))

    def LSR(self, operand_address=None):
        if operand_address is None:
            self.carry_flag = self.accumulator % 2
            self.accumulator = self.update_nz(self.accumulator >> 1)
        else:
            self.cycles += 2
            self.carry_flag = self.read_byte(operand_address) % 2
            self.write_byte(operand_address, self.update_nz(self.read_byte(operand_address) >> 1))

    # JUMPS / RETURNS

    def JMP(self, operand_address):
        self.cycles -= 1
        self.program_counter = operand_address

    def JSR(self, operand_address):
        self.cycles += 2
        self.push_word(self.program_counter - 1)
        self.program_counter = operand_address

    def RTS(self):
        self.cycles += 4
        self.program_counter = self.pull_word() + 1

    # BRANCHES

    def BCC(self, operand_address):
        if not self.carry_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BCS(self, operand_address):
        if self.carry_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BEQ(self, operand_address):
        if self.zero_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BNE(self, operand_address):
        if not self.zero_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BMI(self, operand_address):
        if self.sign_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BPL(self, operand_address):
        if not self.sign_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BVC(self, operand_address):
        if not self.overflow_flag:
            self.cycles += 1
            self.program_counter = operand_address

    def BVS(self, operand_address):
        if self.overflow_flag:
            self.cycles += 1
            self.program_counter = operand_address

    # SET / CLEAR FLAGS

    def CLC(self):
        self.carry_flag = 0

    def CLD(self):
        self.decimal_mode_flag = 0

    def CLI(self):
        self.interrupt_disable_flag = 0

    def CLV(self):
        self.overflow_flag = 0

    def SEC(self):
        self.carry_flag = 1

    def SED(self):
        self.decimal_mode_flag = 1

    def SEI(self):
        self.interrupt_disable_flag = 1

    # INCREMENT / DECREMENT

    def DEC(self, operand_address):
        self.cycles += 2
        self.write_byte(operand_address, self.update_nz(self.read_byte(operand_address) - 1))

    def DEX(self):
        self.x_index = self.update_nz(self.x_index - 1)

    def DEY(self):
        self.y_index = self.update_nz(self.y_index - 1)

    def INC(self, operand_address):
        self.cycles += 2
        self.write_byte(operand_address, self.update_nz(self.read_byte(operand_address) + 1))

    def INX(self):
        self.x_index = self.update_nz(self.x_index + 1)

    def INY(self):
        self.y_index = self.update_nz(self.y_index + 1)

    # PUSH / PULL

    def PHA(self):
        self.cycles += 1
        self.push_byte(self.accumulator)

    def PHP(self):
        self.cycles += 1
        self.push_byte(self.status_as_byte())

    def PLA(self):
        self.cycles += 2
        self.accumulator = self.update_nz(self.pull_byte())

    def PLP(self):
        self.cycles += 2
        self.status_from_byte(self.pull_byte())

    # LOGIC

    def AND(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator & self.read_byte(operand_address))

    def ORA(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator | self.read_byte(operand_address))

    def EOR(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator ^ self.read_byte(operand_address))

    # ARITHMETIC

    def ADC(self, operand_address):
        # @@@ doesn't handle BCD yet
        assert not self.decimal_mode_flag

        a2 = self.accumulator
        a1 = signed(a2)
        m2 = self.read_byte(operand_address)
        m1 = signed(m2)

        # twos complement addition
        result1 = a1 + m1 + self.carry_flag

        # unsigned addition
        result2 = a2 + m2 + self.carry_flag

        self.accumulator = self.update_nzc(result2)

        # perhaps this could be calculated from result2 but result1 is more intuitive
        self.overflow_flag = [0, 1][(result1 > 127) | (result1 < -128)]

    def SBC(self, operand_address):
        # @@@ doesn't handle BCD yet
        assert not self.decimal_mode_flag

        a2 = self.accumulator
        a1 = signed(a2)
        m2 = self.read_byte(operand_address)
        m1 = signed(m2)

        # twos complement subtraction
        result1 = a1 - m1 - [1, 0][self.carry_flag]

        # unsigned subtraction
        result2 = a2 - m2 - [1, 0][self.carry_flag]

        self.accumulator = self.update_nz(result2)
        self.carry_flag = [0, 1][(result2 >= 0)]

        # perhaps this could be calculated from result2 but result1 is more intuitive
        self.overflow_flag = [0, 1][(result1 > 127) | (result1 < -128)]

    # BIT

    def BIT(self, operand_address):
        value = self.read_byte(operand_address)
        self.sign_flag = ((value >> 7) % 2)  # bit 7
        self.overflow_flag = ((value >> 6) % 2)  # bit 6
        self.zero_flag = [0, 1][((self.accumulator & value) == 0)]

    # COMPARISON

    def CMP(self, operand_address):
        result = self.accumulator - self.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)

    def CPX(self, operand_address):
        result = self.x_index - self.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)

    def CPY(self, operand_address):
        result = self.y_index - self.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)

    # SYSTEM

    def NOP(self):
        pass

    def BRK(self):
        self.cycles += 5
        self.push_word(self.program_counter + 1)
        self.push_byte(self.status_as_byte())
        self.program_counter = self.read_word(0xFFFE)
        self.break_flag = 1

    def RTI(self):
        self.cycles += 4
        self.status_from_byte(self.pull_byte())
        self.program_counter = self.pull_word()

    # @@@ IRQ
    # @@@ NMI


def usage():
    print >>sys.stderr, "ApplePy - an Apple ][ emulator in Python"
    print >>sys.stderr, "James Tauber / http://jtauber.com/"
    print >>sys.stderr
    print >>sys.stderr, "Usage: cpu6502.py [options]"
    print >>sys.stderr
    print >>sys.stderr, "    -b, --bus      Bus port number"
    print >>sys.stderr, "    -p, --pc       Initial PC value"
    print >>sys.stderr, "    -R, --rom      ROM file to use (default A2ROM.BIN)"
    print >>sys.stderr, "    -r, --ram      RAM file to load (default none)"
    sys.exit(1)


def get_options():
    class Options:
        def __init__(self):
            self.rom = "A2ROM.BIN"
            self.ram = None
            self.bus = None
            self.pc = None

    options = Options()
    a = 1
    while a < len(sys.argv):
        if sys.argv[a].startswith("-"):
            if sys.argv[a] in ("-b", "--bus"):
                a += 1
                options.bus = int(sys.argv[a])
            elif sys.argv[a] in ("-p", "--pc"):
                a += 1
                options.pc = int(sys.argv[a])
            elif sys.argv[a] in ("-R", "--rom"):
                a += 1
                options.rom = sys.argv[a]
            elif sys.argv[a] in ("-r", "--ram"):
                a += 1
                options.ram = sys.argv[a]
            else:
                usage()
        else:
            usage()
        a += 1

    return options


if __name__ == "__main__":
    options = get_options()
    if options.bus is None:
        print "ApplePy cpu core"
        print "Run applepy.py instead"
        sys.exit(0)

    mem = Memory(options)

    cpu = CPU(mem, options.pc)
    cpu.run(options.bus)
