import BaseHTTPServer
import re
import json
import select
import sys


def signed(x):
    if x > 0x7F:
        x = x - 0x100
    return x


class ControlHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server, cpu, disassemble):
        self.cpu = cpu
        self.disassemble = disassemble

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

    def __init__(self, cpu, disassemble):
        self.cpu = cpu
        self.disassemble = disassemble

    def __call__(self, request, client_address, server):
        return ControlHandler(
            request, client_address, server, self.cpu, self.disassemble
        )


class BaseCPU(object):

    def __init__(self, cfg, bus, options, memory, DisassembleClass):
        self.cfg = cfg
        self.bus = bus
        self.memory = memory

        disassemble = DisassembleClass(self, memory)

        self.control_server = BaseHTTPServer.HTTPServer(
            (self.cfg.LOCAL_HOST_IP, self.cfg.HTTPSERVER_PORT),
            ControlHandlerFactory(self, disassemble)
        )

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

        self.cycles = 0

        self.setup_ops()
        self.reset()
        if options.pc is not None:
            self.program_counter = options.pc
        self.running = True
        self.quit = False


    def reset(self):
        self.program_counter = self.read_word(self.cfg.RESET_VECTOR)

    def run(self):
        sys.stdout.flush()
        while not self.quit:

            timeout = 0
            if not self.running:
                timeout = 1
            # Currently this handler blocks from the moment
            # a connection is accepted until the response
            # is sent. TODO: use an async HTTP server that
            # handles input data asynchronously.
            sockets = [self.control_server]
            rs, _, _ = select.select(sockets, [], [], timeout)
            for s in rs:
                if s is self.control_server:
                    self.control_server._handle_request_noblock()
                else:
                    pass

            count = 1000
            while count > 0 and self.running:
                self.cycles += 2 # all instructions take this as a minimum
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
            self.cycles += 2 # all instructions take this as a minimum
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
        self.write_byte(self.cfg.STACK_PAGE + self.stack_pointer, byte)
        self.stack_pointer = (self.stack_pointer - 1) % 0x100

    def pull_byte(self):
        self.stack_pointer = (self.stack_pointer + 1) % 0x100
        return self.read_byte(self.cfg.STACK_PAGE + self.stack_pointer)

    def push_word(self, word):
        hi, lo = divmod(word, 0x100)
        self.push_byte(hi)
        self.push_byte(lo)

    def pull_word(self):
        s = self.cfg.STACK_PAGE + self.stack_pointer + 1
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
        self.sign_flag = ((value >> 7) % 2) # bit 7
        self.overflow_flag = ((value >> 6) % 2) # bit 6
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
