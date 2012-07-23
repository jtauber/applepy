ApplePy - an Apple ][ emulator in Python
========================================

by James Tauber / http://jtauber.com/

Originally written 2001, updated 2011

Apple ][ ROM available from http://www.easy68k.com/paulrsm/6502/index.html


Credits
-------

Some 6502 code came from contributions from Christiaan Kelly in 2007.

Greg Hewgill provided significant fixes and improvements to the 2011 version
(see the commit log for details).

The character generator bitmaps were entered by hand from visual inspection
of http://www.sbprojects.com/projects/apple1/terminal.php


Status
------

With original Apple ][ ROM it boots to the monitor, most monitor commands
work and you can go into Integer BASIC (with E000G or Ctrl-B RETURN) and
write and run programs. With an Apple ][+ ROM it boots to Applesoft Basic and
runs all the programs I've tried so far.

The only I/O supported is the keyboard and screen but 40-column text, LORES
and HIRES graphics are all supported.

ApplePy currently requires Pygame (although there is a minimal applepy_curses.py
that uses curses to display text mode only) and numpy (just for an array for
speaker sounds)
