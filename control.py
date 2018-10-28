from __future__ import print_function
import json
import sys
import urllib

URL_PREFIX = "http://localhost:6502"


def get(url):
    return json.loads(urllib.urlopen(URL_PREFIX + url).read())


def post(url, data=None):
    return urllib.urlopen(URL_PREFIX + url, json.dumps(data) if data is not None else "")


def value(s):
    if s.startswith("$"):
        return int(s[1:], 16)
    if s.startswith("0x"):
        return int(s[2:], 16)
    return int(s)


def format_disassemble(dis):
    r = "%04X-  " % dis["address"]
    for i in range(3):
        if i < len(dis["bytes"]):
            r += "%02X " % dis["bytes"][i]
        else:
            r += "   "
    r += " %s" % dis["mnemonic"]
    if "operand" in dis:
        r += "  %-10s" % dis["operand"]
        if "memory" in dis:
            r += "[%04X] = %0*X" % tuple(dis["memory"])
    return r


def cmd_disassemble(a):
    """Disassemble"""
    if len(a) > 1:
        addr = value(a[1])
    else:
        status = get("/status")
        addr = status["program_counter"]
    disasm = get("/disassemble/%d" % addr)
    for d in disasm:
        print(format_disassemble(d))


def cmd_dump(a):
    """Dump memory"""
    start = value(a[1])
    if len(a) > 2:
        end = value(a[2])
    else:
        end = start + 15
    data = get("/memory/%d-%d" % (start, end))
    addr = start & ~0xF
    while addr <= end:
        s = "%04X-" % addr
        for i in range(16):
            if start <= addr + i <= end:
                s += " %02X" % data[addr + i - start]
            else:
                s += "   "
        s += "  "
        for i in range(16):
            if start <= addr + i <= end:
                c = data[addr + i - start]

                # adjust for apple character set
                c &= 0x3f
                if c < 0x20:
                    c += 0x40

                if 0x20 <= c < 0x7f:
                    s += chr(c)
                else:
                    s += "."
            else:
                s += " "
        print(s)
        addr += 16


def cmd_help(a):
    """Help commands"""
    if len(a) > 1:
        f = Commands.get(a[1])
        if f is not None:
            print(f.__doc__)
        else:
            print("Unknown command:", a[1])
    else:
        print("Commands:")
        for c in sorted(Commands):
            print(" ", c)


def cmd_peek(a):
    """Peek memory location"""
    addr = value(a[1])
    dump = get("/memory/%d" % addr)
    print("%04X: %02X" % (addr, dump[0]))


def cmd_poke(a):
    """Poke memory location"""
    addr = value(a[1])
    val = value(a[2])
    post("/memory/%d" % addr, [val])


def cmd_status(a):
    """CPU status"""
    status = get("/status")
    print("A=%02X X=%02X Y=%02X S=%02X PC=%04X F=%c%c0%c%c%c%c%c" % (
        status["accumulator"],
        status["x_index"],
        status["y_index"],
        status["stack_pointer"],
        status["program_counter"],
        "N" if status["sign_flag"] else "n",
        "V" if status["overflow_flag"] else "v",
        "B" if status["break_flag"] else "b",
        "D" if status["decimal_mode_flag"] else "d",
        "I" if status["interrupt_disable_flag"] else "i",
        "Z" if status["zero_flag"] else "z",
        "C" if status["carry_flag"] else "c",
    ))
    disasm = get("/disassemble/%d" % status["program_counter"])
    print(format_disassemble(disasm[0]))


def cmd_quit(a):
    """Quit"""
    sys.exit(0)


def cmd_reset(a):
    """Reset"""
    post("/reset")

Commands = {
    "disassemble": cmd_disassemble,
    "dump": cmd_dump,
    "help": cmd_help,
    "peek": cmd_peek,
    "poke": cmd_poke,
    "status": cmd_status,
    "quit": cmd_quit,
    "reset": cmd_reset,
}


def main():
    print("ApplePy control console")
    while True:
        s = raw_input("6502> ")
        a = s.strip().split()
        f = Commands.get(a[0])
        if f is not None:
            f(a)
        else:
            print("Unknown command:", s)

if __name__ == "__main__":
    main()
