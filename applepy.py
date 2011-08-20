# ApplePy - an Apple ][ emulator in Python
# James Tauber / http://jtauber.com/
# originally written 2001, updated 2011


import numpy
import pygame
import struct
import subprocess
import sys
import time
import wave


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
        self.mix = False
        self.flash_time = time.time()
        self.flash_on = False
        self.flash_chars = [[0] * 0x400] * 2
        
        self.chargen = []
        for c in self.characters:
            chars = [[pygame.Surface((14, 16)), pygame.Surface((14, 16))],
                     [pygame.Surface((14, 16)), pygame.Surface((14, 16))]]
            for colour in (0, 1):
                hue = (255, 255, 255) if colour else (0, 200, 0)
                for inv in (0, 1):
                    pixels = pygame.PixelArray(chars[colour][inv])
                    off = hue if inv else (0, 0, 0)
                    on = (0, 0, 0) if inv else hue
                    for row in range(8):
                        b = c[row] << 1
                        for col in range(7):
                            bit = (b >> (6 - col)) & 1
                            pixels[2 * col][2 * row] = on if bit else off
                            pixels[2 * col + 1][2 * row] = on if bit else off
                    del pixels
            self.chargen.append(chars)
    
    def txtclr(self):
        self.text = False
    
    def txtset(self):
        self.text = True
        self.colour = False
    
    def mixclr(self):
        self.mix = False
    
    def mixset(self):
        self.mix = True
        self.colour = True
    
    def lowscr(self):
        self.page = 1
    
    def hiscr(self):
        self.page = 2
    
    def lores(self):
        self.high_res = False
    
    def hires(self):
        self.high_res = True
    
    def update(self, address, value):
        if self.page == 1:
            start_text = 0x400
            start_hires = 0x2000
        elif self.page == 2:
            start_text = 0x800
            start_hires = 0x4000
        else:
            return
        
        if start_text <= address <= start_text + 0x3FF:
            base = address - start_text
            self.flash_chars[self.page - 1][base] = value
            hi, lo = divmod(base, 0x80)
            row_group, column  = divmod(lo, 0x28)
            row = hi + 8 * row_group
            
            if row_group == 3:
                return
            
            if self.text or not self.mix or not row < 20:
                mode, ch = divmod(value, 0x40)
                
                if mode == 0:
                    inv = True
                elif mode == 1:
                    inv = self.flash_on
                else:
                    inv = False
                
                self.screen.blit(self.chargen[ch][self.colour][inv], (2 * (column * 7), 2 * (row * 8)))
            else:
                pixels = pygame.PixelArray(self.screen)
                if not self.high_res:
                    lower, upper = divmod(value, 0x10)
                    
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
            
        elif start_hires <= address <= start_hires + 0x1FFF:
            if self.high_res:
                base = address - start_hires
                row8, b = divmod(base, 0x400)
                hi, lo = divmod(b, 0x80)
                row_group, column  = divmod(lo, 0x28)
                row = 8 * (hi + 8 * row_group) + row8
                
                if self.mix and row >= 160:
                    return
                
                if row < 192 and column < 40:
                    
                    pixels = pygame.PixelArray(self.screen)
                    msb = value // 0x80
                    
                    for b in range(7):
                        c = value & (1 << b)
                        xx = (column * 7 + b)
                        x = 2 * xx
                        y = 2 * row
                        
                        if msb:
                            if xx % 2:
                                pixels[x][y] = (0, 0, 0)
                                # orange
                                pixels[x + 1][y] = (255, 192, 0) if c else (0, 0, 0)
                            else:
                                # blue
                                pixels[x][y] = (0, 192, 255) if c else (0, 0, 0)
                                pixels[x + 1][y] = (0, 0, 0)
                        else:
                            if xx % 2:
                                pixels[x][y] = (0, 0, 0)
                                # green
                                pixels[x + 1][y] = (0, 255, 0) if c else (0, 0, 0)
                            else:
                                # violet
                                pixels[x][y] = (255, 0, 255) if c else (0, 0, 0)
                                pixels[x + 1][y] = (0, 0, 0)
                                
                        pixels[x][y + 1] = (0, 0, 0)
                        pixels[x + 1][y + 1] = (0, 0, 0)
                        
                    del pixels

    def flash(self):
        if time.time() - self.flash_time >= 0.5:
            self.flash_on = not self.flash_on
            for offset, char in enumerate(self.flash_chars[self.page - 1]):
                if (char & 0xC0) == 0x40:
                    self.update(0x400 + offset, char)
            self.flash_time = time.time()


