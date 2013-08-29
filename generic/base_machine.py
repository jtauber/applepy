import socket
import sys
import subprocess
import select
import struct
import pygame


class BaseMachine(object):
    def __init__(self, cfg, options, display, speaker, softswitches):
        self.cfg = cfg
        self.display = display
        self.speaker = speaker
        self.softswitches = softswitches


        listener = socket.socket()
        listener.bind((self.cfg.LOCAL_HOST_IP, 0))
        listener.listen(0)
        bus_port = listener.getsockname()[1]

        print "bus I/O listen on %s:%s" % (self.cfg.LOCAL_HOST_IP, bus_port)

        cpu_script = cfg.get_cpu_script()

        args = [
            sys.executable,
            cpu_script,
            "--bus", str(bus_port),
            "--rom", options.rom,
        ]
        if options.ram:
            args.extend([
                "--ram", options.ram,
            ])
        if options.pc is not None:
            args.extend([
                "--pc", str(options.pc),
            ])
        self.core = subprocess.Popen(args)

        rs, _, _ = select.select([listener], [], [], 2)
        if not rs:
            print >> sys.stderr, "CPU module did not start '%s'" % " ".join(args)
            sys.exit(1)
        self.cpu, _ = listener.accept()

    def run(self):
        sys.stdout.flush()
        update_cycle = 0
        quit = False
        while not quit:
            op = self.cpu.recv(8)
            if len(op) == 0:
                break
            cycle, rw, addr, val = struct.unpack("<IBHB", op)
            if rw == 0:
                self.cpu.send(chr(self.softswitches.read_byte(cycle, addr)))
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
                        key = self.cfg.KEY_LEFT
                    if event.key == pygame.K_RIGHT:
                        key = self.cfg.KEY_RIGHT
                    if key:
                        if key == 0x7F:
                            key = self.cfg.KEY_LEFT
                        self.softswitches.kbd = 0x80 + (key & 0x7F)

            update_cycle += 1
            if update_cycle >= 1024:
                self.display.flash()
                pygame.display.flip()
                if self.speaker:
                    self.speaker.update(cycle)
                update_cycle = 0
