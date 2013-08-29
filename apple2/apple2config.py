
from generic.generic_config import BaseConfig


class Apple2Config(BaseConfig):
    # Memory
    ROM_START = 0xD000
    ROM_SIZE = 0x3000
    ROM_END = ROM_START + ROM_SIZE # 0x10000

    RAM_START = 0x0000
    RAM_SIZE = 0xC000
    RAM_END = RAM_START + RAM_SIZE # 0xc000

    # CPU
    STACK_PAGE = 0x100
    RESET_VECTOR = 0xFFFC

    HTTPSERVER_PORT = 6502

    CPU_MODULE = "apple2.cpu6502"

    KEY_LEFT = 0x08
    KEY_RIGHT = 0x15


if __name__ == "__main__":
    cfg = Apple2Config()
    cfg.print_debug_info()
    print "CPU script:", cfg.get_cpu_script()
