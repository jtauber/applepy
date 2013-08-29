from generic.generic_config import BaseConfig

class Dragon32Config(BaseConfig):
    """
    FIXME: Wrong values here?


    max Memory is 64KB ($FFFF Bytes)

    32 kB RAM ($0000-$7FFF)
    16 kB ROM ($8000-$BFFF)
    ~16 kB free/reseved ($C000-$FEFF)
    $FF00-$FFFF 6883-SAM / PIA
    """
    # Memory
    RAM_START = 0x0000
    RAM_SIZE = 0x7FFF
    RAM_END = RAM_START + RAM_SIZE

    ROM_START = 0x8000
    ROM_SIZE = 0x4000
    ROM_END = ROM_START + ROM_SIZE

    # CPU
    STACK_PAGE = 0x100
#     RESET_VECTOR = 0xb44f
    RESET_VECTOR = 0xB3B4
#     RESET_VECTOR = 0xfffe

    HTTPSERVER_PORT = 6809

    CPU_MODULE = "Dragon32.cpu6809"

    KEY_LEFT = 0x08 # ???
    KEY_RIGHT = 0x15 # ???


if __name__ == "__main__":
    cfg = Dragon32Config()
    cfg.print_debug_info()
