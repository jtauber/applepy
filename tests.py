import unittest
from applepy import Memory, CPU


class TestMemory(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
    
    def test_load(self):
        self.memory.load(0x1000, [0x01, 0x02, 0x03])
        self.assertEqual(self.memory.read_byte(0x1000), 0x01)
        self.assertEqual(self.memory.read_byte(0x1001), 0x02)
        self.assertEqual(self.memory.read_byte(0x1002), 0x03)
    
    def test_write(self):
        self.memory.write_byte(0x1000, 0x11)
        self.memory.write_byte(0x1001, 0x12)
        self.memory.write_byte(0x1002, 0x13)
        self.assertEqual(self.memory.read_byte(0x1000), 0x11)
        self.assertEqual(self.memory.read_byte(0x1001), 0x12)
        self.assertEqual(self.memory.read_byte(0x1002), 0x13)


class TestLoadStoreOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
        self.memory.load(0x1000, [0x00, 0x01, 0x7F, 0x80, 0xFF])
    
    def test_LDA(self):
        self.cpu.LDA(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.LDA(0x1001)
        self.assertEqual(self.cpu.accumulator, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDA(0x1002)
        self.assertEqual(self.cpu.accumulator, 0x7F)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDA(0x1003)
        self.assertEqual(self.cpu.accumulator, 0x80)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDA(0x1004)
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_LDX(self):
        self.cpu.LDX(0x1000)
        self.assertEqual(self.cpu.x_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.LDX(0x1001)
        self.assertEqual(self.cpu.x_index, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDX(0x1002)
        self.assertEqual(self.cpu.x_index, 0x7F)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDX(0x1003)
        self.assertEqual(self.cpu.x_index, 0x80)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDX(0x1004)
        self.assertEqual(self.cpu.x_index, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_LDY(self):
        self.cpu.LDY(0x1000)
        self.assertEqual(self.cpu.y_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.LDY(0x1001)
        self.assertEqual(self.cpu.y_index, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDY(0x1002)
        self.assertEqual(self.cpu.y_index, 0x7F)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDY(0x1003)
        self.assertEqual(self.cpu.y_index, 0x80)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.LDY(0x1004)
        self.assertEqual(self.cpu.y_index, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_STA(self):
        self.cpu.accumulator = 0x37
        self.cpu.STA(0x2000)
        self.assertEqual(self.memory.read_byte(0x2000), 0x37)
    
    def test_STX(self):
        self.cpu.x_index = 0x38
        self.cpu.STX(0x2000)
        self.assertEqual(self.memory.read_byte(0x2000), 0x38)
    
    def test_STY(self):
        self.cpu.y_index = 0x39
        self.cpu.STY(0x2000)
        self.assertEqual(self.memory.read_byte(0x2000), 0x39)


class TestRegisterTransferOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_TAX(self):
        self.cpu.accumulator = 0x00
        self.cpu.TAX()
        self.assertEqual(self.cpu.x_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.accumulator = 0x01
        self.cpu.TAX()
        self.assertEqual(self.cpu.x_index, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.accumulator = 0xFF
        self.cpu.TAX()
        self.assertEqual(self.cpu.x_index, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_TAY(self):
        self.cpu.accumulator = 0x00
        self.cpu.TAY()
        self.assertEqual(self.cpu.y_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.accumulator = 0x01
        self.cpu.TAY()
        self.assertEqual(self.cpu.y_index, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.accumulator = 0xFF
        self.cpu.TAY()
        self.assertEqual(self.cpu.y_index, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_TXA(self):
        self.cpu.x_index = 0x00
        self.cpu.TXA()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.x_index = 0x01
        self.cpu.TXA()
        self.assertEqual(self.cpu.accumulator, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.x_index = 0xFF
        self.cpu.TXA()
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_TYA(self):
        self.cpu.y_index = 0x00
        self.cpu.TYA()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.y_index = 0x01
        self.cpu.TYA()
        self.assertEqual(self.cpu.accumulator, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.y_index = 0xFF
        self.cpu.TYA()
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)


class TestStackOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_TSX(self):
        s = self.cpu.stack_pointer
        self.cpu.TSX()
        self.assertEqual(self.cpu.x_index, s)
        # @@@ check NZ?
    
    def test_TXS(self):
        x = self.cpu.x_index
        self.cpu.TXS()
        self.assertEqual(self.cpu.stack_pointer, x)
    
    def test_PHA_and_PLA(self):
        self.cpu.accumulator = 0x00
        self.cpu.PHA()
        self.cpu.accumulator = 0x01
        self.cpu.PHA()
        self.cpu.accumulator = 0xFF
        self.cpu.PHA()
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.cpu.PLA()
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.cpu.PLA()
        self.assertEqual(self.cpu.accumulator, 0x01)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.cpu.PLA()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 0)
    
    def test_PHP_and_PLP(self):
        p = self.cpu.status_as_byte()
        self.cpu.PHP()
        self.cpu.status_from_byte(0xFF)
        self.cpu.PLP()
        self.assertEqual(self.cpu.status_as_byte(), p)


class TestLogicalOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_AND(self):
        self.memory.write_byte(0x1000, 0x37)
        self.cpu.accumulator = 0x34
        self.cpu.AND(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x34)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.cpu.accumulator = 0x40
        self.cpu.AND(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 0)
    
    def test_EOR(self):
        self.memory.write_byte(0x1000, 0x37)
        self.cpu.accumulator = 0x34
        self.cpu.EOR(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x03)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.cpu.accumulator = 0x90
        self.cpu.EOR(0x1000)
        self.assertEqual(self.cpu.accumulator, 0xA7)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.cpu.accumulator = 0x37
        self.cpu.EOR(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 0)
    
    def test_ORA(self):
        self.memory.write_byte(0x1000, 0x37)
        self.cpu.accumulator = 0x34
        self.cpu.ORA(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x37)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.cpu.accumulator = 0x90
        self.cpu.ORA(0x1000)
        self.assertEqual(self.cpu.accumulator, 0xB7)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.cpu.accumulator = 0x00
        self.cpu.ORA(0x1001)
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 0)
    
    def test_BIT(self):
        self.memory.write_byte(0x1000, 0x00)
        self.cpu.accumulator = 0x00
        self.cpu.BIT(0x1000)
        self.assertEqual(self.cpu.overflow_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.memory.write_byte(0x1000, 0x40)
        self.cpu.accumulator = 0x00
        self.cpu.BIT(0x1000)
        self.assertEqual(self.cpu.overflow_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.memory.write_byte(0x1000, 0x80)
        self.cpu.accumulator = 0x00
        self.cpu.BIT(0x1000)
        self.assertEqual(self.cpu.overflow_flag, 0)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.memory.write_byte(0x1000, 0xC0)
        self.cpu.accumulator = 0x00
        self.cpu.BIT(0x1000)
        self.assertEqual(self.cpu.overflow_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.memory.write_byte(0x1000, 0xC0)
        self.cpu.accumulator = 0xC0
        self.cpu.BIT(0x1000)
        self.assertEqual(self.cpu.overflow_flag, 1)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)


class TestArithmeticOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_ADC_without_BCD(self):
        
        ## test cases from http://www.6502.org/tutorials/vflag.html
        
        # 1 + 1 = 2  (C = 0; V = 0)
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0x01
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.ADC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x02)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.assertEqual(self.cpu.overflow_flag, 0)
        
        # 1 + -1 = 0  (C = 1; V = 0)
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0x01
        self.memory.write_byte(0x1000, 0xFF)
        self.cpu.ADC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.assertEqual(self.cpu.overflow_flag, 0)
        
        # 127 + 1 = 128  (C = 0; V = 1)
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0x7F
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.ADC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x80) # @@@
        self.assertEqual(self.cpu.carry_flag, 0)
        self.assertEqual(self.cpu.overflow_flag, 1)
        
        # -128 + -1 = -129  (C = 1; V = 1)
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0x80
        self.memory.write_byte(0x1000, 0xFF)
        self.cpu.ADC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x7F) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
        self.assertEqual(self.cpu.overflow_flag, 1)
        
        # 63 + 64 + 1 = 128  (C = 0; V = 1)
        self.cpu.carry_flag = 1
        self.cpu.accumulator = 0x3F
        self.memory.write_byte(0x1000, 0x40)
        self.cpu.ADC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x80)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.assertEqual(self.cpu.overflow_flag, 1)
    
    def test_SBC_without_BCD(self):
        self.cpu.accumulator = 0x02
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.SBC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.assertEqual(self.cpu.overflow_flag, 0)
        
        self.cpu.accumulator = 0x01
        self.memory.write_byte(0x1000, 0x02)
        self.cpu.SBC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.assertEqual(self.cpu.overflow_flag, 0) # @@@
        
        ## test cases from http://www.6502.org/tutorials/vflag.html
        
        # 0 - 1 = -1  (V = 0)
        self.cpu.carry_flag = 1
        self.cpu.accumulator = 0x00
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.SBC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0xFF)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.assertEqual(self.cpu.overflow_flag, 0) # @@@
        
        # -128 - 1 = -129  (V = 1)
        self.cpu.carry_flag = 1
        self.cpu.accumulator = 0x80
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.SBC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x7F)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.assertEqual(self.cpu.overflow_flag, 1)
        
        # 127 - -1 = 128  (V = 1)
        self.cpu.carry_flag = 1
        self.cpu.accumulator = 0x7F
        self.memory.write_byte(0x1000, 0xFF)
        self.cpu.SBC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x80)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.assertEqual(self.cpu.overflow_flag, 1)
        
        # -64 -64 -1 = -129  (V = 1)
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0xC0
        self.memory.write_byte(0x1000, 0x40)
        self.cpu.SBC(0x1000)
        self.assertEqual(self.cpu.accumulator, 0x7F)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.assertEqual(self.cpu.overflow_flag, 1) # @@@
    
    ## @@@ BCD versions still to do
    
    def test_CMP(self):
        self.cpu.accumulator = 0x0A
        self.memory.write_byte(0x1000, 0x09)
        self.cpu.CMP(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.accumulator = 0x0A
        self.memory.write_byte(0x1000, 0x0B)
        self.cpu.CMP(0x1000)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
        
        self.cpu.accumulator = 0x0A
        self.memory.write_byte(0x1000, 0x0A)
        self.cpu.CMP(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.accumulator = 0xA0
        self.memory.write_byte(0x1000, 0x0A)
        self.cpu.CMP(0x1000)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.accumulator = 0x0A
        self.memory.write_byte(0x1000, 0xA0)
        self.cpu.CMP(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0) # @@@
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
    
    def test_CPX(self):
        self.cpu.x_index = 0x0A
        self.memory.write_byte(0x1000, 0x09)
        self.cpu.CPX(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.x_index = 0x0A
        self.memory.write_byte(0x1000, 0x0B)
        self.cpu.CPX(0x1000)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
        
        self.cpu.x_index = 0x0A
        self.memory.write_byte(0x1000, 0x0A)
        self.cpu.CPX(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.x_index = 0xA0
        self.memory.write_byte(0x1000, 0x0A)
        self.cpu.CPX(0x1000)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.x_index = 0x0A
        self.memory.write_byte(0x1000, 0xA0)
        self.cpu.CPX(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0) # @@@
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
    
    def test_CPY(self):
        self.cpu.y_index = 0x0A
        self.memory.write_byte(0x1000, 0x09)
        self.cpu.CPY(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.y_index = 0x0A
        self.memory.write_byte(0x1000, 0x0B)
        self.cpu.CPY(0x1000)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
        
        self.cpu.y_index = 0x0A
        self.memory.write_byte(0x1000, 0x0A)
        self.cpu.CPY(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.y_index = 0xA0
        self.memory.write_byte(0x1000, 0x0A)
        self.cpu.CPY(0x1000)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 1)
        
        self.cpu.y_index = 0x0A
        self.memory.write_byte(0x1000, 0xA0)
        self.cpu.CPY(0x1000)
        self.assertEqual(self.cpu.sign_flag, 0) # @@@
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)


class TestIncrementDecrementOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_INC(self):
        self.memory.write_byte(0x1000, 0x00)
        self.cpu.INC(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.memory.write_byte(0x1000, 0x7F)
        self.cpu.INC(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x80)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.memory.write_byte(0x1000, 0xFF)
        self.cpu.INC(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
    
    def test_INX(self):
        self.cpu.x_index = 0x00
        self.cpu.INX()
        self.assertEqual(self.cpu.x_index, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.x_index = 0x7F
        self.cpu.INX()
        self.assertEqual(self.cpu.x_index, 0x80)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.x_index = 0xFF
        self.cpu.INX()
        self.assertEqual(self.cpu.x_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
    
    def test_INY(self):
        self.cpu.y_index = 0x00
        self.cpu.INY()
        self.assertEqual(self.cpu.y_index, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.y_index = 0x7F
        self.cpu.INY()
        self.assertEqual(self.cpu.y_index, 0x80)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.y_index = 0xFF
        self.cpu.INY()
        self.assertEqual(self.cpu.y_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
    
    def test_DEC(self):
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.DEC(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.memory.write_byte(0x1000, 0x80)
        self.cpu.DEC(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x7F)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.memory.write_byte(0x1000, 0x00)
        self.cpu.DEC(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_DEX(self):
        self.cpu.x_index = 0x01
        self.cpu.DEX()
        self.assertEqual(self.cpu.x_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.x_index = 0x80
        self.cpu.DEX()
        self.assertEqual(self.cpu.x_index, 0x7F)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.x_index = 0x00
        self.cpu.DEX()
        self.assertEqual(self.cpu.x_index, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)
    
    def test_DEY(self):
        self.cpu.y_index = 0x01
        self.cpu.DEY()
        self.assertEqual(self.cpu.y_index, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.cpu.y_index = 0x80
        self.cpu.DEY()
        self.assertEqual(self.cpu.y_index, 0x7F)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.cpu.y_index = 0x00
        self.cpu.DEY()
        self.assertEqual(self.cpu.y_index, 0xFF)
        self.assertEqual(self.cpu.sign_flag, 1)
        self.assertEqual(self.cpu.zero_flag, 0)


class TestShiftOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_ASL(self):
        self.cpu.accumulator = 0x01
        self.cpu.ASL()
        self.assertEqual(self.cpu.accumulator, 0x02)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.memory.write_byte(0x1000, 0x02)
        self.cpu.ASL(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x04)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
        self.cpu.accumulator = 0x80
        self.cpu.ASL()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
    
    def test_LSR(self):
        self.cpu.accumulator = 0x01
        self.cpu.LSR()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.LSR(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.accumulator = 0x80
        self.cpu.LSR()
        self.assertEqual(self.cpu.accumulator, 0x40)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0)
        self.assertEqual(self.cpu.carry_flag, 0)
    
    def test_ROL(self):
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0x80
        self.cpu.ROL()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1)
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.carry_flag = 1
        self.cpu.accumulator = 0x80
        self.cpu.ROL()
        self.assertEqual(self.cpu.accumulator, 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.carry_flag = 0
        self.memory.write_byte(0x1000, 0x80)
        self.cpu.ROL(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.carry_flag = 1
        self.memory.write_byte(0x1000, 0x80)
        self.cpu.ROL(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x01)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 0) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
    
    def test_ROR(self):
        self.cpu.carry_flag = 0
        self.cpu.accumulator = 0x01
        self.cpu.ROR()
        self.assertEqual(self.cpu.accumulator, 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.carry_flag = 1
        self.cpu.accumulator = 0x01
        self.cpu.ROR()
        self.assertEqual(self.cpu.accumulator, 0x80)
        self.assertEqual(self.cpu.sign_flag, 1) # @@@
        self.assertEqual(self.cpu.zero_flag, 0) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.carry_flag = 0
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.ROR(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x00)
        self.assertEqual(self.cpu.sign_flag, 0)
        self.assertEqual(self.cpu.zero_flag, 1) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)
        self.cpu.carry_flag = 1
        self.memory.write_byte(0x1000, 0x01)
        self.cpu.ROR(0x1000)
        self.assertEqual(self.memory.read_byte(0x1000), 0x80)
        self.assertEqual(self.cpu.sign_flag, 1) # @@@
        self.assertEqual(self.cpu.zero_flag, 0) # @@@
        self.assertEqual(self.cpu.carry_flag, 1)


class TestJumpCallOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_JMP(self):
        self.cpu.JMP(0x1000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
    
    def test_JSR(self):
        self.cpu.program_counter = 0x1000
        self.cpu.JSR(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
        self.assertEqual(self.memory.read_byte(self.cpu.STACK_PAGE + self.cpu.stack_pointer + 1), 0xFF)
        self.assertEqual(self.memory.read_byte(self.cpu.STACK_PAGE + self.cpu.stack_pointer + 2), 0x0F)
    
    def test_RTS(self):
        self.memory.write_byte(self.cpu.STACK_PAGE + 0xFF, 0x12)
        self.memory.write_byte(self.cpu.STACK_PAGE + 0xFE, 0x33)
        self.cpu.stack_pointer = 0xFD
        self.cpu.RTS()
        self.assertEqual(self.cpu.program_counter, 0x1234)
    
    def test_JSR_and_RTS(self):
        self.cpu.program_counter = 0x1000
        self.cpu.JSR(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
        self.cpu.RTS()
        self.assertEqual(self.cpu.program_counter, 0x1000) # @@@


class TestBranchOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_BCC(self):
        self.cpu.program_counter = 0x1000
        self.cpu.carry_flag = 1
        self.cpu.BCC(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.carry_flag = 0
        self.cpu.BCC(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BCS(self):
        self.cpu.program_counter = 0x1000
        self.cpu.carry_flag = 0
        self.cpu.BCS(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.carry_flag = 1
        self.cpu.BCS(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BEQ(self):
        self.cpu.program_counter = 0x1000
        self.cpu.zero_flag = 0
        self.cpu.BEQ(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.zero_flag = 1
        self.cpu.BEQ(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BMI(self):
        self.cpu.program_counter = 0x1000
        self.cpu.sign_flag = 0
        self.cpu.BMI(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.sign_flag = 1
        self.cpu.BMI(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BNE(self):
        self.cpu.program_counter = 0x1000
        self.cpu.zero_flag = 1
        self.cpu.BNE(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.zero_flag = 0
        self.cpu.BNE(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BPL(self):
        self.cpu.program_counter = 0x1000
        self.cpu.sign_flag = 1
        self.cpu.BPL(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.sign_flag = 0
        self.cpu.BPL(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BVC(self):
        self.cpu.program_counter = 0x1000
        self.cpu.overflow_flag = 1
        self.cpu.BVC(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.overflow_flag = 0
        self.cpu.BVC(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)
    
    def test_BVS(self):
        self.cpu.program_counter = 0x1000
        self.cpu.overflow_flag = 0
        self.cpu.BVS(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x1000)
        self.cpu.program_counter = 0x1000
        self.cpu.overflow_flag = 1
        self.cpu.BVS(0x2000)
        self.assertEqual(self.cpu.program_counter, 0x2000)


class TestStatusFlagOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_CLC(self):
        self.cpu.carry_flag = 1
        self.cpu.CLC()
        self.assertEqual(self.cpu.carry_flag, 0)
    
    def test_CLD(self):
        self.cpu.decimal_mode_flag = 1
        self.cpu.CLD()
        self.assertEqual(self.cpu.decimal_mode_flag, 0)
    
    def test_CLI(self):
        self.cpu.interrupt_disable_flag = 1
        self.cpu.CLI()
        self.assertEqual(self.cpu.interrupt_disable_flag, 0)
    
    def test_CLV(self):
        self.cpu.overflow_flag = 1
        self.cpu.CLV()
        self.assertEqual(self.cpu.overflow_flag, 0)
    
    def test_SEC(self):
        self.cpu.carry_flag = 0
        self.cpu.SEC()
        self.assertEqual(self.cpu.carry_flag, 1)
    
    def test_SED(self):
        self.cpu.decimal_mode_flag = 0
        self.cpu.SED()
        self.assertEqual(self.cpu.decimal_mode_flag, 1)
    
    def test_SEI(self):
        self.cpu.interrupt_disable_flag = 0
        self.cpu.SEI()
        self.assertEqual(self.cpu.interrupt_disable_flag, 1)


class TestSystemFunctionOperations(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_BRK(self):
        self.cpu.program_counter = 0x1000
        self.memory.rom.load(0xFFFE, [0x00, 0x20])
        status = self.cpu.status_as_byte()
        self.cpu.BRK()
        self.assertEqual(self.cpu.program_counter, 0x2000)
        self.assertEqual(self.cpu.break_flag, 1)
        self.assertEqual(self.memory.read_byte(self.cpu.STACK_PAGE + self.cpu.stack_pointer + 1), status)
        self.assertEqual(self.memory.read_byte(self.cpu.STACK_PAGE + self.cpu.stack_pointer + 2), 0x01)
        self.assertEqual(self.memory.read_byte(self.cpu.STACK_PAGE + self.cpu.stack_pointer + 3), 0x10)
    
    def test_RTI(self):
        self.memory.write_byte(self.cpu.STACK_PAGE + 0xFF, 0x12)
        self.memory.write_byte(self.cpu.STACK_PAGE + 0xFE, 0x33)
        self.memory.write_byte(self.cpu.STACK_PAGE + 0xFD, 0x20)
        self.cpu.stack_pointer = 0xFC
        self.cpu.RTI()
        self.assertEqual(self.cpu.program_counter, 0x1233)
        self.assertEqual(self.cpu.status_as_byte(), 0x20)
    
    def test_NOP(self):
        self.cpu.NOP()


class Test6502Bugs(unittest.TestCase):
    
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
    
    def test_zero_page_x(self):
        self.cpu.x_index = 0x01
        self.memory.load(0x1000, [0x00, 0x7F, 0xFF])
        self.cpu.program_counter = 0x1000
        self.assertEqual(self.cpu.zero_page_x_mode(), 0x01)
        self.assertEqual(self.cpu.zero_page_x_mode(), 0x80)
        self.assertEqual(self.cpu.zero_page_x_mode(), 0x00)
    
    def test_indirect(self):
        self.memory.load(0x20, [0x00, 0x20])
        self.memory.load(0x00, [0x12])
        self.memory.load(0xFF, [0x34])
        self.memory.load(0x100, [0x56])
        self.memory.load(0x1000, [0x20, 0x20, 0xFF, 0xFF, 0x00, 0x45, 0x23])
        self.memory.load(0x2000, [0x05])
        self.memory.load(0x1234, [0x05])
        self.memory.load(0x2345, [0x00, 0xF0])
        
        self.cpu.program_counter = 0x1000
        
        self.cpu.x_index = 0x00
        self.cpu.LDA(self.cpu.indirect_x_mode())
        self.assertEqual(self.cpu.accumulator, 0x05)
        
        self.cpu.y_index = 0x00
        self.cpu.LDA(self.cpu.indirect_y_mode())
        self.assertEqual(self.cpu.accumulator, 0x05)
        
        self.cpu.y_index = 0x00
        self.cpu.LDA(self.cpu.indirect_y_mode())
        self.assertEqual(self.cpu.accumulator, 0x05)
        
        self.cpu.x_index = 0x00
        self.cpu.LDA(self.cpu.indirect_x_mode())
        self.assertEqual(self.cpu.accumulator, 0x05)
        
        self.cpu.x_index = 0xFF
        self.cpu.LDA(self.cpu.indirect_x_mode())
        self.assertEqual(self.cpu.accumulator, 0x05)
        
        self.assertEqual(self.cpu.indirect_mode(), 0xF000)


if __name__ == "__main__":
    unittest.main()
