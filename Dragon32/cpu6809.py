
"""
    TODO: Just a copy of cpi6502.py yet :(
"""


import BaseHTTPServer
import json
import re
import select
import socket
import sys

from dragon32memory import Memory, RAM, ROM
from generic.cpu import BaseCPU
from generic.disassembler import BaseDisassemble
from Dragon32.dragon32config import Dragon32Config


class Disassemble6809(BaseDisassemble):
    def setup_ops(self):
        self.ops = [(1, "???")] * 0x100
        self.ops[0x00] = (1, "BRK",)
        self.ops[0x01] = (2, "ORA", self.indirect_x_mode)
        self.ops[0x05] = (2, "ORA", self.zero_page_mode)
        self.ops[0x06] = (2, "ASL", self.zero_page_mode)
        self.ops[0x08] = (1, "PHP",)
        self.ops[0x09] = (2, "ORA", self.immediate_mode)
        self.ops[0x0A] = (1, "ASL",)
        self.ops[0x0D] = (3, "ORA", self.absolute_mode)
        self.ops[0x0E] = (3, "ASL", self.absolute_mode)
        self.ops[0x10] = (2, "BPL", self.relative_mode)
        self.ops[0x11] = (2, "ORA", self.indirect_y_mode)
        self.ops[0x15] = (2, "ORA", self.zero_page_x_mode)
        self.ops[0x16] = (2, "ASL", self.zero_page_x_mode)
        self.ops[0x18] = (1, "CLC",)
        self.ops[0x19] = (3, "ORA", self.absolute_y_mode)
        self.ops[0x1D] = (3, "ORA", self.absolute_x_mode)
        self.ops[0x1E] = (3, "ASL", self.absolute_x_mode)
        self.ops[0x20] = (3, "JSR", self.absolute_mode)
        self.ops[0x21] = (2, "AND", self.indirect_x_mode)
        self.ops[0x24] = (2, "BIT", self.zero_page_mode)
        self.ops[0x25] = (2, "AND", self.zero_page_mode)
        self.ops[0x26] = (2, "ROL", self.zero_page_mode)
        self.ops[0x28] = (1, "PLP",)
        self.ops[0x29] = (2, "AND", self.immediate_mode)
        self.ops[0x2A] = (1, "ROL",)
        self.ops[0x2C] = (3, "BIT", self.absolute_mode)
        self.ops[0x2D] = (3, "AND", self.absolute_mode)
        self.ops[0x2E] = (3, "ROL", self.absolute_mode)
        self.ops[0x30] = (2, "BMI", self.relative_mode)
        self.ops[0x31] = (2, "AND", self.indirect_y_mode)
        self.ops[0x35] = (2, "AND", self.zero_page_x_mode)
        self.ops[0x36] = (2, "ROL", self.zero_page_x_mode)
        self.ops[0x38] = (1, "SEC",)
        self.ops[0x39] = (3, "AND", self.absolute_y_mode)
        self.ops[0x3D] = (3, "AND", self.absolute_x_mode)
        self.ops[0x3E] = (3, "ROL", self.absolute_x_mode)
        self.ops[0x40] = (1, "RTI",)
        self.ops[0x41] = (2, "EOR", self.indirect_x_mode)
        self.ops[0x45] = (2, "EOR", self.zero_page_mode)
        self.ops[0x46] = (2, "LSR", self.zero_page_mode)
        self.ops[0x48] = (1, "PHA",)
        self.ops[0x49] = (2, "EOR", self.immediate_mode)
        self.ops[0x4A] = (1, "LSR",)
        self.ops[0x4C] = (3, "JMP", self.absolute_mode)
        self.ops[0x4D] = (3, "EOR", self.absolute_mode)
        self.ops[0x4E] = (3, "LSR", self.absolute_mode)
        self.ops[0x50] = (2, "BVC", self.relative_mode)
        self.ops[0x51] = (2, "EOR", self.indirect_y_mode)
        self.ops[0x55] = (2, "EOR", self.zero_page_x_mode)
        self.ops[0x56] = (2, "LSR", self.zero_page_x_mode)
        self.ops[0x58] = (1, "CLI",)
        self.ops[0x59] = (3, "EOR", self.absolute_y_mode)
        self.ops[0x5D] = (3, "EOR", self.absolute_x_mode)
        self.ops[0x5E] = (3, "LSR", self.absolute_x_mode)
        self.ops[0x60] = (1, "RTS",)
        self.ops[0x61] = (2, "ADC", self.indirect_x_mode)
        self.ops[0x65] = (2, "ADC", self.zero_page_mode)
        self.ops[0x66] = (2, "ROR", self.zero_page_mode)
        self.ops[0x68] = (1, "PLA",)
        self.ops[0x69] = (2, "ADC", self.immediate_mode)
        self.ops[0x6A] = (1, "ROR",)
        self.ops[0x6C] = (3, "JMP", self.indirect_mode)
        self.ops[0x6D] = (3, "ADC", self.absolute_mode)
        self.ops[0x6E] = (3, "ROR", self.absolute_mode)
        self.ops[0x70] = (2, "BVS", self.relative_mode)
        self.ops[0x71] = (2, "ADC", self.indirect_y_mode)
        self.ops[0x75] = (2, "ADC", self.zero_page_x_mode)
        self.ops[0x76] = (2, "ROR", self.zero_page_x_mode)
        self.ops[0x78] = (1, "SEI",)
        self.ops[0x79] = (3, "ADC", self.absolute_y_mode)
        self.ops[0x7D] = (3, "ADC", self.absolute_x_mode)
        self.ops[0x7E] = (3, "ROR", self.absolute_x_mode)
        self.ops[0x81] = (2, "STA", self.indirect_x_mode)
        self.ops[0x84] = (2, "STY", self.zero_page_mode)
        self.ops[0x85] = (2, "STA", self.zero_page_mode)
        self.ops[0x86] = (2, "STX", self.zero_page_mode)
        self.ops[0x88] = (1, "DEY",)
        self.ops[0x8A] = (1, "TXA",)
        self.ops[0x8C] = (3, "STY", self.absolute_mode)
        self.ops[0x8D] = (3, "STA", self.absolute_mode)
        self.ops[0x8E] = (3, "STX", self.absolute_mode)
        self.ops[0x90] = (2, "BCC", self.relative_mode)
        self.ops[0x91] = (2, "STA", self.indirect_y_mode)
        self.ops[0x94] = (2, "STY", self.zero_page_x_mode)
        self.ops[0x95] = (2, "STA", self.zero_page_x_mode)
        self.ops[0x96] = (2, "STX", self.zero_page_y_mode)
        self.ops[0x98] = (1, "TYA",)
        self.ops[0x99] = (3, "STA", self.absolute_y_mode)
        self.ops[0x9A] = (1, "TXS",)
        self.ops[0x9D] = (3, "STA", self.absolute_x_mode)
        self.ops[0xA0] = (2, "LDY", self.immediate_mode)
        self.ops[0xA1] = (2, "LDA", self.indirect_x_mode)
        self.ops[0xA2] = (2, "LDX", self.immediate_mode)
        self.ops[0xA4] = (2, "LDY", self.zero_page_mode)
        self.ops[0xA5] = (2, "LDA", self.zero_page_mode)
        self.ops[0xA6] = (2, "LDX", self.zero_page_mode)
        self.ops[0xA8] = (1, "TAY",)
        self.ops[0xA9] = (2, "LDA", self.immediate_mode)
        self.ops[0xAA] = (1, "TAX",)
        self.ops[0xAC] = (3, "LDY", self.absolute_mode)
        self.ops[0xAD] = (3, "LDA", self.absolute_mode)
        self.ops[0xAE] = (3, "LDX", self.absolute_mode)
        self.ops[0xB0] = (2, "BCS", self.relative_mode)
        self.ops[0xB1] = (2, "LDA", self.indirect_y_mode)
        self.ops[0xB4] = (2, "LDY", self.zero_page_x_mode)
        self.ops[0xB5] = (2, "LDA", self.zero_page_x_mode)
        self.ops[0xB6] = (2, "LDX", self.zero_page_y_mode)
        self.ops[0xB8] = (1, "CLV",)
        self.ops[0xB9] = (3, "LDA", self.absolute_y_mode)
        self.ops[0xBA] = (1, "TSX",)
        self.ops[0xBC] = (3, "LDY", self.absolute_x_mode)
        self.ops[0xBD] = (3, "LDA", self.absolute_x_mode)
        self.ops[0xBE] = (3, "LDX", self.absolute_y_mode)
        self.ops[0xC0] = (2, "CPY", self.immediate_mode)
        self.ops[0xC1] = (2, "CMP", self.indirect_x_mode)
        self.ops[0xC4] = (2, "CPY", self.zero_page_mode)
        self.ops[0xC5] = (2, "CMP", self.zero_page_mode)
        self.ops[0xC6] = (2, "DEC", self.zero_page_mode)
        self.ops[0xC8] = (1, "INY",)
        self.ops[0xC9] = (2, "CMP", self.immediate_mode)
        self.ops[0xCA] = (1, "DEX",)
        self.ops[0xCC] = (3, "CPY", self.absolute_mode)
        self.ops[0xCD] = (3, "CMP", self.absolute_mode)
        self.ops[0xCE] = (3, "DEC", self.absolute_mode)
        self.ops[0xD0] = (2, "BNE", self.relative_mode)
        self.ops[0xD1] = (2, "CMP", self.indirect_y_mode)
        self.ops[0xD5] = (2, "CMP", self.zero_page_x_mode)
        self.ops[0xD6] = (2, "DEC", self.zero_page_x_mode)
        self.ops[0xD8] = (1, "CLD",)
        self.ops[0xD9] = (3, "CMP", self.absolute_y_mode)
        self.ops[0xDD] = (3, "CMP", self.absolute_x_mode)
        self.ops[0xDE] = (3, "DEC", self.absolute_x_mode)
        self.ops[0xE0] = (2, "CPX", self.immediate_mode)
        self.ops[0xE1] = (2, "SBC", self.indirect_x_mode)
        self.ops[0xE4] = (2, "CPX", self.zero_page_mode)
        self.ops[0xE5] = (2, "SBC", self.zero_page_mode)
        self.ops[0xE6] = (2, "INC", self.zero_page_mode)
        self.ops[0xE8] = (1, "INX",)
        self.ops[0xE9] = (2, "SBC", self.immediate_mode)
        self.ops[0xEA] = (1, "NOP",)
        self.ops[0xEC] = (3, "CPX", self.absolute_mode)
        self.ops[0xED] = (3, "SBC", self.absolute_mode)
        self.ops[0xEE] = (3, "INC", self.absolute_mode)
        self.ops[0xF0] = (2, "BEQ", self.relative_mode)
        self.ops[0xF1] = (2, "SBC", self.indirect_y_mode)
        self.ops[0xF5] = (2, "SBC", self.zero_page_x_mode)
        self.ops[0xF6] = (2, "INC", self.zero_page_x_mode)
        self.ops[0xF8] = (1, "SED",)
        self.ops[0xF9] = (3, "SBC", self.absolute_y_mode)
        self.ops[0xFD] = (3, "SBC", self.absolute_x_mode)
        self.ops[0xFE] = (3, "INC", self.absolute_x_mode)





