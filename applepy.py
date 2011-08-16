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

    def read_byte(self, cycle):
        sys.stdout.write(str(cycle * 22000 / 1000000) + "\r")
        return ord(self.raw[cycle * 22000 / 1000000])


class SoftSwitches:
    
    def __init__(self, display, speaker, cassette):
        self.kbd = 0x00
        self.display = display
        self.speaker = speaker
        self.cassette = cassette
    
    def read_byte(self, cycle, address):
        assert 0xC000 <= address <= 0xCFFF
        if address == 0xC000:
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
            return self.cassette.read_byte(cycle)
        else:
            pass # print "%04X" % address
        return 0x00


class Apple2:

    def __init__(self, options, display, speaker, cassette):
        self.display = display
        self.speaker = speaker
        self.softswitches = SoftSwitches(display, speaker, cassette)

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
                self.core.stdin.write(chr(self.softswitches.read_byte(cycle, addr)))
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
                        self.softswitches.kbd = 0x80 + key
            
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
    print >>sys.stderr, "    -R, --rom      ROM file to use (default A2ROM.BIN)"
    print >>sys.stderr, "    -r, --ram      RAM file to load (default none)"
    print >>sys.stderr, "    -q, --quiet    Quiet mode, no sounds (default sounds)"
    sys.exit(1)


def get_options():
    class Options:
        def __init__(self):
            self.rom = "A2ROM.BIN"
            self.ram = None
            self.quiet = False

    options = Options()
    a = 1
    while a < len(sys.argv):
        if sys.argv[a].startswith("-"):
            if sys.argv[a] in ("-R", "--rom"):
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
    cassette = Cassette("k7_apple_600202300_littlebrickout.wav")

    apple = Apple2(options, display, speaker, cassette)
    apple.run()
