from generic.cpu import signed


class BaseDisassemble(object):
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory

        self.setup_ops()

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