class Speaker:
    
    CPU_CYCLES_PER_SAMPLE = 60
    CHECK_INTERVAL = 1000
    
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1)
        pygame.init()
        self.reset()
    
    def toggle(self, cycle):
        if self.last_toggle is not None:
            l = (cycle - self.last_toggle) / Speaker.CPU_CYCLES_PER_SAMPLE
            self.buffer.extend([0, 0.8] if self.polarity else [0, -0.8])
            self.buffer.extend((l - 2) * [0.5] if self.polarity else [-0.5])
            self.polarity = not self.polarity
        self.last_toggle = cycle
    
    def reset(self):
        self.last_toggle = None
        self.buffer = []
        self.polarity = False
    
    def play(self):
        sample_array = numpy.array(self.buffer)
        sound = pygame.sndarray.make_sound(sample_array)
        sound.play()
        self.reset()
    
    def update(self, cycle):
        if self.buffer and (cycle - self.last_toggle) > self.CHECK_INTERVAL:
            self.play()


class Cassette:

    def __init__(self, fn):
        wav = wave.open(fn, "r")
        self.raw = wav.readframes(wav.getnframes())
        self.start_cycle = 0
        self.start_offset = 0

        for i, b in enumerate(self.raw):
            if ord(b) > 0xA0:
                self.start_offset = i
                break

    def read_byte(self, cycle):
        if self.start_cycle == 0:
            self.start_cycle = cycle
        offset = self.start_offset + (cycle - self.start_cycle) * 22000 / 1000000
        return ord(self.raw[offset]) if offset < len(self.raw) else 0x80


class IO:
    
    def __init__(self, display, speaker, cassette):
        self.kbd = 0x00
        self.display = display
        self.speaker = speaker
        self.cassette = cassette
        self.slots = [None] * 8
    
    def add_card(self, slot, card):
        assert 0 < slot < 8
        self.slots[slot] = card
    
    def read_byte(self, cycle, address):
        assert 0xC000 <= address <= 0xCFFF
        if 0xC080 <= address <= 0xC0FF:
            slot, switch = divmod(address - 0xC080, 0x10)
            if self.slots[slot] is not None:
                return self.slots[slot].switch(cycle, switch)
            else:
                print "%04X" % address
                return 0x00
        elif 0xC100 <= address <= 0xC7FF:
            hi, lo = divmod(address, 0x100)
            slot = hi - 0xC0
            if self.slots[slot] is not None:
                return self.slots[slot].read_byte(lo)
            else:
                print "%04X" % address
                return 0x00
        elif address == 0xC000:
            return self.kbd
        elif address == 0xC010:
            self.kbd = self.kbd & 0x7F
        elif address == 0xC030:
            if self.speaker:
                self.speaker.toggle(cycle)
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
        elif address == 0xC060:
            if self.cassette:
                return self.cassette.read_byte(cycle)
        else:
            pass # print "%04X" % address
        return 0x00