class CPU6502(BaseCPU):

    def __init__(self, *args, **kwargs):
        super(CPU6502, self).__init__(*args, **kwargs)

        self.stack_pointer = 0xFF

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



def usage():
    print >> sys.stderr, "ApplePy - an Apple ][ emulator in Python"
    print >> sys.stderr, "James Tauber / http://jtauber.com/"
    print >> sys.stderr
    print >> sys.stderr, "Usage: cpu6502.py [options]"
    print >> sys.stderr
    print >> sys.stderr, "    -b, --bus      Bus port number"
    print >> sys.stderr, "    -p, --pc       Initial PC value"
    print >> sys.stderr, "    -R, --rom      ROM file to use (default A2ROM.BIN)"
    print >> sys.stderr, "    -r, --ram      RAM file to load (default none)"
    sys.exit(1)


def get_options():
    class Options:
        def __init__(self):
            self.rom = "d32.rom"
            self.ram = None
            self.bus = None
            self.pc = None

    options = Options()
    a = 1
    while a < len(sys.argv):
        if sys.argv[a].startswith("-"):
            if sys.argv[a] in ("-b", "--bus"):
                a += 1
                options.bus_port = int(sys.argv[a])
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
    if options.bus_port is None:
        print "Dragon 32 cpu core"
        print "Run dragonpy.py instead"
        sys.exit(0)

    cfg = Dragon32Config()

    bus = socket.socket()
    bus_address = (cfg.LOCAL_HOST_IP, options.bus_port)
    print "bus I/O connect to %s" % repr(bus_address)
    bus.connect(bus_address)

    mem = Memory(cfg, bus, RAM, ROM, options)

    cpu = CPU6502(cfg, bus, options, mem, Disassemble6809)
    cpu.run()
