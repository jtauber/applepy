# ApplePy - an Apple ][ emulator in Python
# James Tauber / http://jtauber.com/
# originally written 2001, updated 2011


import curses
import struct
import subprocess
import sys


kbd = 0


def write_screen(win, address, value):
    base = address - 0x400
    hi, lo = divmod(base, 0x80)
    row_group, column  = divmod(lo, 0x28)
    row = hi + 8 * row_group
    
    # skip if writing to row group 3
    if row_group == 3:
        return
    
    c = chr(0x20 + ((value + 0x20) % 0x40))
    
    if value < 0x40:
        attr = curses.A_DIM
    elif value < 0x80:
        attr = curses.A_REVERSE
    elif value < 0xA0:
        attr = curses.A_UNDERLINE
    else:
        attr = curses.A_DIM
    
    try:
        win.addch(row, column, c, attr)
    except curses.error:
        pass


def read(addr, val):
    global kbd
    if addr == 0xC000:
        return kbd
    elif addr == 0xC010:
        kbd = kbd & 0x7F
    return 0x00


def write(win, addr, val):
    if 0x400 <= addr <= 0x800:
        write_screen(win, addr, val)


def run(win):
    global kbd
    p = subprocess.Popen(
        args=[sys.executable, "cpu6502.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    win.clear()
    curses.noecho()
    win.nodelay(True)
    while True:
        op = p.stdout.read(8)
        cycle, rw, addr, val = struct.unpack("<IBHB", op)
        if rw == 0:
            p.stdin.write(chr(read(addr, val)))
            p.stdin.flush()
        elif rw == 1:
            write(win, addr, val)
        else:
            break
        try:
            key = ord(win.getkey())
            if key == 0xA:
                key = 0xD
            elif key == 0x7F:
                key = 0x8
            # win.addstr(15, 50, hex(key))
            kbd = 0x80 | key
        except curses.error:
            pass
        except TypeError:
            pass


if __name__ == "__main__":
    curses.wrapper(run)