class DiskController:
    
    # 16-sector controller
    ROM = [
        0xa2, 0x20, 0xa0, 0x00, 0xa2, 0x03, 0x86, 0x3c,
        0x8a, 0x0a, 0x24, 0x3c, 0xf0, 0x10, 0x05, 0x3c,
        0x49, 0xff, 0x29, 0x7e, 0xb0, 0x08, 0x4a, 0xd0,
        0xfb, 0x98, 0x9d, 0x56, 0x03, 0xc8, 0xe8, 0x10,
        0xe5, 0x20, 0x58, 0xff, 0xba, 0xbd, 0x00, 0x01,
        0x0a, 0x0a, 0x0a, 0x0a, 0x85, 0x2b, 0xaa, 0xbd,
        0x8e, 0xc0, 0xbd, 0x8c, 0xc0, 0xbd, 0x8a, 0xc0,
        0xbd, 0x89, 0xc0, 0xa0, 0x50, 0xbd, 0x80, 0xc0,
        0x98, 0x29, 0x03, 0x0a, 0x05, 0x2b, 0xaa, 0xbd,
        0x81, 0xc0, 0xa9, 0x56, 0x20, 0xa8, 0xfc, 0x88,
        0x10, 0xeb, 0x85, 0x26, 0x85, 0x3d, 0x85, 0x41,
        0xa9, 0x08, 0x85, 0x27, 0x18, 0x08, 0xbd, 0x8c,
        0xc0, 0x10, 0xfb, 0x49, 0xd5, 0xd0, 0xf7, 0xbd,
        0x8c, 0xc0, 0x10, 0xfb, 0xc9, 0xaa, 0xd0, 0xf3,
        0xea, 0xbd, 0x8c, 0xc0, 0x10, 0xfb, 0xc9, 0x96,
        0xf0, 0x09, 0x28, 0x90, 0xdf, 0x49, 0xad, 0xf0,
        0x25, 0xd0, 0xd9, 0xa0, 0x03, 0x85, 0x40, 0xbd,
        0x8c, 0xc0, 0x10, 0xfb, 0x2a, 0x85, 0x3c, 0xbd,
        0x8c, 0xc0, 0x10, 0xfb, 0x25, 0x3c, 0x88, 0xd0,
        0xec, 0x28, 0xc5, 0x3d, 0xd0, 0xbe, 0xa5, 0x40,
        0xc5, 0x41, 0xd0, 0xb8, 0xb0, 0xb7, 0xa0, 0x56,
        0x84, 0x3c, 0xbc, 0x8c, 0xc0, 0x10, 0xfb, 0x59,
        0xd6, 0x02, 0xa4, 0x3c, 0x88, 0x99, 0x00, 0x03,
        0xd0, 0xee, 0x84, 0x3c, 0xbc, 0x8c, 0xc0, 0x10,
        0xfb, 0x59, 0xd6, 0x02, 0xa4, 0x3c, 0x91, 0x26,
        0xc8, 0xd0, 0xef, 0xbc, 0x8c, 0xc0, 0x10, 0xfb,
        0x59, 0xd6, 0x02, 0xd0, 0x87, 0xa0, 0x00, 0xa2,
        0x56, 0xca, 0x30, 0xfb, 0xb1, 0x26, 0x5e, 0x00,
        0x03, 0x2a, 0x5e, 0x00, 0x03, 0x2a, 0x91, 0x26,
        0xc8, 0xd0, 0xee, 0xe6, 0x27, 0xe6, 0x3d, 0xa5,
        0x3d, 0xcd, 0x00, 0x08, 0xa6, 0x2b, 0x90, 0xdb,
        0x4c, 0x01, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    
    def __init__(self):
        self.phases = [0, 0, 0, 0]
        self.track_index = 11
    
    def switch(self, cycle, address):
        assert 0x00 <= address <= 0x0F
        if 0x00 <= address <= 0x07:
            phase, on = divmod(address, 2)
            self.phases[phase] = on
            
            current_phase = self.track_index & 0x7
            if self.phases == [1, 0, 0, 0] or self.phases == [1, 1, 0, 1]:
                next_phase = 0
            elif self.phases == [1, 1, 0, 0]:
                next_phase = 1
            elif self.phases == [0, 1, 0, 0] or self.phases == [1, 1, 1, 0]:
                next_phase = 2
            elif self.phases == [0, 1, 1, 0]:
                next_phase = 3
            elif self.phases == [0, 0, 1, 0] or self.phases == [0, 1, 1, 1]:
                next_phase = 4
            elif self.phases == [0, 0, 1, 1]:
                next_phase = 5
            elif self.phases == [0, 0, 0, 1] or self.phases == [1, 0, 1, 1]:
                next_phase = 6
            elif self.phases == [1, 0, 0, 1]:
                next_phase = 7
            else: # [0, 0, 0, 0] [1, 0, 1, 0] [0, 1, 0, 1] [1, 1, 1, 1]
                next_phase = current_phase
            
            phase_difference = ((next_phase - current_phase + 4) & 0x7) - 4
            self.track_index += phase_difference
            if self.track_index < 0:
                self.track_index = 0
            if self.track_index > 69:
                self.track_index = 69
            print "TRACK", self.track_index, phase_difference
            raw_input()
            
        elif address == 0x09:
            print "motor on"
        elif address == 0x0A:
            print "select drive 1"
        elif address == 0x0C:
            pass # print "read data"
        elif address == 0x0E:
            print "set read"
        else:
            pass # print "%d %04X" % (cycle, 0xC080 + address)
        return 0x00
    
    def read_byte(self, address):
        assert 0x00 <= address <= 0xFF
        return DiskController.ROM[address]


class Apple2:

    def __init__(self, options, display, speaker, cassette):
        self.display = display
        self.speaker = speaker
        self.io = IO(display, speaker, cassette)
        self.io.add_card(6, DiskController())

        args = [
            sys.executable,
            "cpu6502.py",
            "--rom", options.rom,
        ]
        if options.ram:
            args.extend([
                "--ram", options.ram,
            ])
        self.core = subprocess.Popen(
            args=args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def run(self):
        update_cycle = 0
        quit = False
        while not quit:
            op = self.core.stdout.read(8)
            cycle, rw, addr, val = struct.unpack("<IBHB", op)
            if rw == 0:
                self.core.stdin.write(chr(self.io.read_byte(cycle, addr)))
                self.core.stdin.flush()
            elif rw == 1:
                self.display.update(addr, val)
            else:
                break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True
                
                if event.type == pygame.KEYDOWN:
                    key = ord(event.unicode) if event.unicode else 0
                    if event.key == pygame.K_LEFT:
                        key = 0x08
                    if event.key == pygame.K_RIGHT:
                        key = 0x15
                    if key:
                        if key == 0x7F:
                            key = 0x08
                        self.io.kbd = 0x80 + key
            
            update_cycle += 1
            if update_cycle >= 1024:
                self.display.flash()
                pygame.display.flip()
                if self.speaker:
                    self.speaker.update(cycle)
                update_cycle = 0
    

def usage():
    print >>sys.stderr, "ApplePy - an Apple ][ emulator in Python"
    print >>sys.stderr, "James Tauber / http://jtauber.com/"
    print >>sys.stderr
    print >>sys.stderr, "Usage: applepy.py [options]"
    print >>sys.stderr
    print >>sys.stderr, "    -c, --cassette Cassette wav file to load"
    print >>sys.stderr, "    -R, --rom      ROM file to use (default A2ROM.BIN)"
    print >>sys.stderr, "    -r, --ram      RAM file to load (default none)"
    print >>sys.stderr, "    -q, --quiet    Quiet mode, no sounds (default sounds)"
    sys.exit(1)


def get_options():
    class Options:
        def __init__(self):
            self.cassette = None
            self.rom = "A2ROM.BIN"
            self.ram = None
            self.quiet = False

    options = Options()
    a = 1
    while a < len(sys.argv):
        if sys.argv[a].startswith("-"):
            if sys.argv[a] in ("-c", "--cassette"):
                a += 1
                options.cassette = sys.argv[a]
            elif sys.argv[a] in ("-R", "--rom"):
                a += 1
                options.rom = sys.argv[a]
            elif sys.argv[a] in ("-r", "--ram"):
                a += 1
                options.ram = sys.argv[a]
            elif sys.argv[a] in ("-q", "--quiet"):
                options.quiet = True
            else:
                usage()
        else:
            usage()
        a += 1

    return options


if __name__ == "__main__":
    options = get_options()
    display = Display()
    speaker = None if options.quiet else Speaker()
    cassette = Cassette(options.cassette) if options.cassette else None

    apple = Apple2(options, display, speaker, cassette)
    apple.run()
