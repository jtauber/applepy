# ApplePy - an Apple ][ emulator in Python
# James Tauber / http://jtauber.com/
# originally written 2001, updated 2011


import pygame
import colorsys

def signed(x):
    if x > 0x7F:
        x = x - 0x100
    return x


class Display:
    
    characters = [
        [0b00000, 0b01110, 0b10001, 0b10101, 0b10111, 0b10110, 0b10000, 0b01111],
        [0b00000, 0b00100, 0b01010, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01111, 0b10000, 0b10000, 0b10000, 0b10011, 0b10001, 0b01111],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b00001, 0b00001, 0b00001, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111],
        [0b00000, 0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
        [0b00000, 0b01110, 0b10001, 0b10000, 0b01110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
        [0b00000, 0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001],
        [0b00000, 0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b11000, 0b11000, 0b11000, 0b11000, 0b11000, 0b11111],
        [0b00000, 0b00000, 0b10000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00000],
        [0b00000, 0b11111, 0b00011, 0b00011, 0b00011, 0b00011, 0b00011, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b01010, 0b10001, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
        [0b00000, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010],
        [0b00000, 0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100],
        [0b00000, 0b11000, 0b11001, 0b00010, 0b00100, 0b01000, 0b10011, 0b00011],
        [0b00000, 0b01000, 0b10100, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101],
        [0b00000, 0b00100, 0b00100, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00100, 0b01000, 0b10000, 0b10000, 0b10000, 0b01000, 0b00100],
        [0b00000, 0b00100, 0b00010, 0b00001, 0b00001, 0b00001, 0b00010, 0b00100],
        [0b00000, 0b00100, 0b10101, 0b01110, 0b00100, 0b01110, 0b10101, 0b00100],
        [0b00000, 0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00100],
        [0b00000, 0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b00000],
        [0b00000, 0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
        [0b00000, 0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00110, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
        [0b00000, 0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
        [0b00000, 0b00111, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
        [0b00000, 0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b11100],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00000, 0b00000],
        [0b00000, 0b00000, 0b00000, 0b00100, 0b00000, 0b00100, 0b00100, 0b01000],
        [0b00000, 0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010],
        [0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000],
        [0b00000, 0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000],
        [0b00000, 0b01110, 0b10001, 0b00010, 0b00100, 0b00100, 0b00000, 0b00100]
    ]
    
    lores_colours = [
        (0, 0, 0), # black
        (208, 0, 48), # magenta / dark red
        (0, 0, 128), # dark blue
        (255, 0, 255), # purple / violet
        (0, 128, 0), # dark green
        (128, 128, 128), # gray 1
        (0, 0, 255), # medium blue / blue
        (96, 160, 255), # light blue
        (128, 80, 0), # brown / dark orange
        (255, 128 ,0), # orange
        (192, 192, 192), # gray 2
        (255, 144, 128), # pink / light red
        (0, 255, 0), # light green / green
        (255, 255, 0), # yellow / light orange
        (64, 255, 144), # aquamarine / light green
        (255, 255, 255), # white
    ]
    
    def __init__(self):
        self.screen = pygame.display.set_mode((560, 384))
        pygame.display.set_caption("ApplePy")
    
    def txtclr(self):
        self.text = False
    
    def txtset(self):
        self.text = True
    
    def mixclr(self):
        self.mix = False
    
    def mixset(self):
        self.mix = True
    
    def lowscr(self):
        self.page = 1
    
    def hiscr(self):
        self.page = 2
    
    def lores(self):
        self.high_res = False
    
    def hires(self):
        self.high_res = True
    
    def update(self, address, value):
        if self.page == 1 and 0x400 <= address <= 0x7FF:
            if self.text:
                self.update_text(address - 0x400, value, False)
            elif self.mix:
                self.update_lores(address - 0x400, value, True)
                self.update_text(address - 0x400, value, True)
            else:
                self.update_lores(address - 0x400, value, False)
        if self.page == 2 and 0x800 <= address <= 0xBFF:
            if self.text:
                self.update_text(address - 0x800, value, False)
            elif self.mix:
                self.update_lores(address - 0x400, value, True)
                self.update_text(address - 0x400, value, True)
            else:
                self.update_lores(address - 0x800, value, False)
    
    def update_text(self, base, value, mixed):
        hi, lo = divmod(base, 0x80)
        row_group, column  = divmod(lo, 0x28)
        row = hi + 8 * row_group
        
        if mixed and row < 20:
            return
            
        # skip if writing to row group 3
        if row_group == 3:
            return
        
        mode, ch = divmod(value, 0x40)
        
        if mode == 0: # inverse
            on = (0, 0, 0)
            off = (0, 200, 0)
        elif mode == 1: # flash
            on = (0, 0, 0)
            off = (0, 200, 0)
        else: # normal
            on = (0, 200, 0)
            off = (0, 0, 0)
            
        pixels = pygame.PixelArray(self.screen)
        for line in range(8):
            b = self.characters[ch][line] << 1
            for i in range(7):
                x = 2 * (column * 7 + (5 - i))
                y = 2 * (row * 8 + line)
                bit = (b >> i) % 2
                pixels[x][y] = on if bit else off
                pixels[x + 1][y] = on if bit else off
        del pixels
    
    def update_lores(self, base, value, mixed):
        hi, lo = divmod(base, 0x80)
        row_group, column  = divmod(lo, 0x28)
        row = hi + 8 * row_group
        
        if mixed and row >= 20:
            return
        
        lower, upper = divmod(value, 0x10)
        
        pixels = pygame.PixelArray(self.screen)
        for dx in range(14):
            for dy in range(8):
                x = column * 14 + dx
                y = row * 16 + dy
                pixels[x][y] = self.lores_colours[upper]
            for dy in range(8, 16):
                x = column * 14 + dx
                y = row * 16 + dy
                pixels[x][y] = self.lores_colours[lower]
        del pixels


class RAM:
    
    def __init__(self, start, size):
        self.start = start
        self.end = start + size - 1
        self.__mem = [0x00] * size
    
    def load(self, address, data):
        for offset, datum in enumerate(data):
            self.__mem[address - self.start + offset] = datum
    
    def read_byte(self, address):
        assert self.start <= address <= self.end
        return self.__mem[address - self.start]
    
    def write_byte(self, address, value):
        self.__mem[address] = value


class SoftSwitches:
    
    def __init__(self, display):
        self.kbd = 0x00
        self.display = display
    
    def read_byte(self, address):
        assert 0xC000 <= address <= 0xCFFF
        if address == 0xC000:
            return self.kbd
        elif address == 0xC010:
            self.kbd = self.kbd & 0x7F
        elif address == 0xC030:
            pass # toggle speaker
        elif address == 0xC050:
            self.display.txtclr()
        elif address == 0xC051:
            self.display.txtset()
        elif address == 0xC052:
            self.display.mixclr()
        elif address == 0xC053:
            self.display.mixset()
        elif address == 0xC054:
            self.display.lowscr()
        elif address == 0xC055:
            self.display.hiscr()
        elif address == 0xC056:
            self.display.lores()
        elif address == 0xC057:
            self.display.hires()
        else:
            pass # print "%04X" % address
        return 0x00


class ROM:
    
    def __init__(self, start, size):
        self.start = start
        self.end = start + size - 1
        self.__mem = [0x00] * size
    
    def load(self, address, data):
        for offset, datum in enumerate(data):
            self.__mem[address - self.start + offset] = datum
    
    def load_file(self, address, filename):
        with open(filename) as f:
            for offset, datum in enumerate(f.read()):
                self.__mem[address - self.start + offset] = ord(datum)
    
    def read_byte(self, address):
        assert self.start <= address <= self.end
        return self.__mem[address - self.start]


class Memory:
    
    def __init__(self, display=None):
        self.display = display
        self.rom = ROM(0xD000, 0x3000)
        
        # available from http://www.easy68k.com/paulrsm/6502/index.html
        self.rom.load_file(0xD000, "A2ROM.BIN")
        
        self.ram = RAM(0x0000, 0xC000)
        self.softswitches = SoftSwitches(display)
    
    def load(self, address, data):
        if address < 0xC000:
            self.ram.load(address, data)
    
    def read_byte(self, address):
        if address < 0xC000:
            return self.ram.read_byte(address)
        elif address < 0xD000:
            return self.softswitches.read_byte(address)
        else:
            return self.rom.read_byte(address)
    
    def read_word(self, address):
        return self.read_byte(address) + (self.read_byte(address + 1) << 8)
    
    def read_word_bug(self, address):
        if address % 0x100 == 0xFF:
            return self.read_byte(address) + (self.read_byte(address & 0xFF00) << 8)
        else:
            return self.read_word(address)
    
    def write_byte(self, address, value):
        if address < 0xC000:
            self.ram.write_byte(address, value)
        if 0x400 <= address < 0x800 and display:
            self.display.update(address, value)


class Disassemble:
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory
        
        self.setup_ops()
    
    def setup_ops(self):
        self.ops = [None] * 0x100
        self.ops[0x00] = ("BRK", )
        self.ops[0x01] = ("ORA", self.indirect_x_mode)
        self.ops[0x05] = ("ORA", self.zero_page_mode)
        self.ops[0x06] = ("ASL", self.zero_page_mode)
        self.ops[0x08] = ("PHP", )
        self.ops[0x09] = ("ORA", self.immediate_mode)
        self.ops[0x0A] = ("ASL", )
        self.ops[0x0D] = ("ORA", self.absolute_mode)
        self.ops[0x0E] = ("ASL", self.absolute_mode)
        self.ops[0x10] = ("BPL", self.relative_mode)
        self.ops[0x11] = ("ORA", self.indirect_y_mode)
        self.ops[0x15] = ("ORA", self.zero_page_x_mode)
        self.ops[0x16] = ("ASL", self.zero_page_x_mode)
        self.ops[0x18] = ("CLC", )
        self.ops[0x19] = ("ORA", self.absolute_y_mode)
        self.ops[0x1D] = ("ORA", self.absolute_x_mode)
        self.ops[0x1E] = ("ASL", self.absolute_x_mode)
        self.ops[0x20] = ("JSR", self.absolute_mode)
        self.ops[0x21] = ("AND", self.indirect_x_mode)
        self.ops[0x24] = ("BIT", self.zero_page_mode)
        self.ops[0x25] = ("AND", self.zero_page_mode)
        self.ops[0x26] = ("ROL", self.zero_page_mode)
        self.ops[0x28] = ("PLP", )
        self.ops[0x29] = ("AND", self.immediate_mode)
        self.ops[0x2A] = ("ROL", )
        self.ops[0x2C] = ("BIT", self.absolute_mode)
        self.ops[0x2D] = ("AND", self.absolute_mode)
        self.ops[0x2E] = ("ROL", self.absolute_mode)
        self.ops[0x30] = ("BMI", self.relative_mode)
        self.ops[0x31] = ("AND", self.indirect_y_mode)
        self.ops[0x35] = ("AND", self.zero_page_x_mode)
        self.ops[0x36] = ("ROL", self.zero_page_x_mode)
        self.ops[0x38] = ("SEC", )
        self.ops[0x39] = ("AND", self.absolute_y_mode)
        self.ops[0x3D] = ("AND", self.absolute_x_mode)
        self.ops[0x3E] = ("ROL", self.absolute_x_mode)
        self.ops[0x40] = ("RTI", )
        self.ops[0x41] = ("EOR", self.indirect_x_mode)
        self.ops[0x45] = ("EOR", self.zero_page_mode)
        self.ops[0x46] = ("LSR", self.zero_page_mode)
        self.ops[0x48] = ("PHA", )
        self.ops[0x49] = ("EOR", self.immediate_mode)
        self.ops[0x4A] = ("LSR", )
        self.ops[0x4C] = ("JMP", self.absolute_mode)
        self.ops[0x4D] = ("EOR", self.absolute_mode)
        self.ops[0x4E] = ("LSR", self.absolute_mode)
        self.ops[0x50] = ("BVC", self.relative_mode)
        self.ops[0x51] = ("EOR", self.indirect_y_mode)
        self.ops[0x55] = ("EOR", self.zero_page_x_mode)
        self.ops[0x56] = ("LSR", self.zero_page_x_mode)
        self.ops[0x58] = ("CLI", )
        self.ops[0x59] = ("EOR", self.absolute_y_mode)
        self.ops[0x5D] = ("EOR", self.absolute_x_mode)
        self.ops[0x5E] = ("LSR", self.absolute_x_mode)
        self.ops[0x60] = ("RTS", )
        self.ops[0x61] = ("ADC", self.indirect_x_mode)
        self.ops[0x65] = ("ADC", self.zero_page_mode)
        self.ops[0x66] = ("ROR", self.zero_page_mode)
        self.ops[0x68] = ("PLA", )
        self.ops[0x69] = ("ADC", self.immediate_mode)
        self.ops[0x6A] = ("ROR", )
        self.ops[0x6C] = ("JMP", self.indirect_mode)
        self.ops[0x6D] = ("ADC", self.absolute_mode)
        self.ops[0x6E] = ("ROR", self.absolute_mode)
        self.ops[0x70] = ("BVS", self.relative_mode)
        self.ops[0x71] = ("ADC", self.indirect_y_mode)
        self.ops[0x75] = ("ADC", self.zero_page_x_mode)
        self.ops[0x76] = ("ROR", self.zero_page_x_mode)
        self.ops[0x78] = ("SEI", )
        self.ops[0x79] = ("ADC", self.absolute_y_mode)
        self.ops[0x7D] = ("ADC", self.absolute_x_mode)
        self.ops[0x7E] = ("ROR", self.absolute_x_mode)
        self.ops[0x81] = ("STA", self.indirect_x_mode)
        self.ops[0x84] = ("STY", self.zero_page_mode)
        self.ops[0x85] = ("STA", self.zero_page_mode)
        self.ops[0x86] = ("STX", self.zero_page_mode)
        self.ops[0x88] = ("DEY", )
        self.ops[0x8A] = ("TXA", )
        self.ops[0x8C] = ("STY", self.absolute_mode)
        self.ops[0x8D] = ("STA", self.absolute_mode)
        self.ops[0x8E] = ("STX", self.absolute_mode)
        self.ops[0x90] = ("BCC", self.relative_mode)
        self.ops[0x91] = ("STA", self.indirect_y_mode)
        self.ops[0x94] = ("STY", self.zero_page_x_mode)
        self.ops[0x95] = ("STA", self.zero_page_x_mode)
        self.ops[0x96] = ("STX", self.zero_page_y_mode)
        self.ops[0x98] = ("TYA", )
        self.ops[0x99] = ("STA", self.absolute_y_mode)
        self.ops[0x9A] = ("TXS", )
        self.ops[0x9D] = ("STA", self.absolute_x_mode)
        self.ops[0xA0] = ("LDY", self.immediate_mode)
        self.ops[0xA1] = ("LDA", self.indirect_x_mode)
        self.ops[0xA2] = ("LDX", self.immediate_mode)
        self.ops[0xA4] = ("LDY", self.zero_page_mode)
        self.ops[0xA5] = ("LDA", self.zero_page_mode)
        self.ops[0xA6] = ("LDX", self.zero_page_mode)
        self.ops[0xA8] = ("TAY", )
        self.ops[0xA9] = ("LDA", self.immediate_mode)
        self.ops[0xAA] = ("TAX", )
        self.ops[0xAC] = ("LDY", self.absolute_mode)
        self.ops[0xAD] = ("LDA", self.absolute_mode)
        self.ops[0xAE] = ("LDX", self.absolute_mode)
        self.ops[0xB0] = ("BCS", self.relative_mode)
        self.ops[0xB1] = ("LDA", self.indirect_y_mode)
        self.ops[0xB4] = ("LDY", self.zero_page_x_mode)
        self.ops[0xB5] = ("LDA", self.zero_page_x_mode)
        self.ops[0xB6] = ("LDX", self.zero_page_y_mode)
        self.ops[0xB8] = ("CLV", )
        self.ops[0xB9] = ("LDA", self.absolute_y_mode)
        self.ops[0xBA] = ("TSX", )
        self.ops[0xBC] = ("LDY", self.absolute_x_mode)
        self.ops[0xBD] = ("LDA", self.absolute_x_mode)
        self.ops[0xBE] = ("LDX", self.absolute_y_mode)
        self.ops[0xC0] = ("CPY", self.immediate_mode)
        self.ops[0xC1] = ("CMP", self.indirect_x_mode)
        self.ops[0xC4] = ("CPY", self.zero_page_mode)
        self.ops[0xC5] = ("CMP", self.zero_page_mode)
        self.ops[0xC6] = ("DEC", self.zero_page_mode)
        self.ops[0xC8] = ("INY", )
        self.ops[0xC9] = ("CMP", self.immediate_mode)
        self.ops[0xCA] = ("DEX", )
        self.ops[0xCC] = ("CPY", self.absolute_mode)
        self.ops[0xCD] = ("CMP", self.absolute_mode)
        self.ops[0xCE] = ("DEC", self.absolute_mode)
        self.ops[0xD0] = ("BNE", self.relative_mode)
        self.ops[0xD1] = ("CMP", self.indirect_y_mode)
        self.ops[0xD5] = ("CMP", self.zero_page_x_mode)
        self.ops[0xD6] = ("DEC", self.zero_page_x_mode)
        self.ops[0xD8] = ("CLD", )
        self.ops[0xD9] = ("CMP", self.absolute_y_mode)
        self.ops[0xDD] = ("CMP", self.absolute_x_mode)
        self.ops[0xDE] = ("DEC", self.absolute_x_mode)
        self.ops[0xE0] = ("CPX", self.immediate_mode)
        self.ops[0xE1] = ("SBC", self.indirect_x_mode)
        self.ops[0xE4] = ("CPX", self.zero_page_mode)
        self.ops[0xE5] = ("SBC", self.zero_page_mode)
        self.ops[0xE6] = ("INC", self.zero_page_mode)
        self.ops[0xE8] = ("INX", )
        self.ops[0xE9] = ("SBC", self.immediate_mode)
        self.ops[0xEA] = ("NOP", )
        self.ops[0xEC] = ("CPX", self.absolute_mode)
        self.ops[0xED] = ("SBC", self.absolute_mode)
        self.ops[0xEE] = ("INC", self.absolute_mode)
        self.ops[0xF0] = ("BEQ", self.relative_mode)
        self.ops[0xF1] = ("SBC", self.indirect_y_mode)
        self.ops[0xF5] = ("SBC", self.zero_page_x_mode)
        self.ops[0xF6] = ("INC", self.zero_page_x_mode)
        self.ops[0xF8] = ("SED", )
        self.ops[0xF9] = ("SBC", self.absolute_y_mode)
        self.ops[0xFD] = ("SBC", self.absolute_x_mode)
        self.ops[0xFE] = ("INC", self.absolute_x_mode)
    
    def absolute_mode(self, pc):
        a = self.memory.read_word(pc + 1)
        return "$%04X    [%04X] = %02X" % (a, a, self.memory.read_word(a))
    
    def absolute_x_mode(self, pc):
        a = self.memory.read_word(pc + 1)
        e = a + self.cpu.x_index
        return "$%04X,X  [%04X] = %02X" % (a, e, self.memory.read_byte(e))
    
    def absolute_y_mode(self, pc):
        a = self.memory.read_word(pc + 1)
        e = a + self.cpu.y_index
        return "$%04X,Y    [%04X] = %02X" % (a, e, self.memory.read_byte(e))
    
    def immediate_mode(self, pc):
        return "#$%02X" % (self.memory.read_byte(pc + 1))
    
    def indirect_mode(self, pc):
        a = self.memory.read_word(pc + 1)
        return "($%04X)  [%04X] = %02X" % (a, a, self.memory.read_word(a))
    
    def indirect_x_mode(self, pc):
        z = self.memory.read_byte(pc + 1)
        a = self.memory.read_word((z + self.cpu.x_index) % 0x100)
        return "($%02X,X)   [%04X] = %02X" % (z, a, self.memory.read_byte(a))
    
    def indirect_y_mode(self, pc):
        z = self.memory.read_byte(pc + 1)
        a = self.memory.read_word(z) + self.cpu.y_index
        return "($%02X),Y  [%04X] = %02X" % (z, a, self.memory.read_byte(a))
    
    def relative_mode(self, pc):
        return "$%04X" % (pc + signed(self.memory.read_byte(pc + 1) + 2))
    
    def zero_page_mode(self, pc):
        a = self.memory.read_byte(pc + 1)
        return "$%02X      [%04X] = %02X" % (a, a, self.memory.read_byte(a))
    
    def zero_page_x_mode(self, pc):
        z = self.memory.read_byte(pc + 1)
        a = (z + self.cpu.x_index) % 0x100
        return "$%02X,X    [%04X] = %02X" % (z, a, self.memory.read_byte(a))
    
    def zero_page_y_mode(self, pc):
        z = self.memory.read_byte(pc + 1)
        a = (z + self.cpu.y_index) % 0x100
        return "$%02X,Y    [%04X] = %02X" % (z, a, self.memory.read_byte(a))
    
    def disasm(self, pc):
        op = self.memory.read_byte(pc)
        info = self.ops[op]
        s = "%02X %s" % (pc, info[0])
        if len(info) > 1:
            s += " " + info[1](pc)
        return s


class CPU:
    
    STACK_PAGE = 0x100
    RESET_VECTOR = 0xFFFC
    
    def __init__(self, memory):
        self.memory = memory
        self.disassemble = Disassemble(self, memory)
        
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
        
        self.setup_ops()
        self.reset()
    
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
        self.ops[0x1E] = lambda: self.ASL(self.absolute_x_mode())
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
        self.ops[0x3E] = lambda: self.ROL(self.absolute_x_mode())
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
        self.ops[0x5E] = lambda: self.LSR(self.absolute_x_mode())
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
        self.ops[0x7E] = lambda: self.ROR(self.absolute_x_mode())
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
        self.ops[0x91] = lambda: self.STA(self.indirect_y_mode())
        self.ops[0x94] = lambda: self.STY(self.zero_page_x_mode())
        self.ops[0x95] = lambda: self.STA(self.zero_page_x_mode())
        self.ops[0x96] = lambda: self.STX(self.zero_page_y_mode())
        self.ops[0x98] = lambda: self.TYA()
        self.ops[0x99] = lambda: self.STA(self.absolute_y_mode())
        self.ops[0x9A] = lambda: self.TXS()
        self.ops[0x9D] = lambda: self.STA(self.absolute_x_mode())
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
        self.ops[0xDE] = lambda: self.DEC(self.absolute_x_mode())
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
        self.ops[0xFE] = lambda: self.INC(self.absolute_x_mode())
        
    def reset(self):
        self.program_counter = self.memory.read_word(self.RESET_VECTOR)
    
    def run(self):
        update_cycle = 0
        quit = False
        while not quit:
            op = self.read_pc_byte()
            func = self.ops[op]
            if func is None:
                print "UNKNOWN OP"
                print hex(self.program_counter - 1)
                print hex(op)
                break
            else:
                self.ops[op]()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True
                
                if event.type == pygame.KEYDOWN:
                    if event.unicode:
                        key = ord(event.unicode)
                        if key == 0x7F:
                            key = 0x08
                        self.memory.softswitches.kbd = 0x80 + key
            
            update_cycle += 1
            if update_cycle >= 1024:
                pygame.display.flip()
                update_cycle = 0
    
    ####
    
    def get_pc(self, inc=1):
        pc = self.program_counter
        self.program_counter += inc
        return pc
    
    def read_pc_byte(self):
        return self.memory.read_byte(self.get_pc())
    
    def read_pc_word(self):
        return self.memory.read_word(self.get_pc(2))
    
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
        self.memory.write_byte(self.STACK_PAGE + self.stack_pointer, byte)
        self.stack_pointer = (self.stack_pointer - 1) % 0x100
    
    def pull_byte(self):
        self.stack_pointer = (self.stack_pointer + 1) % 0x100
        return self.memory.read_byte(self.STACK_PAGE + self.stack_pointer)
    
    def push_word(self, word):
        hi, lo = divmod(word, 0x100)
        self.push_byte(hi)
        self.push_byte(lo)
    
    def pull_word(self):
        s = self.STACK_PAGE + self.stack_pointer + 1
        self.stack_pointer += 2
        return self.memory.read_word(s)
    
    ####
    
    def immediate_mode(self):
        return self.get_pc()
    
    def absolute_mode(self):
        return self.read_pc_word()
    
    def absolute_x_mode(self):
        return self.absolute_mode() + self.x_index
    
    def absolute_y_mode(self):
        return self.absolute_mode() + self.y_index
    
    def zero_page_mode(self):
        return self.read_pc_byte()
    
    def zero_page_x_mode(self):
        return (self.zero_page_mode() + self.x_index) % 0x100
    
    def zero_page_y_mode(self):
        return (self.zero_page_mode() + self.y_index) % 0x100
    
    def indirect_mode(self):
        return self.memory.read_word_bug(self.absolute_mode())
    
    def indirect_x_mode(self):
        return self.memory.read_word_bug((self.read_pc_byte() + self.x_index) % 0x100)
    
    def indirect_y_mode(self):
        return self.memory.read_word_bug(self.read_pc_byte()) + self.y_index
    
    def relative_mode(self):
        pc = self.get_pc()
        return pc + 1 + signed(self.memory.read_byte(pc))
    
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
        self.accumulator = self.update_nz(self.memory.read_byte(operand_address))
    
    def LDX(self, operand_address):
        self.x_index = self.update_nz(self.memory.read_byte(operand_address))
    
    def LDY(self, operand_address):
        self.y_index = self.update_nz(self.memory.read_byte(operand_address))
    
    def STA(self, operand_address):
        self.memory.write_byte(operand_address, self.accumulator)
    
    def STX(self, operand_address):
        self.memory.write_byte(operand_address, self.x_index)
    
    def STY(self, operand_address):
        self.memory.write_byte(operand_address, self.y_index)
    
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
            self.memory.write_byte(operand_address, self.update_nzc(self.memory.read_byte(operand_address) << 1))
    
    def ROL(self, operand_address=None):
        if operand_address is None:
            a = self.accumulator << 1
            if self.carry_flag:
                a = a | 0x01
            self.accumulator = self.update_nzc(a)
        else:
            m = self.memory.read_byte(operand_address) << 1
            if self.carry_flag:
                m = m | 0x01
            self.memory.write_byte(operand_address, self.update_nzc(m))
    
    def ROR(self, operand_address=None):
        if operand_address is None:
            if self.carry_flag:
                self.accumulator = self.accumulator | 0x100
            self.carry_flag = self.accumulator % 2
            self.accumulator = self.update_nz(self.accumulator >> 1)
        else:
            m = self.memory.read_byte(operand_address)
            if self.carry_flag:
                m = m | 0x100
            self.carry_flag = m % 2
            self.memory.write_byte(operand_address, self.update_nz(m >> 1))
    
    def LSR(self, operand_address=None):
        if operand_address is None:
            self.carry_flag = self.accumulator % 2
            self.accumulator = self.update_nz(self.accumulator >> 1)
        else:
            self.carry_flag = self.memory.read_byte(operand_address) % 2
            self.memory.write_byte(operand_address,  self.update_nz(self.memory.read_byte(operand_address) >> 1))
    
    # JUMPS / RETURNS
    
    def JMP(self, operand_address):
        self.program_counter = operand_address
    
    def JSR(self, operand_address):
        self.push_word(self.program_counter - 1)
        self.program_counter = operand_address
    
    def RTS(self):
        self.program_counter = self.pull_word() + 1
    
    # BRANCHES
    
    def BCC(self, operand_address):
        if not self.carry_flag:
            self.program_counter = operand_address
    
    def BCS(self, operand_address):
        if self.carry_flag:
            self.program_counter = operand_address
    
    def BEQ(self, operand_address):
        if self.zero_flag:
            self.program_counter = operand_address
    
    def BNE(self, operand_address):
        if not self.zero_flag:
            self.program_counter = operand_address
    
    def BMI(self, operand_address):
        if self.sign_flag:
            self.program_counter = operand_address
    
    def BPL(self, operand_address):
        if not self.sign_flag:
            self.program_counter = operand_address
    
    def BVC(self, operand_address):
        if not self.overflow_flag:
            self.program_counter = operand_address
    
    def BVS(self, operand_address):
        if self.overflow_flag:
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
        self.memory.write_byte(operand_address, self.update_nz(self.memory.read_byte(operand_address) - 1))
    
    def DEX(self):
        self.x_index = self.update_nz(self.x_index - 1)
    
    def DEY(self):
        self.y_index = self.update_nz(self.y_index - 1)
    
    def INC(self, operand_address):
        self.memory.write_byte(operand_address, self.update_nz(self.memory.read_byte(operand_address) + 1))
    
    def INX(self):
        self.x_index = self.update_nz(self.x_index + 1)
    
    def INY(self):
        self.y_index = self.update_nz(self.y_index + 1)
    
    # PUSH / PULL
    
    def PHA(self):
        self.push_byte(self.accumulator)
    
    def PHP(self):
        self.push_byte(self.status_as_byte())
    
    def PLA(self):
        self.accumulator = self.update_nz(self.pull_byte())
    
    def PLP(self):
        self.status_from_byte(self.pull_byte())
    
    # LOGIC
    
    def AND(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator & self.memory.read_byte(operand_address))
    
    def ORA(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator | self.memory.read_byte(operand_address))
    
    def EOR(self, operand_address):
        self.accumulator = self.update_nz(self.accumulator ^ self.memory.read_byte(operand_address))
    
    # ARITHMETIC
    
    def ADC(self, operand_address):
        # @@@ doesn't handle BCD yet
        assert not self.decimal_mode_flag
        
        a2 = self.accumulator
        a1 = signed(a2)
        m2 = self.memory.read_byte(operand_address)
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
        m2 = self.memory.read_byte(operand_address)
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
        value = self.memory.read_byte(operand_address)
        self.sign_flag = ((value >> 7) % 2) # bit 7
        self.overflow_flag = ((value >> 6) % 2) # bit 6
        self.zero_flag = [0, 1][((self.accumulator & value) == 0)]
    
    # COMPARISON
    
    def CMP(self, operand_address):
        result = self.accumulator - self.memory.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)
    
    def CPX(self, operand_address):
        result = self.x_index - self.memory.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)
    
    def CPY(self, operand_address):
        result = self.y_index - self.memory.read_byte(operand_address)
        self.carry_flag = [0, 1][(result >= 0)]
        self.update_nz(result)
    
    # SYSTEM
    
    def NOP(self):
        pass
    
    def BRK(self):
        self.push_word(self.program_counter + 1)
        self.push_byte(self.status_as_byte())
        self.program_counter = self.memory.read_word(0xFFFE)
        self.break_flag = 1
    
    def RTI(self):
        self.status_from_byte(self.pull_byte())
        self.program_counter = self.pull_word()
    
    
    # @@@ IRQ
    # @@@ NMI


if __name__ == "__main__":
    display = Display()
    mem = Memory(display)
    
    cpu = CPU(mem)
    cpu.run()
