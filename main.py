#!/usr/bin/env python
import sys
import termios
import os
import struct
import fcntl

def isctrl(char):
	if len(char) is 0:
		return False
	return ord(char) < 32 or ord(char) > 126

def ctrl_key(char):
	return (ord(char) & (0x1f))

class Key(object):
	PAGE_UP = 1000
	PAGE_DOWN = 1001
	ARROW_LEFT = 1002
	ARROW_RIGHT = 1003
	ARROW_UP = 1004
	ARROW_DOWN = 1005

	
class Editor(object):
	def write(self, content):
		self.buffer += content

	def draw(self):
		wrote = os.write(sys.stdout.fileno(), self.buffer)
		self.buffer = ""
	
	def enable_raw_mode(self):
		self.orig_termios = termios.tcgetattr(sys.stdin.fileno())
		#formatted like this: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
		new = termios.tcgetattr(sys.stdin)
		new[0] &= ~(termios.IXON | termios.ICRNL | termios.BRKINT | termios.ISTRIP | termios.INPCK)
		new[1] &= ~(termios.OPOST)
		new[2] |=  (termios.CS8)
		new[3] &= ~(termios.ECHO | termios.ICANON | termios.ISIG | termios.IEXTEN)
		new[6][termios.VMIN] = 0
		new[6][termios.VTIME] = 1;
		termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, new)

	def disable_raw_mode(self):
		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.orig_termios)

	def read_key(self):
		while True:
			char = sys.stdin.read(1)
			if len(char) is 0:
				continue
			else:
				if char == "\x1b":
					seq = sys.stdin.read(1)
					if len(seq) != 1:
						return "\x1b"
					seq += sys.stdin.read(1)
					if len(seq) != 2:
						return "\x1b"
					if seq[0] == "[":
						if seq[1] == "A":
							return "w"
						elif seq[1] == "B":
							return "s"
						elif seq[1] == "C":
							return "d"
						elif seq[1] == "D":
							return "a"
				return char

	def move_cursor(self, char):
		if char == "a":
			if self.cx != 0:
				self.cx -= 1
		elif char == "d":
			if self.cx != self.cols - 1:
				self.cx += 1
		elif char == "w":
			if self.cy != 0:
				self.cy -= 1
		elif char == "s":
			if self.cy != self.rows - 1:
				self.cy += 1

	def process_keypress(self):
		char = self.read_key()
		if ord(char) == ctrl_key('q'):
			self.cleanup()
		if char == "a" or char == "s" or char == "d" or char == "w":
			self.move_cursor(char)

	def get_window_size(self):
		winsize = struct.pack('HHHH', 0, 0, 0, 0)
		try:
			ws = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, winsize)
		except:
			print "Error getting term size"
			self.cleanup()
		row,col = struct.unpack('HHHH', ws)[0:2]
		self.rows = row
		self.cols = col

	def refresh_screen(self):
		# hide cursor
		self.write(b"\x1b[?25l")
		# position cursor at (1,1)
		self.write(b"\x1b[H")
		self.draw_rows()
		self.write("\x1b[{};{}H".format(self.cy + 1, self.cx + 1))
		# display the cursor
		self.write(b"\x1b[?25h")
		self.draw()
	
	def draw_rows(self):
		for x in range(0,self.rows):
			self.write("~")
			# clear the screen to the right of the cursor
			self.write(b"\x1b[K")
			if x < self.rows - 1:
				self.write("\r\n")
	
	def cleanup(self):
		self.write(b"\x1b[2J")
		self.write(b"\x1b[H")
		self.draw()
		self.disable_raw_mode()
		sys.exit(0)

	def __init__(self):
		self.enable_raw_mode()
		self.buffer = ""
		self.rows = 0
		self.cols = 0
		self.cx = 0
		self.cy = 0
		self.get_window_size()

		


if __name__ == "__main__":
	editor = Editor()
	while True:
		editor.refresh_screen()
		editor.process_keypress()


