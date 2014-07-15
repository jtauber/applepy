# ApplePy - an Apple ][ emulator in Python
# James Tauber / http://jtauber.com/
# originally written 2001, updated 2011


import curses
import socket
import struct
import subprocess
import sys


kbd = 0


def write_screen(win, address, value):
    base = address - 0x400
    hi, lo = divmod(base, 0x80)
    row_group, column = divmod(lo, 0x28)
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

    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(0)

    args = [
        sys.executable,
        "cpu6502.py",
        "--bus", str(listener.getsockname()[1]),
        "--rom", options.rom,
    ]

    subprocess.Popen(args)
    cpu, _ = listener.accept()

    win.clear()
    curses.noecho()
    win.nodelay(True)
    while True:
        op = cpu.recv(8)
        cycle, rw, addr, val = struct.unpack("<IBHB", op)
        if rw == 0:
            cpu.send(chr(read(addr, val)))
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


def usage():
    print >>sys.stderr, "ApplePy - an Apple ][ emulator in Python"
    print >>sys.stderr, "James Tauber / http://jtauber.com/"
    print >>sys.stderr
    print >>sys.stderr, "Usage: applepy_curses.py [options]"
    print >>sys.stderr
    print >>sys.stderr, "    -R, --rom      ROM file to use (default A2ROM.BIN)"
    sys.exit(1)


def get_options():
    class Options:
        def __init__(self):
            self.rom = "A2ROM.BIN"

    options = Options()
    a = 1
    while a < len(sys.argv):
        if sys.argv[a].startswith("-"):
            if sys.argv[a] in ("-R", "--rom"):
                a += 1
                options.rom = sys.argv[a]
            else:
                usage()
        else:
            usage()
        a += 1

    return options


if __name__ == "__main__":
    options = get_options()
    curses.wrapper(run)
